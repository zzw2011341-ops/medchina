"""Authentication API routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
import os

from storage.database.db import get_session
from storage.database.shared.model import Admin
from admin.schemas.common import ResponseModel, LoginRequest, LoginResponse
from admin.auth import create_access_token, get_current_admin

router = APIRouter(prefix="/admin/api/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)

# Default admin credentials (should be moved to environment variables in production)
DEFAULT_ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")


@router.post("/login", response_model=ResponseModel)
async def login(
    credentials: LoginRequest,
    db: Session = Depends(get_session)
):
    """Admin login"""
    try:
        # For simplicity, we'll use environment variables for admin credentials
        # In production, this should be validated against database with hashed passwords
        
        if credentials.username == DEFAULT_ADMIN_USERNAME and credentials.password == DEFAULT_ADMIN_PASSWORD:
            # Create access token
            token_data = {
                "sub": credentials.username,
                "type": "admin",
                "role": "super_admin"
            }
            access_token = create_access_token(token_data)
            
            return ResponseModel(
                success=True,
                message="Login successful",
                data=LoginResponse(
                    access_token=access_token,
                    admin={
                        "username": credentials.username,
                        "role": "super_admin"
                    }
                ).model_dump()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/me", response_model=ResponseModel)
async def get_current_admin_info(
    current_admin: dict = Depends(get_current_admin)
):
    """Get current admin information"""
    try:
        return ResponseModel(
            success=True,
            message="Admin info retrieved successfully",
            data=current_admin
        )
    except Exception as e:
        logger.error(f"Error getting admin info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
