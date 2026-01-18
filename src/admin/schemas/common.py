"""Common Pydantic schemas for admin API"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


class ResponseModel(BaseModel):
    """Standard API response model"""
    success: bool = True
    message: str = ""
    data: Optional[Any] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class AdminRoleEnum(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"


class UserCreate(BaseModel):
    """User creation schema"""
    name: str = Field(..., min_length=1, max_length=128)
    email: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    passport_number: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field(None, max_length=50)
    language: str = Field(default="en", max_length=10)
    status: UserStatusEnum = Field(default=UserStatusEnum.PENDING)


class UserUpdate(BaseModel):
    """User update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    email: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    passport_number: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=10)
    status: Optional[UserStatusEnum] = None
    avatar_url: Optional[str] = Field(None, max_length=512)


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    name: str
    email: str
    phone: Optional[str]
    passport_number: Optional[str]
    country: Optional[str]
    language: str
    status: str
    avatar_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class HospitalCreate(BaseModel):
    """Hospital creation schema"""
    name: str = Field(..., max_length=256)
    name_en: Optional[str] = Field(None, max_length=256)
    city: str = Field(..., max_length=100)
    province: str = Field(..., max_length=100)
    address: Optional[str] = None
    level: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    specialties: Optional[List[str]] = None
    logo_url: Optional[str] = Field(None, max_length=512)
    image_urls: Optional[List[str]] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=256)
    rating: Optional[float] = Field(None, ge=0, le=5)
    is_featured: bool = False
    is_active: bool = True


class HospitalUpdate(BaseModel):
    """Hospital update schema"""
    name: Optional[str] = Field(None, max_length=256)
    name_en: Optional[str] = Field(None, max_length=256)
    city: Optional[str] = Field(None, max_length=100)
    province: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = None
    level: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    specialties: Optional[List[str]] = None
    logo_url: Optional[str] = Field(None, max_length=512)
    image_urls: Optional[List[str]] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=256)
    rating: Optional[float] = Field(None, ge=0, le=5)
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None


class DiseaseCreate(BaseModel):
    """Disease creation schema"""
    name: str = Field(..., max_length=256)
    name_en: Optional[str] = Field(None, max_length=256)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    treatment_methods: Optional[List[str]] = None
    recovery_time: Optional[str] = Field(None, max_length=100)
    is_active: bool = True


class DoctorCreate(BaseModel):
    """Doctor creation schema"""
    hospital_id: Optional[int] = None
    name: str = Field(..., max_length=128)
    name_en: Optional[str] = Field(None, max_length=128)
    title: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    specialties: Optional[List[str]] = None
    description: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0)
    education: Optional[str] = Field(None, max_length=256)
    avatar_url: Optional[str] = Field(None, max_length=512)
    image_urls: Optional[List[str]] = None
    success_rate: Optional[float] = Field(None, ge=0, le=100)
    rating: Optional[float] = Field(None, ge=0, le=5)
    consultation_fee_min: Optional[float] = Field(None, ge=0)
    consultation_fee_max: Optional[float] = Field(None, ge=0)
    surgery_fee_min: Optional[float] = Field(None, ge=0)
    surgery_fee_max: Optional[float] = Field(None, ge=0)
    surgery_duration: Optional[str] = Field(None, max_length=100)
    recovery_duration: Optional[str] = Field(None, max_length=100)
    contact_info: Optional[dict] = None
    is_featured: bool = False
    is_active: bool = True


class AttractionCreate(BaseModel):
    """Attraction creation schema"""
    name: str = Field(..., max_length=256)
    name_en: Optional[str] = Field(None, max_length=256)
    city: str = Field(..., max_length=100)
    province: str = Field(..., max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    image_urls: Optional[List[str]] = None
    ticket_price: Optional[float] = Field(None, ge=0)
    rating: Optional[float] = Field(None, ge=0, le=5)
    review_count: Optional[int] = Field(None, ge=0)
    is_featured: bool = False
    is_active: bool = True


class LoginRequest(BaseModel):
    """Admin login request"""
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    """Admin login response"""
    access_token: str
    token_type: str = "bearer"
    admin: dict
