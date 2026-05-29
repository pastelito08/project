"""
routers/posts.py
----------------
Post endpoints:
- POST   /posts              : create a new post (authenticated users only)
- GET    /posts              : get all posts with pagination
- GET    /posts/{id}         : get a single post with its comments
- PUT    /posts/{id}         : update a post (owner only)
- DELETE /posts/{id}         : delete a post (owner only)
- GET    /posts/search       : search posts by title, category, or author
- POST   /posts/{id}/like    : like or unlike a post
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.post import Post, Like
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate, PostResponse, PostSummary, PaginatedPosts
from app.utils.dependencies import get_current_user

router = APIRouter()


def build_post_response(post, db):
    """
    Builds a post dict with computed like_count and comment_count.
    Used instead of setting @property attributes directly on the ORM object.
    """
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "category": post.category,
        "tags": post.tags,
        "image_url": post.image_url,
        "is_published": post.is_published,
        "author_id": post.author_id,
        "author": post.author,
        "like_count": len(post.likes),
        "comment_count": len(post.comments),
        "created_at": post.created_at,
        "updated_at": post.updated_at,
    }


@router.post(
    "/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new post",
)
def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Creates a new post for the authenticated user.
    Only users with role 'author' can create posts.
    """
    if current_user.role != "author":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only authors can create posts",
        )

    new_post = Post(
        title=post_data.title,
        content=post_data.content,
        category=post_data.category,
        tags=post_data.tags,
        image_url=post_data.image_url,
        is_published=post_data.is_published,
        author_id=current_user.id,
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return build_post_response(new_post, db)


@router.get(
    "/",
    response_model=PaginatedPosts,
    summary="Get all posts with pagination",
)
def get_posts(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=50, description="Posts per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db),
):
    """
    Returns a paginated list of all published posts.
    Optionally filter by category.
    """
    query = db.query(Post).filter(Post.is_published == True)

    if category:
        query = query.filter(Post.category == category)

    total = query.count()

    posts = (
        query.order_by(Post.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "posts": [build_post_response(p, db) for p in posts],
    }


@router.get(
    "/search",
    response_model=PaginatedPosts,
    summary="Search posts by title, category, or author",
)
def search_posts(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    Searches published posts by title, category, or author username.
    """
    query = (
        db.query(Post)
        .join(User, Post.author_id == User.id)
        .filter(Post.is_published == True)
        .filter(
            Post.title.ilike(f"%{q}%") |
            Post.category.ilike(f"%{q}%") |
            User.username.ilike(f"%{q}%")
        )
    )

    total = query.count()
    posts = (
        query.order_by(Post.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "posts": [build_post_response(p, db) for p in posts],
    }


@router.get(
    "/{post_id}",
    response_model=PostResponse,
    summary="Get a single post with its comments",
)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """
    Returns a single post by ID including author and comment count.
    Raises 404 if the post does not exist.
    """
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found",
        )

    return build_post_response(post, db)


@router.put(
    "/{post_id}",
    response_model=PostResponse,
    summary="Update a post (owner only)",
)
def update_post(
    post_id: int,
    post_data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Updates a post. Only the post owner can update it.
    Only fields provided in the request body are updated.
    """
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own posts")

    update_data = post_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)

    db.commit()
    db.refresh(post)

    return build_post_response(post, db)


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a post (owner only)",
)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Deletes a post. Only the post owner can delete it.
    Returns 204 No Content on success.
    """
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own posts")

    db.delete(post)
    db.commit()


@router.post(
    "/{post_id}/like",
    status_code=status.HTTP_200_OK,
    summary="Like or unlike a post",
)
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Toggles a like on a post.
    If already liked — removes the like. If not — adds a like.
    """
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing_like = (
        db.query(Like)
        .filter(Like.post_id == post_id, Like.user_id == current_user.id)
        .first()
    )

    if existing_like:
        db.delete(existing_like)
        db.commit()
        return {"message": "Post unliked", "liked": False}
    else:
        new_like = Like(post_id=post_id, user_id=current_user.id)
        db.add(new_like)
        db.commit()
        return {"message": "Post liked", "liked": True}
