"""
models/comment.py
-----------------
Comment table — belongs to a post and a user.
Supports one level of threaded replies via self-referencing parent_id.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Comment(Base):
    __tablename__ = "comments"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Comment body text
    content = Column(Text, nullable=False)

    # FK to the post this comment is on
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)

    # FK to the user who wrote the comment
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Optional: FK to parent comment for threaded replies
    parent_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)

    # Auto-managed timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")
    replies = relationship(
    "Comment",
    primaryjoin="Comment.parent_id == Comment.id",
    foreign_keys=[parent_id],
    lazy="select",
)   

    def __repr__(self):
        return f"<Comment id={self.id} post_id={self.post_id}>"
