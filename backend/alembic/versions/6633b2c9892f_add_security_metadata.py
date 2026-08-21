"""add security metadata

Revision ID: 6633b2c9892f
Revises: f8eeadb522a0
Create Date: 2026-08-21 15:24:01.517857

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6633b2c9892f'
down_revision: Union[str, Sequence[str], None] = 'f8eeadb522a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ---------------------------------------------------------------
    # 1. Add security columns as nullable temporarily
    # ---------------------------------------------------------------

    op.add_column(
        "documents",
        sa.Column(
            "tenant_id",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "chunks",
        sa.Column(
            "tenant_id",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "chunks",
        sa.Column(
            "access_tags",
            postgresql.ARRAY(sa.String()),
            nullable=True,
        ),
    )

    # ---------------------------------------------------------------
    # 2. Backfill existing documents
    # ---------------------------------------------------------------

    op.execute(
        """
        UPDATE documents
        SET tenant_id = 'default'
        WHERE tenant_id IS NULL
        """
    )

    # ---------------------------------------------------------------
    # 3. Backfill existing chunks
    #
    #    Chunks inherit tenant_id from their parent document.
    # ---------------------------------------------------------------

    op.execute(
        """
        UPDATE chunks
        SET tenant_id = documents.tenant_id
        FROM documents
        WHERE chunks.document_id = documents.id
          AND chunks.tenant_id IS NULL
        """
    )

    # Existing chunks get an empty access-tag list.
    op.execute(
        """
        UPDATE chunks
        SET access_tags = ARRAY[]::VARCHAR[]
        WHERE access_tags IS NULL
        """
    )

    # ---------------------------------------------------------------
    # 4. Enforce NOT NULL after backfill
    # ---------------------------------------------------------------

    op.alter_column(
        "documents",
        "tenant_id",
        existing_type=sa.String(length=100),
        nullable=False,
    )

    op.alter_column(
        "chunks",
        "tenant_id",
        existing_type=sa.String(length=100),
        nullable=False,
    )

    op.alter_column(
        "chunks",
        "access_tags",
        existing_type=postgresql.ARRAY(sa.String()),
        nullable=False,
    )

    # ---------------------------------------------------------------
    # 5. Add indexes
    # ---------------------------------------------------------------

    op.create_index(
        op.f("ix_documents_tenant_id"),
        "documents",
        ["tenant_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_chunks_tenant_id"),
        "chunks",
        ["tenant_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_chunks_tenant_id"),
        table_name="chunks",
    )

    op.drop_index(
        op.f("ix_documents_tenant_id"),
        table_name="documents",
    )

    op.drop_column("chunks", "access_tags")
    op.drop_column("chunks", "tenant_id")
    op.drop_column("documents", "tenant_id")
