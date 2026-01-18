"""
景点门票预定工具
"""
from langchain.tools import tool, ToolRuntime
from typing import Optional, cast
from datetime import datetime
from coze_coding_dev_sdk.database import get_session
from storage.database.shared.model import AttractionTicketOrder, User, TravelPlan, TouristAttraction, OrderStatus


def _generate_booking_reference(prefix: str = "TK") -> str:
    """生成预订参考号"""
    timestamp = datetime.now().strftime("%Y%m%d")
    import random
    random_str = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    return f"{prefix}{timestamp}{random_str}"


@tool
def book_attraction_ticket(
    user_id: int,
    attraction_id: int,
    visit_date: str,
    visitor_name: str,
    ticket_type: str = "adult",
    ticket_count: int = 1,
    visit_time: Optional[str] = None,
    travel_plan_id: Optional[int] = None,
    visitor_phone: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    预定景点门票
    
    Args:
        user_id: 用户ID
        attraction_id: 景点ID
        visit_date: 游览日期（格式: YYYY-MM-DD）
        visitor_name: 游客姓名
        ticket_type: 门票类型（adult/child/senior/group等）
        ticket_count: 门票数量
        visit_time: 游览时间（可选，格式: HH:MM）
        travel_plan_id: 出行方案ID（可选）
        visitor_phone: 游客电话
        runtime: 运行时上下文
    
    Returns:
        预定结果
    """
    db = get_session()
    try:
        # 检查用户是否存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return f"❌ 错误: 用户ID {user_id} 不存在"
        
        # 检查景点是否存在
        attraction = db.query(TouristAttraction).filter(TouristAttraction.id == attraction_id).first()
        if not attraction:
            return f"❌ 错误: 景点ID {attraction_id} 不存在"
        
        # 解析日期
        try:
            visit_dt = datetime.strptime(visit_date, "%Y-%m-%d")
        except ValueError:
            return "❌ 错误: 日期格式不正确，请使用 YYYY-MM-DD 格式"
        
        # 计算价格（根据门票类型）
        base_price = attraction.ticket_price if attraction.ticket_price else 50.0  # type: ignore
        
        if ticket_type == "child":
            base_price *= 0.5
        elif ticket_type == "senior":
            base_price *= 0.7
        elif ticket_type == "group":
            base_price *= 0.8
        
        unit_price = base_price
        total_price = unit_price * ticket_count
        
        # 创建门票订单
        order = AttractionTicketOrder(
            user_id=user_id,
            travel_plan_id=travel_plan_id,
            attraction_id=attraction_id,
            attraction_name=attraction.name,
            visit_date=visit_dt,
            visit_time=visit_time,
            ticket_type=ticket_type,
            ticket_count=ticket_count,
            visitor_name=visitor_name,
            visitor_phone=visitor_phone,
            unit_price=float(unit_price),
            total_price=float(total_price),
            status=OrderStatus.PENDING,
            booking_reference=_generate_booking_reference("TK")
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        return f"""✅ 景点门票预定成功！
🎫 门票订单信息:
- 订单ID: {order.id}
- 预订参考号: {order.booking_reference}
- 景点名称: {attraction.name}
- 游览日期: {visit_date}
- 游览时间: {visit_time or '全天'}
- 游客姓名: {visitor_name}
- 门票类型: {ticket_type}
- 门票数量: {ticket_count}
- 单价: ${unit_price:.2f}
- 总价: ${total_price:.2f}
- 状态: 待支付

⚠️ 注意事项:
1. 请在游览日前完成支付
2. 使用 book_attraction_ticket_with_payment 工具创建带支付的预定
3. 支持的支付方式: 微信支付、VISA、MasterCard、支付宝、PayPal、银联"""
    
    except Exception as e:
        db.rollback()
        return f"❌ 门票预定失败: {str(e)}"
    finally:
        db.close()


@tool
def book_attraction_ticket_with_payment(
    user_id: int,
    attraction_id: int,
    visit_date: str,
    visitor_name: str,
    payment_method: str = "visa",
    ticket_type: str = "adult",
    ticket_count: int = 1,
    visit_time: Optional[str] = None,
    travel_plan_id: Optional[int] = None,
    visitor_phone: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    预定景点门票并创建支付订单（一站式预定+支付）
    
    Args:
        user_id: 用户ID
        attraction_id: 景点ID
        visit_date: 游览日期（格式: YYYY-MM-DD）
        visitor_name: 游客姓名
        payment_method: 支付方式（wechat_pay/visa/mastercard/alipay/paypal/unionpay）
        ticket_type: 门票类型（adult/child/senior/group等）
        ticket_count: 门票数量
        visit_time: 游览时间（可选，格式: HH:MM）
        travel_plan_id: 出行方案ID（可选）
        visitor_phone: 游客电话
        runtime: 运行时上下文
    
    Returns:
        预定和支付订单信息
    """
    db = get_session()
    try:
        # 检查用户是否存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return f"❌ 错误: 用户ID {user_id} 不存在"
        
        # 检查景点是否存在
        attraction = db.query(TouristAttraction).filter(TouristAttraction.id == attraction_id).first()
        if not attraction:
            return f"❌ 错误: 景点ID {attraction_id} 不存在"
        
        # 解析日期
        try:
            visit_dt = datetime.strptime(visit_date, "%Y-%m-%d")
        except ValueError:
            return "❌ 错误: 日期格式不正确，请使用 YYYY-MM-DD 格式"
        
        # 计算价格（根据门票类型）
        base_price = attraction.ticket_price if attraction.ticket_price else 50.0  # type: ignore
        
        if ticket_type == "child":
            base_price *= 0.5
        elif ticket_type == "senior":
            base_price *= 0.7
        elif ticket_type == "group":
            base_price *= 0.8
        
        unit_price = base_price
        total_price = unit_price * ticket_count
        
        # 创建门票订单
        order = AttractionTicketOrder(
            user_id=user_id,
            travel_plan_id=travel_plan_id,
            attraction_id=attraction_id,
            attraction_name=attraction.name,
            visit_date=visit_dt,
            visit_time=visit_time,
            ticket_type=ticket_type,
            ticket_count=ticket_count,
            visitor_name=visitor_name,
            visitor_phone=visitor_phone,
            unit_price=float(unit_price),
            total_price=float(total_price),
            status=OrderStatus.PENDING,
            booking_reference=_generate_booking_reference("TK")
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        # 创建支付订单
        from tools.payment_tool import create_payment as create_payment_func
        
        payment_result = create_payment_func(
            user_id=user_id,
            order_type="ticket",
            order_id=order.id,
            amount=float(total_price),
            payment_method=payment_method,
            remark=f"景点门票预定 {attraction.name} - {visit_date}"
        )
        
        # 关联支付订单到门票订单
        payment_id = None
        if "支付订单ID:" in payment_result:
            try:
                payment_id_str = payment_result.split("支付订单ID: ")[1].split("\n")[0]
                payment_id = int(payment_id_str)
            except (ValueError, IndexError):
                pass
        
        if payment_id:
            order.payment_id = payment_id  # type: ignore
            db.commit()
        
        return f"""✅ 景点门票预定和支付订单创建成功！

🎫 门票信息:
- 订单ID: {order.id}
- 预订参考号: {order.booking_reference}
- 景点名称: {attraction.name}
- 景点地址: {attraction.address}
- 游览日期: {visit_date}
- 游览时间: {visit_time or '全天'}
- 游客姓名: {visitor_name}
- 门票类型: {ticket_type}
- 门票数量: {ticket_count}
- 总价: ${total_price:.2f}

💳 支付信息:
{payment_result}

💡 下一步:
请使用 process_payment 工具完成支付，支付完成后门票将自动确认，支付成功后将生成入园二维码"""
    
    except Exception as e:
        db.rollback()
        return f"❌ 门票预定失败: {str(e)}"
    finally:
        db.close()


@tool
def get_attraction_ticket_order_detail(
    order_id: int,
    runtime: ToolRuntime = None
) -> str:
    """
    获取景点门票订单详细信息
    
    Args:
        order_id: 订单ID
        runtime: 运行时上下文
    
    Returns:
        订单详细信息
    """
    db = get_session()
    try:
        from storage.database.shared.model import PaymentRecord, PaymentStatus
        
        order = db.query(AttractionTicketOrder).filter(AttractionTicketOrder.id == order_id).first()
        
        if not order:
            return f"❌ 错误: 门票订单 {order_id} 不存在"
        
        status_text = {
            OrderStatus.PENDING: "⏳ 待确认",
            OrderStatus.CONFIRMED: "✅ 已确认",
            OrderStatus.CANCELLED: "🚫 已取消",
            OrderStatus.COMPLETED: "✨ 已完成",
            OrderStatus.REFUNDED: "💰 已退款"
        }
        
        result = f"""🎫 景点门票订单详细信息:
- 订单ID: {order.id}
- 预订参考号: {order.booking_reference}
- 景点名称: {order.attraction_name}
- 游览日期: {order.visit_date.strftime('%Y-%m-%d') if cast(datetime, order.visit_date) else '未指定'}  # type: ignore
- 游览时间: {order.visit_time or '全天'}
- 游客姓名: {order.visitor_name}
- 游客电话: {order.visitor_phone or '未填写'}
- 门票类型: {order.ticket_type}
- 门票数量: {order.ticket_count}
- 单价: ${order.unit_price:.2f}
- 总价: ${order.total_price:.2f}
- 状态: {status_text.get(order.status, order.status.value)}
"""
        
        if order.qr_code:  # type: ignore
            result += f"\n📱 入园二维码: {order.qr_code}\n"
        
        if order.payment_id:  # type: ignore
            payment = db.query(PaymentRecord).filter(PaymentRecord.id == order.payment_id).first()
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
        
        return result
    
    finally:
        db.close()


@tool
def cancel_attraction_ticket_order(
    order_id: int,
    reason: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    取消景点门票订单
    
    Args:
        order_id: 订单ID
        reason: 取消原因
        runtime: 运行时上下文
    
    Returns:
        取消结果
    """
    db = get_session()
    try:
        order = db.query(AttractionTicketOrder).filter(AttractionTicketOrder.id == order_id).first()
        
        if not order:
            return f"❌ 错误: 门票订单 {order_id} 不存在"
        
        # 检查是否在取消期内（假设游览日前24小时可以免费取消）
        if order.status == OrderStatus.CONFIRMED:  # type: ignore
            if bool(order.visit_date):  # type: ignore  # type: ignore
                hours_until_visit = (order.visit_date - datetime.now()).total_seconds() / 3600
                if hours_until_visit < 24:
                    return "❌ 距离游览不足24小时，无法取消，如需取消请联系客服申请退款"
        
        order.status = OrderStatus.CANCELLED  # type: ignore
        
        db.commit()
        
        return f"""✅ 景点门票订单已取消！
🎫 取消信息:
- 订单ID: {order.id}
- 预订参考号: {order.booking_reference}
- 景点名称: {order.attraction_name}
- 取消时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 取消原因: {reason or '无'}"""
    
    except Exception as e:
        db.rollback()
        return f"❌ 取消失败: {str(e)}"
    finally:
        db.close()
