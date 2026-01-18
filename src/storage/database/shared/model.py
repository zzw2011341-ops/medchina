from typing import Optional
import datetime
import enum

from sqlalchemy import MetaData, BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String, Text, JSON, func, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# 创建自定义 Base 类
class Base(DeclarativeBase):
    """数据库模型基类"""
    pass

class UserStatus(str, enum.Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class AdminRole(str, enum.Enum):
    """管理员角色枚举"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"

class OperationType(str, enum.Enum):
    """操作类型枚举"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    QUERY = "query"
    EXPORT = "export"
    APPROVE = "approve"
    REJECT = "reject"

class BillType(str, enum.Enum):
    """账单类型枚举"""
    MEDICAL = "medical"
    FLIGHT = "flight"
    HOTEL = "hotel"
    TRAIN = "train"
    TICKET = "ticket"
    GUIDE = "guide"
    OTHER = "other"

class ExpenseType(str, enum.Enum):
    """费用类型枚举"""
    SERVICE_FEE = "service_fee"
    COMMISSION = "commission"
    REFUND = "refund"
    OPERATING_COST = "operating_cost"
    OTHER = "other"

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

class PaymentMethod(str, enum.Enum):
    """支付方式枚举"""
    WECHAT_PAY = "wechat_pay"
    VISA = "visa"
    MASTERCARD = "mastercard"
    ALIPAY = "alipay"
    PAYPAL = "paypal"
    UNIONPAY = "unionpay"

class PaymentStatus(str, enum.Enum):
    """支付状态枚举"""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class OrderStatus(str, enum.Enum):
    """订单状态枚举"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    REFUNDED = "refunded"

class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, comment="用户邮箱")
    phone = Column(String(20), nullable=True, comment="手机号码")
    name = Column(String(128), nullable=False, comment="用户姓名")
    passport_number = Column(String(50), nullable=True, comment="护照号码")
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
    payment_records = relationship("PaymentRecord", cascade="all, delete-orphan")
    
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
    payment_id = Column(Integer, ForeignKey("payment_records.id"), nullable=True, comment="支付记录ID")
    consultation_fee = Column(Float, nullable=True, comment="咨询费用")
    surgery_fee = Column(Float, nullable=True, comment="手术费用")
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

class PaymentRecord(Base):
    """支付记录表"""
    __tablename__ = "payment_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    order_type = Column(String(50), nullable=False, comment="订单类型（appointment/flight/hotel/train/ticket）")
    order_id = Column(Integer, nullable=True, comment="关联订单ID")
    amount = Column(Float, nullable=False, comment="支付金额")
    currency = Column(String(10), default="USD", nullable=False, comment="货币类型")
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False, comment="支付方式")
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False, comment="支付状态")
    transaction_id = Column(String(128), nullable=True, comment="交易流水号")
    payment_time = Column(DateTime(timezone=True), nullable=True, comment="支付时间")
    refund_time = Column(DateTime(timezone=True), nullable=True, comment="退款时间")
    refund_amount = Column(Float, nullable=True, comment="退款金额")
    remark = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")
    
    __table_args__ = (
        Index("ix_payments_user", "user_id"),
        Index("ix_payments_order", "order_id"),
        Index("ix_payments_status", "status"),
    )

class FlightOrder(Base):
    """机票订单表"""
    __tablename__ = "flight_orders"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    travel_plan_id = Column(Integer, ForeignKey("travel_plans.id"), nullable=True, comment="出行方案ID")
    flight_number = Column(String(50), nullable=False, comment="航班号")
    airline = Column(String(100), nullable=True, comment="航空公司")
    departure_city = Column(String(100), nullable=False, comment="出发城市")
    arrival_city = Column(String(100), nullable=False, comment="到达城市")
    departure_time = Column(DateTime(timezone=True), nullable=False, comment="出发时间")
    arrival_time = Column(DateTime(timezone=True), nullable=False, comment="到达时间")
    passenger_name = Column(String(128), nullable=False, comment="乘客姓名")
    passenger_id_number = Column(String(50), nullable=True, comment="证件号码")
    seat_class = Column(String(20), nullable=True, comment="舱位等级（economy/business/first）")
    seat_number = Column(String(10), nullable=True, comment="座位号")
    price = Column(Float, nullable=False, comment="机票价格")
    currency = Column(String(10), default="USD", nullable=False, comment="货币类型")
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False, comment="订单状态")
    payment_id = Column(Integer, ForeignKey("payment_records.id"), nullable=True, comment="支付记录ID")
    booking_reference = Column(String(50), nullable=True, comment="预订参考号")
    notes = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")
    
    __table_args__ = (
        Index("ix_flight_orders_user", "user_id"),
        Index("ix_flight_orders_plan", "travel_plan_id"),
        Index("ix_flight_orders_status", "status"),
    )

class HotelOrder(Base):
    """酒店订单表"""
    __tablename__ = "hotel_orders"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    travel_plan_id = Column(Integer, ForeignKey("travel_plans.id"), nullable=True, comment="出行方案ID")
    hotel_name = Column(String(256), nullable=False, comment="酒店名称")
    hotel_address = Column(Text, nullable=True, comment="酒店地址")
    city = Column(String(100), nullable=False, comment="城市")
    room_type = Column(String(100), nullable=True, comment="房型（single/double/suite等）")
    check_in_date = Column(DateTime(timezone=True), nullable=False, comment="入住日期")
    check_out_date = Column(DateTime(timezone=True), nullable=False, comment="退房日期")
    guest_name = Column(String(128), nullable=False, comment="入住人姓名")
    number_of_rooms = Column(Integer, default=1, nullable=False, comment="房间数量")
    number_of_guests = Column(Integer, default=1, nullable=False, comment="入住人数")
    price_per_night = Column(Float, nullable=False, comment="每晚价格")
    total_price = Column(Float, nullable=False, comment="总价格")
    currency = Column(String(10), default="USD", nullable=False, comment="货币类型")
    breakfast_included = Column(Boolean, default=False, nullable=False, comment="是否含早餐")
    cancellation_policy = Column(Text, nullable=True, comment="取消政策")
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False, comment="订单状态")
    payment_id = Column(Integer, ForeignKey("payment_records.id"), nullable=True, comment="支付记录ID")
    booking_reference = Column(String(50), nullable=True, comment="预订参考号")
    notes = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")
    
    __table_args__ = (
        Index("ix_hotel_orders_user", "user_id"),
        Index("ix_hotel_orders_plan", "travel_plan_id"),
        Index("ix_hotel_orders_status", "status"),
    )

class TrainTicketOrder(Base):
    """车票订单表"""
    __tablename__ = "train_ticket_orders"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    travel_plan_id = Column(Integer, ForeignKey("travel_plans.id"), nullable=True, comment="出行方案ID")
    train_number = Column(String(50), nullable=False, comment="车次")
    train_type = Column(String(20), nullable=True, comment="车型（high_speed/express/regular）")
    departure_station = Column(String(100), nullable=False, comment="出发车站")
    arrival_station = Column(String(100), nullable=False, comment="到达车站")
    departure_city = Column(String(100), nullable=False, comment="出发城市")
    arrival_city = Column(String(100), nullable=False, comment="到达城市")
    departure_time = Column(DateTime(timezone=True), nullable=False, comment="出发时间")
    arrival_time = Column(DateTime(timezone=True), nullable=False, comment="到达时间")
    passenger_name = Column(String(128), nullable=False, comment="乘客姓名")
    passenger_id_number = Column(String(50), nullable=True, comment="证件号码")
    seat_type = Column(String(20), nullable=True, comment="座席类型（first/second/soft_sleeper/hard_sleeper等）")
    seat_number = Column(String(10), nullable=True, comment="座位号")
    carriage_number = Column(String(10), nullable=True, comment="车厢号")
    price = Column(Float, nullable=False, comment="车票价格")
    currency = Column(String(10), default="USD", nullable=False, comment="货币类型")
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False, comment="订单状态")
    payment_id = Column(Integer, ForeignKey("payment_records.id"), nullable=True, comment="支付记录ID")
    booking_reference = Column(String(50), nullable=True, comment="预订参考号")
    notes = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")
    
    __table_args__ = (
        Index("ix_train_orders_user", "user_id"),
        Index("ix_train_orders_plan", "travel_plan_id"),
        Index("ix_train_orders_status", "status"),
    )

class AttractionTicketOrder(Base):
    """景点门票订单表"""
    __tablename__ = "attraction_ticket_orders"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    travel_plan_id = Column(Integer, ForeignKey("travel_plans.id"), nullable=True, comment="出行方案ID")
    attraction_id = Column(Integer, ForeignKey("tourist_attractions.id"), nullable=False, comment="景点ID")
    attraction_name = Column(String(256), nullable=False, comment="景点名称")
    visit_date = Column(DateTime(timezone=True), nullable=False, comment="游览日期")
    visit_time = Column(String(50), nullable=True, comment="游览时间")
    ticket_type = Column(String(50), nullable=True, comment="门票类型（adult/child/senior/group等）")
    ticket_count = Column(Integer, default=1, nullable=False, comment="门票数量")
    visitor_name = Column(String(128), nullable=False, comment="游客姓名")
    visitor_phone = Column(String(20), nullable=True, comment="游客电话")
    unit_price = Column(Float, nullable=False, comment="单价")
    total_price = Column(Float, nullable=False, comment="总价")
    currency = Column(String(10), default="USD", nullable=False, comment="货币类型")
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False, comment="订单状态")
    payment_id = Column(Integer, ForeignKey("payment_records.id"), nullable=True, comment="支付记录ID")
    booking_reference = Column(String(50), nullable=True, comment="预订参考号")
    qr_code = Column(String(512), nullable=True, comment="二维码（用于入园验证）")
    notes = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")
    
    __table_args__ = (
        Index("ix_ticket_orders_user", "user_id"),
        Index("ix_ticket_orders_plan", "travel_plan_id"),
        Index("ix_ticket_orders_attraction", "attraction_id"),
        Index("ix_ticket_orders_status", "status"),
    )

class Admin(Base):
    """管理员表"""
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(128), unique=True, nullable=False, comment="用户名")
    email = Column(String(255), unique=True, nullable=False, comment="邮箱")
    phone = Column(String(20), nullable=True, comment="手机号码")
    name = Column(String(128), nullable=False, comment="姓名")
    password_hash = Column(String(256), nullable=False, comment="密码哈希")
    role = Column(SQLEnum(AdminRole), default=AdminRole.MANAGER, nullable=False, comment="角色")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否启用")
    last_login_at = Column(DateTime(timezone=True), nullable=True, comment="最后登录时间")
    last_login_ip = Column(String(50), nullable=True, comment="最后登录IP")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")
    
    # 关系
    operation_logs = relationship("OperationLog", back_populates="admin")
    
    __table_args__ = (
        Index("ix_admins_username", "username"),
        Index("ix_admins_email", "email"),
        Index("ix_admins_role", "role"),
    )

class OperationLog(Base):
    """操作日志表"""
    __tablename__ = "operation_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False, comment="管理员ID")
    operation_type = Column(SQLEnum(OperationType), nullable=False, comment="操作类型")
    module = Column(String(50), nullable=False, comment="操作模块")
    action = Column(String(100), nullable=False, comment="操作动作")
    target_id = Column(Integer, nullable=True, comment="目标ID")
    target_type = Column(String(50), nullable=True, comment="目标类型")
    request_params = Column(JSON, nullable=True, comment="请求参数")
    response_data = Column(JSON, nullable=True, comment="响应数据")
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    user_agent = Column(String(512), nullable=True, comment="用户代理")
    status = Column(String(20), default="success", nullable=False, comment="操作状态")
    error_message = Column(Text, nullable=True, comment="错误信息")
    execution_time = Column(Integer, nullable=True, comment="执行时间（毫秒）")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    
    # 关系
    admin = relationship("Admin", back_populates="operation_logs")
    
    __table_args__ = (
        Index("ix_operation_logs_admin", "admin_id"),
        Index("ix_operation_logs_type", "operation_type"),
        Index("ix_operation_logs_created", "created_at"),
    )

class FinanceConfig(Base):
    """财务配置表"""
    __tablename__ = "finance_configs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(100), unique=True, nullable=False, comment="配置键")
    config_value = Column(Text, nullable=False, comment="配置值")
    config_type = Column(String(50), default="string", nullable=False, comment="配置类型")
    description = Column(Text, nullable=True, comment="配置描述")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")
    
    __table_args__ = (
        Index("ix_finance_configs_key", "config_key"),
    )

class BillDetail(Base):
    """账单明细表"""
    __tablename__ = "bill_details"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    payment_id = Column(Integer, ForeignKey("payment_records.id"), nullable=True, comment="支付记录ID")
    travel_plan_id = Column(Integer, ForeignKey("travel_plans.id"), nullable=True, comment="出行方案ID")
    bill_type = Column(SQLEnum(BillType), nullable=False, comment="账单类型")
    item_name = Column(String(256), nullable=False, comment="项目名称")
    item_description = Column(Text, nullable=True, comment="项目描述")
    quantity = Column(Integer, default=1, nullable=False, comment="数量")
    unit_price = Column(Float, nullable=False, comment="单价")
    total_price = Column(Float, nullable=False, comment="总价")
    currency = Column(String(10), default="USD", nullable=False, comment="货币类型")
    discount = Column(Float, default=0.0, nullable=False, comment="折扣金额")
    actual_amount = Column(Float, nullable=False, comment="实际金额")
    service_fee_rate = Column(Float, default=0.05, nullable=False, comment="中介费率（默认5%）")
    service_fee = Column(Float, default=0.0, nullable=False, comment="中介费金额")
    reference_order_id = Column(Integer, nullable=True, comment="关联订单ID")
    reference_order_type = Column(String(50), nullable=True, comment="关联订单类型")
    is_confirmed = Column(Boolean, default=False, nullable=False, comment="是否已确认")
    confirmed_at = Column(DateTime(timezone=True), nullable=True, comment="确认时间")
    notes = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")
    
    __table_args__ = (
        Index("ix_bill_details_user", "user_id"),
        Index("ix_bill_details_payment", "payment_id"),
        Index("ix_bill_details_type", "bill_type"),
        Index("ix_bill_details_created", "created_at"),
    )

class IncomeRecord(Base):
    """收入记录表"""
    __tablename__ = "income_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_id = Column(Integer, ForeignKey("payment_records.id"), nullable=True, comment="支付记录ID")
    bill_id = Column(Integer, ForeignKey("bill_details.id"), nullable=True, comment="账单明细ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    income_type = Column(String(50), nullable=False, comment="收入类型")
    amount = Column(Float, nullable=False, comment="收入金额")
    currency = Column(String(10), default="USD", nullable=False, comment="货币类型")
    service_fee_rate = Column(Float, nullable=False, comment="中介费率")
    service_fee_amount = Column(Float, nullable=False, comment="中介费金额")
    net_amount = Column(Float, nullable=False, comment="净收入（扣除中介费后）")
    transaction_date = Column(DateTime(timezone=True), nullable=False, comment="交易日期")
    status = Column(String(20), default="settled", nullable=False, comment="状态")
    notes = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")
    
    __table_args__ = (
        Index("ix_income_records_payment", "payment_id"),
        Index("ix_income_records_user", "user_id"),
        Index("ix_income_records_type", "income_type"),
        Index("ix_income_records_date", "transaction_date"),
    )

class ExpenseRecord(Base):
    """费用记录表"""
    __tablename__ = "expense_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    expense_type = Column(SQLEnum(ExpenseType), nullable=False, comment="费用类型")
    amount = Column(Float, nullable=False, comment="费用金额")
    currency = Column(String(10), default="USD", nullable=False, comment="货币类型")
    related_payment_id = Column(Integer, ForeignKey("payment_records.id"), nullable=True, comment="关联支付记录ID")
    related_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="关联用户ID")
    description = Column(Text, nullable=True, comment="费用描述")
    expense_date = Column(DateTime(timezone=True), nullable=False, comment="费用日期")
    status = Column(String(20), default="pending", nullable=False, comment="状态")
    approval_status = Column(String(20), default="pending", nullable=False, comment="审批状态")
    approved_by = Column(Integer, ForeignKey("admins.id"), nullable=True, comment="审批人ID")
    approved_at = Column(DateTime(timezone=True), nullable=True, comment="审批时间")
    notes = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")
    
    __table_args__ = (
        Index("ix_expense_records_type", "expense_type"),
        Index("ix_expense_records_date", "expense_date"),
        Index("ix_expense_records_status", "status"),
    )

