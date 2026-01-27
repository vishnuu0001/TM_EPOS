from fastapi import FastAPI, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List, Optional
from datetime import datetime, timedelta
import sys
from pathlib import Path
import os
import tempfile

sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.database import get_db, engine
from shared.middleware import setup_middleware
from shared.auth import get_current_user
from shared.models import User

from models import Base, Room, Booking, Billing, Housekeeping, RoomStatus, BookingStatus, RoomType
from schemas import (
    RoomCreate, RoomUpdate, RoomResponse,
    BookingCreate, BookingUpdate, BookingResponse,
    CheckInRequest, CheckOutRequest,
    BillingCreate, BillingUpdate, BillingResponse,
    HousekeepingCreate, HousekeepingUpdate, HousekeepingResponse,
    DashboardStats, AvailabilityResponse
)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Guest House Management Service", version="1.0.0")
setup_middleware(app)


def _should_seed() -> bool:
    return os.getenv("SEED_DATA_ON_STARTUP", "true").strip().lower() in {"1", "true", "yes"}


def _require_seed_token(request: Request) -> None:
    token = os.getenv("SEED_ENDPOINT_TOKEN")
    if not token:
        raise HTTPException(status_code=403, detail="Seed endpoint disabled")
    provided = request.headers.get("x-seed-token") or request.query_params.get("token")
    if provided != token:
        raise HTTPException(status_code=401, detail="Invalid seed token")


def _should_seed_first_boot(service_name: str) -> bool:
    flag = os.getenv("SEED_ON_FIRST_BOOT", "false").strip().lower() in {"1", "true", "yes"}
    if not flag:
        return True
    marker_dir = os.getenv("SEED_MARKER_DIR") or tempfile.gettempdir()
    marker_path = os.path.join(marker_dir, f"epos_seeded_{service_name}.flag")
    return not os.path.exists(marker_path)


def _mark_seeded(service_name: str) -> None:
    flag = os.getenv("SEED_ON_FIRST_BOOT", "false").strip().lower() in {"1", "true", "yes"}
    if not flag:
        return
    marker_dir = os.getenv("SEED_MARKER_DIR") or tempfile.gettempdir()
    os.makedirs(marker_dir, exist_ok=True)
    marker_path = os.path.join(marker_dir, f"epos_seeded_{service_name}.flag")
    with open(marker_path, "w", encoding="utf-8") as handle:
        handle.write("seeded")


def _seed_guesthouse_data(db: Session) -> None:
    """Seed guesthouse rooms up to target count."""
    target = int(os.getenv("SEED_GUESTHOUSE_ROOMS", "1000"))
    existing = db.query(Room).count()
    if existing >= target:
        return

    existing_numbers = {
        r.room_number for r in db.query(Room.room_number).all()
    }
    base_index = existing + 1
    type_cycle = [RoomType.SINGLE, RoomType.DOUBLE, RoomType.SUITE, RoomType.DORMITORY]
    created = 0
    i = base_index
    while existing + created < target:
        room_number = f"GH-{100 + i}"
        if room_number in existing_numbers:
            i += 1
            continue

        room_type = type_cycle[i % len(type_cycle)]
        capacity = 1 if room_type == RoomType.SINGLE else 2 if room_type == RoomType.DOUBLE else 4
        db.add(
            Room(
                room_number=room_number,
                room_type=room_type,
                floor=((i - 1) % 10) + 1,
                capacity=capacity,
                amenities="[\"AC\", \"WiFi\"]",
                rate_per_night=1500 + (i % 5) * 250,
                status=RoomStatus.AVAILABLE,
                description="Auto-seeded room",
            )
        )
        existing_numbers.add(room_number)
        created += 1
        i += 1
    db.commit()


