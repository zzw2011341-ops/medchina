"""
机票预定工具
"""
from langchain.tools import tool, ToolRuntime
from typing import Optional
from datetime import datetime
from coze_coding_dev_sdk.database import get_session
from storage.database.shared.model import FlightOrder, User, TravelPlan, OrderStatus
import random


def _generate_booking_reference(prefix: str = "FL") -> str:
    """生成预订参考号"""
    timestamp = datetime.now().strftime("%Y%m%d")
    import random
    random_str = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    return f"{prefix}{timestamp}{random_str}"


@tool
def search_flights(
    departure_city: str,
    arrival_city: str,
    departure_date: str,
    runtime: ToolRuntime = None
) -> str:
    """
    搜索航班信息（模拟数据）
    
    Args:
        departure_city: 出发城市
        arrival_city: 到达城市
        departure_date: 出发日期（格式: YYYY-MM-DD）
        runtime: 运行时上下文
    
    Returns:
        航班列表
    """
    # 导入 random 模块
    import random
    
    # 模拟航班数据
    airlines = ["中国国际航空", "东方航空", "南方航空", "海南航空", "厦门航空"]
    flight_numbers = [
        f"CA{datetime.now().hour}{random.randint(100, 999)}"
        for _ in range(5)
    ]

    # 生成模拟航班
    random.seed(int(datetime.now().timestamp()))
    flights = []
    
    for i in range(min(5, len(flight_numbers))):
        airline = airlines[i % len(airlines)]
        flight_num = f"CA{1000 + i}"
        departure_time = datetime.strptime(f"{departure_date} {6 + i*2:02d}:00", "%Y-%m-%d %H:%M")
        duration_hours = 2 + random.random() * 3
        arrival_time = departure_time.replace(hour=(departure_time.hour + int(duration_hours)) % 24)
        
        price = 100 + random.random() * 800
        
        flights.append({
            "flight_number": flight_num,
            "airline": airline,
            "departure_city": departure_city,
            "arrival_city": arrival_city,
            "departure_time": departure_time.strftime("%Y-%m-%d %H:%M"),
            "arrival_time": arrival_time.strftime("%Y-%m-%d %H:%M"),
            "duration": f"{int(duration_hours)}小时{int((duration_hours % 1) * 60)}分钟",
            "price": f"${price:.2f}",
            "seat_class": "经济舱"
        })
    
    result = f"✈️ 从 {departure_city} 到 {arrival_city} 的航班 ({departure_date}):\n\n"
    for idx, flight in enumerate(flights, 1):
        result += f"{idx}. {flight['airline']} {flight['flight_number']}\n"
        result += f"   出发: {flight['departure_time']} | 到达: {flight['arrival_time']}\n"
        result += f"   飞行时长: {flight['duration']} | 价格: {flight['price']}\n\n"
    
    return result


