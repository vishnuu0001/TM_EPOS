"""
Shared utility package for all backend services
"""
from .config import settings
from .database import Base, get_db, init_db
from .auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_token,
    get_current_user,
    require_role
)

__all__ = [
    "settings",
    "Base",
    "get_db",
    "init_db",
    "get_password_hash",
    "verify_password",
    "create_access_token",
    "decode_token",
    "get_current_user",
    "require_role"
]
