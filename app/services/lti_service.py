import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.models.platform import Platform

import jwt
import requests
from typing import Dict, Any
from jose import jwk
from jose.backends import RSAKey
from jose import jwt as jose_jwt

# In-memory storage for nonces and state (use Redis in production)
_nonce_store: Dict[str, datetime] = {}
_state_store: Dict[str, dict] = {}

def generate_nonce() -> str:
    """Generate cryptographically secure nonce"""
    return secrets.token_urlsafe(32)

def generate_state() -> str:
    """Generate cryptographically secure state"""
    return secrets.token_urlsafe(32)

def store_nonce(nonce: str, expiry_minutes: int = 10):
    """Store nonce with expiration"""
    expiry = datetime.utcnow() + timedelta(minutes=expiry_minutes)
    _nonce_store[nonce] = expiry

def validate_nonce(nonce: str) -> bool:
    """Check if nonce exists and hasn't expired"""
    if nonce not in _nonce_store:
        return False
    
    if datetime.utcnow() > _nonce_store[nonce]:
        del _nonce_store[nonce]
        return False
    
    # Nonce is valid, remove it (one-time use)
    del _nonce_store[nonce]
    return True

def store_state(state: str, data: dict, expiry_minutes: int = 10):
    """Store state with associated data"""
    _state_store[state] = {
        "data": data,
        "expiry": datetime.utcnow() + timedelta(minutes=expiry_minutes)
    }

def get_state_data(state: str) -> Optional[dict]:
    """Retrieve and validate state data"""
    if state not in _state_store:
        return None
    
    state_info = _state_store[state]
    
    if datetime.utcnow() > state_info["expiry"]:
        del _state_store[state]
        return None
    
    # State is valid, remove it (one-time use)
    data = state_info["data"]
    del _state_store[state]
    return data

def get_platform_by_issuer(db: Session, issuer: str) -> Optional[Platform]:
    """Get platform by issuer URL or fallback to first active platform"""
    # First try to match by ID (if issuer matches a platform ID)
    platform = db.query(Platform).filter(
        Platform.id == issuer,
        Platform.active == True
    ).first()
    
    if platform:
        return platform
    
    # If not found, return the first active platform as fallback
    # (This works for single-platform setups)
    return db.query(Platform).filter(Platform.active == True).first()
    



def fetch_platform_keys(key_set_url: str) -> Dict[str, Any]:
    """Fetch platform's public keys from JWKS endpoint"""
    response = requests.get(key_set_url, timeout=10)
    response.raise_for_status()
    return response.json()

def get_key_by_kid(jwks: Dict[str, Any], kid: str):
    """Find a specific key in a JWKS dictionary and construct a Jose key object"""
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            if "alg" not in key:
                key["alg"] = "RS256"
            # FIX: Use 'jwk' instead of 'jose_jwt'
            return jwk.construct(key) 
    
    return None

def validate_jwt_token(
    token: str,
    platform: Platform,
    expected_nonce: str,
    expected_client_id: str
) -> Dict[str, Any]:
    """
    Validate JWT token from LMS
    
    Steps:
    1. Decode header to get kid
    2. Fetch platform's public keys
    3. Find matching key
    4. Verify signature
    5. Validate claims
    """
    # Decode header without verification (just to get kid)
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")
    
    if not kid:
        raise ValueError("Token missing 'kid' in header")
    
    # Fetch platform's public keys
    platform_keys = fetch_platform_keys(platform.key_set_url)
    
    # Get the specific key
    public_key = get_key_by_kid(platform_keys, kid)
    if not public_key:
        raise ValueError(f"Key with kid '{kid}' not found in platform JWKS")
    
    # Verify and decode token
    try:
        payload = jwt.decode(
            token,
            public_key.to_pem().decode('utf-8'),
            algorithms=["RS256"],
            audience=expected_client_id,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": True
            }
        )
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidAudienceError:
        raise ValueError("Invalid audience")
    except jwt.InvalidSignatureError:
        raise ValueError("Invalid signature")
    except Exception as e:
        raise ValueError(f"Token validation failed: {str(e)}")
    
    # Validate nonce
    token_nonce = payload.get("nonce")
    if not token_nonce or token_nonce != expected_nonce:
        raise ValueError("Invalid or missing nonce")
    
    # Validate issuer
    # if payload.get("iss") != platform.id:
    #     raise ValueError("Issuer mismatch")
    
    return payload