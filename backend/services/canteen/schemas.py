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
    full_name: str
    employee_id: str
    phone: Optional[str] = None
    email: Optional[str] = None
    worker_type: WorkerTypeEnum
    department: Optional[str] = None
    designation: Optional[str] = None
    contractor_name: Optional[str] = None
    meal_entitlement: Optional[str] = None
    subsidy_applicable: bool = True


class WorkerUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    worker_type: Optional[WorkerTypeEnum] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    contractor_name: Optional[str] = None
    is_active: Optional[bool] = None
    canteen_access: Optional[bool] = None
    meal_entitlement: Optional[str] = None
    wallet_balance: Optional[float] = None
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
    menu_name: Optional[str] = None
    description: Optional[str] = None


class MenuUpdate(BaseModel):
    menu_name: Optional[str] = None
    description: Optional[str] = None
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
    menu_id: str
    item_name: str
    item_name_hindi: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    base_price: float = 0.0
    subsidized_price: float = 0.0
    quantity_prepared: int = 0
    calories: Optional[int] = None
    is_vegetarian: bool = True
    is_vegan: bool = False
    contains_allergens: Optional[str] = None
    image_url: Optional[str] = None
    display_order: int = 0


class MenuItemUpdate(BaseModel):
    item_name: Optional[str] = None
    item_name_hindi: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    base_price: Optional[float] = None
    subsidized_price: Optional[float] = None
    is_available: Optional[bool] = None
    quantity_prepared: Optional[int] = None
    quantity_remaining: Optional[int] = None
    calories: Optional[int] = None
    is_vegetarian: Optional[bool] = None
    is_vegan: Optional[bool] = None
    contains_allergens: Optional[str] = None
    image_url: Optional[str] = None
    display_order: Optional[int] = None


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
    worker_id: str
    menu_id: str
    meal_type: MealTypeEnum
    items: str  # JSON string
    total_amount: float
    subsidy_amount: float = 0.0
    payable_amount: float
    payment_method: Optional[str] = "wallet"
    kiosk_id: Optional[str] = None


class OrderUpdate(BaseModel):
    status: Optional[OrderStatusEnum] = None
    payment_status: Optional[PaymentStatusEnum] = None
    counter_number: Optional[str] = None
    cancellation_reason: Optional[str] = None


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
    order_id: str
    worker_id: str
    meal_type: MealTypeEnum
    consumption_date: date
    items_ordered: str
    items_consumed: Optional[str] = None
    items_wasted: Optional[str] = None
    wastage_percentage: float = 0.0
    wastage_reason: Optional[str] = None
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
    worker_id: str
    meal_type: MealTypeEnum
    food_quality_rating: Optional[int] = None
    taste_rating: Optional[int] = None
    quantity_rating: Optional[int] = None
    hygiene_rating: Optional[int] = None
    service_rating: Optional[int] = None
    overall_rating: Optional[int] = None
    comments: Optional[str] = None
    suggestions: Optional[str] = None
    complaint: bool = False
    complaint_category: Optional[str] = None
    complaint_description: Optional[str] = None


class FeedbackUpdate(BaseModel):
    responded: Optional[bool] = None
    response_text: Optional[str] = None


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
    item_name: str
    item_name_hindi: Optional[str] = None
    category: Optional[str] = None
    unit: str
    current_stock: float = 0.0
    minimum_stock: float = 0.0
    maximum_stock: float = 0.0
    reorder_level: float = 0.0
    unit_price: float = 0.0
    supplier_name: Optional[str] = None
    supplier_contact: Optional[str] = None
    is_perishable: bool = False
    expiry_date: Optional[date] = None


class InventoryUpdate(BaseModel):
    item_name: Optional[str] = None
    item_name_hindi: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    current_stock: Optional[float] = None
    minimum_stock: Optional[float] = None
    maximum_stock: Optional[float] = None
    reorder_level: Optional[float] = None
    status: Optional[InventoryStatusEnum] = None
    unit_price: Optional[float] = None
    total_value: Optional[float] = None
    supplier_name: Optional[str] = None
    supplier_contact: Optional[str] = None
    last_purchase_date: Optional[date] = None
    last_purchase_quantity: Optional[float] = None
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
    item_id: str
    quantity: int = 1


class KioskOrderCreate(BaseModel):
    biometric_id: str
    menu_id: str
    meal_type: MealTypeEnum
    items: List[KioskOrderItem]


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
