"""
models/post.py
--------------
Post and Like tables.
A post belongs to one author and can have many comments and likes.
"""

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Post(Base):
    __tablename__ = "posts"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Short searchable title
    title = Column(String(255), nullable=False, index=True)

    # Full post body
    content = Column(Text, nullable=False)

    # Optional category for filtering (e.g. "tech", "lifestyle")
    category = Column(String(100), nullable=True, index=True)

    # Comma-separated tags for filtering (e.g. "python,fastapi")
    tags = Column(String(500), nullable=True)

    # Optional cover image URL
    image_url = Column(String(500), nullable=True)

    # Draft vs published
    is_published = Column(Boolean, default=True)

    # FK to the user who wrote this post
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Auto-managed timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")

    @property
    def like_count(self):
        """Returns total number of likes on this post."""
        return len(self.likes)

    @property
    def tags_list(self):
        """Returns tags as a list instead of a comma-separated string."""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(",")]

    def __repr__(self):
        return f"<Post id={self.id} title={self.title!r}>"


class Like(Base):
    __tablename__ = "likes"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # The user who liked the post
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # The post that was liked
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationship back to post
    post = relationship("Post", back_populates="likes")

    def __repr__(self):
        return f"<Like user_id={self.user_id} post_id={self.post_id}>"
