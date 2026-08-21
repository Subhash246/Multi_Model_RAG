from logging.config import fileConfig

import sys
from pathlib import Path

from alembic import context


# ------------------------------------------------------------------
# Make sure the backend directory is available on Python's path.
# ------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


# ------------------------------------------------------------------
# Application imports
# ------------------------------------------------------------------

from app.core.config import get_settings
from app.core.database import Base

# Import all models so SQLAlchemy metadata contains them.
from app.models import Chunk, Document  # noqa: F401


# ------------------------------------------------------------------
# Alembic configuration
# ------------------------------------------------------------------

config = context.config


# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# ------------------------------------------------------------------
# Application settings
# ------------------------------------------------------------------

settings = get_settings()


# ------------------------------------------------------------------
# SQLAlchemy metadata
# ------------------------------------------------------------------

target_metadata = Base.metadata

def include_object(
    object,
    name,
    type_,
    reflected,
    compare_to,
):
    """
    Control which database objects Alembic manages.

    LiteLLM owns its own tables, so our application
    migrations must ignore them.
    """

    if type_ == "table" and reflected:
        if name.startswith("LiteLLM_"):
            return False

    return True
# ------------------------------------------------------------------
# Offline migrations
# ------------------------------------------------------------------

def run_migrations_offline() -> None:
    """
    Run migrations without creating a database connection.
    """

    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        include_object=include_object,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
    )

    with context.begin_transaction():
        context.run_migrations()


# ------------------------------------------------------------------
# Online migrations
# ------------------------------------------------------------------

def run_migrations_online() -> None:
    """
    Run migrations using a live database connection.
    """

    from sqlalchemy import create_engine
    from sqlalchemy import pool

    connectable = create_engine(
        settings.database_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
    )

        with context.begin_transaction():
            context.run_migrations()


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()