from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum
from sqlalchemy.orm import Session
import sys
import os
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import get_db, init_db, SessionLocal
from shared.auth import create_access_token, verify_password, get_password_hash
from shared.models import User
from shared.schemas import TokenResponse, UserResponse, MessageResponse

# Initialize FastAPI app
app = FastAPI(
    title="ePOS API Gateway",
    description="Enterprise Plant Operations System - API Gateway",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

def _ensure_default_admin() -> None:
    """
    Create a default admin user if none exists and env vars are provided.
    This avoids 401 on first login in a fresh Vercel SQLite database.
    """
    email = os.getenv("DEFAULT_ADMIN_EMAIL")
    password = os.getenv("DEFAULT_ADMIN_PASSWORD")
    employee_id = os.getenv("DEFAULT_ADMIN_EMPLOYEE_ID", "EMP0001")
    full_name = os.getenv("DEFAULT_ADMIN_FULL_NAME", "Admin User")

    if not email or not password:
        return

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return

        user = User(
            email=email,
            employee_id=employee_id,
            full_name=full_name,
            password_hash=get_password_hash(password),
            is_active=True,
        )
        db.add(user)
        db.commit()
    finally:
        db.close()


@app.on_event("startup")
def _startup_init_db():
    init_db()
    _ensure_default_admin()

# CORS Configuration for Vercel
_raw_cors = os.getenv("CORS_ORIGINS", "").strip()
_frontend_origin = os.getenv("FRONTEND_URL", "").strip()
_cors_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
]
if _frontend_origin:
    _cors_origins.append(_frontend_origin)
if _raw_cors:
    try:
        parsed = json.loads(_raw_cors)
        if isinstance(parsed, list):
            _cors_origins.extend(parsed)
    except json.JSONDecodeError:
        _cors_origins.extend([origin.strip() for origin in _raw_cors.split(",") if origin.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def _cors_on_error(request: Request, call_next):
    """
    Ensure CORS headers are present even if an unhandled exception occurs.
    This prevents the browser from masking 500s as CORS failures.
    """
    origin = request.headers.get("origin")
    try:
        response = await call_next(request)
    except Exception:
        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )

    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Vary"] = "Origin"

    return response

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": "ePOS API Gateway",
        "version": "1.0.0",
        "status": "running",
        "environment": "vercel"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "platform": "vercel"}

# Vercel function path can strip /api prefix; provide alias
@app.get("/health")
async def health_check_alias():
    """Health check alias for Vercel routing"""
    return {"status": "healthy", "platform": "vercel"}


@app.options("/{path:path}")
async def preflight_handler(path: str, request: Request):
    """Handle CORS preflight requests explicitly."""
    origin = request.headers.get("origin", "*")
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Vary"] = "Origin"
    return response

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

@app.post("/api/auth/logout")
async def logout():
    """Logout endpoint"""
    return MessageResponse(message="Logged out successfully")

# Vercel serverless handler
handler = Mangum(app)
