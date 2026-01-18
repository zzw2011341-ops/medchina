"""Attraction management API routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from storage.database.db import get_session
from storage.database.shared.model import TouristAttraction
from admin.schemas.common import ResponseModel, AttractionCreate
from admin.auth import get_current_admin

router = APIRouter(prefix="/admin/api/attractions", tags=["Attraction Management"])
logger = logging.getLogger(__name__)


@router.get("", response_model=ResponseModel)
async def get_attractions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    city: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    search: Optional[str] = None,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get paginated list of attractions"""
    try:
        query = db.query(TouristAttraction)
        
        if city:
            query = query.filter(TouristAttraction.city.ilike(f"%{city}%"))
        
        if category:
            query = query.filter(TouristAttraction.category == category)
        
        if is_active is not None:
            query = query.filter(TouristAttraction.is_active == is_active)
        
        if is_featured is not None:
            query = query.filter(TouristAttraction.is_featured == is_featured)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (TouristAttraction.name.ilike(search_pattern)) |
                (TouristAttraction.name_en.ilike(search_pattern))
            )
        
        total = query.count()
        offset = (page - 1) * page_size
        attractions = query.order_by(TouristAttraction.created_at.desc()).offset(offset).limit(page_size).all()
        
        attraction_data = []
        for attraction in attractions:
            attraction_dict = {
                "id": attraction.id,
                "name": attraction.name,
                "name_en": attraction.name_en,
                "city": attraction.city,
                "province": attraction.province,
                "category": attraction.category,
                "ticket_price": attraction.ticket_price,
                "rating": attraction.rating,
                "review_count": attraction.review_count,
                "is_featured": attraction.is_featured,
                "is_active": attraction.is_active,
                "created_at": attraction.created_at
            }
            attraction_data.append(attraction_dict)
        
        return ResponseModel(
            success=True,
            message="Attractions retrieved successfully",
            data={
                "items": attraction_data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        )
    except Exception as e:
        logger.error(f"Error getting attractions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{attraction_id}", response_model=ResponseModel)
async def get_attraction(
    attraction_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get attraction by ID"""
    try:
        attraction = db.query(TouristAttraction).filter(TouristAttraction.id == attraction_id).first()
        
        if not attraction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attraction not found"
            )
        
        attraction_dict = {
            "id": attraction.id,
            "name": attraction.name,
            "name_en": attraction.name_en,
            "city": attraction.city,
            "province": attraction.province,
            "category": attraction.category,
            "description": attraction.description,
            "image_urls": attraction.image_urls,
            "ticket_price": attraction.ticket_price,
            "rating": attraction.rating,
            "review_count": attraction.review_count,
            "is_featured": attraction.is_featured,
            "is_active": attraction.is_active,
            "created_at": attraction.created_at,
            "updated_at": attraction.updated_at
        }
        
        return ResponseModel(
            success=True,
            message="Attraction retrieved successfully",
            data=attraction_dict
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting attraction {attraction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("", response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
async def create_attraction(
    attraction_data: AttractionCreate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Create new attraction"""
    try:
        new_attraction = TouristAttraction(**attraction_data.model_dump())
        db.add(new_attraction)
        db.commit()
        db.refresh(new_attraction)
        
        return ResponseModel(
            success=True,
            message="Attraction created successfully",
            data={"id": new_attraction.id}
        )
    except Exception as e:
        logger.error(f"Error creating attraction: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{attraction_id}", response_model=ResponseModel)
async def update_attraction(
    attraction_id: int,
    attraction_data: dict,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Update attraction"""
    try:
        attraction = db.query(TouristAttraction).filter(TouristAttraction.id == attraction_id).first()
        
        if not attraction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attraction not found"
            )
        
        for field, value in attraction_data.items():
            if value is not None and hasattr(attraction, field):
                setattr(attraction, field, value)
        
        db.commit()
        db.refresh(attraction)
        
        return ResponseModel(
            success=True,
            message="Attraction updated successfully",
            data={"id": attraction.id}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating attraction {attraction_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{attraction_id}", response_model=ResponseModel)
async def delete_attraction(
    attraction_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Delete attraction"""
    try:
        attraction = db.query(TouristAttraction).filter(TouristAttraction.id == attraction_id).first()
        
        if not attraction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attraction not found"
            )
        
        db.delete(attraction)
        db.commit()
        
        return ResponseModel(
            success=True,
            message="Attraction deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting attraction {attraction_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
