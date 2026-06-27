import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from config import setting
from database import Base

# Import every ORM module so each Table registers on Base.metadata.
# `target_metadata` below is only as complete as these imports — a missing import
# makes `--autogenerate` think a table should be DROPPED. This is the #1 autogenerate gotcha.
import models.user  # noqa: F401


config = context.config

# Wire Python logging from alembic.ini ([loggers]/[handlers]/...). Optional but lets
# students see "Running upgrade c8f01 -> c8f02" output during a migration.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# The "desired" schema: built from the ORM models above. Autogenerate diffs THIS
# against the live database's actual schema (via SQLAlchemy's Inspector).
target_metadata = Base.metadata


def get_url() -> str:
    """Single source of the DB URL — the app's DATABASE_URL, not a copy in alembic.ini.
    Avoids the classic "migrated the wrong database" mistake of a stale ini URL."""
    return setting.database_url


def run_migrations_offline() -> None:
    """OFFLINE apply mode (`alembic upgrade head --sql`): render SQL, do not connect.

    No Engine is created, so no DBAPI/driver is ever imported — the `+asyncpg`
    token in the URL is harmless here. Alembic only uses the dialect to COMPILE
    PostgreSQL DDL; the same SQL is emitted regardless of driver. (This mirrors
    the stock `alembic init -t async` template, which passes the URL unchanged.)
    `literal_binds=True` inlines parameter values so the emitted SQL is runnable as-is.
    """
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Shared online-apply body. Runs on a real connection.

    compare_type / compare_server_default sharpen `--autogenerate` so it notices
    column TYPE and DEFAULT changes (off by default). They only affect autogenerate
    diffing, not hand-written upgrade()/downgrade() calls.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """ONLINE apply mode: open an async engine (asyncpg), then hand the sync-style
    Alembic migration body to `connection.run_sync` so Alembic's synchronous API
    runs correctly on top of the async driver."""
    connectable = async_engine_from_config(
        {"sqlalchemy.url": get_url()},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


# Entry point: Alembic decides offline vs online from the `--sql` flag.
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
