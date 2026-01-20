from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
from app.db.base import Base

class Platform(Base):
    __tablename__ = "platforms"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    client_id: Mapped[str] = mapped_column(String)
    auth_login_url: Mapped[str] = mapped_column(String)
    auth_token_url: Mapped[str] = mapped_column(String)
    key_set_url: Mapped[str] = mapped_column(String)
    deployment_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now(), nullable=True)