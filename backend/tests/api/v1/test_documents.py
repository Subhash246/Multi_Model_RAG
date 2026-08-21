from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db
from app.models.document import Document
from app.api.v1.dependencies import get_ingestion_service
from app.services.security.dependency import get_security_context


client = TestClient(app)


# ------------------------------------------------------------------
# Fake security context
# ------------------------------------------------------------------

def fake_security_context():
    from app.services.security.context import SecurityContext

    return SecurityContext(
        tenant_id="default",
        user_id="test-user",
        roles=["user"],
        permissions=[
            "document:write",
            "document:read",
        ],
    )


# ------------------------------------------------------------------
# Fake ingestion service
# ------------------------------------------------------------------

class FakeIngestionService:

    def __init__(self, behavior="success"):
        self.behavior = behavior

    def process_document(
        self,
        document,
        security_context,
    ):
        if self.behavior == "permission":
            raise PermissionError(
                "You do not have permission to process this document."
            )

        if self.behavior == "value":
            raise ValueError(
                "Unsupported document type."
            )

        if self.behavior == "error":
            raise RuntimeError(
                "Unexpected processing failure."
            )

        normalized_document = SimpleNamespace(
            page_count=2,
            character_count=35,
            text="First page content.\nSecond page content.",
        )

        return SimpleNamespace(
            document=normalized_document
        )


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def create_document(db, status="uploaded"):
    document = Document(
        id="api-test-document",
        tenant_id="default",
        filename="test.pdf",
        content_type="application/pdf",
        size_bytes=100,
        storage_key="api-test-document.pdf",
        status=status,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def cleanup_document(db):
    db.query(Document).filter(
        Document.id == "api-test-document"
    ).delete(
        synchronize_session=False
    )

    db.commit()


# ------------------------------------------------------------------
# Fixtures / dependency overrides
# ------------------------------------------------------------------

def override_db():
    db = get_db()

    session = next(db)

    try:
        yield session
    finally:
        session.close()


def override_ingestion_success():
    return FakeIngestionService("success")


def override_ingestion_permission():
    return FakeIngestionService("permission")


def override_ingestion_value():
    return FakeIngestionService("value")


def override_ingestion_error():
    return FakeIngestionService("error")


app.dependency_overrides[get_db] = override_db
app.dependency_overrides[get_security_context] = fake_security_context


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------

def test_process_document_returns_404_for_missing_document():
    app.dependency_overrides[
        get_ingestion_service
    ] = override_ingestion_success

    response = client.post(
        "/api/v1/documents/nonexistent-document/process"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found."


def test_process_document_returns_409_for_processing_document(db):
    app.dependency_overrides[
        get_ingestion_service
    ] = override_ingestion_success

    try:
        create_document(
            db,
            status="processing",
        )

        response = client.post(
            "/api/v1/documents/api-test-document/process"
        )

        assert response.status_code == 409
        assert (
            response.json()["detail"]
            == "Document is already being processed."
        )

    finally:
        cleanup_document(db)


def test_process_document_returns_409_for_processed_document(db):
    app.dependency_overrides[
        get_ingestion_service
    ] = override_ingestion_success

    try:
        create_document(
            db,
            status="processed",
        )

        response = client.post(
            "/api/v1/documents/api-test-document/process"
        )

        assert response.status_code == 409
        assert (
            response.json()["detail"]
            == "Document has already been processed."
        )

    finally:
        cleanup_document(db)


def test_process_document_success(db):
    app.dependency_overrides[
        get_ingestion_service
    ] = override_ingestion_success

    try:
        create_document(
            db,
            status="uploaded",
        )

        response = client.post(
            "/api/v1/documents/api-test-document/process"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["file_id"] == "api-test-document"
        assert data["filename"] == "test.pdf"
        assert data["content_type"] == "application/pdf"
        assert data["status"] == "processed"
        assert data["page_count"] == 2
        assert data["character_count"] == 35
        assert (
            data["extracted_text_preview"]
            == "First page content.\nSecond page content."
        )

        document = (
            db.query(Document)
            .filter(
                Document.id == "api-test-document"
            )
            .first()
        )

        assert document.status == "processed"

    finally:
        cleanup_document(db)


def test_process_document_returns_403_on_permission_error(db):
    app.dependency_overrides[
        get_ingestion_service
    ] = override_ingestion_permission

    try:
        create_document(
            db,
            status="uploaded",
        )

        response = client.post(
            "/api/v1/documents/api-test-document/process"
        )

        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == "You do not have permission to process this document."
        )

        document = (
            db.query(Document)
            .filter(
                Document.id == "api-test-document"
            )
            .first()
        )

        assert document.status == "failed"

    finally:
        cleanup_document(db)


def test_process_document_returns_415_on_value_error(db):
    app.dependency_overrides[
        get_ingestion_service
    ] = override_ingestion_value

    try:
        create_document(
            db,
            status="uploaded",
        )

        response = client.post(
            "/api/v1/documents/api-test-document/process"
        )

        assert response.status_code == 415
        assert (
            response.json()["detail"]
            == "Unsupported document type."
        )

        document = (
            db.query(Document)
            .filter(
                Document.id == "api-test-document"
            )
            .first()
        )

        assert document.status == "failed"

    finally:
        cleanup_document(db)


def test_process_document_returns_500_on_unexpected_error(db):
    app.dependency_overrides[
        get_ingestion_service
    ] = override_ingestion_error

    try:
        create_document(
            db,
            status="uploaded",
        )

        response = client.post(
            "/api/v1/documents/api-test-document/process"
        )

        assert response.status_code == 500
        assert (
            response.json()["detail"]
            == "Failed to process document."
        )

        document = (
            db.query(Document)
            .filter(
                Document.id == "api-test-document"
            )
            .first()
        )

        assert document.status == "failed"

    finally:
        cleanup_document(db)

def test_process_document_returns_404_for_document_from_another_tenant(db):
    app.dependency_overrides[
        get_ingestion_service
    ] = override_ingestion_success

    other_tenant_document_id = "api-test-other-tenant-document"

    try:
        document = Document(
            id=other_tenant_document_id,
            tenant_id="other-tenant",
            filename="other-tenant.pdf",
            content_type="application/pdf",
            size_bytes=100,
            storage_key="api-test-other-tenant-document.pdf",
            status="uploaded",
        )

        db.add(document)
        db.commit()

        response = client.post(
            f"/api/v1/documents/{other_tenant_document_id}/process"
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Document not found."

        # Verify that the document was not modified.
        db.refresh(document)

        assert document.status == "uploaded"
        assert document.tenant_id == "other-tenant"

    finally:
        db.query(Document).filter(
            Document.id == other_tenant_document_id
        ).delete(
            synchronize_session=False
        )
        db.commit()