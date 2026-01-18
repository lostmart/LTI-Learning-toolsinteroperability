from jose import jwt, JWTError
from typing import Dict, Any


def decode_jwt(token: str, public_key: str, algorithms: list[str] = ["RS256"]) -> Dict[str, Any]:
    """
    Decode and validate a JWT token
    
    Args:
        token: The JWT string
        public_key: Public key to verify signature
        algorithms: Allowed algorithms
    
    Returns:
        Decoded JWT payload
    
    Raises:
        JWTError: If validation fails
    """
    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=algorithms,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": False,  # We'll verify manually
            }
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid JWT: {str(e)}")


def validate_lti_token(token: str, platform_jwks: str) -> Dict[str, Any]:
    """
    Validate an LTI 1.3 ID token
    
    Args:
        token: The ID token from LTI launch
        platform_jwks: The platform's public key (JWK or PEM)
    
    Returns:
        Validated token payload
    """
    # For now, just decode without validation
    # We'll add full validation later
    payload = decode_jwt(token, platform_jwks)
    
    # TODO: Validate required LTI claims
    # TODO: Validate nonce
    # TODO: Validate audience
    
    return payload