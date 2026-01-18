"""Disease management API routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from storage.database.db import get_session
from storage.database.shared.model import Disease
from admin.schemas.common import ResponseModel, DiseaseCreate
from admin.auth import get_current_admin

router = APIRouter(prefix="/admin/api/diseases", tags=["Disease Management"])
logger = logging.getLogger(__name__)


@router.get("", response_model=ResponseModel)
async def get_diseases(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get paginated list of diseases"""
    try:
        query = db.query(Disease)
        
        if category:
            query = query.filter(Disease.category == category)
        
        if is_active is not None:
            query = query.filter(Disease.is_active == is_active)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (Disease.name.ilike(search_pattern)) |
                (Disease.name_en.ilike(search_pattern))
            )
        
        total = query.count()
        offset = (page - 1) * page_size
        diseases = query.order_by(Disease.created_at.desc()).offset(offset).limit(page_size).all()
        
        disease_data = []
        for disease in diseases:
            disease_dict = {
                "id": disease.id,
                "name": disease.name,
                "name_en": disease.name_en,
                "category": disease.category,
                "treatment_methods": disease.treatment_methods,
                "recovery_time": disease.recovery_time,
                "is_active": disease.is_active,
                "created_at": disease.created_at
            }
            disease_data.append(disease_dict)
        
        return ResponseModel(
            success=True,
            message="Diseases retrieved successfully",
            data={
                "items": disease_data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        )
    except Exception as e:
        logger.error(f"Error getting diseases: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{disease_id}", response_model=ResponseModel)
async def get_disease(
    disease_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get disease by ID"""
    try:
        disease = db.query(Disease).filter(Disease.id == disease_id).first()
        
        if not disease:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Disease not found"
            )
        
        disease_dict = {
            "id": disease.id,
            "name": disease.name,
            "name_en": disease.name_en,
            "category": disease.category,
            "description": disease.description,
            "treatment_methods": disease.treatment_methods,
            "recovery_time": disease.recovery_time,
            "is_active": disease.is_active,
            "created_at": disease.created_at,
            "updated_at": disease.updated_at
        }
        
        return ResponseModel(
            success=True,
            message="Disease retrieved successfully",
            data=disease_dict
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting disease {disease_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("", response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
async def create_disease(
    disease_data: DiseaseCreate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Create new disease"""
    try:
        new_disease = Disease(**disease_data.model_dump())
        db.add(new_disease)
        db.commit()
        db.refresh(new_disease)
        
        return ResponseModel(
            success=True,
            message="Disease created successfully",
            data={"id": new_disease.id}
        )
    except Exception as e:
        logger.error(f"Error creating disease: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{disease_id}", response_model=ResponseModel)
async def update_disease(
    disease_id: int,
    disease_data: dict,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Update disease"""
    try:
        disease = db.query(Disease).filter(Disease.id == disease_id).first()
        
        if not disease:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Disease not found"
            )
        
        for field, value in disease_data.items():
            if value is not None and hasattr(disease, field):
                setattr(disease, field, value)
        
        db.commit()
        db.refresh(disease)
        
        return ResponseModel(
            success=True,
            message="Disease updated successfully",
            data={"id": disease.id}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating disease {disease_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{disease_id}", response_model=ResponseModel)
async def delete_disease(
    disease_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Delete disease"""
    try:
        disease = db.query(Disease).filter(Disease.id == disease_id).first()
        
        if not disease:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Disease not found"
            )
        
        db.delete(disease)
        db.commit()
        
        return ResponseModel(
            success=True,
            message="Disease deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting disease {disease_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
