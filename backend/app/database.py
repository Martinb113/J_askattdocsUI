"""
Database configuration and session management.
Uses async SQLAlchemy 2.0 with PostgreSQL.
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import settings


# Create async engine with connection pooling
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,  # Maximum number of connections in pool
    max_overflow=10,  # Maximum overflow connections
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections every hour
    echo=settings.DEBUG  # Log SQL queries in debug mode
)

# Create async session factory
# CRITICAL: expire_on_commit=False prevents greenlet errors in async
async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,  # CRITICAL for async operations
    autoflush=False,
    class_=AsyncSession
)


# Base class for all models
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


async def get_db() -> AsyncSession:
    """
    Dependency for FastAPI endpoints to get database session.

    Usage:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database by creating all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database engine and connections."""
    await engine.dispose()
