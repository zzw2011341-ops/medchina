"""User management API routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from storage.database.db import get_session
from storage.database.shared.model import User, UserStatus
from admin.schemas.common import (
    ResponseModel, UserCreate, UserUpdate, UserResponse,
    UserStatusEnum
)
from admin.auth import get_current_admin

router = APIRouter(prefix="/admin/api/users", tags=["User Management"])
logger = logging.getLogger(__name__)


@router.get("", response_model=ResponseModel)
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[UserStatusEnum] = None,
    country: Optional[str] = None,
    search: Optional[str] = None,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """
    Get paginated list of users
    """
    try:
        query = db.query(User)
        
        # Apply filters
        if status:
            query = query.filter(User.status == UserStatus(status.value))
        
        if country:
            query = query.filter(User.country.ilike(f"%{country}%"))
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (User.name.ilike(search_pattern)) |
                (User.email.ilike(search_pattern)) |
                (User.phone.ilike(search_pattern))
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        users = query.order_by(User.created_at.desc()).offset(offset).limit(page_size).all()
        
        # Convert to response models
        user_data = [UserResponse.model_validate(user) for user in users]
        
        return ResponseModel(
            success=True,
            message="Users retrieved successfully",
            data={
                "items": user_data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        )
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{user_id}", response_model=ResponseModel)
async def get_user(
    user_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get user by ID"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return ResponseModel(
            success=True,
            message="User retrieved successfully",
            data=UserResponse.model_validate(user)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("", response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Create new user"""
    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Create user
        new_user = User(
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone,
            passport_number=user_data.passport_number,
            country=user_data.country,
            language=user_data.language,
            status=UserStatus(user_data.status.value)
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return ResponseModel(
            success=True,
            message="User created successfully",
            data=UserResponse.model_validate(new_user)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{user_id}", response_model=ResponseModel)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Update user"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check email uniqueness if email is being updated
        if user_data.email and user_data.email != user.email:
            existing_user = db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
        
        # Update fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None and field != "status":
                setattr(user, field, value)
        
        # Handle status separately
        if user_data.status is not None:
            user.status = UserStatus(user_data.status.value)
        
        db.commit()
        db.refresh(user)
        
        return ResponseModel(
            success=True,
            message="User updated successfully",
            data=UserResponse.model_validate(user)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{user_id}", response_model=ResponseModel)
async def delete_user(
    user_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Delete user"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        db.delete(user)
        db.commit()
        
        return ResponseModel(
            success=True,
            message="User deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/{user_id}/status", response_model=ResponseModel)
async def update_user_status(
    user_id: int,
    new_status: UserStatusEnum,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Update user status"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.status = UserStatus(new_status.value)
        db.commit()
        db.refresh(user)
        
        return ResponseModel(
            success=True,
            message="User status updated successfully",
            data=UserResponse.model_validate(user)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user status {user_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
