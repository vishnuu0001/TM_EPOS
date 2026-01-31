from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from enum import Enum


class WorkerTypeEnum(str, Enum):
    PERMANENT = "permanent"
    CONTRACT = "contract"
    CASUAL = "casual"
    TEMPORARY = "temporary"


class MealTypeEnum(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACKS = "snacks"


class OrderStatusEnum(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    SERVED = "served"
    CANCELLED = "cancelled"


class PaymentStatusEnum(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    SUBSIDIZED = "subsidized"
    FREE = "free"


class InventoryStatusEnum(str, Enum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"


# Worker Schemas
class WorkerCreate(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=200)
    employee_id: str = Field(..., min_length=1, max_length=50)
    phone: Optional[str] = Field(None, min_length=1, max_length=20)
    email: Optional[str] = Field(None, min_length=1, max_length=255)
    worker_type: WorkerTypeEnum
    department: Optional[str] = Field(None, min_length=1, max_length=100)
    designation: Optional[str] = Field(None, min_length=1, max_length=100)
    contractor_name: Optional[str] = Field(None, min_length=1, max_length=200)
    meal_entitlement: Optional[str] = Field(None, min_length=1)
    subsidy_applicable: bool = True


class WorkerUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    phone: Optional[str] = Field(None, min_length=1, max_length=20)
    email: Optional[str] = Field(None, min_length=1, max_length=255)
    worker_type: Optional[WorkerTypeEnum] = None
    department: Optional[str] = Field(None, min_length=1, max_length=100)
    designation: Optional[str] = Field(None, min_length=1, max_length=100)
    contractor_name: Optional[str] = Field(None, min_length=1, max_length=200)
    is_active: Optional[bool] = None
    canteen_access: Optional[bool] = None
    meal_entitlement: Optional[str] = Field(None, min_length=1)
    wallet_balance: Optional[float] = Field(None, ge=0)
    subsidy_applicable: Optional[bool] = None


class WorkerResponse(BaseModel):
    id: UUID
    worker_number: str
    full_name: str
    employee_id: str
    phone: Optional[str]
    email: Optional[str]
    worker_type: WorkerTypeEnum
    department: Optional[str]
    designation: Optional[str]
    contractor_name: Optional[str]
    biometric_id: Optional[str]
    fingerprint_enrolled: bool
    face_enrolled: bool
    is_active: bool
    canteen_access: bool
    meal_entitlement: Optional[str]
    wallet_balance: float
    subsidy_applicable: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Menu Schemas
class MenuCreate(BaseModel):
    menu_date: date
    meal_type: MealTypeEnum
    menu_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)


class MenuUpdate(BaseModel):
    menu_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    is_active: Optional[bool] = None
    is_published: Optional[bool] = None


class MenuResponse(BaseModel):
    id: UUID
    menu_date: date
    meal_type: MealTypeEnum
    menu_name: Optional[str]
    description: Optional[str]
    is_active: bool
    is_published: bool
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Menu Item Schemas
class MenuItemCreate(BaseModel):
    menu_id: str = Field(..., min_length=1)
    item_name: str = Field(..., min_length=1, max_length=200)
    item_name_hindi: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    base_price: float = Field(0.0, ge=0)
    subsidized_price: float = Field(0.0, ge=0)
    quantity_prepared: int = Field(0, ge=0)
    calories: Optional[int] = Field(None, ge=0)
    is_vegetarian: bool = True
    is_vegan: bool = False
    contains_allergens: Optional[str] = Field(None, min_length=1)
    image_url: Optional[str] = Field(None, min_length=1, max_length=500)
    display_order: int = Field(0, ge=0)


class MenuItemUpdate(BaseModel):
    item_name: Optional[str] = Field(None, min_length=1, max_length=200)
    item_name_hindi: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    base_price: Optional[float] = Field(None, ge=0)
    subsidized_price: Optional[float] = Field(None, ge=0)
    is_available: Optional[bool] = None
    quantity_prepared: Optional[int] = Field(None, ge=0)
    quantity_remaining: Optional[int] = Field(None, ge=0)
    calories: Optional[int] = Field(None, ge=0)
    is_vegetarian: Optional[bool] = None
    is_vegan: Optional[bool] = None
    contains_allergens: Optional[str] = Field(None, min_length=1)
    image_url: Optional[str] = Field(None, min_length=1, max_length=500)
    display_order: Optional[int] = Field(None, ge=0)


class MenuItemResponse(BaseModel):
    id: UUID
    menu_id: UUID
    item_name: str
    item_name_hindi: Optional[str]
    description: Optional[str]
    category: Optional[str]
    base_price: float
    subsidized_price: float
    is_available: bool
    quantity_prepared: int
    quantity_remaining: int
    calories: Optional[int]
    is_vegetarian: bool
    is_vegan: bool
    contains_allergens: Optional[str]
    image_url: Optional[str]
    display_order: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Order Schemas
class OrderCreate(BaseModel):
    worker_id: str = Field(..., min_length=1)
    menu_id: str = Field(..., min_length=1)
    meal_type: MealTypeEnum
    items: str = Field(..., min_length=1)  # JSON string
    total_amount: float = Field(..., ge=0)
    subsidy_amount: float = Field(0.0, ge=0)
    payable_amount: float = Field(..., ge=0)
    payment_method: Optional[str] = Field("wallet", min_length=1, max_length=50)
    kiosk_id: Optional[str] = Field(None, min_length=1, max_length=100)


class OrderUpdate(BaseModel):
    status: Optional[OrderStatusEnum] = None
    payment_status: Optional[PaymentStatusEnum] = None
    counter_number: Optional[str] = Field(None, min_length=1, max_length=50)
    cancellation_reason: Optional[str] = Field(None, min_length=1)


class OrderResponse(BaseModel):
    id: UUID
    order_number: str
    token_number: int
    worker_id: UUID
    menu_id: Optional[UUID]
    meal_type: MealTypeEnum
    order_date: date
    order_time: datetime
    items: str
    total_amount: float
    subsidy_amount: float
    payable_amount: float
    payment_status: PaymentStatusEnum
    payment_method: Optional[str]
    payment_time: Optional[datetime]
    status: OrderStatusEnum
    confirmed_at: Optional[datetime]
    prepared_at: Optional[datetime]
    served_at: Optional[datetime]
    kiosk_id: Optional[str]
    counter_number: Optional[str]
    cancelled_at: Optional[datetime]
    cancellation_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Consumption Schemas
class ConsumptionCreate(BaseModel):
    order_id: str = Field(..., min_length=1)
    worker_id: str = Field(..., min_length=1)
    meal_type: MealTypeEnum
    consumption_date: date
    items_ordered: str = Field(..., min_length=1)
    items_consumed: Optional[str] = Field(None, min_length=1)
    items_wasted: Optional[str] = Field(None, min_length=1)
    wastage_percentage: float = Field(0.0, ge=0, le=100)
    wastage_reason: Optional[str] = Field(None, min_length=1)
    meal_completed: bool = True


class ConsumptionResponse(BaseModel):
    id: UUID
    order_id: UUID
    worker_id: UUID
    meal_type: MealTypeEnum
    consumption_date: date
    consumption_time: datetime
    items_ordered: str
    items_consumed: Optional[str]
    items_wasted: Optional[str]
    wastage_percentage: float
    wastage_reason: Optional[str]
    meal_completed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Feedback Schemas
class FeedbackCreate(BaseModel):
    worker_id: str = Field(..., min_length=1)
    meal_type: MealTypeEnum
    food_quality_rating: Optional[int] = Field(None, ge=1, le=5)
    taste_rating: Optional[int] = Field(None, ge=1, le=5)
    quantity_rating: Optional[int] = Field(None, ge=1, le=5)
    hygiene_rating: Optional[int] = Field(None, ge=1, le=5)
    service_rating: Optional[int] = Field(None, ge=1, le=5)
    overall_rating: Optional[int] = Field(None, ge=1, le=5)
    comments: Optional[str] = Field(None, min_length=1)
    suggestions: Optional[str] = Field(None, min_length=1)
    complaint: bool = False
    complaint_category: Optional[str] = Field(None, min_length=1)
    complaint_description: Optional[str] = Field(None, min_length=1)


class FeedbackUpdate(BaseModel):
    responded: Optional[bool] = None
    response_text: Optional[str] = Field(None, min_length=1)


class FeedbackResponse(BaseModel):
    id: UUID
    worker_id: UUID
    feedback_date: date
    meal_type: MealTypeEnum
    food_quality_rating: Optional[int]
    taste_rating: Optional[int]
    quantity_rating: Optional[int]
    hygiene_rating: Optional[int]
    service_rating: Optional[int]
    overall_rating: Optional[int]
    comments: Optional[str]
    suggestions: Optional[str]
    complaint: bool
    complaint_category: Optional[str]
    complaint_description: Optional[str]
    responded: bool
    response_by: Optional[UUID]
    response_text: Optional[str]
    response_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Inventory Schemas
class InventoryCreate(BaseModel):
    item_name: str = Field(..., min_length=1, max_length=200)
    item_name_hindi: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    unit: str = Field(..., min_length=1, max_length=50)
    current_stock: float = Field(0.0, ge=0)
    minimum_stock: float = Field(0.0, ge=0)
    maximum_stock: float = Field(0.0, ge=0)
    reorder_level: float = Field(0.0, ge=0)
    unit_price: float = Field(0.0, ge=0)
    supplier_name: Optional[str] = Field(None, min_length=1, max_length=200)
    supplier_contact: Optional[str] = Field(None, min_length=1, max_length=100)
    is_perishable: bool = False
    expiry_date: Optional[date] = None


class InventoryUpdate(BaseModel):
    item_name: Optional[str] = Field(None, min_length=1, max_length=200)
    item_name_hindi: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    unit: Optional[str] = Field(None, min_length=1, max_length=50)
    current_stock: Optional[float] = Field(None, ge=0)
    minimum_stock: Optional[float] = Field(None, ge=0)
    maximum_stock: Optional[float] = Field(None, ge=0)
    reorder_level: Optional[float] = Field(None, ge=0)
    status: Optional[InventoryStatusEnum] = None
    unit_price: Optional[float] = Field(None, ge=0)
    total_value: Optional[float] = Field(None, ge=0)
    supplier_name: Optional[str] = Field(None, min_length=1, max_length=200)
    supplier_contact: Optional[str] = Field(None, min_length=1, max_length=100)
    last_purchase_date: Optional[date] = None
    last_purchase_quantity: Optional[float] = Field(None, ge=0)
    is_perishable: Optional[bool] = None
    expiry_date: Optional[date] = None


class InventoryResponse(BaseModel):
    id: UUID
    item_code: str
    item_name: str
    item_name_hindi: Optional[str]
    category: Optional[str]
    unit: str
    current_stock: float
    minimum_stock: float
    maximum_stock: float
    reorder_level: float
    status: InventoryStatusEnum
    unit_price: float
    total_value: float
    supplier_name: Optional[str]
    supplier_contact: Optional[str]
    last_purchase_date: Optional[date]
    last_purchase_quantity: Optional[float]
    last_updated: datetime
    is_perishable: bool
    expiry_date: Optional[date]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Kiosk Order
class KioskOrderItem(BaseModel):
    item_id: str = Field(..., min_length=1)
    quantity: int = Field(1, ge=1)


class KioskOrderCreate(BaseModel):
    biometric_id: str = Field(..., min_length=1)
    menu_id: str = Field(..., min_length=1)
    meal_type: MealTypeEnum
    items: List[KioskOrderItem] = Field(..., min_items=1)


# Dashboard Stats
class DashboardStats(BaseModel):
    total_workers: int
    today_orders: int
    today_consumption: int
    pending_orders: int
    low_stock_items: int
    average_rating: float
    today_revenue: float
    
    class Config:
        from_attributes = True
