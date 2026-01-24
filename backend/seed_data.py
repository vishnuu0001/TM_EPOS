"""
Seed data script for ePOS system
Populates database with sample data for all modules
"""
import sys
import os
sys.path.append('.')

from shared.database import SessionLocal, init_db
from shared.models import User
from shared.auth import get_password_hash
from datetime import datetime, date, timedelta
import json
import importlib.util


def import_from_path(module_name, file_path):
    """Import a module from a specific file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Import models from different services
guesthouse_models = import_from_path("guesthouse_models", "services/guesthouse/models.py")
vehicle_models = import_from_path("vehicle_models", "services/vehicle/models.py")
visitor_models = import_from_path("visitor_models", "services/visitor/models.py")
colony_models = import_from_path("colony_models", "services/colony-maintenance/models.py")
equipment_models = import_from_path("equipment_models", "services/equipment/models.py")
vigilance_models = import_from_path("vigilance_models", "services/vigilance/models.py")
canteen_models = import_from_path("canteen_models", "services/canteen/models.py")

# Extract classes
Room = guesthouse_models.Room
Booking = guesthouse_models.Booking
Vehicle = vehicle_models.Vehicle
Driver = vehicle_models.Driver
VehicleRequisition = vehicle_models.VehicleRequisition
VisitorRequest = visitor_models.VisitorRequest
MaintenanceRequest = colony_models.MaintenanceRequest
Vendor = colony_models.Vendor
Asset = colony_models.Asset
ServiceCategory = colony_models.ServiceCategory
Equipment = equipment_models.Equipment
Checkpoint = vigilance_models.Checkpoint
Worker = canteen_models.Worker
Menu = canteen_models.Menu
MenuItem = canteen_models.MenuItem


def create_users(db):
    """Create sample users"""
    print("Creating users...")
    
    users = [
        {
            "email": "admin@epos.com",
            "employee_id": "EMP0001",
            "full_name": "Admin User",
            "password": "Admin@123",
            "department": "Administration",
            "designation": "Administrator",
            "is_active": True
        },
        {
            "email": "manager@epos.com",
            "employee_id": "EMP0002",
            "full_name": "Manager User",
            "password": "Manager@123",
            "department": "Management",
            "designation": "Manager",
            "is_active": True
        },
        {
            "email": "supervisor@epos.com",
            "employee_id": "EMP0003",
            "full_name": "Supervisor User",
            "password": "Supervisor@123",
            "department": "Operations",
            "designation": "Supervisor",
            "is_active": True
        },
        {
            "email": "employee@epos.com",
            "employee_id": "EMP0004",
            "full_name": "Employee User",
            "password": "Employee@123",
            "department": "Operations",
            "designation": "Employee",
            "is_active": True
        }
    ]
    
    created_users = []
    for user_data in users:
        # Check if user already exists
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            user = User(
                email=user_data["email"],
                employee_id=user_data["employee_id"],
                full_name=user_data["full_name"],
                password_hash=get_password_hash(user_data["password"]),
                department=user_data["department"],
                designation=user_data["designation"],
                is_active=user_data["is_active"]
            )
            db.add(user)
            created_users.append(user)
    
    db.commit()
    print(f"âœ“ Created {len(created_users)} users")
    return created_users


def create_guesthouse_data(db, users):
    """Create sample guest house data"""
    print("Creating guest house data...")
    
    # Check if rooms already exist
    existing_rooms = db.query(Room).count()
    if existing_rooms > 0:
        print(f"  Skipping - {existing_rooms} rooms already exist")
        return
    
    # Create rooms
    rooms = [
        {"room_number": "101", "room_type": "single", "floor": 1, "capacity": 1, "rate_per_night": 1500, "status": "available"},
        {"room_number": "102", "room_type": "double", "floor": 1, "capacity": 2, "rate_per_night": 2000, "status": "available"},
        {"room_number": "103", "room_type": "suite", "floor": 1, "capacity": 4, "rate_per_night": 3500, "status": "available"},
        {"room_number": "201", "room_type": "single", "floor": 2, "capacity": 1, "rate_per_night": 1500, "status": "occupied"},
        {"room_number": "202", "room_type": "double", "floor": 2, "capacity": 2, "rate_per_night": 2000, "status": "available"},
        {"room_number": "203", "room_type": "suite", "floor": 2, "capacity": 4, "rate_per_night": 3500, "status": "maintenance"},
    ]
    
    for room_data in rooms:
        room = Room(**room_data)
        db.add(room)
    
    db.commit()
    
    # Create bookings
    room_objs = db.query(Room).all()
    bookings = [
        {
            "booking_number": "BK202600001",
            "guest_name": "Rajesh Kumar",
            "guest_phone": "9876543210",
            "guest_email": "rajesh@example.com",
            "check_in_date": date.today() + timedelta(days=1),
            "check_out_date": date.today() + timedelta(days=3),
            "room_id": room_objs[0].id,
            "number_of_guests": 1,
            "total_amount": 3000,
            "status": "Confirmed"
        },
        {
            "booking_number": "BK202600002",
            "guest_name": "Priya Sharma",
            "guest_phone": "9876543211",
            "guest_email": "priya@example.com",
            "check_in_date": date.today(),
            "check_out_date": date.today() + timedelta(days=2),
            "room_id": room_objs[3].id,
            "number_of_guests": 2,
            "total_amount": 4000,
            "status": "CheckedIn"
        }
    ]
    
    for booking_data in bookings:
        booking = Booking(**booking_data)
        db.add(booking)
    
    db.commit()
    print("âœ“ Created 6 rooms and 2 bookings")


def create_vehicle_data(db, users):
    """Create sample vehicle data"""
    print("Creating vehicle data...")
    
    # Check if vehicles already exist
    existing = db.query(Vehicle).count()
    if existing > 0:
        print(f"  Skipping - {existing} vehicles already exist")
        return
    
    # Create vehicles
    vehicles = [
        {"registration_number": "DL01AB1234", "vehicle_type": "CAR", "make": "Maruti", "model": "Swift", "year": 2020, "capacity": 4, "fuel_type": "Petrol", "current_odometer": 15000, "status": "AVAILABLE"},
        {"registration_number": "DL01CD5678", "vehicle_type": "CAR", "make": "Mahindra", "model": "Scorpio", "year": 2021, "capacity": 7, "fuel_type": "Diesel", "current_odometer": 25000, "status": "AVAILABLE"},
        {"registration_number": "DL01EF9012", "vehicle_type": "BUS", "make": "Tata", "model": "LP 410", "year": 2019, "capacity": 30, "fuel_type": "Diesel", "current_odometer": 50000, "status": "IN_USE"}
    ]
    
    for vehicle_data in vehicles:
        vehicle = Vehicle(**vehicle_data)
        db.add(vehicle)
    
    db.commit()
    
    # Create drivers - must have user_id and license_expiry
    from datetime import timedelta
    # Get actual users from database to ensure we have the right ones
    all_users = db.query(User).all()
    if len(all_users) < 2:
        print("  Skipping drivers - not enough users in database")
        return
    
    drivers = [
        {
            "user_id": all_users[1].id if len(all_users) > 1 else all_users[0].id,
            "license_number": "DL123456",
            "license_expiry": datetime.now() + timedelta(days=365),
            "license_type": "Light Motor Vehicle",
            "is_active": True
        },
        {
            "user_id": all_users[2].id if len(all_users) > 2 else all_users[0].id,
            "license_number": "DL789012",
            "license_expiry": datetime.now() + timedelta(days=730),
            "license_type": "Heavy Vehicle",
            "is_active": True
        }
    ]
    
    for driver_data in drivers:
        # Check if driver already exists
        existing = db.query(Driver).filter(Driver.license_number == driver_data["license_number"]).first()
        if not existing:
            driver = Driver(**driver_data)
            db.add(driver)
    
    db.commit()
    
    # Create requisitions
    vehicle_objs = db.query(Vehicle).all()
    requisitions = [
        {
            "requisition_number": "VR202600001",
            "requester_id": users[0].id,
            "requester_name": users[0].full_name,
            "department": "HR",
            "purpose": "Site Visit",
            "destination": "Gurgaon Plant",
            "pickup_location": "Main Office",
            "requested_date": date.today() + timedelta(days=1),
            "requested_time": "10:00",
            "number_of_passengers": 3,
            "vehicle_type": "Sedan",
            "status": "Pending"
        }
    ]
    
    for req_data in requisitions:
        req = VehicleRequisition(**req_data)
        db.add(req)
    
    db.commit()
    print("âœ“ Created 3 vehicles, 2 drivers, and 1 requisition")


def create_visitor_data(db, users):
    """Create sample visitor data"""
    print("Creating visitor data...")
    
    # Check if visitor requests exist
    existing = db.query(VisitorRequest).count()
    if existing > 0:
        print(f"  Skipping - {existing} visitor requests already exist")
        return
    
    # Create visitor requests
    all_users = db.query(User).all()
    if len(all_users) == 0:
        print("  Skipping - no users in database")
        return
    
    requests = [
        {
            "request_number": "VR202600001",
            "visitor_name": "Amit Verma",
            "visitor_company": "ABC Corp",
            "visitor_phone": "9876543230",
            "visitor_email": "amit@abccorp.com",
            "visitor_type": "business",
            "sponsor_employee_id": all_users[0].id,
            "sponsor_name": all_users[0].full_name,
            "sponsor_department": all_users[0].department,
            "purpose_of_visit": "Business Meeting to discuss new project collaboration",
            "visit_date": datetime.combine(date.today() + timedelta(days=1), datetime.min.time()),
            "expected_duration": 2,
            "areas_to_visit": "Conference Room A, Production Floor",
            "status": "submitted",
            "safety_required": True,
            "medical_required": False
        }
    ]
    
    for req_data in requests:
        req = VisitorRequest(**req_data)
        db.add(req)
    
    db.commit()
    print("âœ“ Created 1 visitor request")


def create_colony_data(db, users):
    """Create sample colony maintenance data"""
    print("Creating colony maintenance data...")
    
    # Check if service categories exist
    existing = db.query(ServiceCategory).count()
    if existing > 0:
        print(f"  Skipping - {existing} service categories already exist")
        return
    
    # Create service categories
    categories = [
        {"name": "Plumbing", "description": "Water supply and drainage"},
        {"name": "Electrical", "description": "Electrical repairs and maintenance"},
        {"name": "Carpentry", "description": "Furniture and fixture repairs"},
        {"name": "Painting", "description": "Interior and exterior painting"}
    ]
    
    for cat_data in categories:
        category = ServiceCategory(**cat_data)
        db.add(category)
    
    db.commit()
    
    # Create vendors
    vendors = [
        {"name": "Quick Fix Plumbing", "category": "Plumbing", "contact_person": "Raju", "phone": "9876543240", "is_active": True},
        {"name": "Bright Electricals", "category": "Electrical", "contact_person": "Suresh", "phone": "9876543241", "is_active": True}
    ]
    
    for vendor_data in vendors:
        vendor = Vendor(**vendor_data)
        db.add(vendor)
    
    db.commit()
    
    # Create assets
    assets = [
        {"asset_number": "AST00001", "name": "Water Pump", "category": "Equipment", "location": "Building A", "status": "Operational"},
        {"asset_number": "AST00002", "name": "Generator", "category": "Equipment", "location": "Building B", "status": "Operational"}
    ]
    
    for asset_data in assets:
        asset = Asset(**asset_data)
        db.add(asset)
    
    db.commit()
    
    # Create maintenance requests
    requests = [
        {
            "request_number": "MR202600001",
            "resident_id": users[3].id,
            "category": "Plumbing",
            "title": "Leaking Tap",
            "description": "Kitchen tap is leaking water",
            "location": "A-101",
            "priority": "Medium",
            "status": "Open"
        }
    ]
    
    for req_data in requests:
        req = MaintenanceRequest(**req_data)
        db.add(req)
    
    db.commit()
    print("âœ“ Created 4 categories, 2 vendors, 2 assets, and 1 maintenance request")


def create_equipment_data(db, users):
    """Create sample equipment data"""
    print("Creating equipment data...")
    
    # Check if equipment exists
    existing = db.query(Equipment).count()
    if existing > 0:
        print(f"  Skipping - {existing} equipment already exist")
        return
    
    # Create equipment
    equipment_list = [
        {"equipment_number": "EQ00001", "name": "Overhead Crane", "equipment_type": "CRANE", "capacity": "10 Ton", "location": "Bay 1", "status": "AVAILABLE", "hourly_rate": 500, "requires_certification": True},
        {"equipment_number": "EQ00002", "name": "Forklift 5T", "equipment_type": "FORKLIFT", "capacity": "5 Ton", "location": "Warehouse", "status": "AVAILABLE", "hourly_rate": 300, "requires_certification": True},
        {"equipment_number": "EQ00003", "name": "Excavator CAT", "equipment_type": "EXCAVATOR", "capacity": "20 Ton", "location": "Yard", "status": "IN_USE", "hourly_rate": 800, "requires_certification": True}
    ]
    
    for eq_data in equipment_list:
        equipment = Equipment(**eq_data)
        db.add(equipment)
    
    db.commit()
    print("âœ“ Created 3 equipment items")


def create_vigilance_data(db, users):
    """Create sample vigilance data"""
    print("Creating vigilance data...")
    
    # Check if checkpoints exist
    existing = db.query(Checkpoint).count()
    if existing > 0:
        print(f"  Skipping - {existing} checkpoints already exist")
        return
    
    # Create checkpoints
    checkpoints = [
        {"checkpoint_number": "CP001", "name": "Main Gate", "location": "North Entrance", "qr_code": "MG001", "is_active": True},
        {"checkpoint_number": "CP002", "name": "Building A", "location": "Building A Entrance", "qr_code": "BA001", "is_active": True},
        {"checkpoint_number": "CP003", "name": "Warehouse", "location": "Warehouse Gate", "qr_code": "WH001", "is_active": True}
    ]
    
    for cp_data in checkpoints:
        checkpoint = Checkpoint(**cp_data)
        db.add(checkpoint)
    
    db.commit()
    print("âœ“ Created 3 checkpoints")


def create_canteen_data(db, users):
    """Create sample canteen data"""
    print("Creating canteen data...")
    
    # Check if workers exist
    existing = db.query(Worker).count()
    if existing > 0:
        print(f"  Skipping - {existing} workers already exist")
        return
    
    # Create workers
    workers = [
        {"worker_number": "W202600001", "full_name": "Mohan Kumar", "employee_id": "EMP001", "worker_type": "permanent", "department": "Production", "is_active": True, "canteen_access": True, "wallet_balance": 500},
        {"worker_number": "W202600002", "full_name": "Ramesh Singh", "employee_id": "EMP002", "worker_type": "contract", "department": "Maintenance", "is_active": True, "canteen_access": True, "wallet_balance": 300}
    ]
    
    for worker_data in workers:
        worker = Worker(**worker_data)
        db.add(worker)
    
    db.commit()
    
    # Create menu for today
    today = date.today()
    menus = [
        {"menu_date": today, "meal_type": "breakfast", "menu_name": "Breakfast Menu", "is_active": True, "is_published": True},
        {"menu_date": today, "meal_type": "lunch", "menu_name": "Lunch Menu", "is_active": True, "is_published": True},
        {"menu_date": today, "meal_type": "dinner", "menu_name": "Dinner Menu", "is_active": True, "is_published": True}
    ]
    
    for menu_data in menus:
        menu = Menu(**menu_data)
        db.add(menu)
    
    db.commit()
    
    # Create menu items
    menu_objs = db.query(Menu).all()
    if menu_objs:
        items = [
            {"menu_id": menu_objs[0].id, "item_name": "Poha", "category": "Main", "base_price": 30, "subsidized_price": 10, "is_available": True, "quantity_prepared": 50, "quantity_remaining": 50},
            {"menu_id": menu_objs[1].id, "item_name": "Dal Tadka", "category": "Dal", "base_price": 40, "subsidized_price": 15, "is_available": True, "quantity_prepared": 100, "quantity_remaining": 100},
            {"menu_id": menu_objs[1].id, "item_name": "Roti", "category": "Roti", "base_price": 10, "subsidized_price": 5, "is_available": True, "quantity_prepared": 200, "quantity_remaining": 200},
            {"menu_id": menu_objs[2].id, "item_name": "Rice", "category": "Rice", "base_price": 30, "subsidized_price": 10, "is_available": True, "quantity_prepared": 80, "quantity_remaining": 80}
        ]
        
        for item_data in items:
            item = MenuItem(**item_data)
            db.add(item)
        
        db.commit()
    
    print("âœ“ Created 2 workers, 3 menus, and 4 menu items")


def main():
    """Main seed function"""
    print("\n" + "="*50)
    print("ePOS Database Seed Script")
    print("="*50 + "\n")
    
    # Initialize database
    print("Initializing database...")
    init_db()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Create users first (needed for foreign keys)
        users = create_users(db)
        
        # Get existing users if they weren't just created
        if not users:
            users = db.query(User).all()
        
        # Create data for all modules
        create_guesthouse_data(db, users)
        create_vehicle_data(db, users)
        create_visitor_data(db, users)
        create_colony_data(db, users)
        create_equipment_data(db, users)
        create_vigilance_data(db, users)
        create_canteen_data(db, users)
        
        print("\n" + "="*50)
        print("âœ“ Seed data created successfully!")
        print("="*50 + "\n")
        
        print("Login credentials:")
        print("  Admin:      admin@epos.com / Admin@123")
        print("  Manager:    manager@epos.com / Manager@123")
        print("  Supervisor: supervisor@epos.com / Supervisor@123")
        print("  Employee:   employee@epos.com / Employee@123")
        print()
        
    except Exception as e:
        print(f"\nâœ— Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

