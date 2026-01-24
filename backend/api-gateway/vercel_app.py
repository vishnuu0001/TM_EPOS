from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from sqlalchemy.orm import Session
import sys
import os
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import get_db
from shared.auth import create_access_token, verify_password
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

# CORS Configuration for Vercel
_raw_cors = os.getenv("CORS_ORIGINS", "").strip()
_cors_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
]
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
