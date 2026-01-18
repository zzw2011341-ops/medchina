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


@tool
def book_doctor_appointment(
    user_id: int,
    doctor_id: int,
    appointment_date: str,
    appointment_time: str,
    disease_info: Optional[str] = None,
    symptoms: Optional[str] = None,
    notes: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    预约医生（创建预约订单）
    
    Args:
        user_id: 用户ID
        doctor_id: 医生ID
        appointment_date: 预约日期（格式: YYYY-MM-DD）
        appointment_time: 预约时间（格式: HH:MM）
        disease_info: 病情描述
        symptoms: 症状列表（JSON字符串或逗号分隔）
        notes: 备注信息
        runtime: 运行时上下文
    
    Returns:
        预约创建结果
    """
    from datetime import datetime
    import json
    from storage.database.shared.model import User, Appointment, AppointmentStatus
    
    db = get_session()
    try:
        # 检查用户是否存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return f"❌ 错误: 用户ID {user_id} 不存在"
        
        # 检查医生是否存在
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            return f"❌ 错误: 医生ID {doctor_id} 不存在"
        
        # 解析日期
        try:
            appointment_dt = datetime.strptime(appointment_date, "%Y-%m-%d")
        except ValueError:
            return "❌ 错误: 预约日期格式不正确，请使用 YYYY-MM-DD 格式"
        
        # 解析症状
        symptoms_list = None
        if symptoms:
            try:
                symptoms_list = json.loads(symptoms)
            except json.JSONDecodeError:
                symptoms_list = [s.strip() for s in symptoms.split(",")]
        
        # 创建预约
        appointment = Appointment(
            user_id=user_id,
            doctor_id=doctor_id,
            hospital_id=doctor.hospital_id,
            appointment_date=appointment_dt,
            appointment_time=appointment_time,
            disease_info=disease_info,
            symptoms=symptoms_list,
            status=AppointmentStatus.PENDING,
            notes=notes
        )
        
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        
        # 获取医生费用信息
        consultation_fee = doctor.consultation_fee_min or doctor.consultation_fee_max
        surgery_fee = doctor.surgery_fee_min or doctor.surgery_fee_max
        
        fee_info = []
        if consultation_fee:
            fee_info.append(f"咨询费: ${consultation_fee}")
        if surgery_fee:
            fee_info.append(f"手术费: ${surgery_fee} - ${doctor.surgery_fee_max}")
        
        return f"""✅ 预约申请已提交！
📋 预约信息:
- 预约ID: {appointment.id}
- 医生: {doctor.name} ({doctor.title})
- 医院: {doctor.hospital.name if doctor.hospital else '未指定'}
- 预约日期: {appointment_date}
- 预约时间: {appointment_time}
- 病情描述: {disease_info or '未填写'}
- 状态: 待确认

💰 费用信息:
{chr(10).join(fee_info) if fee_info else '费用信息请联系医院'}

⚠️ 注意事项:
1. 请在24小时内完成预约支付
2. 使用 book_appointment_with_payment 工具创建带支付的预约
3. 支持的支付方式: 微信支付、VISA、MasterCard、支付宝、PayPal、银联"""
    
    except Exception as e:
        db.rollback()
        return f"❌ 预约失败: {str(e)}"
    finally:
        db.close()


@tool
def book_appointment_with_payment(
    user_id: int,
    doctor_id: int,
    appointment_date: str,
    appointment_time: str,
    payment_method: str = "visa",
    disease_info: Optional[str] = None,
    symptoms: Optional[str] = None,
    notes: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    预约医生并创建支付订单（一站式预约+支付）
    
    Args:
        user_id: 用户ID
        doctor_id: 医生ID
        appointment_date: 预约日期（格式: YYYY-MM-DD）
        appointment_time: 预约时间（格式: HH:MM）
        payment_method: 支付方式（wechat_pay/visa/mastercard/alipay/paypal/unionpay）
        disease_info: 病情描述
        symptoms: 症状列表（JSON字符串或逗号分隔）
        notes: 备注信息
        runtime: 运行时上下文
    
    Returns:
        预约和支付订单信息
    """
    from datetime import datetime
    import json
    from storage.database.shared.model import User, Appointment, AppointmentStatus
    
    db = get_session()
    try:
        # 检查用户是否存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return f"❌ 错误: 用户ID {user_id} 不存在"
        
        # 检查医生是否存在
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            return f"❌ 错误: 医生ID {doctor_id} 不存在"
        
        # 解析日期
        try:
            appointment_dt = datetime.strptime(appointment_date, "%Y-%m-%d")
        except ValueError:
            return "❌ 错误: 预约日期格式不正确，请使用 YYYY-MM-DD 格式"
        
        # 解析症状
        symptoms_list = None
        if symptoms:
            try:
                symptoms_list = json.loads(symptoms)
            except json.JSONDecodeError:
                symptoms_list = [s.strip() for s in symptoms.split(",")]
        
        # 创建预约
        appointment = Appointment(
            user_id=user_id,
            doctor_id=doctor_id,
            hospital_id=doctor.hospital_id,
            appointment_date=appointment_dt,
            appointment_time=appointment_time,
            disease_info=disease_info,
            symptoms=symptoms_list,
            status=AppointmentStatus.PENDING,
            notes=notes,
            consultation_fee=doctor.consultation_fee_min,
            surgery_fee=doctor.surgery_fee_min
        )
        
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        
        # 计算支付金额（使用咨询费或手术费）
        amount = doctor.surgery_fee_min or doctor.consultation_fee_min or 100.0
        if amount is None:
            amount = 100.0  # 默认金额
        
        # 创建支付订单
        from tools.payment_tool import create_payment as create_payment_func
        
        payment_result = create_payment_func(
            user_id=user_id,
            order_type="appointment",
            order_id=appointment.id,
            amount=float(amount),
            payment_method=payment_method,
            remark=f"预约医生 {doctor.name} - {appointment_date} {appointment_time}"
        )
        
        # 关联支付订单到预约
        payment_id = None
        if "支付订单ID:" in payment_result:
            try:
                payment_id_str = payment_result.split("支付订单ID: ")[1].split("\n")[0]
                payment_id = int(payment_id_str)
            except (ValueError, IndexError):
                pass
        
        if payment_id:
            appointment.payment_id = payment_id
            db.commit()
        
        return f"""✅ 预约和支付订单创建成功！

📋 预约信息:
- 预约ID: {appointment.id}
- 医生: {doctor.name} ({doctor.title})
- 医院: {doctor.hospital.name if doctor.hospital else '未指定'}
- 预约日期: {appointment_date}
- 预约时间: {appointment_time}

💳 支付信息:
{payment_result}

💡 下一步:
请使用 process_payment 工具完成支付，支付完成后预约将自动确认"""
    
    except Exception as e:
        db.rollback()
        return f"❌ 预约失败: {str(e)}"
    finally:
        db.close()


@tool
def get_appointment_detail(
    appointment_id: int,
    runtime: ToolRuntime = None
) -> str:
    """
    获取预约详细信息
    
    Args:
        appointment_id: 预约ID
        runtime: 运行时上下文
    
    Returns:
        预约详细信息
    """
    db = get_session()
    try:
        from storage.database.shared.model import Appointment, AppointmentStatus, PaymentStatus
        
        appointment = db.query(Appointment).options(
            joinedload(Appointment.doctor).joinedload(Doctor.hospital),
            joinedload(Appointment.user)
        ).filter(Appointment.id == appointment_id).first()
        
        if not appointment:
            return f"❌ 错误: 预约ID {appointment_id} 不存在"
        
        status_text = {
            AppointmentStatus.PENDING: "⏳ 待确认",
            AppointmentStatus.CONFIRMED: "✅ 已确认",
            AppointmentStatus.CANCELLED: "🚫 已取消",
            AppointmentStatus.COMPLETED: "✨ 已完成"
        }
        
        result = f"""📋 预约详细信息:
- 预约ID: {appointment.id}
- 医生: {appointment.doctor.name} ({appointment.doctor.title})
- 医院: {appointment.doctor.hospital.name if appointment.doctor.hospital else '未指定'}
- 科室: {appointment.doctor.department}
- 预约日期: {appointment.appointment_date.strftime('%Y-%m-%d') if appointment.appointment_date else '未指定'}
- 预约时间: {appointment.appointment_time or '未指定'}
- 状态: {status_text.get(appointment.status, appointment.status.value)}
- 病情描述: {appointment.disease_info or '未填写'}
"""
        
        if appointment.consultation_fee:
            result += f"- 咨询费用: ${appointment.consultation_fee}\n"
        
        if appointment.surgery_fee:
            result += f"- 手术费用: ${appointment.surgery_fee}\n"
        
        if appointment.payment_id:
            from storage.database.shared.model import PaymentRecord
            payment = db.query(PaymentRecord).filter(PaymentRecord.id == appointment.payment_id).first()
            if payment:
                payment_status_text = {
                    PaymentStatus.PENDING: "⏳ 待支付",
                    PaymentStatus.PAID: "✅ 已支付",
                    PaymentStatus.FAILED: "❌ 支付失败",
                    PaymentStatus.CANCELLED: "🚫 已取消",
                    PaymentStatus.REFUNDED: "💰 已退款"
                }
                result += f"\n💳 支付信息:\n"
                result += f"- 支付订单ID: {payment.id}\n"
                result += f"- 支付金额: {payment.currency} {payment.amount}\n"
                result += f"- 支付方式: {payment.payment_method.value}\n"
                result += f"- 支付状态: {payment_status_text.get(payment.status, payment.status.value)}\n"
        
        if appointment.notes:
            result += f"\n📝 备注: {appointment.notes}\n"
        
        return result
    
    finally:
        db.close()
