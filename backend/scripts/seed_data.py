"""
Seed script to populate database with initial roles, domains, and configurations.

Run this script after database migrations to create default data.

Usage:
    python scripts/seed_data.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.database import async_session_factory
from app.models.user import Role
from app.models.domain import Domain, Configuration
from app.core.security import get_password_hash


async def seed_roles():
    """Create default roles."""
    print("Creating roles...")

    roles_data = [
        {
            "name": "USER",
            "display_name": "User",
            "description": "Basic user with access to general chat (AskAT&T)"
        },
        {
            "name": "OIS",
            "display_name": "OIS Team",
            "description": "OIS team with access to OIS-specific knowledge bases"
        },
        {
            "name": "SIM",
            "display_name": "SIM Team",
            "description": "SIM team with access to SIM-specific knowledge bases"
        },
        {
            "name": "MANAGER",
            "display_name": "Manager",
            "description": "Manager with access to multiple knowledge bases"
        },
        {
            "name": "KNOWLEDGE_STEWARD",
            "display_name": "Knowledge Steward",
            "description": "Knowledge steward with access to manage documentation"
        },
        {
            "name": "ADMIN",
            "display_name": "Administrator",
            "description": "Administrator with full system access"
        },
    ]

    async with async_session_factory() as session:
        created_roles = []

        for role_data in roles_data:
            # Check if role already exists
            stmt = select(Role).where(Role.name == role_data["name"])
            result = await session.execute(stmt)
            existing_role = result.scalar_one_or_none()

            if existing_role:
                print(f"  - Role '{role_data['name']}' already exists, skipping")
                created_roles.append(existing_role)
            else:
                role = Role(**role_data)
                session.add(role)
                created_roles.append(role)
                print(f"  ✓ Created role: {role_data['name']}")

        await session.commit()
        print(f"Roles created: {len([r for r in created_roles if r not in session.new])}")

    return created_roles


async def seed_domains():
    """Create sample AskDocs domains."""
    print("\nCreating domains...")

    domains_data = [
        {
            "domain_key": "att_support",
            "display_name": "AT&T Customer Support",
            "description": "Customer support documentation and FAQs"
        },
        {
            "domain_key": "network_ops",
            "display_name": "Network Operations",
            "description": "Network operations and infrastructure documentation"
        },
        {
            "domain_key": "security_policies",
            "display_name": "Security Policies",
            "description": "Corporate security policies and procedures"
        },
        {
            "domain_key": "hr_policies",
            "display_name": "HR Policies",
            "description": "Human resources policies and employee handbook"
        },
    ]

    async with async_session_factory() as session:
        created_domains = []

        for domain_data in domains_data:
            # Check if domain already exists
            stmt = select(Domain).where(Domain.domain_key == domain_data["domain_key"])
            result = await session.execute(stmt)
            existing_domain = result.scalar_one_or_none()

            if existing_domain:
                print(f"  - Domain '{domain_data['domain_key']}' already exists, skipping")
                created_domains.append(existing_domain)
            else:
                domain = Domain(**domain_data)
                session.add(domain)
                created_domains.append(domain)
                print(f"  ✓ Created domain: {domain_data['display_name']}")

        await session.commit()
        print(f"Domains created: {len([d for d in created_domains if d not in session.new])}")

    return created_domains


async def seed_configurations():
    """Create sample AskDocs configurations with role assignments."""
    print("\nCreating configurations...")

    async with async_session_factory() as session:
        # Get existing roles and domains
        roles_result = await session.execute(select(Role))
        roles = {role.name: role for role in roles_result.scalars().all()}

        domains_result = await session.execute(select(Domain))
        domains = {domain.domain_key: domain for domain in domains_result.scalars().all()}

        configurations_data = [
            {
                "domain_key": "att_support",
                "config_key": "support_prod",
                "display_name": "AT&T Support (Production)",
                "description": "Production customer support knowledge base",
                "environment": "production",
                "role_names": ["USER", "MANAGER", "ADMIN"]
            },
            {
                "domain_key": "network_ops",
                "config_key": "network_ops_prod",
                "display_name": "Network Operations (Production)",
                "description": "Production network operations documentation",
                "environment": "production",
                "role_names": ["OIS", "MANAGER", "ADMIN"]
            },
            {
                "domain_key": "security_policies",
                "config_key": "security_prod",
                "display_name": "Security Policies (Production)",
                "description": "Production security policies and procedures",
                "environment": "production",
                "role_names": ["SIM", "MANAGER", "KNOWLEDGE_STEWARD", "ADMIN"]
            },
            {
                "domain_key": "hr_policies",
                "config_key": "hr_prod",
                "display_name": "HR Policies (Production)",
                "description": "Production HR policies and employee handbook",
                "environment": "production",
                "role_names": ["USER", "MANAGER", "ADMIN"]
            },
            {
                "domain_key": "att_support",
                "config_key": "support_stage",
                "display_name": "AT&T Support (Staging)",
                "description": "Staging customer support knowledge base",
                "environment": "stage",
                "role_names": ["KNOWLEDGE_STEWARD", "ADMIN"]
            },
        ]

        created_count = 0

        for config_data in configurations_data:
            # Check if configuration already exists
            domain = domains.get(config_data["domain_key"])
            if not domain:
                print(f"  ! Domain '{config_data['domain_key']}' not found, skipping config")
                continue

            stmt = select(Configuration).where(
                Configuration.domain_id == domain.id,
                Configuration.config_key == config_data["config_key"]
            )
            result = await session.execute(stmt)
            existing_config = result.scalar_one_or_none()

            if existing_config:
                print(f"  - Configuration '{config_data['config_key']}' already exists, skipping")
            else:
                # Get roles for this configuration
                config_roles = [roles[role_name] for role_name in config_data["role_names"] if role_name in roles]

                config = Configuration(
                    domain_id=domain.id,
                    config_key=config_data["config_key"],
                    display_name=config_data["display_name"],
                    description=config_data["description"],
                    environment=config_data["environment"],
                    is_active=True
                )

                # Assign roles
                config.roles = config_roles

                session.add(config)
                created_count += 1
                print(f"  ✓ Created configuration: {config_data['display_name']} (Roles: {', '.join(config_data['role_names'])})")

        await session.commit()
        print(f"Configurations created: {created_count}")


async def create_admin_user():
    """Create a default admin user for testing."""
    print("\nCreating admin user...")

    admin_data = {
        "attid": "admin",
        "email": "admin@att.com",
        "password": "Admin123!",  # CHANGE THIS IN PRODUCTION!
        "display_name": "Admin User"
    }

    async with async_session_factory() as session:
        # Check if admin already exists
        from app.models.user import User
        stmt = select(User).where(User.attid == admin_data["attid"])
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"  - Admin user already exists, skipping")
            return

        # Get ADMIN role
        stmt = select(Role).where(Role.name == "ADMIN")
        result = await session.execute(stmt)
        admin_role = result.scalar_one_or_none()

        if not admin_role:
            print("  ! ADMIN role not found, cannot create admin user")
            return

        # Create admin user
        admin_user = User(
            attid=admin_data["attid"],
            email=admin_data["email"],
            password_hash=get_password_hash(admin_data["password"]),
            display_name=admin_data["display_name"],
            is_active=True
        )

        admin_user.roles.append(admin_role)

        session.add(admin_user)
        await session.commit()

        print(f"  ✓ Created admin user:")
        print(f"     AT&T ID: {admin_data['attid']}")
        print(f"     Password: {admin_data['password']}")
        print(f"     ⚠️  CHANGE THIS PASSWORD IN PRODUCTION!")


async def main():
    """Run all seed functions."""
    print("=" * 60)
    print("SEEDING DATABASE WITH INITIAL DATA")
    print("=" * 60)

    try:
        await seed_roles()
        await seed_domains()
        await seed_configurations()
        await create_admin_user()

        print("\n" + "=" * 60)
        print("✓ DATABASE SEEDING COMPLETE")
        print("=" * 60)
        print("\nYou can now:")
        print("1. Login with admin credentials (attid: admin, password: Admin123!)")
        print("2. Create additional users via /api/v1/auth/signup")
        print("3. Assign roles to users via /api/v1/admin/users/{user_id}/roles")
        print("4. Test chat endpoints with different configurations")

    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
