"""
schemas/post.py
---------------
Pydantic schemas for Post endpoints.
- PostCreate     : data required to create a new post
- PostUpdate     : optional fields for editing a post
- PostResponse   : full post data returned by the API (includes author + counts)
- PostSummary    : lighter version used in feed/list responses
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator

from app.schemas.user import UserSummary


# ── Request Schemas ────────────────────────────────────────────────────────────

class PostCreate(BaseModel):
    """Schema for creating a new post — title and content are required."""
    title: str
    content: str
    category: Optional[str] = None
    tags: Optional[str] = None        # comma-separated e.g. "python,fastapi"
    image_url: Optional[str] = None
    is_published: bool = True

    @field_validator("title")
    @classmethod
    def title_valid(cls, v):
        """Title must be between 3 and 255 characters."""
        if len(v.strip()) < 3:
            raise ValueError("Title must be at least 3 characters")
        if len(v) > 255:
            raise ValueError("Title must be under 255 characters")
        return v.strip()

    @field_validator("content")
    @classmethod
    def content_valid(cls, v):
        """Content must not be empty."""
        if len(v.strip()) < 1:
            raise ValueError("Content cannot be empty")
        return v.strip()


class PostUpdate(BaseModel):
    """Schema for updating a post — all fields optional."""
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    image_url: Optional[str] = None
    is_published: Optional[bool] = None


# ── Response Schemas ───────────────────────────────────────────────────────────

class PostResponse(BaseModel):
    """
    Full post response including author details and engagement counts.
    Used for GET /posts/{id} (single post view).
    """
    id: int
    title: str
    content: str
    category: Optional[str] = None
    tags: Optional[str] = None
    image_url: Optional[str] = None
    is_published: bool
    author_id: int
    author: UserSummary           # nested author info
    like_count: int = 0
    comment_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PostSummary(BaseModel):
    """
    Lightweight post response used in feed/list views.
    Excludes full content to keep responses fast.
    """
    id: int
    title: str
    category: Optional[str] = None
    tags: Optional[str] = None
    image_url: Optional[str] = None
    author: UserSummary
    like_count: int = 0
    comment_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedPosts(BaseModel):
    """Wraps a list of posts with pagination metadata."""
    total: int                    # total number of matching posts
    page: int                     # current page number
    per_page: int                 # items per page
    posts: List[PostSummary]      # the posts for this page
