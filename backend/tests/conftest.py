import pytest

from app.core.database import SessionLocal


@pytest.fixture
def db():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()

def override_db():
    from app.core.database import SessionLocal

    db = SessionLocal()

    try:
        yield db
    finally:
        db.rollback()
        db.close()