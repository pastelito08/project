"""
routers/comments.py
-------------------
Comment endpoints:
- POST   /posts/{post_id}/comments          : add a comment to a post
- GET    /posts/{post_id}/comments          : get all comments for a post
- PUT    /comments/{comment_id}             : update a comment (owner only)
- DELETE /comments/{comment_id}             : delete a comment (owner only)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.post(
    "/posts/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a comment to a post",
)
def create_comment(
    post_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Creates a new comment on a post.
    Optionally set parent_id to reply to another comment.
    Any authenticated user can comment.
    """

    # Check the post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # If replying to a comment, check the parent comment exists
    if comment_data.parent_id:
        parent = db.query(Comment).filter(Comment.id == comment_data.parent_id).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent comment not found",
            )

    # Create the comment
    new_comment = Comment(
        content=comment_data.content,
        post_id=post_id,
        author_id=current_user.id,
        parent_id=comment_data.parent_id,
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment


@router.get(
    "/posts/{post_id}/comments",
    response_model=List[CommentResponse],
    summary="Get all comments for a post",
)
def get_comments(post_id: int, db: Session = Depends(get_db)):
    """
    Returns all top-level comments for a post (parent_id is None).
    Each comment includes its author and any direct replies.
    """

    # Check the post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Only fetch top-level comments — replies are nested via the relationship
    comments = (
        db.query(Comment)
        .filter(Comment.post_id == post_id, Comment.parent_id == None)
        .order_by(Comment.created_at.asc())
        .all()
    )

    return comments


@router.put(
    "/comments/{comment_id}",
    response_model=CommentResponse,
    summary="Update a comment (owner only)",
)
def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Updates a comment's content.
    Only the comment author can edit it.
    """

    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    # Only the comment owner can edit it
    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own comments",
        )

    # Update the content
    comment.content = comment_data.content
    db.commit()
    db.refresh(comment)

    return comment


@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a comment (owner only)",
)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Deletes a comment.
    Only the comment author can delete it.
    Returns 204 No Content on success.
    """

    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments",
        )

    db.delete(comment)
    db.commit()