def _normalize_guesthouse_enums(db: Session) -> None:
    """Normalize legacy enum values to lowercase, snake_case values."""
    db.execute(text(
        """
        UPDATE guesthouse_rooms
        SET room_type = CASE room_type
            WHEN 'Single' THEN 'single'
            WHEN 'Double' THEN 'double'
            WHEN 'Suite' THEN 'suite'
            WHEN 'Dormitory' THEN 'dormitory'
            ELSE room_type
        END,
            status = CASE status
            WHEN 'Available' THEN 'available'
            WHEN 'Occupied' THEN 'occupied'
            WHEN 'Maintenance' THEN 'maintenance'
            WHEN 'Reserved' THEN 'reserved'
            ELSE status
        END
        """
    ))
    db.execute(text(
        """
        UPDATE guesthouse_bookings
        SET status = CASE status
            WHEN 'Confirmed' THEN 'confirmed'
            WHEN 'CheckedIn' THEN 'checked_in'
            WHEN 'CheckedOut' THEN 'checked_out'
            WHEN 'Cancelled' THEN 'cancelled'
            WHEN 'Pending' THEN 'pending'
            ELSE status
        END
        """
    ))
    db.commit()


@app.on_event("startup")
async def startup_event():
    if _should_seed() and _should_seed_first_boot("guesthouse"):
        db = next(get_db())
        try:
            _seed_guesthouse_data(db)
            _normalize_guesthouse_enums(db)
            _mark_seeded("guesthouse")
        finally:
            db.close()
    else:
        db = next(get_db())
        try:
            _normalize_guesthouse_enums(db)
        finally:
            db.close()

@app.get("/")
async def root():
    return {"service": "Guest House Management", "status": "running", "version": "1.0.0"}


@app.post("/admin/seed")
async def seed_guesthouse_data(request: Request, current_user: User = Depends(get_current_user)):
    _require_seed_token(request)
    db = next(get_db())
    try:
        _seed_guesthouse_data(db)
        return {"seeded": True}
    finally:
        db.close()

