import os
from pathlib import Path
from typing import Optional
import aiofiles
from fastapi import UploadFile, HTTPException
from uuid import uuid4
from datetime import datetime
from .config import settings


async def save_upload_file(file: UploadFile, folder: str = "general") -> dict:
    """Save uploaded file and return file info"""
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Create upload directory
    upload_dir = Path(settings.UPLOAD_DIR) / folder
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    unique_filename = f"{uuid4()}{file_ext}"
    file_path = upload_dir / unique_filename
    
    # Read file content
    content = await file.read()
    
    # Validate file size
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE} bytes"
        )
    
    # Save file
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)
    
    return {
        "filename": file.filename,
        "saved_filename": unique_filename,
        "file_path": str(file_path),
        "file_size": len(content),
        "content_type": file.content_type,
        "uploaded_at": datetime.utcnow()
    }


async def delete_file(file_path: str) -> bool:
    """Delete a file"""
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            return True
        return False
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")
