"""
Database Reset and Initialization Script
Safely resets and reinitializes all database tables
"""
import sys
sys.path.append('.')

from shared.database import engine, Base, SessionLocal
from shared.models import User
from shared.auth import get_password_hash
import importlib.util
from datetime import datetime


def import_models_from_service(service_name):
    """Import models from a service"""
    try:
        spec = importlib.util.spec_from_file_location(
            f"{service_name}_models",
            f"services/{service_name}/models.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"Warning: Could not import {service_name} models: {e}")
        return None


def reset_database():
    """Drop and recreate all tables"""
    print("\n" + "="*60)
    print("DATABASE RESET SCRIPT")
    print("="*60 + "\n")
    
    print("WARNING: This will delete all existing data!")
    response = input("Type 'YES' to continue: ")
    
    if response != 'YES':
        print("Operation cancelled.")
        return False
    
    print("\n[1/4] Dropping all tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        print("  ✓ All tables dropped")
    except Exception as e:
        print(f"  ! Error dropping tables: {e}")
    
    print("\n[2/4] Importing service models...")
    services = [
        'guesthouse',
        'vehicle',
        'visitor',
        'colony-maintenance',
        'equipment',
        'vigilance',
        'canteen'
    ]
    
    for service in services:
        models = import_models_from_service(service)
        if models:
            print(f"  ✓ Imported {service}")
        else:
            print(f"  ! Could not import {service}")
    
    print("\n[3/4] Creating all tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("  ✓ All tables created")
    except Exception as e:
        print(f"  ! Error creating tables: {e}")
        return False
    
    print("\n[4/4] Creating default admin user...")
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == "admin@epos.com").first()
        if not existing_admin:
            admin = User(
                email="admin@epos.com",
                employee_id="ADMIN001",
                full_name="System Administrator",
                password_hash=get_password_hash("Admin@123"),
                department="Administration",
                designation="Administrator",
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(admin)
            db.commit()
            print("  ✓ Admin user created (admin@epos.com / Admin@123)")
        else:
            print("  ✓ Admin user already exists")
    except Exception as e:
        print(f"  ! Error creating admin: {e}")
        db.rollback()
    finally:
        db.close()
    
    print("\n" + "="*60)
    print("Database reset complete!")
    print("="*60 + "\n")
    return True


if __name__ == "__main__":
    reset_database()
