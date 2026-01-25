from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, date, timedelta
import sys
import os
sys.path.append('../..')

from shared.database import get_db, init_db
from shared.auth import get_current_user
from shared.middleware import setup_middleware
from shared.config import settings

from models import (
    Worker, Menu, MenuItem, Order, Consumption,
    Inventory, Feedback,
    MealType, OrderStatus, PaymentStatus, WorkerType
)
from schemas import (
    WorkerCreate, WorkerUpdate, WorkerResponse,
    MenuCreate, MenuUpdate, MenuResponse,
    MenuItemCreate, MenuItemUpdate, MenuItemResponse,
    OrderCreate, OrderUpdate, OrderResponse,
    ConsumptionCreate, ConsumptionResponse,
    InventoryCreate, InventoryUpdate, InventoryResponse,
    FeedbackCreate, FeedbackResponse,
    DashboardStats, KioskOrderCreate
)

# Initialize FastAPI app
app = FastAPI(
    title="Canteen Management Service",
    description="Meal ordering, consumption tracking, and kiosk operations",
    version="1.0.0"
)

# Setup middleware
setup_middleware(app)


def _should_seed() -> bool:
    """Check env flag for seed behavior."""
    return os.getenv("SEED_DATA_ON_STARTUP", "true").strip().lower() in {"1", "true", "yes"}


def _seed_canteen_data(db: Session) -> None:
    """Seed canteen data if empty (menus/workers/menu items)."""
    has_menus = db.query(Menu).count() > 0
    has_items = db.query(MenuItem).count() > 0
    has_workers = db.query(Worker).count() > 0

    if has_menus and has_items and has_workers:
        return

    # Workers
    if not has_workers:
        workers = [
            {
                "worker_number": "W202600001",
                "full_name": "Mohan Kumar",
                "employee_id": "EMP001",
                "worker_type": WorkerType.PERMANENT,
                "department": "Production",
                "is_active": True,
                "canteen_access": True,
                "wallet_balance": 500,
            },
            {
                "worker_number": "W202600002",
                "full_name": "Ramesh Singh",
                "employee_id": "EMP002",
                "worker_type": WorkerType.CONTRACT,
                "department": "Maintenance",
                "is_active": True,
                "canteen_access": True,
                "wallet_balance": 300,
            },
        ]
        for worker_data in workers:
            db.add(Worker(**worker_data))

    # Menus
    if not has_menus:
        today = date.today()
        menus = [
            {
                "menu_date": today,
                "meal_type": MealType.BREAKFAST,
                "menu_name": "Breakfast Menu",
                "is_active": True,
                "is_published": True,
            },
            {
                "menu_date": today,
                "meal_type": MealType.LUNCH,
                "menu_name": "Lunch Menu",
                "is_active": True,
                "is_published": True,
            },
            {
                "menu_date": today,
                "meal_type": MealType.DINNER,
                "menu_name": "Dinner Menu",
                "is_active": True,
                "is_published": True,
            },
        ]
        for menu_data in menus:
            db.add(Menu(**menu_data))

    db.commit()

    # Menu items (after menus exist)
    if not has_items:
        menu_objs = db.query(Menu).order_by(Menu.menu_date.desc()).all()
        if menu_objs:
            items = [
                {
                    "menu_id": menu_objs[0].id,
                    "item_name": "Poha",
                    "category": "Main",
                    "base_price": 30,
                    "subsidized_price": 10,
                    "is_available": True,
                    "quantity_prepared": 50,
                    "quantity_remaining": 50,
                },
                {
                    "menu_id": menu_objs[1].id if len(menu_objs) > 1 else menu_objs[0].id,
                    "item_name": "Dal Tadka",
                    "category": "Dal",
                    "base_price": 40,
                    "subsidized_price": 15,
                    "is_available": True,
                    "quantity_prepared": 100,
                    "quantity_remaining": 100,
                },
                {
                    "menu_id": menu_objs[1].id if len(menu_objs) > 1 else menu_objs[0].id,
                    "item_name": "Roti",
                    "category": "Roti",
                    "base_price": 10,
                    "subsidized_price": 5,
                    "is_available": True,
                    "quantity_prepared": 200,
                    "quantity_remaining": 200,
                },
                {
                    "menu_id": menu_objs[2].id if len(menu_objs) > 2 else menu_objs[-1].id,
                    "item_name": "Rice",
                    "category": "Rice",
                    "base_price": 30,
                    "subsidized_price": 10,
                    "is_available": True,
                    "quantity_prepared": 80,
                    "quantity_remaining": 80,
                },
            ]
            for item_data in items:
                db.add(MenuItem(**item_data))
            db.commit()


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    if _should_seed():
        db = next(get_db())
        try:
            _seed_canteen_data(db)
        finally:
            db.close()


