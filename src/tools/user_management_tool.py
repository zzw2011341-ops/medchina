"""
后台用户管理工具
提供用户列表查询、详情查询、信息更新、状态管理等功能
"""
import json
from typing import Optional, Dict, Any
from langchain.tools import tool, ToolRuntime
from langchain_core.runnables import RunnableConfig
from coze_coding_dev_sdk.database import get_session
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

@tool
def get_user_list(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    country: Optional[str] = None,
    keyword: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    获取用户列表（后台管理用）
    
    Args:
        page: 页码，默认1
        page_size: 每页数量，默认20
        status: 用户状态筛选（active/inactive/pending）
        country: 国家筛选
        keyword: 关键词搜索（姓名、邮箱、电话）
        runtime: 工具运行时上下文
    
    Returns:
        用户列表（JSON格式）
    """
    from storage.database.shared.model import User, UserStatus
    
    try:
        db = get_session()
        query = db.query(User)
        
        # 状态筛选
        if status:
            try:
                status_enum = UserStatus(status)
                query = query.filter(User.status == status_enum)
            except ValueError:
                pass
        
        # 国家筛选
        if country:
            query = query.filter(User.country == country)
        
        # 关键词搜索
        if keyword:
            keyword_filter = or_(
                User.name.ilike(f"%{keyword}%"),
                User.email.ilike(f"%{keyword}%"),
                User.phone.ilike(f"%{keyword}%")
            )
            query = query.filter(keyword_filter)
        
        # 分页
        total = query.count()
        offset = (page - 1) * page_size
        users = query.order_by(User.created_at.desc()).offset(offset).limit(page_size).all()
        
        # 序列化结果
        user_list = []
        for user in users:
            user_dict = {
                "id": user.id,
                "email": user.email,
                "phone": user.phone,
                "name": user.name,
                "passport_number": user.passport_number,
                "avatar_url": user.avatar_url,
                "country": user.country,
                "language": user.language,
                "status": user.status.value if user.status else None,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }
            user_list.append(user_dict)
        
        return str({
            "success": True,
            "data": {
                "users": user_list,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": (total + page_size - 1) // page_size
                }
            }
        })
    except Exception as e:
        return str({
            "success": False,
            "message": f"获取用户列表失败: {str(e)}"
        })

@tool
def get_user_detail(user_id: int, runtime: ToolRuntime = None) -> str:
    """
    获取用户详细信息（后台管理用）
    
    Args:
        user_id: 用户ID
        runtime: 工具运行时上下文
    
    Returns:
        用户详细信息（JSON格式）
    """
    from storage.database.shared.model import User, TravelPlan, Appointment, PaymentRecord
    
    try:
        db = get_session()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return str({
                "success": False,
                "message": "用户不存在"
            })
        
        # 统计数据
        travel_plans_count = db.query(TravelPlan).filter(TravelPlan.user_id == user_id).count()
        appointments_count = db.query(Appointment).filter(Appointment.user_id == user_id).count()
        payments_count = db.query(PaymentRecord).filter(PaymentRecord.user_id == user_id).count()
        total_spent = db.query(PaymentRecord).filter(
            PaymentRecord.user_id == user_id,
            PaymentRecord.status == "paid"
        ).all()
        total_spent_amount = sum(p.amount for p in total_spent) if total_spent else 0
        
        user_dict = {
            "id": user.id,
            "email": user.email,
            "phone": user.phone,
            "name": user.name,
            "passport_number": user.passport_number,
            "avatar_url": user.avatar_url,
            "country": user.country,
            "language": user.language,
            "status": user.status.value if user.status else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "statistics": {
                "travel_plans_count": travel_plans_count,
                "appointments_count": appointments_count,
                "payments_count": payments_count,
                "total_spent": total_spent_amount
            }
        }
        
        return str({
            "success": True,
            "data": user_dict
        })
    except Exception as e:
        return str({
            "success": False,
            "message": f"获取用户详情失败: {str(e)}"
        })

@tool
def update_user_info(user_id: int, user_data: str, runtime: ToolRuntime = None) -> str:
    """
    更新用户信息（后台管理用）
    
    Args:
        user_id: 用户ID
        user_data: 用户数据JSON字符串
        runtime: 工具运行时上下文
    
    Returns:
        更新结果（JSON格式）
    """
    from storage.database.shared.model import User
    
    try:
        data = json.loads(user_data)
        db = get_session()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return str({
                "success": False,
                "message": "用户不存在"
            })
        
        # 更新字段
        update_fields = ["name", "phone", "email", "passport_number", "avatar_url", "country", "language"]
        updated_fields = []
        
        for field in update_fields:
            if field in data and data[field] is not None:
                setattr(user, field, data[field])
                updated_fields.append(field)
        
        db.commit()
        db.refresh(user)
        
        return str({
            "success": True,
            "message": "用户信息更新成功",
            "data": {
                "id": user.id,
                "updated_fields": updated_fields
            }
        })
    except json.JSONDecodeError:
        return str({
            "success": False,
            "message": "用户数据格式错误，请提供有效的JSON格式"
        })
    except Exception as e:
        db.rollback()
        return str({
            "success": False,
            "message": f"更新用户信息失败: {str(e)}"
        })

@tool
def update_user_status(user_id: int, status: str, runtime: ToolRuntime = None) -> str:
    """
    更新用户状态（后台管理用）
    
    Args:
        user_id: 用户ID
        status: 新状态（active/inactive/pending）
        runtime: 工具运行时上下文
    
    Returns:
        更新结果（JSON格式）
    """
    from storage.database.shared.model import User, UserStatus
    
    try:
        db = get_session()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return str({
                "success": False,
                "message": "用户不存在"
            })
        
        # 验证状态值
        try:
            new_status = UserStatus(status)
        except ValueError:
            return str({
                "success": False,
                "message": f"无效的用户状态: {status}"
            })
        
        user.status = new_status
        db.commit()
        db.refresh(user)
        
        return str({
            "success": True,
            "message": f"用户状态已更新为 {status}",
            "data": {
                "id": user.id,
                "status": user.status.value
            }
        })
    except Exception as e:
        db.rollback()
        return str({
            "success": False,
            "message": f"更新用户状态失败: {str(e)}"
        })

@tool
def create_user(user_data: str, runtime: ToolRuntime = None) -> str:
    """
    创建新用户（后台管理用）
    
    Args:
        user_data: 用户数据JSON字符串，必须包含email, name字段
        runtime: 工具运行时上下文
    
    Returns:
        创建结果（JSON格式）
    """
    from storage.database.shared.model import User, UserStatus
    
    try:
        data = json.loads(user_data)
        
        # 必填字段验证
        if "email" not in data or not data["email"]:
            return str({
                "success": False,
                "message": "邮箱为必填字段"
            })
        
        if "name" not in data or not data["name"]:
            return str({
                "success": False,
                "message": "姓名为必填字段"
            })
        
        db = get_session()
        
        # 检查邮箱是否已存在
        existing_user = db.query(User).filter(User.email == data["email"]).first()
        if existing_user:
            return str({
                "success": False,
                "message": "该邮箱已被使用"
            })
        
        # 创建用户
        new_user = User(
            email=data["email"],
            name=data["name"],
            phone=data.get("phone"),
            passport_number=data.get("passport_number"),
            avatar_url=data.get("avatar_url"),
            country=data.get("country"),
            language=data.get("language", "en"),
            status=UserStatus(data.get("status", "pending"))
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return str({
            "success": True,
            "message": "用户创建成功",
            "data": {
                "id": new_user.id,
                "email": new_user.email,
                "name": new_user.name,
                "status": new_user.status.value
            }
        })
    except json.JSONDecodeError:
        return str({
            "success": False,
            "message": "用户数据格式错误，请提供有效的JSON格式"
        })
    except Exception as e:
        db.rollback()
        return str({
            "success": False,
            "message": f"创建用户失败: {str(e)}"
        })

@tool
def delete_user(user_id: int, runtime: ToolRuntime = None) -> str:
    """
    删除用户（软删除，后台管理用）
    
    Args:
        user_id: 用户ID
        runtime: 工具运行时上下文
    
    Returns:
        删除结果（JSON格式）
    """
    from storage.database.shared.model import User
    
    try:
        db = get_session()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return str({
                "success": False,
                "message": "用户不存在"
            })
        
        # 软删除：将状态设置为inactive
        user.status = "inactive"
        db.commit()
        
        return str({
            "success": True,
            "message": "用户已删除（状态设置为inactive）",
            "data": {
                "id": user.id
            }
        })
    except Exception as e:
        db.rollback()
        return str({
            "success": False,
            "message": f"删除用户失败: {str(e)}"
        })