# Room Management
@app.post("/rooms", response_model=RoomResponse)
async def create_room(
    room_data: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    room = Room(**room_data.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room

@app.get("/rooms", response_model=List[RoomResponse])
async def list_rooms(
    status: Optional[RoomStatus] = None,
    room_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        query = db.query(Room)
        if status:
            query = query.filter(Room.status == status)
        if room_type:
            query = query.filter(Room.room_type == room_type)
        return query.offset(skip).limit(limit).all()
    except Exception as e:
        print(f"Error fetching rooms: {str(e)}")
        # Return empty list instead of crashing
        return []

@app.get("/rooms/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@app.put("/rooms/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: str,
    room_data: RoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    for key, value in room_data.model_dump(exclude_unset=True).items():
        setattr(room, key, value)
    
    db.commit()
    db.refresh(room)
    return room

# Booking Management
@app.post("/bookings", response_model=BookingResponse)
async def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.get("id") if isinstance(current_user, dict) else getattr(current_user, "id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user context")
    # Check room availability
    room = db.query(Room).filter(Room.id == booking_data.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Check for overlapping bookings
    overlapping = db.query(Booking).filter(
        Booking.room_id == booking_data.room_id,
        Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN]),
        Booking.check_in_date < booking_data.check_out_date,
        Booking.check_out_date > booking_data.check_in_date
    ).first()
    
    if overlapping:
        raise HTTPException(status_code=400, detail="Room not available for selected dates")
    
    # Generate booking number
    year = datetime.now().year
    count = db.query(Booking).filter(
        Booking.booking_number.like(f"GH{year}%")
    ).count()
    booking_number = f"GH{year}{count + 1:06d}"
    
    booking = Booking(
        **booking_data.model_dump(),
        booking_number=booking_number,
        booked_by_id=user_id
    )
    try:
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create booking: {exc}")

@app.get("/bookings", response_model=List[BookingResponse])
async def list_bookings(
    status: Optional[BookingStatus] = None,
    room_id: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        query = db.query(Booking)
        if status:
            query = query.filter(Booking.status == status)
        if room_id:
            query = query.filter(Booking.room_id == room_id)
        if from_date:
            query = query.filter(Booking.check_in_date >= from_date)
        if to_date:
            query = query.filter(Booking.check_out_date <= to_date)
        
        return query.order_by(Booking.check_in_date.desc()).offset(skip).limit(limit).all()
    except Exception as e:
        print(f"Error fetching bookings: {str(e)}")
        return []

@app.get("/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@app.put("/bookings/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: str,
    booking_data: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    for key, value in booking_data.model_dump(exclude_unset=True).items():
        setattr(booking, key, value)
    
    db.commit()
    db.refresh(booking)
    return booking

# Check-in/Check-out
@app.post("/checkin")
async def check_in(
    request: CheckInRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == request.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.actual_check_in = request.actual_check_in or datetime.now()
    booking.status = BookingStatus.CHECKED_IN
    
    # Update room status
    room = db.query(Room).filter(Room.id == booking.room_id).first()
    room.status = RoomStatus.OCCUPIED
    
    db.commit()
    return {"message": "Check-in successful", "booking_id": booking.id}

@app.post("/checkout")
async def check_out(
    request: CheckOutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == request.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.actual_check_out = request.actual_check_out or datetime.now()
    booking.status = BookingStatus.CHECKED_OUT
    
    # Update room status
    room = db.query(Room).filter(Room.id == booking.room_id).first()
    room.status = RoomStatus.AVAILABLE
    
    # Generate billing if not exists
    billing = db.query(Billing).filter(Billing.booking_id == booking.id).first()
    if not billing:
        days = (booking.actual_check_out - booking.actual_check_in).days or 1
        room_charges = days * room.daily_rate
        tax_amount = room_charges * 0.18  # 18% GST
        total = room_charges + tax_amount
        
        invoice_count = db.query(Billing).count()
        invoice_number = f"INV{datetime.now().year}{invoice_count + 1:06d}"
        
        billing = Billing(
            booking_id=booking.id,
            invoice_number=invoice_number,
            room_charges=room_charges,
            tax_amount=tax_amount,
            total_amount=total
        )
        db.add(billing)
    
    # Create housekeeping task
    housekeeping = Housekeeping(
        room_id=booking.room_id,
        task_type="Cleaning",
        task_description=f"Post-checkout cleaning for booking {booking.booking_number}"
    )
    db.add(housekeeping)
    
    db.commit()
    return {"message": "Check-out successful", "booking_id": booking.id, "invoice_number": billing.invoice_number}

# Billing
@app.get("/billing/{booking_id}", response_model=BillingResponse)
async def get_billing(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    billing = db.query(Billing).filter(Billing.booking_id == booking_id).first()
    if not billing:
        raise HTTPException(status_code=404, detail="Billing not found")
    return billing

@app.put("/billing/{billing_id}", response_model=BillingResponse)
async def update_billing(
    billing_id: str,
    billing_data: BillingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    billing = db.query(Billing).filter(Billing.id == billing_id).first()
    if not billing:
        raise HTTPException(status_code=404, detail="Billing not found")
    
    for key, value in billing_data.model_dump(exclude_unset=True).items():
        setattr(billing, key, value)
    
    # Recalculate total
    billing.total_amount = (
        billing.room_charges + 
        billing.meal_charges + 
        billing.extra_service_charges + 
        billing.tax_amount - 
        billing.discount
    )
    
    if billing_data.paid:
        billing.payment_date = datetime.now()
    
    db.commit()
    db.refresh(billing)
    return billing

# Housekeeping
@app.post("/housekeeping", response_model=HousekeepingResponse)
async def create_housekeeping_task(
    task_data: HousekeepingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = Housekeeping(**task_data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@app.get("/housekeeping", response_model=List[HousekeepingResponse])
async def list_housekeeping_tasks(
    status: Optional[str] = None,
    room_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Housekeeping)
    if status:
        query = query.filter(Housekeeping.status == status)
    if room_id:
        query = query.filter(Housekeeping.room_id == room_id)
    
    return query.order_by(Housekeeping.created_at.desc()).offset(skip).limit(limit).all()

@app.put("/housekeeping/{task_id}", response_model=HousekeepingResponse)
async def update_housekeeping_task(
    task_id: str,
    task_data: HousekeepingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Housekeeping).filter(Housekeeping.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Housekeeping task not found")
    
    for key, value in task_data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    
    if task_data.status == "in_progress" and not task.started_at:
        task.started_at = datetime.now()
    elif task_data.status == "completed" and not task.completed_at:
        task.completed_at = datetime.now()
    
    db.commit()
    db.refresh(task)
    return task

# Availability Check
@app.get("/availability", response_model=AvailabilityResponse)
async def check_availability(
    check_in_date: datetime = Query(...),
    check_out_date: datetime = Query(...),
    room_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get all rooms
    query = db.query(Room).filter(Room.status == RoomStatus.AVAILABLE)
    if room_type:
        query = query.filter(Room.room_type == room_type)
    
    all_rooms = query.all()
    
    # Filter out booked rooms
    available_rooms = []
    for room in all_rooms:
        overlapping = db.query(Booking).filter(
            Booking.room_id == room.id,
            Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN]),
            Booking.check_in_date < check_out_date,
            Booking.check_out_date > check_in_date
        ).first()
        
        if not overlapping:
            available_rooms.append(room)
    
    return {
        "available_rooms": available_rooms,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date
    }

# Dashboard Stats
@app.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        total_rooms = db.query(Room).count()
        available_rooms = db.query(Room).filter(Room.status == RoomStatus.AVAILABLE).count()
        occupied_rooms = db.query(Room).filter(Room.status == RoomStatus.OCCUPIED).count()
        maintenance_rooms = db.query(Room).filter(Room.status == RoomStatus.MAINTENANCE).count()
        
        total_bookings = db.query(Booking).count()
        active_bookings = db.query(Booking).filter(
            Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN])
        ).count()

        pending_bookings = db.query(Booking).filter(
            Booking.status == BookingStatus.PENDING
        ).count()

        checked_in_guests = db.query(Booking).filter(
            Booking.status == BookingStatus.CHECKED_IN
        ).count()
        
        today = datetime.now().date()
        checked_in_today = db.query(Booking).filter(
            Booking.actual_check_in >= datetime.combine(today, datetime.min.time()),
            Booking.actual_check_in < datetime.combine(today + timedelta(days=1), datetime.min.time())
        ).count()
        
        checking_out_today = db.query(Booking).filter(
            Booking.check_out_date >= datetime.combine(today, datetime.min.time()),
            Booking.check_out_date < datetime.combine(today + timedelta(days=1), datetime.min.time()),
            Booking.status == BookingStatus.CHECKED_IN
        ).count()
        
        occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
        
        pending_housekeeping = db.query(Housekeeping).filter(
            Housekeeping.status == "pending"
        ).count()

        start_of_month = datetime(today.year, today.month, 1)
        if today.month == 12:
            start_of_next_month = datetime(today.year + 1, 1, 1)
        else:
            start_of_next_month = datetime(today.year, today.month + 1, 1)

        revenue_today = db.query(func.sum(Billing.total_amount)).filter(
            func.date(Billing.created_at) == today
        ).scalar() or 0

        revenue_month = db.query(func.sum(Billing.total_amount)).filter(
            Billing.created_at >= start_of_month,
            Billing.created_at < start_of_next_month
        ).scalar() or 0
        
        return {
            "total_rooms": total_rooms,
            "available_rooms": available_rooms,
            "occupied_rooms": occupied_rooms,
            "maintenance_rooms": maintenance_rooms,
            "total_bookings": total_bookings,
            "active_bookings": active_bookings,
            "pending_bookings": pending_bookings,
            "checked_in_guests": checked_in_guests,
            "checked_in_today": checked_in_today,
            "checking_out_today": checking_out_today,
            "occupancy_rate": round(occupancy_rate, 2),
            "pending_housekeeping": pending_housekeeping,
            "revenue_today": round(revenue_today, 2),
            "revenue_month": round(revenue_month, 2)
        }
    except Exception as e:
        print(f"Error fetching dashboard stats: {str(e)}")
        return {
            "total_rooms": 0,
            "available_rooms": 0,
            "occupied_rooms": 0,
            "maintenance_rooms": 0,
            "total_bookings": 0,
            "active_bookings": 0,
            "checked_in_today": 0,
            "checking_out_today": 0,
            "occupancy_rate": 0,
            "pending_housekeeping": 0
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
