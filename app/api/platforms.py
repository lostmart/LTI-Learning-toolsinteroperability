from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.platform import Platform
from app.schemas.platform import PlatformCreate, PlatformResponse

router = APIRouter(prefix="/platforms", tags=["platforms"])


@router.post("/", response_model=PlatformResponse)
def create_platform(platform: PlatformCreate, db: Session = Depends(get_db)):
    """Register a new LMS Platform"""
    
    # Check if issuer already exists
    existing = db.query(Platform).filter(Platform.issuer == platform.issuer).first()
    if existing:
        raise HTTPException(status_code=400, detail="Platform with this issuer already exists")
    
    # Create new platform
    db_platform = Platform(**platform.model_dump())
    db.add(db_platform)
    db.commit()
    db.refresh(db_platform)
    
    return db_platform


@router.get("/", response_model=list[PlatformResponse])
def list_platforms(db: Session = Depends(get_db)):
    """List all registered Platforms"""
    platforms = db.query(Platform).all()
    return platforms


@router.get("/{platform_id}", response_model=PlatformResponse)
def get_platform(platform_id: int, db: Session = Depends(get_db)):
    """Get a specific Platform"""
    platform = db.query(Platform).filter(Platform.id == platform_id).first()
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    return platform