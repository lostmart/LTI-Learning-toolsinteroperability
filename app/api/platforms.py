from datetime import datetime
import json
from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.platform import Platform
from app.models.user import User
from app.schemas.platform import PlatformCreate, PlatformResponse
from app.services import lti_service

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


@router.delete("/{platform_id:path}")  # Add :path to accept slashes
def delete_platform_param(platform_id: str, db: Session = Depends(get_db)):
    """Soft delete platform"""
    platform = db.query(Platform).filter(Platform.id == platform_id).first()
    if not platform:
        raise HTTPException(404, "Platform not found")
    
    platform.active = False
    db.commit()
    return {"message": "Platform deactivated"}


@router.post("/launch")
def lti_launch(
    id_token: str = Form(...),
    state: str = Form(...),
    db: Session = Depends(get_db)
):
    """LTI Launch - Receive and validate JWT from LMS"""
    
    # Validate state
    state_data = lti_service.get_state_data(state)
    if not state_data:
        raise HTTPException(400, "Invalid or expired state")
    
    issuer = state_data["issuer"]
    client_id = state_data["client_id"]
    
    # Get platform
    platform = lti_service.get_platform_by_issuer(db, issuer)
    if not platform:
        raise HTTPException(400, f"Unknown platform: {issuer}")
    
    # Decode JWT without validation first to get nonce
    unverified_payload = jose_jwt.get_unverified_claims(id_token) # type: ignore
    token_nonce = unverified_payload.get("nonce")
    
    # Validate nonce
    if not lti_service.validate_nonce(token_nonce):
        raise HTTPException(400, "Invalid or expired nonce")
    
    # Now validate JWT properly
    try:
        payload = lti_service.validate_jwt_token(
            id_token,
            platform,
            expected_nonce=token_nonce,
            expected_client_id=client_id
        )
    except ValueError as e:
        raise HTTPException(400, f"Token validation failed: {str(e)}")
    
    # Extract user info
    lti_user_id = payload.get("sub")
    email = payload.get("email")
    name = payload.get("name")
    
    if not lti_user_id:
        raise HTTPException(400, "Token missing 'sub' claim")
    
    # Create or update user
    user = db.query(User).filter(
        User.platform_id == platform.id,
        User.lti_user_id == lti_user_id
    ).first()
    
    if not user:
        user = User(
            platform_id=platform.id,
            lti_user_id=lti_user_id,
            email=email,
            name=name
        )
        db.add(user)
    else:
        user.email = email # type: ignore
        user.name = name # type: ignore
        user.last_launch_at = datetime.utcnow() # type: ignore
    
    db.commit()
    db.refresh(user)
    
    # Success page
    return HTMLResponse(f"""
        <html>
            <head><title>LTI Launch Successful</title></head>
            <body style="font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px;">
                <h1>✅ Welcome to LTI Lab Platform!</h1>
                <p>Successfully authenticated via LTI 1.3</p>
                <hr>
                <h2>User Information:</h2>
                <ul>
                    <li><strong>Name:</strong> {name or 'Not provided'}</li>
                    <li><strong>Email:</strong> {email or 'Not provided'}</li>
                    <li><strong>Platform:</strong> {platform.name}</li>
                    <li><strong>User ID:</strong> {lti_user_id}</li>
                </ul>
                <hr>
                <h3>Course Context:</h3>
                <pre>{json.dumps(payload.get('https://purl.imsglobal.org/spec/lti/claim/context', {}), indent=2)}</pre>
                <h3>Assignment:</h3>
                <pre>{json.dumps(payload.get('https://purl.imsglobal.org/spec/lti/claim/resource_link', {}), indent=2)}</pre>
            </body>
        </html>
    """)