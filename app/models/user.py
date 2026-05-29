"""
models/user.py
--------------
User table — stores account info, credentials, and profile data.
One user can have many posts, comments, and follows.
"""

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Unique login username
    username = Column(String(50), unique=True, nullable=False, index=True)

    # Unique email address
    email = Column(String(255), unique=True, nullable=False, index=True)

    # bcrypt hashed password — never store plain text
    hashed_password = Column(String(255), nullable=False)

    # Optional profile bio
    bio = Column(Text, nullable=True)

    # URL to profile picture (Cloudinary or similar)
    profile_picture_url = Column(String(500), nullable=True)

    # Soft disable without deleting the account
    is_active = Column(Boolean, default=True)

    # "author" can create posts; "reader" can only comment
    role = Column(String(20), default="author", nullable=False)

    # Auto-managed timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    following = relationship(
        "Follow", foreign_keys="Follow.follower_id",
        back_populates="follower", cascade="all, delete-orphan",
    )
    followers = relationship(
        "Follow", foreign_keys="Follow.followed_id",
        back_populates="followed", cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User id={self.id} username={self.username!r}>"
