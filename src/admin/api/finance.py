"""Finance management API routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from storage.database.db import get_session
from storage.database.shared.model import (
    FinanceConfig, BillDetail, IncomeRecord, ExpenseRecord,
    PaymentRecord, BillType, ExpenseType
)
from admin.schemas.common import ResponseModel
from admin.auth import get_current_admin

router = APIRouter(prefix="/admin/api/finance", tags=["Finance Management"])
logger = logging.getLogger(__name__)


@router.get("/statistics", response_model=ResponseModel)
async def get_finance_statistics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get finance statistics summary"""
    try:
        # Default to current month if no date range provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = datetime(end_date.year, end_date.month, 1)
        
        # Get commission rate
        config = db.query(FinanceConfig).filter(FinanceConfig.key == "commission_rate").first()
        commission_rate = float(config.value) if config else 5.0
        
        # Calculate income
        income_records = db.query(IncomeRecord).filter(
            IncomeRecord.created_at >= start_date,
            IncomeRecord.created_at <= end_date
        ).all()
        total_income = sum([r.amount for r in income_records if r.amount])
        
        # Calculate expenses
        expense_records = db.query(ExpenseRecord).filter(
            ExpenseRecord.created_at >= start_date,
            ExpenseRecord.created_at <= end_date
        ).all()
        total_expenses = sum([r.amount for r in expense_records if r.amount])
        
        # Calculate profit
        profit = total_income - total_expenses
        
        # Get payment stats
        payment_query = db.query(PaymentRecord).filter(
            PaymentRecord.created_at >= start_date,
            PaymentRecord.created_at <= end_date
        )
        total_payments = payment_query.count()
        paid_amount = sum([p.amount for p in payment_query.filter(PaymentRecord.status == "paid").all() if p.amount])
        
        stats = {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "commission_rate": commission_rate,
            "income": float(total_income) if total_income else 0,
            "expenses": float(total_expenses) if total_expenses else 0,
            "profit": float(profit) if profit else 0,
            "total_payments": total_payments,
            "paid_amount": float(paid_amount) if paid_amount else 0
        }
        
        return ResponseModel(
            success=True,
            message="Finance statistics retrieved successfully",
            data=stats
        )
    except Exception as e:
        logger.error(f"Error getting finance statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/commission-rate", response_model=ResponseModel)
async def get_commission_rate(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get current commission rate"""
    try:
        config = db.query(FinanceConfig).filter(FinanceConfig.key == "commission_rate").first()
        rate = float(config.value) if config else 5.0
        
        return ResponseModel(
            success=True,
            message="Commission rate retrieved successfully",
            data={"commission_rate": rate}
        )
    except Exception as e:
        logger.error(f"Error getting commission rate: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/commission-rate", response_model=ResponseModel)
async def update_commission_rate(
    new_rate: float,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Update commission rate"""
    try:
        if not (0 <= new_rate <= 100):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Commission rate must be between 0 and 100"
            )
        
        config = db.query(FinanceConfig).filter(FinanceConfig.key == "commission_rate").first()
        
        if config:
            config.value = str(new_rate)
        else:
            config = FinanceConfig(
                key="commission_rate",
                value=str(new_rate),
                description="Commission rate percentage"
            )
            db.add(config)
        
        db.commit()
        
        return ResponseModel(
            success=True,
            message="Commission rate updated successfully",
            data={"commission_rate": new_rate}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating commission rate: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/bills", response_model=ResponseModel)
async def get_bill_details(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    order_id: Optional[int] = None,
    bill_type: Optional[str] = None,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get paginated list of bill details"""
    try:
        query = db.query(BillDetail)
        
        if order_id:
            query = query.filter(BillDetail.order_id == order_id)
        
        if bill_type:
            query = query.filter(BillDetail.bill_type == BillType(bill_type))
        
        total = query.count()
        offset = (page - 1) * page_size
        bills = query.order_by(BillDetail.created_at.desc()).offset(offset).limit(page_size).all()
        
        bill_data = []
        for bill in bills:
            bill_dict = {
                "id": bill.id,
                "order_id": bill.order_id,
                "bill_type": bill.bill_type,
                "description": bill.description,
                "amount": bill.amount,
                "created_at": bill.created_at
            }
            bill_data.append(bill_dict)
        
        return ResponseModel(
            success=True,
            message="Bill details retrieved successfully",
            data={
                "items": bill_data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        )
    except Exception as e:
        logger.error(f"Error getting bill details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/income", response_model=ResponseModel)
async def get_income_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get paginated list of income records"""
    try:
        query = db.query(IncomeRecord)
        
        total = query.count()
        offset = (page - 1) * page_size
        records = query.order_by(IncomeRecord.created_at.desc()).offset(offset).limit(page_size).all()
        
        record_data = []
        for record in records:
            record_dict = {
                "id": record.id,
                "amount": record.amount,
                "description": record.description,
                "created_at": record.created_at
            }
            record_data.append(record_dict)
        
        return ResponseModel(
            success=True,
            message="Income records retrieved successfully",
            data={
                "items": record_data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        )
    except Exception as e:
        logger.error(f"Error getting income records: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/expenses", response_model=ResponseModel)
async def get_expense_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    expense_type: Optional[str] = None,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get paginated list of expense records"""
    try:
        query = db.query(ExpenseRecord)
        
        if expense_type:
            query = query.filter(ExpenseRecord.expense_type == ExpenseType(expense_type))
        
        total = query.count()
        offset = (page - 1) * page_size
        records = query.order_by(ExpenseRecord.created_at.desc()).offset(offset).limit(page_size).all()
        
        record_data = []
        for record in records:
            record_dict = {
                "id": record.id,
                "amount": record.amount,
                "expense_type": record.expense_type,
                "description": record.description,
                "created_at": record.created_at
            }
            record_data.append(record_dict)
        
        return ResponseModel(
            success=True,
            message="Expense records retrieved successfully",
            data={
                "items": record_data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        )
    except Exception as e:
        logger.error(f"Error getting expense records: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
