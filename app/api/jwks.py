from fastapi import APIRouter, Request, Response
from app.core.security import get_jwks

router = APIRouter(tags=["LTI"])

@router.get("/.well-known/jwks.json")
def get_jwks_endpoint(response: Response):
    """
    JWKS endpoint - publishes public keys for LMS platforms.
    We add the bypass header so Localtunnel doesn't block Canvas.
    """
    response.headers["Bypass-Tunnel-Reminder"] = "true"
    return get_jwks()

@router.get("/lti/config.xml")
def get_lti_config_xml(request: Request):
    """
    LTI 1.3 Configuration XML for Canvas
    
    Canvas will fetch this to auto-configure the tool
    """
    base_url = str(request.base_url).rstrip('/')
    
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<cartridge_basiclti_link xmlns="http://www.imsglobal.org/xsd/imslticc_v1p0"
    xmlns:blti="http://www.imsglobal.org/xsd/imsbasiclti_v1p0"
    xmlns:lticm="http://www.imsglobal.org/xsd/imslticm_v1p0"
    xmlns:lticp="http://www.imsglobal.org/xsd/imslticp_v1p0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.imsglobal.org/xsd/imslticc_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticc_v1p0.xsd
    http://www.imsglobal.org/xsd/imsbasiclti_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imsbasiclti_v1p0p1.xsd
    http://www.imsglobal.org/xsd/imslticm_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticm_v1p0.xsd
    http://www.imsglobal.org/xsd/imslticp_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticp_v1p0.xsd">
    <blti:title>LTI Lab Platform</blti:title>
    <blti:description>Coding exercises with LTI 1.3 integration</blti:description>
    <blti:launch_url>{base_url}/lti/launch</blti:launch_url>
    <blti:extensions platform="canvas.instructure.com">
        <lticm:property name="privacy_level">public</lticm:property>
        <lticm:property name="tool_id">lti_lab_platform</lticm:property>
        <lticm:options name="course_navigation">
            <lticm:property name="enabled">true</lticm:property>
            <lticm:property name="text">Lab Exercises</lticm:property>
        </lticm:options>
        <lticm:options name="assignment_selection">
            <lticm:property name="enabled">true</lticm:property>
            <lticm:property name="message_type">LtiResourceLinkRequest</lticm:property>
        </lticm:options>
    </blti:extensions>
    <blti:custom>
        <lticm:property name="canvas_user_id">$Canvas.user.id</lticm:property>
        <lticm:property name="canvas_course_id">$Canvas.course.id</lticm:property>
    </blti:custom>
</cartridge_basiclti_link>"""
    
    return Response(content=xml, media_type="application/xml")


@router.get("/lti/config.json")  # Recommendation: Use JSON for LTI 1.3
def get_lti_config(request: Request, response: Response):
    response.headers["Bypass-Tunnel-Reminder"] = "true"
    base_url = str(request.base_url).rstrip('/')
    
    # LTI 1.3 Tools in Canvas are easier to configure via JSON
    config = {
        "title": "LTI Lab Platform",
        "scopes": [],
        "extensions": [{
            "domain": "major-cases-itch.loca.lt",
            "tool_id": "lti_lab_platform",
            "platform": "canvas.instructure.com",
            "settings": {
                "text": "Lab Exercises",
                "placements": [{
                    "placement": "course_navigation",
                    "target_link_uri": f"{base_url}/lti/launch"
                }]
            }
        }],
        "public_jwk_url": f"{base_url}/.well-known/jwks.json",
        "description": "Coding exercises with LTI 1.3 integration",
        "target_link_uri": f"{base_url}/lti/launch",
        "oidc_initiation_url": f"{base_url}/lti/login"
    }
    return config