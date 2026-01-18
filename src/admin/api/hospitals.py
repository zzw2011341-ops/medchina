"""Hospital management API routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from storage.database.db import get_session
from storage.database.shared.model import Hospital
from admin.schemas.common import ResponseModel, HospitalCreate, HospitalUpdate
from admin.auth import get_current_admin

router = APIRouter(prefix="/admin/api/hospitals", tags=["Hospital Management"])
logger = logging.getLogger(__name__)


@router.get("", response_model=ResponseModel)
async def get_hospitals(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    city: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    search: Optional[str] = None,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get paginated list of hospitals"""
    try:
        query = db.query(Hospital)
        
        if city:
            query = query.filter(Hospital.city.ilike(f"%{city}%"))
        
        if is_active is not None:
            query = query.filter(Hospital.is_active == is_active)
        
        if is_featured is not None:
            query = query.filter(Hospital.is_featured == is_featured)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (Hospital.name.ilike(search_pattern)) |
                (Hospital.name_en.ilike(search_pattern)) |
                (Hospital.province.ilike(search_pattern))
            )
        
        total = query.count()
        offset = (page - 1) * page_size
        hospitals = query.order_by(Hospital.created_at.desc()).offset(offset).limit(page_size).all()
        
        hospital_data = []
        for hospital in hospitals:
            hospital_dict = {
                "id": hospital.id,
                "name": hospital.name,
                "name_en": hospital.name_en,
                "city": hospital.city,
                "province": hospital.province,
                "level": hospital.level,
                "rating": hospital.rating,
                "review_count": hospital.review_count,
                "is_featured": hospital.is_featured,
                "is_active": hospital.is_active,
                "created_at": hospital.created_at
            }
            hospital_data.append(hospital_dict)
        
        return ResponseModel(
            success=True,
            message="Hospitals retrieved successfully",
            data={
                "items": hospital_data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        )
    except Exception as e:
        logger.error(f"Error getting hospitals: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{hospital_id}", response_model=ResponseModel)
async def get_hospital(
    hospital_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get hospital by ID"""
    try:
        hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
        
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found"
            )
        
        hospital_dict = {
            "id": hospital.id,
            "name": hospital.name,
            "name_en": hospital.name_en,
            "city": hospital.city,
            "province": hospital.province,
            "address": hospital.address,
            "level": hospital.level,
            "description": hospital.description,
            "specialties": hospital.specialties,
            "logo_url": hospital.logo_url,
            "image_urls": hospital.image_urls,
            "contact_phone": hospital.contact_phone,
            "website": hospital.website,
            "rating": hospital.rating,
            "review_count": hospital.review_count,
            "is_featured": hospital.is_featured,
            "is_active": hospital.is_active,
            "created_at": hospital.created_at,
            "updated_at": hospital.updated_at
        }
        
        return ResponseModel(
            success=True,
            message="Hospital retrieved successfully",
            data=hospital_dict
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting hospital {hospital_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("", response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
async def create_hospital(
    hospital_data: HospitalCreate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Create new hospital"""
    try:
        new_hospital = Hospital(**hospital_data.model_dump())
        db.add(new_hospital)
        db.commit()
        db.refresh(new_hospital)
        
        return ResponseModel(
            success=True,
            message="Hospital created successfully",
            data={"id": new_hospital.id}
        )
    except Exception as e:
        logger.error(f"Error creating hospital: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{hospital_id}", response_model=ResponseModel)
async def update_hospital(
    hospital_id: int,
    hospital_data: HospitalUpdate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Update hospital"""
    try:
        hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
        
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found"
            )
        
        update_data = hospital_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(hospital, field, value)
        
        db.commit()
        db.refresh(hospital)
        
        return ResponseModel(
            success=True,
            message="Hospital updated successfully",
            data={"id": hospital.id}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating hospital {hospital_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{hospital_id}", response_model=ResponseModel)
async def delete_hospital(
    hospital_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Delete hospital"""
    try:
        hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
        
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found"
            )
        
        db.delete(hospital)
        db.commit()
        
        return ResponseModel(
            success=True,
            message="Hospital deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting hospital {hospital_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
