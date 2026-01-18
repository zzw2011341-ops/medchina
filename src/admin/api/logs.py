"""Operation log management API routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from storage.database.db import get_session
from storage.database.shared.model import OperationLog, Admin
from admin.schemas.common import ResponseModel
from admin.auth import get_current_admin

router = APIRouter(prefix="/admin/api/logs", tags=["Operation Logs"])
logger = logging.getLogger(__name__)


@router.get("", response_model=ResponseModel)
async def get_operation_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin_id: Optional[int] = None,
    operation_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get paginated list of operation logs"""
    try:
        query = db.query(OperationLog)
        
        if admin_id:
            query = query.filter(OperationLog.admin_id == admin_id)
        
        if operation_type:
            query = query.filter(OperationLog.operation_type == operation_type)
        
        if resource_type:
            query = query.filter(OperationLog.resource_type == resource_type)
        
        if start_date:
            query = query.filter(OperationLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(OperationLog.created_at <= end_date)
        
        total = query.count()
        offset = (page - 1) * page_size
        logs = query.order_by(OperationLog.created_at.desc()).offset(offset).limit(page_size).all()
        
        log_data = []
        for log in logs:
            log_dict = {
                "id": log.id,
                "admin_id": log.admin_id,
                "admin_name": log.admin.username if log.admin else None,
                "operation_type": log.operation_type,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "description": log.description,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "created_at": log.created_at
            }
            log_data.append(log_dict)
        
        return ResponseModel(
            success=True,
            message="Operation logs retrieved successfully",
            data={
                "items": log_data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        )
    except Exception as e:
        logger.error(f"Error getting operation logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/stats/summary", response_model=ResponseModel)
async def get_log_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get operation log statistics"""
    try:
        # Default to last 7 days if no date range provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=7)
        
        query = db.query(OperationLog).filter(
            OperationLog.created_at >= start_date,
            OperationLog.created_at <= end_date
        )
        
        total_operations = query.count()
        
        # Count by operation type
        operation_counts = {}
        for op_type in ["create", "update", "delete", "query", "export", "approve", "reject"]:
            count = query.filter(OperationLog.operation_type == op_type).count()
            operation_counts[op_type] = count
        
        stats = {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "total_operations": total_operations,
            "operation_counts": operation_counts
        }
        
        return ResponseModel(
            success=True,
            message="Log statistics retrieved successfully",
            data=stats
        )
    except Exception as e:
        logger.error(f"Error getting log stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
