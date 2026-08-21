from app.services.security.context import SecurityContext
from app.services.security.policy import SecurityPolicy



def test_same_tenant_is_allowed():
    context = SecurityContext(
        tenant_id="tenant-a",
        user_id="user-1",
    )

    assert SecurityPolicy.can_access_tenant(
        context,
        "tenant-a",
    )


def test_different_tenant_is_denied():
    context = SecurityContext(
        tenant_id="tenant-a",
        user_id="user-1",
    )

    assert not SecurityPolicy.can_access_tenant(
        context,
        "tenant-b",
    )

def test_ingestion_allowed_for_same_tenant_with_write_permission():
    context = SecurityContext(
        tenant_id="tenant-a",
        user_id="user-1",
        permissions=["document:write"],
    )

    assert SecurityPolicy.can_ingest_document(
        context,
        "tenant-a",
    )


def test_ingestion_denied_for_different_tenant():
    context = SecurityContext(
        tenant_id="tenant-a",
        user_id="user-1",
        permissions=["document:write"],
    )

    assert not SecurityPolicy.can_ingest_document(
        context,
        "tenant-b",
    )


def test_ingestion_denied_without_write_permission():
    context = SecurityContext(
        tenant_id="tenant-a",
        user_id="user-1",
        permissions=["document:read"],
    )

    assert not SecurityPolicy.can_ingest_document(
        context,
        "tenant-a",
    )


def test_retrieval_allowed_for_same_tenant_with_read_permission():
    context = SecurityContext(
        tenant_id="tenant-a",
        user_id="user-1",
        permissions=["document:read"],
    )

    assert SecurityPolicy.can_retrieve_document(
        context,
        "tenant-a",
    )


def test_retrieval_denied_for_different_tenant():
    context = SecurityContext(
        tenant_id="tenant-a",
        user_id="user-1",
        permissions=["document:read"],
    )

    assert not SecurityPolicy.can_retrieve_document(
        context,
        "tenant-b",
    )


def test_retrieval_denied_without_read_permission():
    context = SecurityContext(
        tenant_id="tenant-a",
        user_id="user-1",
        permissions=["document:write"],
    )

    assert not SecurityPolicy.can_retrieve_document(
        context,
        "tenant-a",
    )

def test_ingestion_denied_for_different_tenant():
    context = SecurityContext(
        tenant_id="tenant-a",
        user_id="user-1",
        roles=["user"],
        permissions=["document:write"],
    )

    assert (
        SecurityPolicy.can_ingest_document(
            context,
            "tenant-b",
        )
        is False
    )