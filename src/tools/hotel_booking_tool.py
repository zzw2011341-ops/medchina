"""
酒店预定工具
"""
from langchain.tools import tool, ToolRuntime
from typing import Optional
from datetime import datetime, timedelta
from coze_coding_dev_sdk.database import get_session
from storage.database.shared.model import HotelOrder, User, TravelPlan, OrderStatus


def _generate_booking_reference(prefix: str = "HT") -> str:
    """生成预订参考号"""
    timestamp = datetime.now().strftime("%Y%m%d")
    import random
    random_str = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    return f"{prefix}{timestamp}{random_str}"


@tool
def search_hotels(
    city: str,
    check_in_date: str,
    check_out_date: str,
    room_type: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    搜索酒店信息（模拟数据）
    
    Args:
        city: 城市
        check_in_date: 入住日期（格式: YYYY-MM-DD）
        check_out_date: 退房日期（格式: YYYY-MM-DD）
        room_type: 房型（可选）
        runtime: 运行时上下文
    
    Returns:
        酒店列表
    """
    # 模拟酒店数据
    import random
    random.seed(int(datetime.now().timestamp()))
    
    hotels = [
        {
            "name": "希尔顿酒店",
            "address": f"{city}市中心",
            "rating": 4.8,
            "room_types": ["标准间", "大床房", "豪华套房"],
            "amenities": ["免费WiFi", "早餐", "健身房", "游泳池"],
            "price_per_night": 150.0
        },
        {
            "name": "万豪酒店",
            "address": f"{city}商业区",
            "rating": 4.7,
            "room_types": ["标准间", "大床房", "行政套房", "总统套房"],
            "amenities": ["免费WiFi", "早餐", "健身房", "商务中心", "SPA"],
            "price_per_night": 200.0
        },
        {
            "name": "如家酒店",
            "address": f"{city}火车站附近",
            "rating": 4.2,
            "room_types": ["标准间", "大床房"],
            "amenities": ["免费WiFi", "早餐"],
            "price_per_night": 80.0
        },
        {
            "name": "君悦酒店",
            "address": f"{city}金融区",
            "rating": 4.9,
            "room_types": ["大床房", "豪华套房", "总统套房"],
            "amenities": ["免费WiFi", "早餐", "健身房", "游泳池", "SPA", "行政酒廊"],
            "price_per_night": 350.0
        },
        {
            "name": "洲际酒店",
            "address": f"{city}国际会展中心附近",
            "rating": 4.6,
            "room_types": ["标准间", "大床房", "行政套房"],
            "amenities": ["免费WiFi", "早餐", "健身房", "商务中心"],
            "price_per_night": 180.0
        }
    ]
    
    # 计算住宿天数
    try:
        check_in = datetime.strptime(check_in_date, "%Y-%m-%d")
        check_out = datetime.strptime(check_out_date, "%Y-%m-%d")
        nights = (check_out - check_in).days
        if nights <= 0:
            return "❌ 错误: 退房日期必须晚于入住日期"
    except ValueError:
        return "❌ 错误: 日期格式不正确，请使用 YYYY-MM-DD 格式"
    
    result = f"🏨 {city} 的酒店 ({check_in_date} - {check_out_date}, 住 {nights} 晚):\n\n"
    
    for idx, hotel in enumerate(hotels, 1):
        result += f"{idx}. {hotel['name']} ⭐{hotel['rating']}\n"
        result += f"   地址: {hotel['address']}\n"
        result += f"   房型: {', '.join(hotel['room_types'])}\n"
        result += f"   设施: {', '.join(hotel['amenities'])}\n"
        result += f"   价格: ${hotel['price_per_night']:.0f}/晚 (总计: ${hotel['price_per_night'] * nights:.0f})\n\n"
    
    return result


@tool
def book_hotel(
    user_id: int,
    hotel_name: str,
    hotel_address: str,
    city: str,
    check_in_date: str,
    check_out_date: str,
    guest_name: str,
    room_type: str = "standard",
    number_of_rooms: int = 1,
    number_of_guests: int = 1,
    travel_plan_id: Optional[int] = None,
    breakfast_included: bool = False,
    runtime: ToolRuntime = None
) -> str:
    """
    预定酒店
    
    Args:
        user_id: 用户ID
        hotel_name: 酒店名称
        hotel_address: 酒店地址
        city: 城市
        check_in_date: 入住日期（格式: YYYY-MM-DD）
        check_out_date: 退房日期（格式: YYYY-MM-DD）
        guest_name: 入住人姓名
        room_type: 房型（standard/double/suite等）
        number_of_rooms: 房间数量
        number_of_guests: 入住人数
        travel_plan_id: 出行方案ID（可选）
        breakfast_included: 是否含早餐
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
        
        # 解析日期
        try:
            check_in = datetime.strptime(check_in_date, "%Y-%m-%d")
            check_out = datetime.strptime(check_out_date, "%Y-%m-%d")
        except ValueError:
            return "❌ 错误: 日期格式不正确，请使用 YYYY-MM-DD 格式"
        
        if check_out <= check_in:
            return "❌ 错误: 退房日期必须晚于入住日期"
        
        # 计算住宿天数和价格
        nights = (check_out - check_in).days
        
        # 根据房型计算价格（模拟）
        base_price_per_night = 100.0
        if room_type == "double":
            base_price_per_night = 150.0
        elif room_type == "suite":
            base_price_per_night = 300.0
        
        import random
        price_per_night = base_price_per_night + random.random() * 50
        total_price = price_per_night * nights * number_of_rooms
        
        if breakfast_included:
            total_price += 30 * nights * number_of_guests  # 早餐费
        
        # 创建酒店订单
        order = HotelOrder(
            user_id=user_id,
            travel_plan_id=travel_plan_id,
            hotel_name=hotel_name,
            hotel_address=hotel_address,
            city=city,
            room_type=room_type,
            check_in_date=check_in,
            check_out_date=check_out,
            guest_name=guest_name,
            number_of_rooms=number_of_rooms,
            number_of_guests=number_of_guests,
            price_per_night=float(price_per_night),
            total_price=float(total_price),
            breakfast_included=breakfast_included,
            status=OrderStatus.PENDING,
            booking_reference=_generate_booking_reference("HT")
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        return f"""✅ 酒店预定成功！
🏨 酒店订单信息:
- 订单ID: {order.id}
- 预订参考号: {order.booking_reference}
- 酒店名称: {hotel_name}
- 酒店地址: {hotel_address}
- 城市: {city}
- 入住日期: {check_in_date}
- 退房日期: {check_out_date}
- 住宿天数: {nights} 晚
- 入住人: {guest_name}
- 房型: {room_type}
- 房间数量: {number_of_rooms}
- 入住人数: {number_of_guests}
- 每晚价格: ${price_per_night:.2f}
- 总价格: ${total_price:.2f}
- 含早餐: {'是' if breakfast_included else '否'}
- 状态: 待支付

⚠️ 注意事项:
1. 请在24小时内完成支付
2. 使用 book_hotel_with_payment 工具创建带支付的预定
3. 支持的支付方式: 微信支付、VISA、MasterCard、支付宝、PayPal、银联"""
    
    except Exception as e:
        db.rollback()
        return f"❌ 酒店预定失败: {str(e)}"
    finally:
        db.close()


@tool
def book_hotel_with_payment(
    user_id: int,
    hotel_name: str,
    hotel_address: str,
    city: str,
    check_in_date: str,
    check_out_date: str,
    guest_name: str,
    payment_method: str = "visa",
    room_type: str = "standard",
    number_of_rooms: int = 1,
    number_of_guests: int = 1,
    travel_plan_id: Optional[int] = None,
    breakfast_included: bool = False,
    runtime: ToolRuntime = None
) -> str:
    """
    预定酒店并创建支付订单（一站式预定+支付）
    
    Args:
        user_id: 用户ID
        hotel_name: 酒店名称
        hotel_address: 酒店地址
        city: 城市
        check_in_date: 入住日期（格式: YYYY-MM-DD）
        check_out_date: 退房日期（格式: YYYY-MM-DD）
        guest_name: 入住人姓名
        payment_method: 支付方式（wechat_pay/visa/mastercard/alipay/paypal/unionpay）
        room_type: 房型（standard/double/suite等）
        number_of_rooms: 房间数量
        number_of_guests: 入住人数
        travel_plan_id: 出行方案ID（可选）
        breakfast_included: 是否含早餐
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
        
        # 解析日期
        try:
            check_in = datetime.strptime(check_in_date, "%Y-%m-%d")
            check_out = datetime.strptime(check_out_date, "%Y-%m-%d")
        except ValueError:
            return "❌ 错误: 日期格式不正确，请使用 YYYY-MM-DD 格式"
        
        if check_out <= check_in:
            return "❌ 错误: 退房日期必须晚于入住日期"
        
        # 计算住宿天数和价格
        nights = (check_out - check_in).days
        
        # 根据房型计算价格（模拟）
        base_price_per_night = 100.0
        if room_type == "double":
            base_price_per_night = 150.0
        elif room_type == "suite":
            base_price_per_night = 300.0
        
        import random
        price_per_night = base_price_per_night + random.random() * 50
        total_price = price_per_night * nights * number_of_rooms
        
        if breakfast_included:
            total_price += 30 * nights * number_of_guests  # 早餐费
        
        # 创建酒店订单
        order = HotelOrder(
            user_id=user_id,
            travel_plan_id=travel_plan_id,
            hotel_name=hotel_name,
            hotel_address=hotel_address,
            city=city,
            room_type=room_type,
            check_in_date=check_in,
            check_out_date=check_out,
            guest_name=guest_name,
            number_of_rooms=number_of_rooms,
            number_of_guests=number_of_guests,
            price_per_night=float(price_per_night),
            total_price=float(total_price),
            breakfast_included=breakfast_included,
            status=OrderStatus.PENDING,
            booking_reference=_generate_booking_reference("HT")
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        # 创建支付订单
        from tools.payment_tool import create_payment as create_payment_func
        
        payment_result = create_payment_func(
            user_id=user_id,
            order_type="hotel",
            order_id=order.id,
            amount=float(total_price),
            payment_method=payment_method,
            remark=f"酒店预定 {hotel_name} - {check_in_date} 至 {check_out_date}"
        )
        
        # 关联支付订单到酒店订单
        payment_id = None
        if "支付订单ID:" in payment_result:
            try:
                payment_id_str = payment_result.split("支付订单ID: ")[1].split("\n")[0]
                payment_id = int(payment_id_str)
            except (ValueError, IndexError):
                pass
        
        if payment_id:
            order.payment_id = payment_id
            db.commit()
        
        return f"""✅ 酒店预定和支付订单创建成功！

🏨 酒店信息:
- 订单ID: {order.id}
- 预订参考号: {order.booking_reference}
- 酒店名称: {hotel_name}
- 酒店地址: {hotel_address}
- 城市: {city}
- 入住日期: {check_in_date}
- 退房日期: {check_out_date}
- 住宿天数: {nights} 晚
- 入住人: {guest_name}
- 房型: {room_type}
- 房间数量: {number_of_rooms}
- 总价格: ${total_price:.2f}

💳 支付信息:
{payment_result}

💡 下一步:
请使用 process_payment 工具完成支付，支付完成后酒店预定将自动确认"""
    
    except Exception as e:
        db.rollback()
        return f"❌ 酒店预定失败: {str(e)}"
    finally:
        db.close()


@tool
def get_hotel_order_detail(
    order_id: int,
    runtime: ToolRuntime = None
) -> str:
    """
    获取酒店订单详细信息
    
    Args:
        order_id: 订单ID
        runtime: 运行时上下文
    
    Returns:
        订单详细信息
    """
    db = get_session()
    try:
        from storage.database.shared.model import PaymentRecord, PaymentStatus
        
        order = db.query(HotelOrder).filter(HotelOrder.id == order_id).first()
        
        if not order:
            return f"❌ 错误: 酒店订单 {order_id} 不存在"
        
        status_text = {
            OrderStatus.PENDING: "⏳ 待确认",
            OrderStatus.CONFIRMED: "✅ 已确认",
            OrderStatus.CANCELLED: "🚫 已取消",
            OrderStatus.COMPLETED: "✨ 已完成",
            OrderStatus.REFUNDED: "💰 已退款"
        }
        
        nights = (order.check_out_date - order.check_in_date).days if order.check_out_date and order.check_in_date else 0
        
        result = f"""🏨 酒店订单详细信息:
- 订单ID: {order.id}
- 预订参考号: {order.booking_reference}
- 酒店名称: {order.hotel_name}
- 酒店地址: {order.hotel_address}
- 城市: {order.city}
- 入住日期: {order.check_in_date.strftime('%Y-%m-%d') if order.check_in_date else '未指定'}
- 退房日期: {order.check_out_date.strftime('%Y-%m-%d') if order.check_out_date else '未指定'}
- 住宿天数: {nights} 晚
- 入住人: {order.guest_name}
- 房型: {order.room_type}
- 房间数量: {order.number_of_rooms}
- 入住人数: {order.number_of_guests}
- 每晚价格: ${order.price_per_night:.2f}
- 总价格: ${order.total_price:.2f}
- 含早餐: {'是' if order.breakfast_included else '否'}
- 状态: {status_text.get(order.status, order.status.value)}
"""
        
        if order.payment_id:
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
def cancel_hotel_order(
    order_id: int,
    reason: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    取消酒店订单
    
    Args:
        order_id: 订单ID
        reason: 取消原因
        runtime: 运行时上下文
    
    Returns:
        取消结果
    """
    db = get_session()
    try:
        order = db.query(HotelOrder).filter(HotelOrder.id == order_id).first()
        
        if not order:
            return f"❌ 错误: 酒店订单 {order_id} 不存在"
        
        if order.status == OrderStatus.CONFIRMED:
            # 检查是否在免费取消期内（假设入住前24小时可以免费取消）
            if order.check_in_date:
                hours_until_checkin = (order.check_in_date - datetime.now()).total_seconds() / 3600
                if hours_until_checkin < 24:
                    return "❌ 距离入住不足24小时，无法取消，如需取消请联系客服申请退款"
        
        order.status = OrderStatus.CANCELLED
        
        db.commit()
        
        return f"""✅ 酒店订单已取消！
🏨 取消信息:
- 订单ID: {order.id}
- 预订参考号: {order.booking_reference}
- 酒店名称: {order.hotel_name}
- 取消时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 取消原因: {reason or '无'}"""
    
    except Exception as e:
        db.rollback()
        return f"❌ 取消失败: {str(e)}"
    finally:
        db.close()
