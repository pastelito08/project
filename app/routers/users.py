"""
routers/users.py
----------------
User endpoints:
- GET    /users/me          : get your own profile
- PUT    /users/me          : update your own profile
- DELETE /users/me          : delete your own account
- GET    /users/{id}        : get any user's public profile + their posts
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.post import Post
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.post import PostSummary
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get your own profile",
)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Returns the currently authenticated user's full profile.
    No ID needed — identity comes from the JWT token.
    """
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update your own profile",
)
def update_my_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Updates the authenticated user's profile.
    Only fields provided in the request are updated.
    Checks for username conflicts before saving.
    """

    # If username is being changed, check it's not already taken
    if user_data.username and user_data.username != current_user.username:
        existing = db.query(User).filter(User.username == user_data.username).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

    # Update only the fields that were provided
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return current_user


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete your own account",
)
def delete_my_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Permanently deletes the authenticated user's account.
    All posts and comments by this user are also deleted (cascade).
    Returns 204 No Content on success.
    """
    db.delete(current_user)
    db.commit()


@router.get(
    "/{user_id}",
    summary="Get any user's public profile",
)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """
    Returns a user's public profile including their published posts.
    Used by the frontend profile page.
    Raises 404 if the user does not exist.
    """

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Get all published posts by this user
    posts = (
        db.query(Post)
        .filter(Post.author_id == user_id, Post.is_published == True)
        .order_by(Post.created_at.desc())
        .all()
    )

    # Build post summaries with like and comment counts
    posts_data = [
        {
            "id": p.id,
            "title": p.title,
            "category": p.category,
            "tags": p.tags,
            "image_url": p.image_url,
            "author": user,
            "like_count": len(p.likes),
            "comment_count": len(p.comments),
            "created_at": p.created_at,
        }
        for p in posts
    ]

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "bio": user.bio,
        "profile_picture_url": user.profile_picture_url,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "post_count": len(posts),
        "follower_count": len(user.followers),
        "following_count": len(user.following),
        "posts": posts_data,
    }
