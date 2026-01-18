"""Travel plan management API routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from storage.database.db import get_session
from storage.database.shared.model import TravelPlan, User
from admin.schemas.common import ResponseModel
from admin.auth import get_current_admin

router = APIRouter(prefix="/admin/api/travel-plans", tags=["Travel Plan Management"])
logger = logging.getLogger(__name__)


@router.get("", response_model=ResponseModel)
async def get_travel_plans(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get paginated list of travel plans"""
    try:
        query = db.query(TravelPlan)
        
        if user_id:
            query = query.filter(TravelPlan.user_id == user_id)
        
        if status:
            query = query.filter(TravelPlan.status == status)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (TravelPlan.destination.ilike(search_pattern)) |
                (TravelPlan.plan_name.ilike(search_pattern))
            )
        
        total = query.count()
        offset = (page - 1) * page_size
        plans = query.order_by(TravelPlan.created_at.desc()).offset(offset).limit(page_size).all()
        
        plan_data = []
        for plan in plans:
            plan_dict = {
                "id": plan.id,
                "user_id": plan.user_id,
                "user_name": plan.user.name if plan.user else None,
                "user_email": plan.user.email if plan.user else None,
                "plan_name": plan.plan_name,
                "destination": plan.destination,
                "status": plan.status,
                "start_date": plan.start_date,
                "end_date": plan.end_date,
                "total_budget": plan.total_budget,
                "created_at": plan.created_at
            }
            plan_data.append(plan_dict)
        
        return ResponseModel(
            success=True,
            message="Travel plans retrieved successfully",
            data={
                "items": plan_data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        )
    except Exception as e:
        logger.error(f"Error getting travel plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{plan_id}", response_model=ResponseModel)
async def get_travel_plan(
    plan_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get travel plan by ID"""
    try:
        plan = db.query(TravelPlan).filter(TravelPlan.id == plan_id).first()
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Travel plan not found"
            )
        
        plan_dict = {
            "id": plan.id,
            "user_id": plan.user_id,
            "user_name": plan.user.name if plan.user else None,
            "user_email": plan.user.email if plan.user else None,
            "plan_name": plan.plan_name,
            "destination": plan.destination,
            "status": plan.status,
            "start_date": plan.start_date,
            "end_date": plan.end_date,
            "total_budget": plan.total_budget,
            "itinerary": plan.itinerary,
            "created_at": plan.created_at,
            "updated_at": plan.updated_at
        }
        
        return ResponseModel(
            success=True,
            message="Travel plan retrieved successfully",
            data=plan_dict
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting travel plan {plan_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/{plan_id}/status", response_model=ResponseModel)
async def update_travel_plan_status(
    plan_id: int,
    new_status: str,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Update travel plan status"""
    try:
        plan = db.query(TravelPlan).filter(TravelPlan.id == plan_id).first()
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Travel plan not found"
            )
        
        plan.status = new_status
        db.commit()
        
        return ResponseModel(
            success=True,
            message="Travel plan status updated successfully",
            data={"id": plan.id, "status": plan.status}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating travel plan status {plan_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
