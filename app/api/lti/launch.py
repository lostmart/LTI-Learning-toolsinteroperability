from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import urlencode
from jose import jwt as jose_jwt
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization
import json

from app.db.session import get_db
from app.schemas.lti import LtiLoginRequest
from app.services import lti_service
from app.models.user import User
from app.core.security import load_private_key

router = APIRouter(prefix="/lti", tags=["LTI"])

@router.get("/login")
def lti_login(
    request: Request,
    db: Session = Depends(get_db)
):
    """OIDC Login Initiation - First step of LTI 1.3 launch"""
    params = dict(request.query_params)
    
    if "iss" not in params or "login_hint" not in params:
        raise HTTPException(400, "Missing required parameters: iss, login_hint")
    
    issuer = params["iss"]
    login_hint = params["login_hint"]
    target_link_uri = params.get("target_link_uri", f"{request.base_url}lti/launch")
    client_id = params.get("client_id")
    lti_message_hint = params.get("lti_message_hint")
    
    platform = lti_service.get_platform_by_issuer(db, issuer)
    if not platform:
        raise HTTPException(400, f"Unknown platform: {issuer}")
    
    if not client_id:
        client_id = platform.client_id
    
    state = lti_service.generate_state()
    nonce = lti_service.generate_nonce()
    
    lti_service.store_state(state, {
        "issuer": issuer,
        "target_link_uri": target_link_uri,
        "client_id": client_id
    })
    
    lti_service.store_nonce(nonce)
    
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
    
    auth_url = f"{platform.auth_login_url}?{urlencode(auth_params)}"
    
    return RedirectResponse(url=auth_url, status_code=302)


@router.get("/mock-auth")
def mock_auth(
    request: Request,
    db: Session = Depends(get_db)
):
    """TESTING ONLY: Mock LMS authorization endpoint"""
    params = dict(request.query_params)
    
    state = params.get("state")
    nonce = params.get("nonce")
    redirect_uri = params.get("redirect_uri")
    client_id = params.get("client_id")
    
    if not all([state, nonce, redirect_uri]):
        return HTMLResponse("<h1>Error: Missing parameters</h1>", status_code=400)
    
    private_key = load_private_key()
    
    payload = {
        "iss": "https://moodle.example.edu",
        "sub": "test_user_12345",
        "aud": client_id,
        "exp": datetime.utcnow() + timedelta(minutes=5),
        "iat": datetime.utcnow(),
        "nonce": nonce,
        "name": "Test Student",
        "email": "student@example.com",
        "https://purl.imsglobal.org/spec/lti/claim/message_type": "LtiResourceLinkRequest",
        "https://purl.imsglobal.org/spec/lti/claim/version": "1.3.0",
        "https://purl.imsglobal.org/spec/lti/claim/roles": [
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner"
        ],
        "https://purl.imsglobal.org/spec/lti/claim/context": {
            "id": "course_123",
            "label": "CS101",
            "title": "Introduction to Computer Science"
        },
        "https://purl.imsglobal.org/spec/lti/claim/resource_link": {
            "id": "assignment_456",
            "title": "Lab Exercise 1"
        }
    }
    
    id_token = jose_jwt.encode(
        payload,
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8'),
        algorithm="RS256",
        headers={"kid": "lti-key-1"}
    )
    
    return HTMLResponse(f"""
        <html>
        <body>
            <h3>Mock LMS - Auto-redirecting to your tool...</h3>
            <form id="ltiLaunchForm" method="POST" action="{redirect_uri}">
                <input type="hidden" name="id_token" value="{id_token}">
                <input type="hidden" name="state" value="{state}">
                <button type="submit">Continue to Tool</button>
            </form>
            <script>
                document.getElementById('ltiLaunchForm').submit();
            </script>
        </body>
        </html>
    """)


@router.post("/launch")
def lti_launch(
    id_token: str = Form(...),
    state: str = Form(...),
    db: Session = Depends(get_db)
):
    """LTI Launch - Receive and validate JWT from LMS"""
    
    state_data = lti_service.get_state_data(state)
    if not state_data:
        raise HTTPException(400, "Invalid or expired state")
    
    issuer = state_data["issuer"]
    client_id = state_data["client_id"]
    
    platform = lti_service.get_platform_by_issuer(db, issuer)
    if not platform:
        raise HTTPException(400, f"Unknown platform: {issuer}")
    
    unverified_payload = jose_jwt.get_unverified_claims(id_token)
    token_nonce = unverified_payload.get("nonce")
    
    if not lti_service.validate_nonce(token_nonce):
        raise HTTPException(400, "Invalid or expired nonce")
    
    try:
        payload = lti_service.validate_jwt_token(
            id_token,
            platform,
            expected_nonce=token_nonce,
            expected_client_id=client_id
        )
    except ValueError as e:
        raise HTTPException(400, f"Token validation failed: {str(e)}")
    
    lti_user_id = payload.get("sub")
    email = payload.get("email")
    name = payload.get("name")
    
    if not lti_user_id:
        raise HTTPException(400, "Token missing 'sub' claim")
    
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
        user.email = email
        user.name = name
        user.last_launch_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
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