"""
医疗信息查询工具
"""
from langchain.tools import tool, ToolRuntime
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from coze_coding_dev_sdk.database import get_session
from storage.database.shared.model import Doctor, Hospital, Disease, DoctorDisease


def _format_doctor(doctor: Doctor, include_details: bool = False) -> dict:
    """格式化医生信息"""
    hospital_name = None
    hospital_city = None
    if doctor.hospital:
        hospital_name = doctor.hospital.name
        hospital_city = doctor.hospital.city
    
    result = {
        "id": doctor.id,
        "name": doctor.name,
        "name_en": doctor.name_en,
        "title": doctor.title,
        "department": doctor.department,
        "hospital": hospital_name,
        "hospital_city": hospital_city,
        "rating": doctor.rating,
        "success_rate": doctor.success_rate,
        "review_count": doctor.review_count,
    }
    
    if include_details:
        consultation_range = None
        if doctor.consultation_fee_min is not None and doctor.consultation_fee_max is not None:
            consultation_range = f"${doctor.consultation_fee_min}-${doctor.consultation_fee_max}"
        
        surgery_range = None
        if doctor.surgery_fee_min is not None and doctor.surgery_fee_max is not None:
            surgery_range = f"${doctor.surgery_fee_min}-${doctor.surgery_fee_max}"
        
        diseases_list = [d.name for d in doctor.diseases] if doctor.diseases is not None else []
        
        result.update({
            "specialties": doctor.specialties,
            "description": doctor.description,
            "experience_years": doctor.experience_years,
            "education": doctor.education,
            "consultation_fee_range": consultation_range,
            "surgery_fee_range": surgery_range,
            "surgery_duration": doctor.surgery_duration,
            "recovery_duration": doctor.recovery_duration,
            "diseases": diseases_list,
            "contact_info": doctor.contact_info,
        })
    
    return result


def _format_hospital(hospital: Hospital, include_details: bool = False) -> dict:
    """格式化医院信息"""
    result = {
        "id": hospital.id,
        "name": hospital.name,
        "name_en": hospital.name_en,
        "city": hospital.city,
        "province": hospital.province,
        "level": hospital.level,
        "rating": hospital.rating,
        "review_count": hospital.review_count,
        "is_featured": hospital.is_featured,
    }
    
    if include_details:
        doctor_count = len(hospital.doctors) if hospital.doctors else 0
        result.update({
            "address": hospital.address,
            "description": hospital.description,
            "specialties": hospital.specialties,
            "contact_phone": hospital.contact_phone,
            "website": hospital.website,
            "image_urls": hospital.image_urls,
            "doctor_count": doctor_count,
        })
    
    return result


def _format_disease(disease: Disease, include_details: bool = False) -> dict:
    """格式化病种信息"""
    result = {
        "id": disease.id,
        "name": disease.name,
        "name_en": disease.name_en,
        "category": disease.category,
    }
    
    if include_details:
        result.update({
            "description": disease.description,
            "treatment_methods": disease.treatment_methods,
            "recovery_time": disease.recovery_time,
        })
    
    return result


@tool
def search_doctors(
    keyword: str = None,
    city: Optional[str] = None,
    department: Optional[str] = None,
    disease: Optional[str] = None,
    limit: int = 10,
    runtime: ToolRuntime = None
) -> str:
    """
    查询医生信息
    
    Args:
        keyword: 搜索关键词（医生姓名或专长）
        city: 城市（可选）
        department: 科室（可选）
        disease: 病种名称（可选）
        limit: 返回结果数量限制
        runtime: 运行时上下文
    
    Returns:
        JSON格式的医生列表
    """
    db = get_session()
    try:
        query = db.query(Doctor).options(joinedload(Doctor.hospital), joinedload(Doctor.diseases))
        query = query.filter(Doctor.is_active == True)
        
        if city:
            query = query.join(Hospital).filter(Hospital.city.ilike(f"%{city}%"))
        
        if department:
            query = query.filter(Doctor.department.ilike(f"%{department}%"))
        
        if keyword:
            conditions = [
                Doctor.name.ilike(f"%{keyword}%"),
                Doctor.name_en.ilike(f"%{keyword}%")
            ]
            query = query.filter(or_(*conditions))
        
        doctors = query.limit(limit).all()
        
        if disease:
            # 过滤擅长该病种的医生
            disease_obj = db.query(Disease).filter(
                Disease.name.ilike(f"%{disease}%") | Disease.name_en.ilike(f"%{disease}%")
            ).first()
            if disease_obj:
                disease_doctor_ids = {dd.doctor_id for dd in db.query(DoctorDisease).filter(
                    DoctorDisease.disease_id == disease_obj.id
                ).all()}
                doctors = [d for d in doctors if d.id in disease_doctor_ids]
        
        result = [_format_doctor(d, include_details=False) for d in doctors]
        
        return f"找到 {len(result)} 位医生:\n{result}"
    
    finally:
        db.close()


