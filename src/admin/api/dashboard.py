"""Dashboard API routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging
from datetime import datetime, timedelta

from storage.database.db import get_session
from storage.database.shared.model import (
    User, Doctor, Hospital, Disease, TouristAttraction,
    TravelPlan, Appointment, PaymentRecord
)
from admin.schemas.common import ResponseModel
from admin.auth import get_current_admin

router = APIRouter(prefix="/admin/api/dashboard", tags=["Dashboard"])
logger = logging.getLogger(__name__)


@router.get("/stats", response_model=ResponseModel)
async def get_dashboard_stats(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get dashboard statistics"""
    try:
        # Count records
        user_count = db.query(func.count(User.id)).scalar()
        doctor_count = db.query(func.count(Doctor.id)).filter(Doctor.is_active == True).scalar()
        hospital_count = db.query(func.count(Hospital.id)).filter(Hospital.is_active == True).scalar()
        disease_count = db.query(func.count(Disease.id)).filter(Disease.is_active == True).scalar()
        attraction_count = db.query(func.count(TouristAttraction.id)).filter(TouristAttraction.is_active == True).scalar()
        
        # Travel plans by status
        travel_plans_total = db.query(func.count(TravelPlan.id)).scalar()
        travel_plans_confirmed = db.query(func.count(TravelPlan.id)).filter(TravelPlan.status == "confirmed").scalar()
        travel_plans_draft = db.query(func.count(TravelPlan.id)).filter(TravelPlan.status == "draft").scalar()
        
        # Appointments by status
        appointments_total = db.query(func.count(Appointment.id)).scalar()
        appointments_pending = db.query(func.count(Appointment.id)).filter(Appointment.status == "pending").scalar()
        appointments_confirmed = db.query(func.count(Appointment.id)).filter(Appointment.status == "confirmed").scalar()
        
        # Payments
        payments_total = db.query(func.count(PaymentRecord.id)).scalar()
        payments_paid = db.query(func.count(PaymentRecord.id)).filter(PaymentRecord.status == "paid").scalar()
        
        # Calculate revenue (paid payments)
        revenue = db.query(func.sum(PaymentRecord.amount)).filter(PaymentRecord.status == "paid").scalar() or 0
        
        stats = {
            "users": {
                "total": user_count
            },
            "doctors": {
                "active": doctor_count
            },
            "hospitals": {
                "active": hospital_count
            },
            "diseases": {
                "active": disease_count
            },
            "attractions": {
                "active": attraction_count
            },
            "travel_plans": {
                "total": travel_plans_total,
                "confirmed": travel_plans_confirmed,
                "draft": travel_plans_draft
            },
            "appointments": {
                "total": appointments_total,
                "pending": appointments_pending,
                "confirmed": appointments_confirmed
            },
            "payments": {
                "total": payments_total,
                "paid": payments_paid,
                "revenue": float(revenue)
            }
        }
        
        return ResponseModel(
            success=True,
            message="Dashboard statistics retrieved successfully",
            data=stats
        )
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/recent-activity", response_model=ResponseModel)
async def get_recent_activity(
    limit: int = 10,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get recent activity"""
    try:
        # Get recent users
        recent_users = db.query(User).order_by(User.created_at.desc()).limit(5).all()
        
        # Get recent travel plans
        recent_plans = db.query(TravelPlan).order_by(TravelPlan.created_at.desc()).limit(5).all()
        
        # Get recent payments
        recent_payments = db.query(PaymentRecord).order_by(PaymentRecord.created_at.desc()).limit(5).all()
        
        activity = {
            "recent_users": [
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "country": user.country,
                    "created_at": user.created_at
                } for user in recent_users
            ],
            "recent_plans": [
                {
                    "id": plan.id,
                    "user_name": plan.user.name if plan.user else None,
                    "destination": plan.destination,
                    "status": plan.status,
                    "created_at": plan.created_at
                } for plan in recent_plans
            ],
            "recent_payments": [
                {
                    "id": payment.id,
                    "user_name": payment.user.name if payment.user else None,
                    "amount": payment.amount,
                    "status": payment.status,
                    "created_at": payment.created_at
                } for payment in recent_payments
            ]
        }
        
        return ResponseModel(
            success=True,
            message="Recent activity retrieved successfully",
            data=activity
        )
    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
