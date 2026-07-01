import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from database import Base


@pytest_asyncio.fixture
async def db_session():
    # ── SETUP — runs before each test that requests `db_session` ──────
    # Build a fresh in-memory engine. Every test gets its own DB.
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    # Open an async transactional connection and create every ORM table.
    # `run_sync` bridges SQLAlchemy's sync DDL onto the async connection.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Build the session factory and immediately open one session for the test.
    # `expire_on_commit=False` keeps loaded attrs usable after commit().
    db = async_sessionmaker(engine, expire_on_commit=False)()

    # ── HAND-OFF — pytest pauses the fixture here and runs the test ──
    try:
        yield db  # test receives this as the `db_session` arg

    finally:
        # ── TEARDOWN — runs even if the test raised an exception ────────
        # `try / finally` is the guarantee — without it a failing assert
        # would skip the cleanup and the next test would inherit junk.
        # Release the connection back to the engine's pool.
        await db.close()
        # Wipe the schema. Belt-and-braces — the engine is being disposed
        # next anyway, but explicit cleanup is the lesson here.
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        # Dispose the engine — closes the underlying connection pool.
        await engine.dispose()