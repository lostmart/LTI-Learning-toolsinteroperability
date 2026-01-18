from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models import Base


class User(Base):
    """User from LTI launch"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # LTI identifiers
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    lti_user_id = Column(String(255), nullable=False, index=True)
    
    # User info from LTI
    email = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_launch_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    platform = relationship("Platform", backref="users")
    
    # Unique: one user per platform
    __table_args__ = (
        UniqueConstraint('platform_id', 'lti_user_id', name='unique_platform_user'),
    )