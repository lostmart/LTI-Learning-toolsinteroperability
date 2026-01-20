from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.platform import Platform
from app.schemas.platform import PlatformCreate, PlatformResponse

router = APIRouter(prefix="/platforms", tags=["platforms"])

@router.post("/", response_model=PlatformResponse, status_code=201)
def create_platform(platform: PlatformCreate, db: Session = Depends(get_db)):
    """Register a new LMS platform"""
    existing = db.query(Platform).filter(Platform.id == platform.id).first()
    if existing:
        raise HTTPException(400, "Platform already registered")
    
    # Convert Pydantic model to dict, then convert HttpUrl to str
    platform_data = platform.model_dump()
    platform_data["auth_login_url"] = str(platform_data["auth_login_url"])
    platform_data["auth_token_url"] = str(platform_data["auth_token_url"])
    platform_data["key_set_url"] = str(platform_data["key_set_url"])
    
    db_platform = Platform(**platform_data)
    db.add(db_platform)
    db.commit()
    db.refresh(db_platform)
    return db_platform

@router.get("/", response_model=List[PlatformResponse])
def list_platforms(db: Session = Depends(get_db)):
    """List all registered platforms"""
    return db.query(Platform).filter(Platform.active == True).all()

@router.get("/{platform_id}", response_model=PlatformResponse)
def get_platform(platform_id: str, db: Session = Depends(get_db)):
    """Get platform by ID"""
    platform = db.query(Platform).filter(Platform.id == platform_id).first()
    if not platform:
        raise HTTPException(404, "Platform not found")
    return platform

@router.delete("/{platform_id}")
def delete_platform(platform_id: str, db: Session = Depends(get_db)):
    """Soft delete platform"""
    platform = db.query(Platform).filter(Platform.id == platform_id).first()
    if not platform:
        raise HTTPException(404, "Platform not found")
    
    platform.active = False
    db.commit()
    return {"message": "Platform deactivated"}