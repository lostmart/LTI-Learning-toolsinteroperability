from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.base import Base

class Platform(Base):
    __tablename__ = "platforms"
    
    id = Column(String, primary_key=True)  # issuer URL
    name = Column(String, nullable=False)
    client_id = Column(String, nullable=False)
    
    # OAuth/OIDC endpoints
    auth_login_url = Column(String, nullable=False)
    auth_token_url = Column(String, nullable=False)
    
    # Public keys
    key_set_url = Column(String, nullable=False)
    
    # Optional
    deployment_id = Column(String, nullable=True)
    
    # Metadata
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())