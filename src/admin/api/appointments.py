"""Appointment management API routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from storage.database.db import get_session
from storage.database.shared.model import Appointment, User, Doctor
from admin.schemas.common import ResponseModel
from admin.auth import get_current_admin

router = APIRouter(prefix="/admin/api/appointments", tags=["Appointment Management"])
logger = logging.getLogger(__name__)


@router.get("", response_model=ResponseModel)
async def get_appointments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get paginated list of appointments"""
    try:
        query = db.query(Appointment)
        
        if user_id:
            query = query.filter(Appointment.user_id == user_id)
        
        if doctor_id:
            query = query.filter(Appointment.doctor_id == doctor_id)
        
        if status:
            query = query.filter(Appointment.status == status)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (Appointment.appointment_type.ilike(search_pattern)) |
                (Appointment.notes.ilike(search_pattern))
            )
        
        total = query.count()
        offset = (page - 1) * page_size
        appointments = query.order_by(Appointment.created_at.desc()).offset(offset).limit(page_size).all()
        
        appointment_data = []
        for apt in appointments:
            apt_dict = {
                "id": apt.id,
                "user_id": apt.user_id,
                "user_name": apt.user.name if apt.user else None,
                "user_email": apt.user.email if apt.user else None,
                "doctor_id": apt.doctor_id,
                "doctor_name": apt.doctor.name if apt.doctor else None,
                "appointment_date": apt.appointment_date,
                "status": apt.status,
                "appointment_type": apt.appointment_type,
                "fee": apt.fee,
                "created_at": apt.created_at
            }
            appointment_data.append(apt_dict)
        
        return ResponseModel(
            success=True,
            message="Appointments retrieved successfully",
            data={
                "items": appointment_data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        )
    except Exception as e:
        logger.error(f"Error getting appointments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{appointment_id}", response_model=ResponseModel)
async def get_appointment(
    appointment_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get appointment by ID"""
    try:
        apt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        
        if not apt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        apt_dict = {
            "id": apt.id,
            "user_id": apt.user_id,
            "user_name": apt.user.name if apt.user else None,
            "user_email": apt.user.email if apt.user else None,
            "doctor_id": apt.doctor_id,
            "doctor_name": apt.doctor.name if apt.doctor else None,
            "hospital_id": apt.hospital_id,
            "appointment_date": apt.appointment_date,
            "status": apt.status,
            "appointment_type": apt.appointment_type,
            "fee": apt.fee,
            "notes": apt.notes,
            "created_at": apt.created_at,
            "updated_at": apt.updated_at
        }
        
        return ResponseModel(
            success=True,
            message="Appointment retrieved successfully",
            data=apt_dict
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting appointment {appointment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/{appointment_id}/status", response_model=ResponseModel)
async def update_appointment_status(
    appointment_id: int,
    new_status: str,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Update appointment status"""
    try:
        apt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        
        if not apt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        apt.status = new_status
        db.commit()
        
        return ResponseModel(
            success=True,
            message="Appointment status updated successfully",
            data={"id": apt.id, "status": apt.status}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating appointment status {appointment_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