@app.get("/")
async def root():
    return {"service": "Canteen Management", "status": "running"}


# Worker Endpoints
@app.post("/workers", response_model=WorkerResponse)
async def create_worker(
    worker_data: WorkerCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new worker"""
    # Generate worker number
    count = db.query(Worker).count()
    worker_number = f"W{datetime.now().year}{count + 1:06d}"
    
    worker = Worker(
        worker_number=worker_number,
        **worker_data.dict()
    )
    
    db.add(worker)
    db.commit()
    db.refresh(worker)
    
    return worker


@app.get("/workers", response_model=List[WorkerResponse])
async def get_workers(
    worker_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all workers"""
    query = db.query(Worker)
    
    if worker_type:
        query = query.filter(Worker.worker_type == worker_type)
    if is_active is not None:
        query = query.filter(Worker.is_active == is_active)
    
    workers = query.offset(skip).limit(limit).all()
    return workers


@app.get("/workers/{worker_id}", response_model=WorkerResponse)
async def get_worker(
    worker_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get worker by ID"""
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker


@app.put("/workers/{worker_id}", response_model=WorkerResponse)
async def update_worker(
    worker_id: str,
    worker_data: WorkerUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update worker"""
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    for field, value in worker_data.dict(exclude_unset=True).items():
        setattr(worker, field, value)
    
    worker.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(worker)
    
    return worker


# Menu Endpoints
@app.post("/menus", response_model=MenuResponse)
async def create_menu(
    menu_data: MenuCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new menu"""
    menu = Menu(
        created_by=current_user["id"],
        **menu_data.dict()
    )
    
    db.add(menu)
    db.commit()
    db.refresh(menu)
    
    return menu


@app.get("/menus", response_model=List[MenuResponse])
async def get_menus(
    menu_date: Optional[date] = None,
    meal_type: Optional[str] = None,
    is_published: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all menus"""
    query = db.query(Menu)
    
    if menu_date:
        query = query.filter(Menu.menu_date == menu_date)
    if meal_type:
        query = query.filter(Menu.meal_type == meal_type)
    if is_published is not None:
        query = query.filter(Menu.is_published == is_published)
    
    menus = query.order_by(Menu.menu_date.desc()).offset(skip).limit(limit).all()
    return menus


@app.get("/menus/today")
async def get_today_menus(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get today's published menus"""
    today = date.today()
    menus = db.query(Menu).filter(
        and_(
            Menu.menu_date == today,
            Menu.is_published == True,
            Menu.is_active == True
        )
    ).all()
    return menus


@app.put("/menus/{menu_id}", response_model=MenuResponse)
async def update_menu(
    menu_id: str,
    menu_data: MenuUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update menu"""
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    for field, value in menu_data.dict(exclude_unset=True).items():
        setattr(menu, field, value)
    
    menu.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(menu)
    
    return menu


# Menu Item Endpoints
@app.post("/menu-items", response_model=MenuItemResponse)
async def create_menu_item(
    item_data: MenuItemCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new menu item"""
    item = MenuItem(**item_data.dict())
    
    db.add(item)
    db.commit()
    db.refresh(item)
    
    return item


@app.get("/menu-items/menu/{menu_id}", response_model=List[MenuItemResponse])
async def get_menu_items(
    menu_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all items for a menu"""
    items = db.query(MenuItem).filter(
        MenuItem.menu_id == menu_id
    ).order_by(MenuItem.display_order).all()
    return items


@app.put("/menu-items/{item_id}", response_model=MenuItemResponse)
async def update_menu_item(
    item_id: str,
    item_data: MenuItemUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update menu item"""
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    for field, value in item_data.dict(exclude_unset=True).items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    
    return item


# Order Endpoints
@app.post("/orders", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new order"""
    import json
    
    # Generate order number and token
    count = db.query(Order).count()
    order_number = f"ORD{datetime.now().year}{count + 1:08d}"
    token_number = (count % 999) + 1
    
    # Convert items to JSON
    items_json = json.dumps([item.dict() for item in order_data.items]) if order_data.items else "[]"
    
    order = Order(
        order_number=order_number,
        token_number=token_number,
        worker_id=current_user["id"],
        items=items_json,
        **order_data.dict(exclude={'items'})
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return order


@app.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    status: Optional[str] = None,
    meal_type: Optional[str] = None,
    order_date: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all orders"""
    query = db.query(Order)
    
    if status:
        query = query.filter(Order.status == status)
    if meal_type:
        query = query.filter(Order.meal_type == meal_type)
    if order_date:
        query = query.filter(func.date(Order.order_date) == order_date)
    
    orders = query.order_by(Order.order_date.desc()).offset(skip).limit(limit).all()
    return orders


@app.get("/orders/my-orders", response_model=List[OrderResponse])
async def get_my_orders(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's orders"""
    orders = db.query(Order).filter(
        Order.worker_id == current_user["id"]
    ).order_by(Order.order_date.desc()).limit(50).all()
    return orders


@app.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    status: OrderStatus,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update order status"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status
    order.updated_at = datetime.utcnow()
    
    if status == OrderStatus.SERVED:
        order.served_at = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    
    return order


# Kiosk Order Endpoint
@app.post("/kiosk/order")
async def create_kiosk_order(
    order_data: KioskOrderCreate,
    db: Session = Depends(get_db)
):
    """Create order from kiosk (biometric authentication)"""
    import json
    
    # Verify worker by biometric ID
    worker = db.query(Worker).filter(
        Worker.biometric_id == order_data.biometric_id,
        Worker.is_active == True,
        Worker.canteen_access == True
    ).first()
    
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found or access denied")
    
    # Generate order number and token
    count = db.query(Order).count()
    order_number = f"ORD{datetime.now().year}{count + 1:08d}"
    token_number = (count % 999) + 1
    
    # Calculate total and build items list
    total_amount = 0
    items_list = []
    
    for item_data in order_data.items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item_data.item_id).first()
        if not menu_item:
            continue
        
        price = menu_item.subsidized_price if worker.subsidy_applicable else menu_item.base_price
        item_total = price * item_data.quantity
        
        items_list.append({
            "item_id": str(item_data.item_id),
            "item_name": menu_item.item_name,
            "quantity": item_data.quantity,
            "unit_price": price,
            "total_price": item_total
        })
        total_amount += item_total
    
    order = Order(
        order_number=order_number,
        token_number=token_number,
        worker_id=worker.id,
        menu_id=order_data.menu_id,
        meal_type=order_data.meal_type,
        order_date=datetime.utcnow().date(),
        order_time=datetime.utcnow(),
        items=json.dumps(items_list),
        total_amount=total_amount,
        payable_amount=total_amount,
        payment_status=PaymentStatus.SUBSIDIZED if worker.subsidy_applicable else PaymentStatus.PENDING,
        status=OrderStatus.CONFIRMED
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return {
        "order_number": order.order_number,
        "token_number": order.token_number,
        "worker_name": worker.full_name,
        "total_amount": total_amount,
        "payment_status": order.payment_status
    }


# Consumption Tracking
@app.post("/consumptions", response_model=ConsumptionResponse)
async def record_consumption(
    consumption_data: ConsumptionCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record meal consumption"""
    consumption = Consumption(
        recorded_by=current_user["id"],
        **consumption_data.dict()
    )
    
    db.add(consumption)
    db.commit()
    db.refresh(consumption)
    
    return consumption


@app.get("/consumptions", response_model=List[ConsumptionResponse])
async def get_consumptions(
    consumption_date: Optional[date] = None,
    meal_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get consumption records"""
    query = db.query(Consumption)
    
    if consumption_date:
        query = query.filter(func.date(Consumption.consumption_time) == consumption_date)
    if meal_type:
        query = query.filter(Consumption.meal_type == meal_type)
    
    consumptions = query.order_by(Consumption.consumption_time.desc()).offset(skip).limit(limit).all()
    return consumptions


# Inventory Endpoints
@app.post("/inventory", response_model=InventoryResponse)
async def create_inventory_item(
    item_data: InventoryCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new inventory item"""
    # Generate item code
    count = db.query(Inventory).count()
    item_code = f"INV{count + 1:06d}"
    
    item = Inventory(
        item_code=item_code,
        **item_data.dict()
    )
    
    db.add(item)
    db.commit()
    db.refresh(item)
    
    return item


@app.get("/inventory", response_model=List[InventoryResponse])
async def get_inventory(
    status: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get inventory items"""
    query = db.query(Inventory)
    
    if status:
        query = query.filter(Inventory.status == status)
    if category:
        query = query.filter(Inventory.category == category)
    
    items = query.offset(skip).limit(limit).all()
    return items


@app.put("/inventory/{item_id}", response_model=InventoryResponse)
async def update_inventory_item(
    item_id: str,
    item_data: InventoryUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update inventory item"""
    item = db.query(Inventory).filter(Inventory.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    for field, value in item_data.dict(exclude_unset=True).items():
        setattr(item, field, value)
    
    item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(item)
    
    return item


# Feedback Endpoints
@app.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    feedback_data: FeedbackCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit meal feedback"""
    feedback = Feedback(
        worker_id=current_user["id"],
        **feedback_data.dict()
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    return feedback


@app.get("/feedback", response_model=List[FeedbackResponse])
async def get_feedback(
    rating: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get feedback records"""
    query = db.query(Feedback)
    
    if rating:
        query = query.filter(Feedback.rating == rating)
    
    feedbacks = query.order_by(Feedback.created_at.desc()).offset(skip).limit(limit).all()
    return feedbacks


# Dashboard & Analytics
@app.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    today = date.today()
    
    # Total workers
    total_workers = db.query(Worker).filter(Worker.is_active == True).count()
    
    # Today's orders
    today_orders = db.query(Order).filter(
        func.date(Order.order_date) == today
    ).count()
    
    # Today's consumption
    today_consumption = db.query(Consumption).filter(
        func.date(Consumption.consumption_time) == today
    ).count()
    
    # Pending orders
    pending_orders = db.query(Order).filter(
        Order.status.in_([OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PREPARING])
    ).count()
    
    # Low stock items
    # Treat items at/below reorder level or minimum stock as low/out of stock
    low_stock_items = db.query(Inventory).filter(
        or_(
            Inventory.current_stock <= Inventory.reorder_level,
            Inventory.current_stock <= Inventory.minimum_stock
        )
    ).count()
    
    # Average rating (last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    # Use overall_rating for average; filter nulls to avoid SQL errors
    avg_rating = db.query(func.avg(Feedback.overall_rating)).filter(
        Feedback.overall_rating.isnot(None),
        func.date(Feedback.created_at) >= thirty_days_ago
    ).scalar() or 0
    
    # Revenue today
    today_revenue = db.query(func.sum(Order.total_amount)).filter(
        func.date(Order.order_date) == today,
        Order.payment_status == PaymentStatus.PAID
    ).scalar() or 0
    
    return {
        "total_workers": total_workers,
        "today_orders": today_orders,
        "today_consumption": today_consumption,
        "pending_orders": pending_orders,
        "low_stock_items": low_stock_items,
        "average_rating": round(avg_rating, 2),
        "today_revenue": today_revenue
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
