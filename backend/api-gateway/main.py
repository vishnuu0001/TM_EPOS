from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import sys
import os

# Ensure backend folder is on sys.path for shared imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from shared.config import settings
from shared.database import get_db, init_db
from shared.auth import create_access_token, verify_password, get_current_user
from shared.middleware import setup_cors, setup_gzip, setup_exception_handlers, log_requests_middleware
from shared.models import User
from shared.schemas import TokenResponse, UserResponse, MessageResponse
import httpx
from datetime import timedelta

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    init_db()
    yield
    # Cleanup on shutdown (if needed)

# Initialize FastAPI app
app = FastAPI(
    title="ePOS API Gateway",
    description="Enterprise Plant Operations System - API Gateway",
    version="1.0.0",
    lifespan=lifespan
)

# Setup middleware
setup_cors(app, settings.CORS_ORIGINS)
setup_gzip(app)
setup_exception_handlers(app)
app.middleware("http")(log_requests_middleware)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": "ePOS API Gateway",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/api/health")
async def api_health_check():
    """API Health check endpoint"""
    return {"status": "healthy", "service": "api-gateway"}


# Authentication endpoints
@app.post("/api/auth/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login endpoint"""
    # Find user by email or employee_id
    user = db.query(User).filter(
        (User.email == form_data.username) | (User.employee_id == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    user_id = current_user.get("id")
    user = None
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
    if not user and current_user.get("email"):
        user = db.query(User).filter(User.email == current_user["email"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user




@app.post("/api/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout endpoint"""
    # In a production system, you might want to blacklist the token
    return MessageResponse(message="Logged out successfully")


# Proxy endpoints to microservices
from fastapi import Request
from fastapi.responses import JSONResponse

async def proxy_request(request: Request, service_url: str, path: str):
    """Proxy request to microservice"""
    async with httpx.AsyncClient() as client:
        url = f"{service_url}{path}"
        headers = dict(request.headers)
        headers.pop('host', None)

        try:
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=await request.body(),
                params=request.query_params,
                timeout=10.0,
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Upstream service unavailable at {service_url}. Error: {exc}"
            )


# Colony Maintenance Service routes
@app.api_route("/api/colony/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def colony_proxy(request: Request, path: str, current_user: dict = Depends(get_current_user)):
    """Proxy to Colony Maintenance Service"""
    return await proxy_request(request, settings.COLONY_SERVICE_URL, f"/{path}")


# Guest House Service routes
@app.api_route("/api/guesthouse/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def guesthouse_proxy(request: Request, path: str, current_user: dict = Depends(get_current_user)):
    """Proxy to Guest House Service"""
    return await proxy_request(request, settings.GUESTHOUSE_SERVICE_URL, f"/{path}")


# Equipment Service routes
@app.api_route("/api/equipment/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def equipment_proxy(request: Request, path: str, current_user: dict = Depends(get_current_user)):
    """Proxy to Equipment Service"""
    return await proxy_request(request, settings.EQUIPMENT_SERVICE_URL, f"/{path}")


# Vigilance Service routes
@app.api_route("/api/vigilance/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def vigilance_proxy(request: Request, path: str, current_user: dict = Depends(get_current_user)):
    """Proxy to Vigilance Service"""
    return await proxy_request(request, settings.VIGILANCE_SERVICE_URL, f"/{path}")


# Vehicle Service routes
@app.api_route("/api/vehicle/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def vehicle_proxy(request: Request, path: str, current_user: dict = Depends(get_current_user)):
    """Proxy to Vehicle Service"""
    return await proxy_request(request, settings.VEHICLE_SERVICE_URL, f"/{path}")


# Visitor Service routes
@app.api_route("/api/visitor/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def visitor_proxy(request: Request, path: str, current_user: dict = Depends(get_current_user)):
    """Proxy to Visitor Service"""
    return await proxy_request(request, settings.VISITOR_SERVICE_URL, f"/{path}")


# Canteen Service routes
@app.api_route("/api/canteen/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def canteen_proxy(request: Request, path: str, current_user: dict = Depends(get_current_user)):
    """Proxy to Canteen Service"""
    return await proxy_request(request, settings.CANTEEN_SERVICE_URL, f"/{path}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
