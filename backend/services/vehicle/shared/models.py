from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Float, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .database import Base


def generate_uuid():
    """Generate UUID as string for SQLite compatibility"""
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=False)
    phone = Column(String(20))
    department = Column(String(100))
    designation = Column(String(100))
    plant_location = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = relationship("UserRole", back_populates="user")
    notifications = relationship("Notification", back_populates="user")


class Role(Base):
    __tablename__ = "roles"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    permissions = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    users = relationship("UserRole", back_populates="role")


class UserRole(Base):
    __tablename__ = "user_roles"
    
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(String(36), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    
    # Relationships
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notifications")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    module = Column(String(50), nullable=False)
    entity_type = Column(String(50))
    entity_id = Column(String(36))
    old_values = Column(JSON)
    new_values = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
