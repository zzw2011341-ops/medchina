"""
车票预定工具
"""
from langchain.tools import tool, ToolRuntime
from typing import Optional
from datetime import datetime
from storage.database.db import get_session
from storage.database.shared.model import TrainTicketOrder, User, TravelPlan, OrderStatus


def _generate_booking_reference(prefix: str = "TR") -> str:
    """生成预订参考号"""
    timestamp = datetime.now().strftime("%Y%m%d")
    import random
    random_str = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    return f"{prefix}{timestamp}{random_str}"


@tool
def search_trains(
    departure_city: str,
    arrival_city: str,
    departure_date: str,
    runtime: ToolRuntime = None
) -> str:
    """
    搜索车次信息（模拟数据）
    
    Args:
        departure_city: 出发城市
        arrival_city: 到达城市
        departure_date: 出发日期（格式: YYYY-MM-DD）
        runtime: 运行时上下文
    
    Returns:
        车次列表
    """
    # 模拟车次数据
    import random
    random.seed(int(datetime.now().timestamp()))
    
    train_types = {
        "high_speed": "高铁",
        "express": "动车",
        "regular": "普快"
    }
    
    trains = []
    train_numbers = ["G", "D", "K"]
    base_hour = 6
    
    for i in range(6):
        train_type_key = list(train_types.keys())[i % 3]
        train_type = train_types[train_type_key]
        train_prefix = train_numbers[i % 3]
        train_number = f"{train_prefix}{1000 + i * 100 + random.randint(1, 99)}"
        
        departure_hour = base_hour + i * 2
        departure_time = datetime.strptime(f"{departure_date} {departure_hour:02d}:00", "%Y-%m-%d %H:%M")
        
        # 根据车型估算行程时间
        if train_type_key == "high_speed":
            duration_hours = 2 + random.random() * 2
        elif train_type_key == "express":
            duration_hours = 3 + random.random() * 3
        else:
            duration_hours = 5 + random.random() * 5
        
        arrival_time = departure_time.replace(hour=(int(departure_time.hour + duration_hours) % 24))
        
        # 根据车型计算价格
        if train_type_key == "high_speed":
            price = 80 + random.random() * 100
        elif train_type_key == "express":
            price = 50 + random.random() * 60
        else:
            price = 30 + random.random() * 40
        
        seat_types = []
        if train_type_key == "high_speed":
            seat_types = ["二等座", "一等座", "商务座"]
        elif train_type_key == "express":
            seat_types = ["二等座", "一等座", "软卧", "硬卧"]
        else:
            seat_types = ["硬座", "硬卧", "软卧"]
        
        trains.append({
            "train_number": train_number,
            "train_type": train_type,
            "departure_city": departure_city,
            "arrival_city": arrival_city,
            "departure_time": departure_time.strftime("%Y-%m-%d %H:%M"),
            "arrival_time": arrival_time.strftime("%Y-%m-%d %H:%M"),
            "duration": f"{int(duration_hours)}小时{int((duration_hours % 1) * 60)}分钟",
            "price": f"${price:.0f}",
            "seat_types": seat_types
        })
    
    result = f"🚄 从 {departure_city} 到 {arrival_city} 的车次 ({departure_date}):\n\n"
    for idx, train in enumerate(trains, 1):
        result += f"{idx}. {train['train_type']} {train['train_number']}\n"
        result += f"   出发: {train['departure_time']} | 到达: {train['arrival_time']}\n"
        result += f"   运行时长: {train['duration']} | 价格: {train['price']}起\n"
        result += f"   座席类型: {', '.join(train['seat_types'])}\n\n"
    
    return result