@tool
def get_doctor_detail(
    doctor_id: int,
    runtime: ToolRuntime = None
) -> str:
    """
    获取医生详细信息
    
    Args:
        doctor_id: 医生ID
        runtime: 运行时上下文
    
    Returns:
        JSON格式的医生详细信息
    """
    db = get_session()
    try:
        doctor = db.query(Doctor).options(
            joinedload(Doctor.hospital),
            joinedload(Doctor.diseases)
        ).filter(Doctor.id == doctor_id).first()
        
        if not doctor:
            return "未找到该医生信息"
        
        result = _format_doctor(doctor, include_details=True)
        
        return f"医生详细信息:\n{result}"
    
    finally:
        db.close()


@tool
def search_hospitals(
    keyword: Optional[str] = None,
    city: Optional[str] = None,
    level: Optional[str] = None,
    limit: int = 10,
    runtime: ToolRuntime = None
) -> str:
    """
    查询医院信息
    
    Args:
        keyword: 搜索关键词（医院名称）
        city: 城市（可选）
        level: 医院等级（可选，如"三级甲等"）
        limit: 返回结果数量限制
        runtime: 运行时上下文
    
    Returns:
        JSON格式的医院列表
    """
    db = get_session()
    try:
        query = db.query(Hospital).filter(Hospital.is_active == True)
        
        if keyword:
            query = query.filter(
                Hospital.name.ilike(f"%{keyword}%") |
                Hospital.name_en.ilike(f"%{keyword}%")
            )
        
        if city:
            query = query.filter(Hospital.city.ilike(f"%{city}%"))
        
        if level:
            query = query.filter(Hospital.level.ilike(f"%{level}%"))
        
        # 优先显示推荐的医院
        query = query.order_by(Hospital.is_featured.desc(), Hospital.id)
        
        hospitals = query.limit(limit).all()
        result = [_format_hospital(h, include_details=False) for h in hospitals]
        
        return f"找到 {len(result)} 家医院:\n{result}"
    
    finally:
        db.close()


@tool
def get_hospital_detail(
    hospital_id: int,
    runtime: ToolRuntime = None
) -> str:
    """
    获取医院详细信息
    
    Args:
        hospital_id: 医院ID
        runtime: 运行时上下文
    
    Returns:
        JSON格式的医院详细信息
    """
    db = get_session()
    try:
        hospital = db.query(Hospital).options(joinedload(Hospital.doctors)).filter(
            Hospital.id == hospital_id
        ).first()
        
        if not hospital:
            return "未找到该医院信息"
        
        result = _format_hospital(hospital, include_details=True)
        
        return f"医院详细信息:\n{result}"
    
    finally:
        db.close()


@tool
def search_diseases(
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 10,
    runtime: ToolRuntime = None
) -> str:
    """
    查询病种信息
    
    Args:
        keyword: 搜索关键词（病种名称）
        category: 病种分类（可选）
        limit: 返回结果数量限制
        runtime: 运行时上下文
    
    Returns:
        JSON格式的病种列表
    """
    db = get_session()
    try:
        query = db.query(Disease).filter(Disease.is_active == True)
        
        if keyword:
            query = query.filter(
                Disease.name.ilike(f"%{keyword}%") |
                Disease.name_en.ilike(f"%{keyword}%")
            )
        
        if category:
            query = query.filter(Disease.category.ilike(f"%{category}%"))
        
        diseases = query.limit(limit).all()
        result = [_format_disease(d, include_details=True) for d in diseases]
        
        return f"找到 {len(result)} 个病种:\n{result}"
    
    finally:
        db.close()


@tool
def get_featured_doctors(
    limit: int = 5,
    runtime: ToolRuntime = None
) -> str:
    """
    获取推荐的医生列表
    
    Args:
        limit: 返回结果数量限制
        runtime: 运行时上下文
    
    Returns:
        JSON格式的推荐医生列表
    """
    db = get_session()
    try:
        query = db.query(Doctor).options(
            joinedload(Doctor.hospital),
            joinedload(Doctor.diseases)
        ).filter(Doctor.is_featured == True, Doctor.is_active == True)
        
        doctors = query.order_by(Doctor.rating.desc()).limit(limit).all()
        result = [_format_doctor(d, include_details=True) for d in doctors]
        
        return f"推荐医生 ({len(result)} 位):\n{result}"
    
    finally:
        db.close()


@tool
def get_featured_hospitals(
    limit: int = 5,
    runtime: ToolRuntime = None
) -> str:
    """
    获取推荐的医院列表
    
    Args:
        limit: 返回结果数量限制
        runtime: 运行时上下文
    
    Returns:
        JSON格式的推荐医院列表
    """
    db = get_session()
    try:
        query = db.query(Hospital).filter(Hospital.is_featured == True, Hospital.is_active == True)
        
        hospitals = query.order_by(Hospital.rating.desc()).limit(limit).all()
        result = [_format_hospital(h, include_details=True) for h in hospitals]
        
        return f"推荐医院 ({len(hospitals)} 家):\n{result}"
    
    finally:
        db.close()
