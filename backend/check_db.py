"""Quick script to check if database exists and is accessible."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config import settings

async def check_database():
    """Check if database exists and is accessible."""
    try:
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("[OK] Database connection successful!")
            print(f"     Database: {settings.DATABASE_URL.split('/')[-1]}")
            return True
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_database())
