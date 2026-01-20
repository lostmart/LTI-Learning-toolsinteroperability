from pydantic import BaseModel, HttpUrl
from typing import Optional

class LtiLoginRequest(BaseModel):
    """OIDC Login Initiation Request from LMS"""
    iss: str
    login_hint: str
    target_link_uri: HttpUrl
    lti_message_hint: Optional[str] = None
    client_id: Optional[str] = None
    lti_deployment_id: Optional[str] = None

class LtiLaunchRequest(BaseModel):
    """LTI Launch Request with JWT"""
    id_token: str  # The JWT token
    state: str     # State we generated in login