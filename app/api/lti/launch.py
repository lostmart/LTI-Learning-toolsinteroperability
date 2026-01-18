from fastapi import APIRouter, Request, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter(prefix="/lti", tags=["lti"])


@router.get("/login")
async def oidc_login(
    iss: str,
    login_hint: str,
    target_link_uri: str,
    lti_message_hint: str | None = None,
):
    """
    OIDC Login Initiation - Step 1 of LTI launch
    Platform sends user here first
    """
    
    # TODO: Validate issuer is a registered platform
    # TODO: Generate state and nonce
    # TODO: Redirect to platform's auth endpoint
    
    return {
        "message": "OIDC Login Initiation",
        "issuer": iss,
        "login_hint": login_hint,
        "target_link_uri": target_link_uri
    }


@router.post("/launch")
async def lti_launch(
    id_token: str = Form(...),
    state: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    LTI Launch - Step 2 
    Platform redirects user here with id_token (JWT)
    """
    
    # TODO: Validate JWT signature
    # TODO: Extract user and context from JWT
    # TODO: Create/update user in database
    # TODO: Create session
    # TODO: Redirect to application
    
    return {
        "message": "LTI Launch received",
        "id_token_length": len(id_token),
        "state": state
    }