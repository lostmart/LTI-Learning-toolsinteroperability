from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.models import Base


class Platform(Base):
    """LMS Platform registration (Moodle, Canvas, etc.)"""
    
    __tablename__ = "platforms"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # LTI identifiers
    issuer = Column(String(500), unique=True, nullable=False, index=True)
    client_id = Column(String(255), nullable=False)
    
    # OAuth/OIDC endpoints
    auth_endpoint = Column(String(500), nullable=False)
    token_endpoint = Column(String(500), nullable=False)
    jwks_endpoint = Column(String(500), nullable=False)
    
    # Platform info
    name = Column(String(255), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())