from pydantic import BaseModel, HttpUrl
from datetime import datetime


class PlatformCreate(BaseModel):
    """Schema for creating a Platform"""
    issuer: str
    client_id: str
    auth_endpoint: str
    token_endpoint: str
    jwks_endpoint: str
    name: str | None = None


class PlatformResponse(BaseModel):
    """Schema for Platform response"""
    id: int
    issuer: str
    client_id: str
    auth_endpoint: str
    token_endpoint: str
    jwks_endpoint: str
    name: str | None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  # Allows converting SQLAlchemy model to Pydantic