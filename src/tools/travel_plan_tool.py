"""
出行方案生成工具
"""
from langchain.tools import tool, ToolRuntime
from typing import Optional, Dict, Any
from datetime import datetime
from coze_coding_dev_sdk.database import get_session
from storage.database.shared.model import TravelPlan, User, PlanStatus


@tool
def create_travel_plan(
    user_id: int,
    destination: str,
    departure_city: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    budget_min: Optional[float] = None,
    budget_max: Optional[float] = None,
    travel_purpose: Optional[str] = None,
    medical_info: Optional[str] = None,
    notes: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    创建出行方案
    
    Args:
        user_id: 用户ID
        destination: 目的地城市
        departure_city: 出发城市
        start_date: 开始日期 (格式: YYYY-MM-DD)
        end_date: 结束日期 (格式: YYYY-MM-DD)
        budget_min: 预算最低金额
        budget_max: 预算最高金额
        travel_purpose: 出行目的（医疗/旅游/医疗旅游）
        medical_info: 医疗需求信息（JSON字符串）
        notes: 备注信息
        runtime: 运行时上下文
    
    Returns:
        创建结果
    """
    db = get_session()
    try:
        # 检查用户是否存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return f"错误: 用户ID {user_id} 不存在"
        
        # 解析日期
        start_dt = None
        end_dt = None
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                return "错误: 开始日期格式不正确，请使用 YYYY-MM-DD 格式"
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                return "错误: 结束日期格式不正确，请使用 YYYY-MM-DD 格式"
        
        # 解析医疗信息
        import json
        medical_data = None
        if medical_info:
            try:
                medical_data = json.loads(medical_info)
            except json.JSONDecodeError:
                medical_data = {"description": medical_info}
        
        # 创建出行方案
        plan = TravelPlan(
            user_id=user_id,
            destination=destination,
            departure_city=departure_city,
            start_date=start_dt,
            end_date=end_dt,
            budget_min=budget_min,
            budget_max=budget_max,
            travel_purpose=travel_purpose,
            medical_info=medical_data,
            notes=notes,
            status=PlanStatus.DRAFT
        )
        
        db.add(plan)
        db.commit()
        db.refresh(plan)
        
        return f"✅ 出行方案创建成功！\n方案ID: {plan.id}\n目的地: {destination}\n状态: 草稿\n\n请继续完善方案详情（酒店预订、机票预订、导游预订等）"
    
    except Exception as e:
        db.rollback()
        return f"创建失败: {str(e)}"
    finally:
        db.close()


@tool
def update_travel_plan(
    plan_id: int,
    hotel_booking: Optional[str] = None,
    flight_booking: Optional[str] = None,
    train_booking: Optional[str] = None,
    guide_booking: Optional[str] = None,
    itinerary: Optional[str] = None,
    notes: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    更新出行方案
    
    Args:
        plan_id: 方案ID
        hotel_booking: 酒店预订信息（JSON字符串）
        flight_booking: 机票预订信息（JSON字符串）
        train_booking: 火车票预订信息（JSON字符串）
        guide_booking: 导游预订信息（JSON字符串）
        itinerary: 行程安排（JSON字符串）
        notes: 备注信息
        runtime: 运行时上下文
    
    Returns:
        更新结果
    """
    import json
    
    db = get_session()
    try:
        plan = db.query(TravelPlan).filter(TravelPlan.id == plan_id).first()
        if not plan:
            return f"错误: 方案ID {plan_id} 不存在"
        
        # 更新字段
        if hotel_booking:
            try:
                hotel_data = json.loads(hotel_booking)
            except json.JSONDecodeError:
                hotel_data = {"description": hotel_booking}
            setattr(plan, 'hotel_booking', hotel_data)
        
        if flight_booking:
            try:
                flight_data = json.loads(flight_booking)
            except json.JSONDecodeError:
                flight_data = {"description": flight_booking}
            setattr(plan, 'flight_booking', flight_data)
        
        if train_booking:
            try:
                train_data = json.loads(train_booking)
            except json.JSONDecodeError:
                train_data = {"description": train_booking}
            setattr(plan, 'train_booking', train_data)
        
        if guide_booking:
            try:
                guide_data = json.loads(guide_booking)
            except json.JSONDecodeError:
                guide_data = {"description": guide_booking}
            setattr(plan, 'guide_booking', guide_data)
        
        if itinerary:
            try:
                itinerary_data = json.loads(itinerary)
            except json.JSONDecodeError:
                itinerary_data = {"description": itinerary}
            setattr(plan, 'itinerary', itinerary_data)
        
        if notes:
            setattr(plan, 'notes', notes)
        
        db.commit()
        db.refresh(plan)
        
        return f"✅ 出行方案更新成功！\n方案ID: {plan.id}\n状态: {plan.status.value}"
    
    except Exception as e:
        db.rollback()
        return f"更新失败: {str(e)}"
    finally:
        db.close()


@tool
def confirm_travel_plan(
    plan_id: int,
    runtime: ToolRuntime = None
) -> str:
    """
    确认出行方案
    
    Args:
        plan_id: 方案ID
        runtime: 运行时上下文
    
    Returns:
        确认结果
    """
    db = get_session()
    try:
        plan = db.query(TravelPlan).filter(TravelPlan.id == plan_id).first()
        if not plan:
            return f"错误: 方案ID {plan_id} 不存在"
        
        setattr(plan, 'status', PlanStatus.CONFIRMED)
        db.commit()
        db.refresh(plan)
        
        return f"✅ 出行方案已确认！\n方案ID: {plan.id}\n目的地: {plan.destination}\n状态: 已确认\n\n祝您中国之行愉快！"
    
    except Exception as e:
        db.rollback()
        return f"确认失败: {str(e)}"
    finally:
        db.close()


@tool
def get_travel_plan(
    plan_id: int,
    runtime: ToolRuntime = None
) -> str:
    """
    获取出行方案详情
    
    Args:
        plan_id: 方案ID
        runtime: 运行时上下文
    
    Returns:
        方案详细信息
    """
    db = get_session()
    try:
        plan = db.query(TravelPlan).filter(TravelPlan.id == plan_id).first()
        if not plan:
            return f"错误: 方案ID {plan_id} 不存在"
        
        start_date_str = plan.start_date.strftime("%Y-%m-%d") if plan.start_date is not None else None
        end_date_str = plan.end_date.strftime("%Y-%m-%d") if plan.end_date is not None else None
        
        budget_range = None
        if plan.budget_min is not None and plan.budget_max is not None:
            budget_range = f"${plan.budget_min}-${plan.budget_max}"
        
        result = {
            "id": plan.id,
            "user_id": plan.user_id,
            "destination": plan.destination,
            "departure_city": plan.departure_city,
            "start_date": start_date_str,
            "end_date": end_date_str,
            "budget_range": budget_range,
            "travel_purpose": plan.travel_purpose,
            "status": plan.status.value,
            "hotel_booking": plan.hotel_booking,
            "flight_booking": plan.flight_booking,
            "train_booking": plan.train_booking,
            "guide_booking": plan.guide_booking,
            "itinerary": plan.itinerary,
            "medical_info": plan.medical_info,
            "notes": plan.notes,
        }
        
        return f"出行方案详情:\n{result}"
    
    except Exception as e:
        return f"获取失败: {str(e)}"
    finally:
        db.close()


@tool
def generate_sample_plan(
    destination: str,
    days: int = 7,
    travel_purpose: str = "medical_tourism",
    runtime: ToolRuntime = None
) -> str:
    """
    生成示例出行方案（供参考）
    
    Args:
        destination: 目的地城市
        days: 停留天数
        travel_purpose: 出行目的（medical_tourism/tourism/medical）
        runtime: 运行时上下文
    
    Returns:
        示例出行方案
    """
    # 根据不同的目的地和天数生成示例方案
    sample_plans = {
        "北京": {
            "day_1": "抵达北京，入住酒店，休整",
            "day_2": "医院初诊，医生面诊",
            "day_3": "检查与确诊，制定治疗方案",
            "day_4": "休息日，游览天坛公园",
            "day_5": "治疗或手术",
            "day_6": "术后观察，游览故宫",
            "day_7": "复查，准备返程"
        },
        "上海": {
            "day_1": "抵达上海，入住酒店，休整",
            "day_2": "医院初诊，医生面诊",
            "day_3": "检查与确诊，制定治疗方案",
            "day_4": "休息日，游览外滩",
            "day_5": "治疗或手术",
            "day_6": "术后观察，游览豫园",
            "day_7": "复查，准备返程"
        },
        "广州": {
            "day_1": "抵达广州，入住酒店，休整",
            "day_2": "医院初诊，医生面诊",
            "day_3": "检查与确诊，制定治疗方案",
            "day_4": "休息日，游览广州塔",
            "day_5": "治疗或手术",
            "day_6": "术后观察，游览沙面岛",
            "day_7": "复查，准备返程"
        }
    }
    
    if destination not in sample_plans:
        return f"抱歉，目前还没有 {destination} 的示例行程。请提供更多具体需求，我会为您量身定制行程。"
    
    plan = sample_plans[destination]
    plan_text = f"\n📋 {destination} {days}天{travel_purpose}示例行程:\n\n"
    for day, activity in plan.items():
        plan_text += f"{day}: {activity}\n"
    
    plan_text += f"\n💡 提示: 这只是一个示例行程。请根据您的具体需求（如病种、治疗方案、个人偏好等）进行调整。\n"
    
    return plan_text
