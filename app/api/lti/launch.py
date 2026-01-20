from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import urlencode

from app.db.session import get_db
from app.schemas.lti import LtiLoginRequest
from app.services import lti_service

router = APIRouter(prefix="/lti", tags=["LTI"])

@router.get("/login")
def lti_login(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    OIDC Login Initiation - First step of LTI 1.3 launch
    
    LMS redirects student here to initiate authentication
    """
    # Parse query parameters
    params = dict(request.query_params)
    
    # Validate required parameters
    if "iss" not in params or "login_hint" not in params:
        raise HTTPException(400, "Missing required parameters: iss, login_hint")
    
    issuer = params["iss"]
    login_hint = params["login_hint"]
    target_link_uri = params.get("target_link_uri", f"{request.base_url}lti/launch")
    client_id = params.get("client_id")
    lti_message_hint = params.get("lti_message_hint")
    
    # Get platform configuration
    platform = lti_service.get_platform_by_issuer(db, issuer)
    if not platform:
        raise HTTPException(400, f"Unknown platform: {issuer}")
    
    # Use client_id from request or platform config
    if not client_id:
        client_id = platform.client_id
    
    # Generate security tokens
    state = lti_service.generate_state()
    nonce = lti_service.generate_nonce()
    
    # Store state with context
    lti_service.store_state(state, {
        "issuer": issuer,
        "target_link_uri": target_link_uri,
        "client_id": client_id
    })
    
    # Store nonce for validation later
    lti_service.store_nonce(nonce)
    
    # Build OIDC authorization request
    auth_params = {
        "response_type": "id_token",
        "response_mode": "form_post",
        "scope": "openid",
        "client_id": client_id,
        "redirect_uri": target_link_uri,
        "login_hint": login_hint,
        "state": state,
        "nonce": nonce,
        "prompt": "none"
    }
    
    if lti_message_hint:
        auth_params["lti_message_hint"] = lti_message_hint
    
    # Redirect to LMS authorization endpoint
    auth_url = f"{platform.auth_login_url}?{urlencode(auth_params)}"
    
    return RedirectResponse(url=auth_url, status_code=302)