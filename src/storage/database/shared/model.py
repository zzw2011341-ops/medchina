from coze_coding_dev_sdk.database import Base

from sqlalchemy import MetaData, BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String, Text, JSON, func, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional
import datetime
import enum

metadata = MetaData()

class UserStatus(str, enum.Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class PlanStatus(str, enum.Enum):
    """出行方案状态枚举"""
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class AppointmentStatus(str, enum.Enum):
    """预约状态枚举"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, comment="用户邮箱")
    phone = Column(String(20), nullable=True, comment="手机号码")
    name = Column(String(128), nullable=False, comment="用户姓名")
    avatar_url = Column(String(512), nullable=True, comment="头像URL")
    country = Column(String(50), nullable=True, comment="国家")
    language = Column(String(10), default="en", nullable=False, comment="首选语言")
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING, nullable=False, comment="用户状态")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")
    
    # 关系
    travel_plans = relationship("TravelPlan", back_populates="user", cascade="all, delete-orphan")
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver")
    appointments = relationship("Appointment", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_country", "country"),
    )

class Hospital(Base):
    """医院表"""
    __tablename__ = "hospitals"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False, comment="医院名称")
    name_en = Column(String(256), nullable=True, comment="医院英文名称")
    city = Column(String(100), nullable=False, comment="所在城市")
    province = Column(String(100), nullable=False, comment="所在省份")
    address = Column(Text, nullable=True, comment="详细地址")
    level = Column(String(50), nullable=True, comment="医院等级（如：三级甲等）")
    description = Column(Text, nullable=True, comment="医院简介")
    specialties = Column(JSON, nullable=True, comment="擅长领域列表")
    logo_url = Column(String(512), nullable=True, comment="医院Logo URL")
    image_urls = Column(JSON, nullable=True, comment="医院图片URL列表")
    contact_phone = Column(String(20), nullable=True, comment="联系电话")
    website = Column(String(256), nullable=True, comment="官网地址")
    rating = Column(Float, nullable=True, comment="评分（0-5）")
    review_count = Column(Integer, nullable=True, comment="评价数量")
    is_featured = Column(Boolean, default=False, nullable=False, comment="是否推荐")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")
    
    # 关系
    doctors = relationship("Doctor", back_populates="hospital")
    
    __table_args__ = (
        Index("ix_hospitals_city", "city"),
        Index("ix_hospitals_featured", "is_featured"),
    )

class Disease(Base):
    """病种表"""
    __tablename__ = "diseases"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False, comment="病种名称")
    name_en = Column(String(256), nullable=True, comment="病种英文名称")
    category = Column(String(100), nullable=True, comment="病种分类")
    description = Column(Text, nullable=True, comment="病种描述")
    treatment_methods = Column(JSON, nullable=True, comment="治疗方式列表")
    recovery_time = Column(String(100), nullable=True, comment="恢复周期")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")
    
    # 关系
    doctors = relationship("Doctor", secondary="doctor_diseases", back_populates="diseases")
    
    __table_args__ = (
        Index("ix_diseases_category", "category"),
    )

class Doctor(Base):
    """医生表"""
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True, comment="所属医院ID")
    name = Column(String(128), nullable=False, comment="医生姓名")
    name_en = Column(String(128), nullable=True, comment="医生英文名")
    title = Column(String(100), nullable=True, comment="职称（如：主任医师）")
    department = Column(String(100), nullable=True, comment="科室")
    specialties = Column(JSON, nullable=True, comment="擅长领域列表")
    description = Column(Text, nullable=True, comment="医生简介")
    experience_years = Column(Integer, nullable=True, comment="从业年限")
    education = Column(String(256), nullable=True, comment="学历背景")
    avatar_url = Column(String(512), nullable=True, comment="头像URL")
    image_urls = Column(JSON, nullable=True, comment="图片URL列表")
    success_rate = Column(Float, nullable=True, comment="成功率（0-100）")
    rating = Column(Float, nullable=True, comment="评分（0-5）")
    review_count = Column(Integer, default=0, nullable=False, comment="评价数量")
    consultation_fee_min = Column(Float, nullable=True, comment="咨询费用最低价")
    consultation_fee_max = Column(Float, nullable=True, comment="咨询费用最高价")
    surgery_fee_min = Column(Float, nullable=True, comment="手术费用最低价")
    surgery_fee_max = Column(Float, nullable=True, comment="手术费用最高价")
    surgery_duration = Column(String(100), nullable=True, comment="手术时长")
    recovery_duration = Column(String(100), nullable=True, comment="修养周期")
    contact_info = Column(JSON, nullable=True, comment="联系方式")
    is_featured = Column(Boolean, default=False, nullable=False, comment="是否推荐")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")
    
    # 关系
    hospital = relationship("Hospital", back_populates="doctors")
    diseases = relationship("Disease", secondary="doctor_diseases", back_populates="doctors")
    appointments = relationship("Appointment", back_populates="doctor")
    
    __table_args__ = (
        Index("ix_doctors_hospital", "hospital_id"),
        Index("ix_doctors_department", "department"),
        Index("ix_doctors_featured", "is_featured"),
    )

class DoctorDisease(Base):
    """医生病种关联表"""
    __tablename__ = "doctor_diseases"
    
    doctor_id = Column(Integer, ForeignKey("doctors.id"), primary_key=True, comment="医生ID")
    disease_id = Column(Integer, ForeignKey("diseases.id"), primary_key=True, comment="病种ID")
    expertise_level = Column(String(50), nullable=True, comment="专业程度（expert/advanced/general）")
    experience_years = Column(Integer, nullable=True, comment="相关经验年限")
    success_rate = Column(Float, nullable=True, comment="相关领域成功率")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")

class TouristAttraction(Base):
    """旅游景点表"""
    __tablename__ = "tourist_attractions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False, comment="景点名称")
    name_en = Column(String(256), nullable=True, comment="景点英文名称")
    city = Column(String(100), nullable=False, comment="所在城市")
    province = Column(String(100), nullable=False, comment="所在省份")
    address = Column(Text, nullable=True, comment="详细地址")
    category = Column(String(50), nullable=True, comment="景点类别（自然/人文/历史等）")
    description = Column(Text, nullable=True, comment="景点简介")
    highlights = Column(JSON, nullable=True, comment="景点亮点列表")
    image_urls = Column(JSON, nullable=True, comment="景点图片URL列表")
    ticket_price = Column(Float, nullable=True, comment="门票价格")
    opening_hours = Column(String(100), nullable=True, comment="开放时间")
    recommended_duration = Column(String(50), nullable=True, comment="建议游玩时长")
    best_visit_season = Column(String(50), nullable=True, comment="最佳游览季节")
    rating = Column(Float, nullable=True, comment="评分（0-5）")
    review_count = Column(Integer, default=0, nullable=False, comment="评价数量")
    is_featured = Column(Boolean, default=False, nullable=False, comment="是否推荐")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")
    
    __table_args__ = (
        Index("ix_attractions_city", "city"),
        Index("ix_attractions_featured", "is_featured"),
    )

class TravelPlan(Base):
    """出行方案表"""
    __tablename__ = "travel_plans"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    plan_name = Column(String(256), nullable=True, comment="方案名称")
    destination = Column(String(100), nullable=False, comment="目的地城市")
    departure_city = Column(String(100), nullable=True, comment="出发城市")
    start_date = Column(DateTime(timezone=True), nullable=True, comment="开始日期")
    end_date = Column(DateTime(timezone=True), nullable=True, comment="结束日期")
    budget_min = Column(Float, nullable=True, comment="预算最低")
    budget_max = Column(Float, nullable=True, comment="预算最高")
    travel_purpose = Column(String(100), nullable=True, comment="出行目的（医疗/旅游/医疗旅游）")
    medical_info = Column(JSON, nullable=True, comment="医疗需求信息")
    hotel_booking = Column(JSON, nullable=True, comment="酒店预订信息")
    flight_booking = Column(JSON, nullable=True, comment="机票预订信息")
    train_booking = Column(JSON, nullable=True, comment="火车票预订信息")
    guide_booking = Column(JSON, nullable=True, comment="导游预订信息")
    itinerary = Column(JSON, nullable=True, comment="行程安排")
    status = Column(SQLEnum(PlanStatus), default=PlanStatus.DRAFT, nullable=False, comment="方案状态")
    notes = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")
    
    # 关系
    user = relationship("User", back_populates="travel_plans")
    
    __table_args__ = (
        Index("ix_plans_user", "user_id"),
        Index("ix_plans_status", "status"),
    )

class Message(Base):
    """消息表"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="发送者ID")
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="接收者ID（NULL为系统消息）")
    content = Column(Text, nullable=False, comment="消息内容")
    message_type = Column(String(50), default="text", nullable=False, comment="消息类型（text/image/file）")
    attachments = Column(JSON, nullable=True, comment="附件列表")
    is_read = Column(Boolean, default=False, nullable=False, comment="是否已读")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    
    # 关系
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")
    
    __table_args__ = (
        Index("ix_messages_sender", "sender_id"),
        Index("ix_messages_receiver", "receiver_id"),
        Index("ix_messages_created", "created_at"),
    )

class Appointment(Base):
    """预约记录表"""
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False, comment="医生ID")
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True, comment="医院ID")
    appointment_date = Column(DateTime(timezone=True), nullable=True, comment="预约日期")
    appointment_time = Column(String(50), nullable=True, comment="预约时间")
    disease_info = Column(Text, nullable=True, comment="病情描述")
    symptoms = Column(JSON, nullable=True, comment="症状列表")
    status = Column(SQLEnum(AppointmentStatus), default=AppointmentStatus.PENDING, nullable=False, comment="预约状态")
    notes = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")
    
    # 关系
    user = relationship("User", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    
    __table_args__ = (
        Index("ix_appointments_user", "user_id"),
        Index("ix_appointments_doctor", "doctor_id"),
        Index("ix_appointments_status", "status"),
    )

