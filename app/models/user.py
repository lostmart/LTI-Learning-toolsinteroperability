from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base
from sqlalchemy import UniqueConstraint

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    platform_id = Column(String, ForeignKey("platforms.id"), nullable=False)  # Change from Integer
    lti_user_id = Column(String(255), nullable=False)
    email = Column(String(255))
    name = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_launch_at = Column(DateTime(timezone=True))
    
    __table_args__ = (
        UniqueConstraint('platform_id', 'lti_user_id', name='unique_platform_user'),
    )