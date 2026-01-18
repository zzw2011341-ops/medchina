"""Payment management API routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from storage.database.db import get_session
from storage.database.shared.model import PaymentRecord, User
from admin.schemas.common import ResponseModel
from admin.auth import get_current_admin

router = APIRouter(prefix="/admin/api/payments", tags=["Payment Management"])
logger = logging.getLogger(__name__)


@router.get("", response_model=ResponseModel)
async def get_payments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    payment_method: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get paginated list of payment records"""
    try:
        query = db.query(PaymentRecord)
        
        if user_id:
            query = query.filter(PaymentRecord.user_id == user_id)
        
        if status:
            query = query.filter(PaymentRecord.status == status)
        
        if payment_method:
            query = query.filter(PaymentRecord.payment_method == payment_method)
        
        if start_date:
            query = query.filter(PaymentRecord.created_at >= start_date)
        
        if end_date:
            query = query.filter(PaymentRecord.created_at <= end_date)
        
        total = query.count()
        offset = (page - 1) * page_size
        payments = query.order_by(PaymentRecord.created_at.desc()).offset(offset).limit(page_size).all()
        
        payment_data = []
        for payment in payments:
            payment_dict = {
                "id": payment.id,
                "user_id": payment.user_id,
                "user_name": payment.user.name if payment.user else None,
                "user_email": payment.user.email if payment.user else None,
                "order_id": payment.order_id,
                "amount": payment.amount,
                "currency": payment.currency,
                "payment_method": payment.payment_method,
                "status": payment.status,
                "transaction_id": payment.transaction_id,
                "created_at": payment.created_at,
                "updated_at": payment.updated_at
            }
            payment_data.append(payment_dict)
        
        return ResponseModel(
            success=True,
            message="Payments retrieved successfully",
            data={
                "items": payment_data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        )
    except Exception as e:
        logger.error(f"Error getting payments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{payment_id}", response_model=ResponseModel)
async def get_payment(
    payment_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get payment by ID"""
    try:
        payment = db.query(PaymentRecord).filter(PaymentRecord.id == payment_id).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        payment_dict = {
            "id": payment.id,
            "user_id": payment.user_id,
            "user_name": payment.user.name if payment.user else None,
            "user_email": payment.user.email if payment.user else None,
            "order_id": payment.order_id,
            "amount": payment.amount,
            "currency": payment.currency,
            "payment_method": payment.payment_method,
            "status": payment.status,
            "transaction_id": payment.transaction_id,
            "order_data": payment.order_data,
            "created_at": payment.created_at,
            "updated_at": payment.updated_at
        }
        
        return ResponseModel(
            success=True,
            message="Payment retrieved successfully",
            data=payment_dict
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment {payment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/stats/summary", response_model=ResponseModel)
async def get_payment_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get payment statistics summary"""
    try:
        # Default to last 30 days if no date range provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        query = db.query(PaymentRecord).filter(
            PaymentRecord.created_at >= start_date,
            PaymentRecord.created_at <= end_date
        )
        
        total_payments = query.count()
        total_amount = sum([p.amount for p in query.all() if p.amount])
        paid_payments = query.filter(PaymentRecord.status == "paid").count()
        paid_amount = sum([p.amount for p in query.filter(PaymentRecord.status == "paid").all() if p.amount])
        pending_payments = query.filter(PaymentRecord.status == "pending").count()
        
        stats = {
            "total_payments": total_payments,
            "total_amount": float(total_amount) if total_amount else 0,
            "paid_payments": paid_payments,
            "paid_amount": float(paid_amount) if paid_amount else 0,
            "pending_payments": pending_payments,
            "success_rate": round(paid_payments / total_payments * 100, 2) if total_payments > 0 else 0
        }
        
        return ResponseModel(
            success=True,
            message="Payment statistics retrieved successfully",
            data=stats
        )
    except Exception as e:
        logger.error(f"Error getting payment stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
