from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

class PlatformBase(BaseModel):
    name: str
    client_id: str
    auth_login_url: HttpUrl
    auth_token_url: HttpUrl
    key_set_url: HttpUrl
    deployment_id: Optional[str] = None

class PlatformCreate(PlatformBase):
    id: str  # issuer URL

class PlatformResponse(PlatformBase):
    id: str
    active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True  # SQLAlchemy compatibility