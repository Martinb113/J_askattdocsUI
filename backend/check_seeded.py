"""Check if database has been seeded with initial data."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.config import settings

async def check_seeded():
    """Check if database has been seeded."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as session:
            # Check for admin user
            result = await session.execute(
                text("SELECT attid, display_name FROM users WHERE attid = 'admin'")
            )
            admin = result.fetchone()

            if admin:
                print("[OK] Database has been seeded!")
                print(f"     Admin user found: {admin[1]} (attid: {admin[0]})")

                # Check configurations
                result = await session.execute(text("SELECT COUNT(*) FROM configurations"))
                config_count = result.scalar()
                print(f"     Configurations: {config_count}")

                # Check roles
                result = await session.execute(text("SELECT COUNT(*) FROM roles"))
                role_count = result.scalar()
                print(f"     Roles: {role_count}")

                return True
            else:
                print("[INFO] Database not seeded - no admin user found")
                return False

    except Exception as e:
        print(f"[ERROR] Failed to check seeded data: {e}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_seeded())
