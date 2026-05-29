"""
models/follow.py
----------------
Follow table — tracks which users follow which other users.
Unique constraint prevents a user from following the same person twice.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Follow(Base):
    __tablename__ = "follows"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # The user who clicked Follow
    follower_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # The user being followed
    followed_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Prevent duplicate follows
    __table_args__ = (
        UniqueConstraint("follower_id", "followed_id", name="uq_follower_followed"),
    )

    # Relationships back to User
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    followed = relationship("User", foreign_keys=[followed_id], back_populates="followers")

    def __repr__(self):
        return f"<Follow follower={self.follower_id} -> followed={self.followed_id}>"
