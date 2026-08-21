"""
Security dependencies for API endpoints.

This module is currently a development authentication boundary.

Later this will be replaced by the real authentication
mechanism, such as JWT/OAuth2, without changing downstream
services.
"""

from app.services.security.context import SecurityContext


def get_security_context() -> SecurityContext:
    """
    Return the security context for the current request.

    Temporary development implementation.
    """

    return SecurityContext(
        tenant_id="default",
        user_id="dev-user",
        roles=["user"],
        permissions=[
            "document:write",
            "document:read",
        ],
    )