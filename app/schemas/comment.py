"""
schemas/comment.py
------------------
Pydantic schemas for Comment endpoints.
- CommentCreate   : data required to post a comment
- CommentUpdate   : optional fields for editing a comment
- CommentResponse : comment data returned by the API (includes author info)
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator

from app.schemas.user import UserSummary


# ── Request Schemas ────────────────────────────────────────────────────────────

class CommentCreate(BaseModel):
    """Schema for creating a comment on a post."""
    content: str
    parent_id: Optional[int] = None    # set this to reply to another comment

    @field_validator("content")
    @classmethod
    def content_valid(cls, v):
        """Comment must not be empty and under 1000 characters."""
        if len(v.strip()) < 1:
            raise ValueError("Comment cannot be empty")
        if len(v) > 1000:
            raise ValueError("Comment must be under 1000 characters")
        return v.strip()


class CommentUpdate(BaseModel):
    """Schema for editing an existing comment — content only."""
    content: str

    @field_validator("content")
    @classmethod
    def content_valid(cls, v):
        """Updated comment must not be empty."""
        if len(v.strip()) < 1:
            raise ValueError("Comment cannot be empty")
        return v.strip()


# ── Response Schemas ───────────────────────────────────────────────────────────

class CommentResponse(BaseModel):
    """
    Comment data returned by the API.
    Includes author info and any direct replies.
    """
    id: int
    content: str
    post_id: int
    author_id: int
    author: UserSummary                         # nested author info
    parent_id: Optional[int] = None             # None if top-level comment
    replies: List["CommentResponse"] = []       # nested replies (one level)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Required for self-referencing model (replies inside CommentResponse)
CommentResponse.model_rebuild()
