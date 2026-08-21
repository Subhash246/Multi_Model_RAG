from app.services.security.dependency import (
    get_security_context,
)


def test_development_security_context():
    context = get_security_context()

    assert context.tenant_id == "default"
    assert context.user_id == "dev-user"

    assert "user" in context.roles

    assert "document:write" in context.permissions
    assert "document:read" in context.permissions