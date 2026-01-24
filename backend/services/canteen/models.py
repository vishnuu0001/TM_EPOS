from sqlalchemy import Column, String, Text, DateTime, Boolean, Enum as SQLEnum, Float, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
import sys
sys.path.append('../..')
from shared.database import Base


def generate_uuid():
    """Generate UUID as string for SQLite compatibility"""
    return str(uuid.uuid4())


class WorkerType(str, enum.Enum):
    PERMANENT = "permanent"
    CONTRACT = "contract"
    CASUAL = "casual"
    TEMPORARY = "temporary"


class MealType(str, enum.Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACKS = "snacks"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    SERVED = "served"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    SUBSIDIZED = "subsidized"
    FREE = "free"


class InventoryStatus(str, enum.Enum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"


class Worker(Base):
    __tablename__ = "workers"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    worker_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Personal Information
    full_name = Column(String(200), nullable=False)
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    email = Column(String(255))
    
    # Employment
    worker_type = Column(SQLEnum(WorkerType), nullable=False)
    department = Column(String(100))
    designation = Column(String(100))
    contractor_name = Column(String(200))  # For contract workers
    
    # Biometric (stub for Phase 2)
    biometric_id = Column(String(100), unique=True)
    fingerprint_enrolled = Column(Boolean, default=False)
    face_enrolled = Column(Boolean, default=False)
    
    # Canteen Access
    is_active = Column(Boolean, default=True)
    canteen_access = Column(Boolean, default=True)
    meal_entitlement = Column(Text)  # JSON: {breakfast: true, lunch: true, dinner: false}
    
    # Balance
    wallet_balance = Column(Float, default=0.0)
    subsidy_applicable = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = relationship("Order", back_populates="worker")
    consumptions = relationship("Consumption", back_populates="worker")
    feedbacks = relationship("Feedback", back_populates="worker")


class Menu(Base):
    __tablename__ = "menus"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    menu_date = Column(Date, nullable=False, index=True)
    meal_type = Column(SQLEnum(MealType), nullable=False)
    
    # Menu Details
    menu_name = Column(String(200))
    description = Column(Text)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_published = Column(Boolean, default=False)
    
    # Metadata
    created_by = Column(String(36))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = relationship("MenuItem", back_populates="menu")
    orders = relationship("Order", back_populates="menu")


class MenuItem(Base):
    __tablename__ = "menu_items"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    menu_id = Column(String(36), ForeignKey("menus.id", ondelete="CASCADE"))
    
    # Item Details
    item_name = Column(String(200), nullable=False)
    item_name_hindi = Column(String(200))
    description = Column(Text)
    category = Column(String(100))  # Main Course, Roti, Rice, Dal, Sabzi, etc.
    
    # Pricing
    base_price = Column(Float, default=0.0)
    subsidized_price = Column(Float, default=0.0)
    
    # Availability
    is_available = Column(Boolean, default=True)
    quantity_prepared = Column(Integer, default=0)
    quantity_remaining = Column(Integer, default=0)
    
    # Nutritional Info (optional)
    calories = Column(Integer)
    is_vegetarian = Column(Boolean, default=True)
    is_vegan = Column(Boolean, default=False)
    contains_allergens = Column(Text)  # JSON array
    
    # Display
    image_url = Column(String(500))
    display_order = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    menu = relationship("Menu", back_populates="items")


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    token_number = Column(Integer, nullable=False)  # Display token number
    
    # References
    worker_id = Column(String(36), ForeignKey("workers.id", ondelete="CASCADE"))
    menu_id = Column(String(36), ForeignKey("menus.id", ondelete="SET NULL"))
    
    # Order Details
    meal_type = Column(SQLEnum(MealType), nullable=False)
    order_date = Column(Date, nullable=False, index=True)
    order_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Items (stored as JSON for simplicity)
    items = Column(Text, nullable=False)  # JSON array of {item_id, item_name, quantity, price}
    
    # Pricing
    total_amount = Column(Float, nullable=False)
    subsidy_amount = Column(Float, default=0.0)
    payable_amount = Column(Float, nullable=False)
    
    # Payment
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = Column(String(50))  # wallet, cash, card
    payment_time = Column(DateTime)
    
    # Status
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    confirmed_at = Column(DateTime)
    prepared_at = Column(DateTime)
    served_at = Column(DateTime)
    
    # Kiosk Info
    kiosk_id = Column(String(50))
    counter_number = Column(String(20))
    
    # Cancellation
    cancelled_at = Column(DateTime)
    cancellation_reason = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    worker = relationship("Worker", back_populates="orders")
    menu = relationship("Menu", back_populates="orders")
    consumption = relationship("Consumption", back_populates="order", uselist=False)


class Consumption(Base):
    __tablename__ = "consumptions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    order_id = Column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), unique=True)
    worker_id = Column(String(36), ForeignKey("workers.id", ondelete="CASCADE"))
    
    # Consumption Details
    meal_type = Column(SQLEnum(MealType), nullable=False)
    consumption_date = Column(Date, nullable=False, index=True)
    consumption_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Items Consumed
    items_ordered = Column(Text)  # JSON array
    items_consumed = Column(Text)  # JSON array (actual consumption)
    items_wasted = Column(Text)  # JSON array (what was left)
    
    # Wastage
    wastage_percentage = Column(Float, default=0.0)
    wastage_reason = Column(String(200))
    
    # Satisfaction
    meal_completed = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="consumption")
    worker = relationship("Worker", back_populates="consumptions")


class Feedback(Base):
    __tablename__ = "feedbacks"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    worker_id = Column(String(36), ForeignKey("workers.id", ondelete="CASCADE"))
    
    # Feedback Details
    feedback_date = Column(Date, nullable=False, index=True)
    meal_type = Column(SQLEnum(MealType), nullable=False)
    
    # Ratings (1-5 scale)
    food_quality_rating = Column(Integer)
    taste_rating = Column(Integer)
    quantity_rating = Column(Integer)
    hygiene_rating = Column(Integer)
    service_rating = Column(Integer)
    overall_rating = Column(Integer)
    
    # Comments
    comments = Column(Text)
    suggestions = Column(Text)
    
    # Specific Issues
    complaint = Column(Boolean, default=False)
    complaint_category = Column(String(100))
    complaint_description = Column(Text)
    
    # Response
    responded = Column(Boolean, default=False)
    response_by = Column(String(36))
    response_text = Column(Text)
    response_date = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    worker = relationship("Worker", back_populates="feedbacks")


class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    item_code = Column(String(50), unique=True, nullable=False, index=True)
    
    # Item Details
    item_name = Column(String(200), nullable=False)
    item_name_hindi = Column(String(200))
    category = Column(String(100))  # Vegetables, Grains, Spices, Oil, etc.
    unit = Column(String(50))  # kg, liter, pieces, etc.
    
    # Stock
    current_stock = Column(Float, default=0.0)
    minimum_stock = Column(Float, default=0.0)
    maximum_stock = Column(Float, default=0.0)
    reorder_level = Column(Float, default=0.0)
    
    # Status
    status = Column(SQLEnum(InventoryStatus), default=InventoryStatus.IN_STOCK)
    
    # Pricing
    unit_price = Column(Float, default=0.0)
    total_value = Column(Float, default=0.0)
    
    # Supplier
    supplier_name = Column(String(200))
    supplier_contact = Column(String(20))
    
    # Last Stock Update
    last_purchase_date = Column(Date)
    last_purchase_quantity = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Expiry (if applicable)
    is_perishable = Column(Boolean, default=False)
    expiry_date = Column(Date)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
