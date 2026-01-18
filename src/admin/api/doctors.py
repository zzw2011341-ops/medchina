"""Doctor management API routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from storage.database.db import get_session
from storage.database.shared.model import Doctor, Hospital, Disease
from admin.schemas.common import ResponseModel, DoctorCreate
from admin.auth import get_current_admin

router = APIRouter(prefix="/admin/api/doctors", tags=["Doctor Management"])
logger = logging.getLogger(__name__)


@router.get("", response_model=ResponseModel)
async def get_doctors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    hospital_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    search: Optional[str] = None,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get paginated list of doctors"""
    try:
        query = db.query(Doctor)
        
        if hospital_id:
            query = query.filter(Doctor.hospital_id == hospital_id)
        
        if is_active is not None:
            query = query.filter(Doctor.is_active == is_active)
        
        if is_featured is not None:
            query = query.filter(Doctor.is_featured == is_featured)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (Doctor.name.ilike(search_pattern)) |
                (Doctor.name_en.ilike(search_pattern)) |
                (Doctor.department.ilike(search_pattern))
            )
        
        total = query.count()
        offset = (page - 1) * page_size
        doctors = query.order_by(Doctor.created_at.desc()).offset(offset).limit(page_size).all()
        
        doctor_data = []
        for doctor in doctors:
            doctor_dict = {
                "id": doctor.id,
                "name": doctor.name,
                "name_en": doctor.name_en,
                "title": doctor.title,
                "department": doctor.department,
                "hospital_id": doctor.hospital_id,
                "hospital_name": doctor.hospital.name if doctor.hospital else None,
                "specialties": doctor.specialties,
                "experience_years": doctor.experience_years,
                "rating": doctor.rating,
                "review_count": doctor.review_count,
                "is_featured": doctor.is_featured,
                "is_active": doctor.is_active,
                "created_at": doctor.created_at
            }
            doctor_data.append(doctor_dict)
        
        return ResponseModel(
            success=True,
            message="Doctors retrieved successfully",
            data={
                "items": doctor_data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        )
    except Exception as e:
        logger.error(f"Error getting doctors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{doctor_id}", response_model=ResponseModel)
async def get_doctor(
    doctor_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get doctor by ID"""
    try:
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found"
            )
        
        doctor_dict = {
            "id": doctor.id,
            "name": doctor.name,
            "name_en": doctor.name_en,
            "title": doctor.title,
            "department": doctor.department,
            "hospital_id": doctor.hospital_id,
            "hospital_name": doctor.hospital.name if doctor.hospital else None,
            "specialties": doctor.specialties,
            "description": doctor.description,
            "experience_years": doctor.experience_years,
            "education": doctor.education,
            "avatar_url": doctor.avatar_url,
            "image_urls": doctor.image_urls,
            "success_rate": doctor.success_rate,
            "rating": doctor.rating,
            "review_count": doctor.review_count,
            "consultation_fee_min": doctor.consultation_fee_min,
            "consultation_fee_max": doctor.consultation_fee_max,
            "surgery_fee_min": doctor.surgery_fee_min,
            "surgery_fee_max": doctor.surgery_fee_max,
            "surgery_duration": doctor.surgery_duration,
            "recovery_duration": doctor.recovery_duration,
            "contact_info": doctor.contact_info,
            "is_featured": doctor.is_featured,
            "is_active": doctor.is_active,
            "created_at": doctor.created_at,
            "updated_at": doctor.updated_at
        }
        
        return ResponseModel(
            success=True,
            message="Doctor retrieved successfully",
            data=doctor_dict
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting doctor {doctor_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("", response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
async def create_doctor(
    doctor_data: DoctorCreate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Create new doctor"""
    try:
        # Validate hospital exists
        if doctor_data.hospital_id:
            hospital = db.query(Hospital).filter(Hospital.id == doctor_data.hospital_id).first()
            if not hospital:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Hospital not found"
                )
        
        new_doctor = Doctor(**doctor_data.model_dump())
        db.add(new_doctor)
        db.commit()
        db.refresh(new_doctor)
        
        return ResponseModel(
            success=True,
            message="Doctor created successfully",
            data={"id": new_doctor.id}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating doctor: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{doctor_id}", response_model=ResponseModel)
async def update_doctor(
    doctor_id: int,
    doctor_data: dict,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Update doctor"""
    try:
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found"
            )
        
        for field, value in doctor_data.items():
            if value is not None and hasattr(doctor, field):
                setattr(doctor, field, value)
        
        db.commit()
        db.refresh(doctor)
        
        return ResponseModel(
            success=True,
            message="Doctor updated successfully",
            data={"id": doctor.id}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating doctor {doctor_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{doctor_id}", response_model=ResponseModel)
async def delete_doctor(
    doctor_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Delete doctor"""
    try:
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found"
            )
        
        db.delete(doctor)
        db.commit()
        
        return ResponseModel(
            success=True,
            message="Doctor deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting doctor {doctor_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
