"""
Security context for the current request.

The security context represents the authenticated caller
and is propagated through ingestion and retrieval pipelines.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SecurityContext:
    """
    Identity and authorization context for the current request.

    This object is created at the application/security boundary
    and passed into downstream services.

    tenant_id:
        Tenant to which the authenticated caller belongs.

    user_id:
        Identifier of the authenticated user.

    roles:
        Roles assigned to the authenticated user.

    permissions:
        Fine-grained permissions assigned to the user/role.
    """

    tenant_id: str
    user_id: str | None = None

    roles: list[str] = field(
        default_factory=list
    )

    permissions: list[str] = field(
        default_factory=list
    )