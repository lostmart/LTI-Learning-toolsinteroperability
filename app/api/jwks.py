from fastapi import APIRouter
from app.core.security import get_jwks

router = APIRouter(tags=["LTI"])

@router.get("/.well-known/jwks.json")
def get_jwks_endpoint():
    """
    JWKS endpoint - publishes public keys for LMS platforms
    
    LMS platforms fetch this to verify signatures on tokens we send
    """
    return get_jwks()