@tool
def book_train_ticket(
    user_id: int,
    train_number: str,
    train_type: str,
    departure_city: str,
    arrival_city: str,
    departure_time: str,
    arrival_time: str,
    passenger_name: str,
    seat_type: str = "second",
    travel_plan_id: Optional[int] = None,
    passenger_id_number: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    预定车票
    
    Args:
        user_id: 用户ID
        train_number: 车次号
        train_type: 车型（high_speed/express/regular）
        departure_city: 出发城市
        arrival_city: 到达城市
        departure_time: 出发时间（格式: YYYY-MM-DD HH:MM）
        arrival_time: 到达时间（格式: YYYY-MM-DD HH:MM）
        passenger_name: 乘客姓名
        seat_type: 座席类型（first/second/soft_sleeper/hard_sleeper等）
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
        
        # 根据车型和座席类型计算价格（模拟）
        base_price = 30.0
        if train_type == "high_speed":
            base_price = 80.0
        elif train_type == "express":
            base_price = 50.0
        
        if seat_type == "first":
            base_price *= 1.6
        elif seat_type == "soft_sleeper":
            base_price *= 2.0
        elif seat_type == "hard_sleeper":
            base_price *= 1.3
        
        import random
        price = base_price + random.random() * 30
        
        # 创建车票订单
        order = TrainTicketOrder(
            user_id=user_id,
            travel_plan_id=travel_plan_id,
            train_number=train_number,
            train_type=train_type,
            departure_city=departure_city,
            arrival_city=arrival_city,
            departure_time=departure_dt,
            arrival_time=arrival_dt,
            passenger_name=passenger_name,
            passenger_id_number=passenger_id_number,
            seat_type=seat_type,
            price=float(price),
            status=OrderStatus.PENDING,
            booking_reference=_generate_booking_reference("TR")
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        return f"""✅ 车票预定成功！
🎫 车票订单信息:
- 订单ID: {order.id}
- 预订参考号: {order.booking_reference}
- 车次号: {train_number}
- 车型: {train_type}
- 出发: {departure_city} ({departure_time})
- 到达: {arrival_city} ({arrival_time})
- 乘客姓名: {passenger_name}
- 座席类型: {seat_type}
- 价格: ${price:.2f}
- 状态: 待支付

⚠️ 注意事项:
1. 请在30分钟内完成支付
2. 使用 book_train_ticket_with_payment 工具创建带支付的预定
3. 支持的支付方式: 微信支付、VISA、MasterCard、支付宝、PayPal、银联"""
    
    except Exception as e:
        db.rollback()
        return f"❌ 车票预定失败: {str(e)}"
    finally:
        db.close()


@tool
def book_train_ticket_with_payment(
    user_id: int,
    train_number: str,
    train_type: str,
    departure_city: str,
    arrival_city: str,
    departure_time: str,
    arrival_time: str,
    passenger_name: str,
    payment_method: str = "visa",
    seat_type: str = "second",
    travel_plan_id: Optional[int] = None,
    passenger_id_number: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    预定车票并创建支付订单（一站式预定+支付）
    
    Args:
        user_id: 用户ID
        train_number: 车次号
        train_type: 车型（high_speed/express/regular）
        departure_city: 出发城市
        arrival_city: 到达城市
        departure_time: 出发时间（格式: YYYY-MM-DD HH:MM）
        arrival_time: 到达时间（格式: YYYY-MM-DD HH:MM）
        passenger_name: 乘客姓名
        payment_method: 支付方式（wechat_pay/visa/mastercard/alipay/paypal/unionpay）
        seat_type: 座席类型（first/second/soft_sleeper/hard_sleeper等）
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
        
        # 根据车型和座席类型计算价格（模拟）
        base_price = 30.0
        if train_type == "high_speed":
            base_price = 80.0
        elif train_type == "express":
            base_price = 50.0
        
        if seat_type == "first":
            base_price *= 1.6
        elif seat_type == "soft_sleeper":
            base_price *= 2.0
        elif seat_type == "hard_sleeper":
            base_price *= 1.3
        
        import random
        price = base_price + random.random() * 30
        
        # 创建车票订单
        order = TrainTicketOrder(
            user_id=user_id,
            travel_plan_id=travel_plan_id,
            train_number=train_number,
            train_type=train_type,
            departure_city=departure_city,
            arrival_city=arrival_city,
            departure_time=departure_dt,
            arrival_time=arrival_dt,
            passenger_name=passenger_name,
            passenger_id_number=passenger_id_number,
            seat_type=seat_type,
            price=float(price),
            status=OrderStatus.PENDING,
            booking_reference=_generate_booking_reference("TR")
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        # 创建支付订单
        from tools.payment_tool import create_payment as create_payment_func
        
        payment_result = create_payment_func(
            user_id=user_id,
            order_type="train",
            order_id=order.id,
            amount=float(price),
            payment_method=payment_method,
            remark=f"车票预定 {train_number} - {passenger_name}"
        )
        
        # 关联支付订单到车票订单
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
        
        return f"""✅ 车票预定和支付订单创建成功！

🎫 车票信息:
- 订单ID: {order.id}
- 预订参考号: {order.booking_reference}
- 车次号: {train_number}
- 车型: {train_type}
- 出发: {departure_city} ({departure_time})
- 到达: {arrival_city} ({arrival_time})
- 乘客姓名: {passenger_name}
- 座席类型: {seat_type}
- 价格: ${price:.2f}

💳 支付信息:
{payment_result}

💡 下一步:
请使用 process_payment 工具完成支付，支付完成后车票将自动确认"""
    
    except Exception as e:
        db.rollback()
        return f"❌ 车票预定失败: {str(e)}"
    finally:
        db.close()


@tool
def get_train_ticket_order_detail(
    order_id: int,
    runtime: ToolRuntime = None
) -> str:
    """
    获取车票订单详细信息
    
    Args:
        order_id: 订单ID
        runtime: 运行时上下文
    
    Returns:
        订单详细信息
    """
    db = get_session()
    try:
        from storage.database.shared.model import PaymentRecord, PaymentStatus
        
        order = db.query(TrainTicketOrder).filter(TrainTicketOrder.id == order_id).first()
        
        if not order:
            return f"❌ 错误: 车票订单 {order_id} 不存在"
        
        status_text = {
            OrderStatus.PENDING: "⏳ 待确认",
            OrderStatus.CONFIRMED: "✅ 已确认",
            OrderStatus.CANCELLED: "🚫 已取消",
            OrderStatus.COMPLETED: "✨ 已完成",
            OrderStatus.REFUNDED: "💰 已退款"
        }
        
        result = f"""🎫 车票订单详细信息:
- 订单ID: {order.id}
- 预订参考号: {order.booking_reference}
- 车次号: {order.train_number}
- 车型: {order.train_type}
- 出发: {order.departure_city} ({order.departure_time.strftime('%Y-%m-%d %H:%M')})
- 到达: {order.arrival_city} ({order.arrival_time.strftime('%Y-%m-%d %H:%M')})
- 乘客姓名: {order.passenger_name}
- 座席类型: {order.seat_type}
- 价格: ${order.price:.2f}
- 状态: {status_text.get(order.status, order.status.value)}
"""
        
        if order.carriage_number:  # type: ignore
            result += f"- 车厢号: {order.carriage_number}\n"
        
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
def cancel_train_ticket_order(
    order_id: int,
    reason: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    取消车票订单
    
    Args:
        order_id: 订单ID
        reason: 取消原因
        runtime: 运行时上下文
    
    Returns:
        取消结果
    """
    db = get_session()
    try:
        order = db.query(TrainTicketOrder).filter(TrainTicketOrder.id == order_id).first()
        
        if not order:
            return f"❌ 错误: 车票订单 {order_id} 不存在"
        
        if order.status == OrderStatus.CONFIRMED:  # type: ignore
            return "❌ 已确认的订单无法取消，如需取消请先联系客服申请退款"
        
        order.status = OrderStatus.CANCELLED  # type: ignore
        
        db.commit()
        
        return f"""✅ 车票订单已取消！
🎫 取消信息:
- 订单ID: {order.id}
- 预订参考号: {order.booking_reference}
- 车次号: {order.train_number}
- 取消时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 取消原因: {reason or '无'}"""
    
    except Exception as e:
        db.rollback()
        return f"❌ 取消失败: {str(e)}"
    finally:
        db.close()
