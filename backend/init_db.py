"""
Comprehensive dependency checker and database initialization validator
Checks all imports, paths, and database setup before running
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    """Check all required Python packages"""
    print("=" * 60)
    print("STEP 1: Checking Python Dependencies")
    print("=" * 60)
    
    required_packages = [
        'sqlalchemy',
        'pydantic',
        'pydantic_settings',
        'fastapi',
        'passlib',
        'jose',
        'uvicorn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print("\n⚠ Missing packages detected!")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n✓ All dependencies installed\n")
    return True


def check_paths():
    """Check all paths and directories"""
    print("=" * 60)
    print("STEP 2: Checking File Structure")
    print("=" * 60)
    
    backend_dir = Path(__file__).parent
    print(f"Backend directory: {backend_dir}")
    
    required_paths = {
        'shared': backend_dir / 'shared',
        'shared/__init__.py': backend_dir / 'shared' / '__init__.py',
        'shared/config.py': backend_dir / 'shared' / 'config.py',
        'shared/database.py': backend_dir / 'shared' / 'database.py',
        'shared/models.py': backend_dir / 'shared' / 'models.py',
        'shared/auth.py': backend_dir / 'shared' / 'auth.py',
    }
    
    all_exist = True
    for name, path in required_paths.items():
        if path.exists():
            print(f"✓ {name}")
        else:
            print(f"✗ {name} - MISSING")
            all_exist = False
    
    # Check data directory
    data_dir = backend_dir / 'data'
    if not data_dir.exists():
        print(f"⚠ data directory doesn't exist, will be created")
        data_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created data directory: {data_dir}")
    else:
        print(f"✓ data directory exists: {data_dir}")
    
    if not all_exist:
        print("\n⚠ Missing required files!")
        return False
    
    print("\n✓ All required files present\n")
    return True


def check_imports():
    """Check if all imports work"""
    print("=" * 60)
    print("STEP 3: Checking Module Imports")
    print("=" * 60)
    
    try:
        print("Importing config...", end=" ")
        from shared.config import settings
        print(f"✓ (DATABASE_URL: {settings.DATABASE_URL})")
        
        print("Importing database...", end=" ")
        from shared.database import Base, engine
        print("✓")
        
        print("Importing models...", end=" ")
        from shared.models import User, Role, UserRole
        print("✓")
        
        print("Importing auth...", end=" ")
        from shared.auth import get_password_hash
        print("✓")
        
        print("\n✓ All imports successful\n")
        return True
        
    except Exception as e:
        print(f"\n✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_connection():
    """Test database connection"""
    print("=" * 60)
    print("STEP 4: Testing Database Connection")
    print("=" * 60)
    
    try:
        from shared.database import engine
        from sqlalchemy import text
        
        # Try to connect
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✓ Database connection successful")
            return True
            
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


def initialize_database():
    """Initialize database with tables"""
    print("=" * 60)
    print("STEP 5: Initializing Database")
    print("=" * 60)
    
    try:
        from shared.database import Base, engine
        from shared.models import User, Role, UserRole
        from shared.auth import get_password_hash
        from sqlalchemy.orm import sessionmaker
        import uuid
        
        print("Creating tables...", end=" ")
        Base.metadata.create_all(bind=engine)
        print("✓")
        
        # Create session
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        try:
            # Check if database is already initialized
            existing_admin = db.query(User).filter(User.email == "admin@epos.com").first()
            if existing_admin:
                print("✓ Database already initialized - Admin user exists")
                print("\n" + "=" * 60)
                print("✅ DATABASE READY!")
                print("=" * 60)
                print("\n📧 Default Admin Credentials:")
                print("   Email: admin@epos.com")
                print("   Password: Admin@123")
                print("=" * 60 + "\n")
                return True
            
            print("Creating default roles...", end=" ")
            roles_data = [
                {"name": "Admin", "description": "System Administrator"},
                {"name": "Manager", "description": "Department Manager"},
                {"name": "Resident", "description": "Colony Resident"},
                {"name": "Staff", "description": "Support Staff"},
            ]
            
            roles = []
            for role_data in roles_data:
                # Check if role already exists
                existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
                if existing_role:
                    roles.append(existing_role)
                else:
                    role = Role(
                        id=str(uuid.uuid4()),
                        name=role_data["name"],
                        description=role_data["description"]
                    )
                    db.add(role)
                    roles.append(role)
            
            db.commit()
            print("✓")
            
            print("Creating admin user...", end=" ")
            admin_user = User(
                id=str(uuid.uuid4()),
                employee_id="ADMIN001",
                email="admin@epos.com",
                full_name="System Administrator",
                password_hash=get_password_hash("Admin@123"),
                phone="+91-9876543210",
                department="IT",
                designation="System Admin",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("✓")
            
            print("Assigning admin role...", end=" ")
            admin_role = db.query(Role).filter(Role.name == "Admin").first()
            user_role = UserRole(
                user_id=admin_user.id,
                role_id=admin_role.id
            )
            db.add(user_role)
            db.commit()
            print("✓")
            
            print("\n" + "=" * 60)
            print("✅ DATABASE INITIALIZATION SUCCESSFUL!")
            print("=" * 60)
            print("\n📧 Default Admin Credentials:")
            print("   Email: admin@epos.com")
            print("   Password: Admin@123")
            print("=" * 60 + "\n")
            
            return True
            
        except Exception as e:
            print(f"\n✗ Error during initialization: {e}")
            db.rollback()
            import traceback
            traceback.print_exc()
            return False
        finally:
            db.close()
            
    except Exception as e:
        print(f"\n✗ Failed to initialize database: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all checks and initialize database"""
    print("\n" + "=" * 60)
    print("ePOS DATABASE INITIALIZATION")
    print("=" * 60 + "\n")
    
    # Run all checks
    checks = [
        ("Dependencies", check_dependencies),
        ("File Structure", check_paths),
        ("Module Imports", check_imports),
        ("Database Connection", test_database_connection),
    ]
    
    for check_name, check_func in checks:
        if not check_func():
            print(f"\n❌ {check_name} check failed!")
            print("Please fix the issues above and try again.")
            sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        print("\n❌ Database initialization failed!")
        sys.exit(1)
    
    print("✅ All checks passed! Database is ready to use.\n")


if __name__ == "__main__":
    main()