@tool
def book_flight(
    user_id: int,
    flight_number: str,
    airline: str,
    departure_city: str,
    arrival_city: str,
    departure_time: str,
    arrival_time: str,
    passenger_name: str,
    seat_class: str = "economy",
    travel_plan_id: Optional[int] = None,
    passenger_id_number: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    预定机票
    
    Args:
        user_id: 用户ID
        flight_number: 航班号
        airline: 航空公司
        departure_city: 出发城市
        arrival_city: 到达城市
        departure_time: 出发时间（格式: YYYY-MM-DD HH:MM）
        arrival_time: 到达时间（格式: YYYY-MM-DD HH:MM）
        passenger_name: 乘客姓名
        seat_class: 舱位等级（economy/business/first）
        travel_plan_id: 出行方案ID（可选）
        passenger_id_number: 证件号码
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
        
        # 解析时间
        try:
            departure_dt = datetime.strptime(departure_time, "%Y-%m-%d %H:%M")
            arrival_dt = datetime.strptime(arrival_time, "%Y-%m-%d %H:%M")
        except ValueError:
            return "❌ 错误: 时间格式不正确，请使用 YYYY-MM-DD HH:MM 格式"
        
        # 根据舱位等级计算价格（模拟）
        base_price = 200.0
        if seat_class == "business":
            base_price *= 2.5
        elif seat_class == "first":
            base_price *= 5.0
        
        import random
        price = base_price + random.random() * 200
        
        # 创建机票订单
        order = FlightOrder(
            user_id=user_id,
            travel_plan_id=travel_plan_id,
            flight_number=flight_number,
            airline=airline,
            departure_city=departure_city,
            arrival_city=arrival_city,
            departure_time=departure_dt,
            arrival_time=arrival_dt,
            passenger_name=passenger_name,
            passenger_id_number=passenger_id_number,
            seat_class=seat_class,
            price=float(price),
            status=OrderStatus.PENDING,
            booking_reference=_generate_booking_reference("FL")
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        return f"""✅ 机票预定成功！
🎫 机票订单信息:
- 订单ID: {order.id}
- 预订参考号: {order.booking_reference}
- 航班号: {flight_number}
- 航空公司: {airline}
- 出发: {departure_city} ({departure_time})
- 到达: {arrival_city} ({arrival_time})
- 乘客姓名: {passenger_name}
- 舱位等级: {seat_class}
- 价格: ${price:.2f}
- 状态: 待支付

⚠️ 注意事项:
1. 请在24小时内完成支付
2. 使用 book_flight_with_payment 工具创建带支付的预定
3. 支持的支付方式: 微信支付、VISA、MasterCard、支付宝、PayPal、银联"""
    
    except Exception as e:
        db.rollback()
        return f"❌ 机票预定失败: {str(e)}"
    finally:
        db.close()


@tool
def book_flight_with_payment(
    user_id: int,
    flight_number: str,
    airline: str,
    departure_city: str,
    arrival_city: str,
    departure_time: str,
    arrival_time: str,
    passenger_name: str,
    payment_method: str = "visa",
    seat_class: str = "economy",
    travel_plan_id: Optional[int] = None,
    passenger_id_number: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    预定机票并创建支付订单（一站式预定+支付）
    
    Args:
        user_id: 用户ID
        flight_number: 航班号
        airline: 航空公司
        departure_city: 出发城市
        arrival_city: 到达城市
        departure_time: 出发时间（格式: YYYY-MM-DD HH:MM）
        arrival_time: 到达时间（格式: YYYY-MM-DD HH:MM）
        passenger_name: 乘客姓名
        payment_method: 支付方式（wechat_pay/visa/mastercard/alipay/paypal/unionpay）
        seat_class: 舱位等级（economy/business/first）
        travel_plan_id: 出行方案ID（可选）
        passenger_id_number: 证件号码
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
        
        # 解析时间
        try:
            departure_dt = datetime.strptime(departure_time, "%Y-%m-%d %H:%M")
            arrival_dt = datetime.strptime(arrival_time, "%Y-%m-%d %H:%M")
        except ValueError:
            return "❌ 错误: 时间格式不正确，请使用 YYYY-MM-DD HH:MM 格式"
        
        # 根据舱位等级计算价格（模拟）
        base_price = 200.0
        if seat_class == "business":
            base_price *= 2.5
        elif seat_class == "first":
            base_price *= 5.0
        
        import random
        price = base_price + random.random() * 200
        
        # 创建机票订单
        order = FlightOrder(
            user_id=user_id,
            travel_plan_id=travel_plan_id,
            flight_number=flight_number,
            airline=airline,
            departure_city=departure_city,
            arrival_city=arrival_city,
            departure_time=departure_dt,
            arrival_time=arrival_dt,
            passenger_name=passenger_name,
            passenger_id_number=passenger_id_number,
            seat_class=seat_class,
            price=float(price),
            status=OrderStatus.PENDING,
            booking_reference=_generate_booking_reference("FL")
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        # 创建支付订单
        from tools.payment_tool import create_payment as create_payment_func
        
        payment_result = create_payment_func(
            user_id=user_id,
            order_type="flight",
            order_id=order.id,
            amount=float(price),
            payment_method=payment_method,
            remark=f"机票预定 {airline} {flight_number} - {passenger_name}"
        )
        
        # 关联支付订单到机票订单
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
        
        return f"""✅ 机票预定和支付订单创建成功！

🎫 机票信息:
- 订单ID: {order.id}
- 预订参考号: {order.booking_reference}
- 航班号: {flight_number}
- 航空公司: {airline}
- 出发: {departure_city} ({departure_time})
- 到达: {arrival_city} ({arrival_time})
- 乘客姓名: {passenger_name}
- 舱位等级: {seat_class}
- 价格: ${price:.2f}

💳 支付信息:
{payment_result}

💡 下一步:
请使用 process_payment 工具完成支付，支付完成后机票将自动确认"""
    
    except Exception as e:
        db.rollback()
        return f"❌ 机票预定失败: {str(e)}"
    finally:
        db.close()


@tool
def get_flight_order_detail(
    order_id: int,
    runtime: ToolRuntime = None
) -> str:
    """
    获取机票订单详细信息
    
    Args:
        order_id: 订单ID
        runtime: 运行时上下文
    
    Returns:
        订单详细信息
    """
    db = get_session()
    try:
        from storage.database.shared.model import PaymentRecord, PaymentStatus
        
        order = db.query(FlightOrder).filter(FlightOrder.id == order_id).first()
        
        if not order:
            return f"❌ 错误: 机票订单 {order_id} 不存在"
        
        status_text = {
            OrderStatus.PENDING: "⏳ 待确认",
            OrderStatus.CONFIRMED: "✅ 已确认",
            OrderStatus.CANCELLED: "🚫 已取消",
            OrderStatus.COMPLETED: "✨ 已完成",
            OrderStatus.REFUNDED: "💰 已退款"
        }
        
        result = f"""🎫 机票订单详细信息:
- 订单ID: {order.id}
- 预订参考号: {order.booking_reference}
- 航班号: {order.flight_number}
- 航空公司: {order.airline}
- 出发: {order.departure_city} ({order.departure_time.strftime('%Y-%m-%d %H:%M')})
- 到达: {order.arrival_city} ({order.arrival_time.strftime('%Y-%m-%d %H:%M')})
- 乘客姓名: {order.passenger_name}
- 舱位等级: {order.seat_class}
- 价格: ${order.price:.2f}
- 状态: {status_text.get(order.status, order.status.value)}
"""
        
        if order.seat_number:  # type: ignore
            result += f"- 座位号: {order.seat_number}\n"
        
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
def cancel_flight_order(
    order_id: int,
    reason: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    取消机票订单
    
    Args:
        order_id: 订单ID
        reason: 取消原因
        runtime: 运行时上下文
    
    Returns:
        取消结果
    """
    db = get_session()
    try:
        order = db.query(FlightOrder).filter(FlightOrder.id == order_id).first()
        
        if not order:
            return f"❌ 错误: 机票订单 {order_id} 不存在"
        
        if order.status == OrderStatus.CONFIRMED:  # type: ignore
            return "❌ 已确认的订单无法取消，如需取消请先联系客服申请退款"  # type: ignore
        
        order.status = OrderStatus.CANCELLED  # type: ignore
        
        db.commit()
        
        return f"""✅ 机票订单已取消！
🎫 取消信息:
- 订单ID: {order.id}
- 预订参考号: {order.booking_reference}
- 取消时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 取消原因: {reason or '无'}"""
    
    except Exception as e:
        db.rollback()
        return f"❌ 取消失败: {str(e)}"
    finally:
        db.close()
