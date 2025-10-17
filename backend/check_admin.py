"""Check admin user credentials and try to authenticate."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select
from app.config import settings
from app.models.user import User
from app.core.security import verify_password

async def check_admin():
    """Check admin user and test password."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as session:
            # Get admin user
            stmt = select(User).where(User.attid == 'admin')
            result = await session.execute(stmt)
            admin = result.scalar_one_or_none()

            if admin:
                print("[OK] Admin user found:")
                print(f"     AT&T ID: {admin.attid}")
                print(f"     Email: {admin.email}")
                print(f"     Display Name: {admin.display_name}")
                print(f"     Is Active: {admin.is_active}")
                print(f"     Password Hash (first 50 chars): {admin.password_hash[:50]}...")

                # Test password verification
                print("\n[TEST] Testing password 'Admin123!':")
                is_valid = verify_password("Admin123!", admin.password_hash)
                if is_valid:
                    print("     [OK] Password verification successful!")
                else:
                    print("     [ERROR] Password verification failed!")
                    print("     The password hash may be incorrect.")
            else:
                print("[ERROR] Admin user not found!")

    except Exception as e:
        print(f"[ERROR] Failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_admin())
