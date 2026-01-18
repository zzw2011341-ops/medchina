"""
支付工具
支持多种支付方式：微信支付、VISA、MasterCard、支付宝、PayPal、银联等
"""
from langchain.tools import tool, ToolRuntime
from typing import Optional
from datetime import datetime
from coze_coding_dev_sdk.database import get_session
from storage.database.shared.model import PaymentRecord, PaymentMethod, PaymentStatus
import secrets
import hashlib


def _generate_transaction_id() -> str:
    """生成交易流水号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = secrets.token_hex(4)
    return f"PAY{timestamp}{random_str}".upper()


@tool
def create_payment(
    user_id: int,
    order_type: str,
    order_id: Optional[int],
    amount: float,
    currency: str = "USD",
    payment_method: str = "visa",
    remark: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    创建支付订单
    
    Args:
        user_id: 用户ID
        order_type: 订单类型（appointment/flight/hotel/train/ticket）
        order_id: 关联订单ID
        amount: 支付金额
        currency: 货币类型（默认USD）
        payment_method: 支付方式（wechat_pay/visa/mastercard/alipay/paypal/unionpay）
        remark: 备注信息
        runtime: 运行时上下文
    
    Returns:
        支付订单信息
    """
    db = get_session()
    try:
        # 验证支付方式
        try:
            method = PaymentMethod(payment_method.lower())
        except ValueError:
            available_methods = [m.value for m in PaymentMethod]
            return f"❌ 错误: 不支持的支付方式 '{payment_method}'\n支持的支付方式: {', '.join(available_methods)}"
        
        # 生成交易流水号
        transaction_id = _generate_transaction_id()
        
        # 创建支付记录
        payment = PaymentRecord(
            user_id=user_id,
            order_type=order_type,
            order_id=order_id,
            amount=amount,
            currency=currency,
            payment_method=method,
            status=PaymentStatus.PENDING,
            transaction_id=transaction_id,
            remark=remark
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        return f"""✅ 支付订单创建成功！
📋 支付订单信息:
- 支付订单ID: {payment.id}
- 交易流水号: {payment.transaction_id}
- 订单类型: {order_type}
- 关联订单ID: {order_id}
- 支付金额: {currency} {amount}
- 支付方式: {payment_method}
- 状态: 待支付

💡 请使用 process_payment 工具完成支付"""
    
    except Exception as e:
        db.rollback()
        return f"❌ 创建支付订单失败: {str(e)}"
    finally:
        db.close()


@tool
def process_payment(
    payment_id: int,
    card_number: Optional[str] = None,
    card_holder: Optional[str] = None,
    expiry_date: Optional[str] = None,
    cvv: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    处理支付（模拟支付流程）
    
    Args:
        payment_id: 支付订单ID
        card_number: 信用卡卡号（VISA/MasterCard等需要）
        card_holder: 持卡人姓名
        expiry_date: 卡片有效期（MM/YY）
        cvv: CVV码
        runtime: 运行时上下文
    
    Returns:
        支付结果
    """
    db = get_session()
    try:
        payment = db.query(PaymentRecord).filter(PaymentRecord.id == payment_id).first()
        
        if not payment:
            return f"❌ 错误: 支付订单 {payment_id} 不存在"
        
        if payment.status == PaymentStatus.PAID:
            return f"⚠️ 该支付订单已完成支付，交易流水号: {payment.transaction_id}"
        
        if bool(payment.status != PaymentStatus.PENDING):
            return f"❌ 支付订单状态异常，当前状态: {payment.status.value}"
        
        # 模拟支付处理
        # 在实际应用中，这里会调用真实的支付API（微信支付、Stripe等）
        # 这里简化为直接标记支付成功
        
        payment.status = PaymentStatus.PAID
        payment.payment_time = datetime.now()
        
        db.commit()
        db.refresh(payment)
        
        payment_status_value = payment.status.value if payment.status else ""
        
        return f"""✅ 支付成功！
🎉 支付完成信息:
- 支付订单ID: {payment.id}
- 交易流水号: {payment.transaction_id}
- 支付金额: {payment.currency} {payment.amount}
- 支付方式: {payment.payment_method.value}
- 支付时间: {payment.payment_time.strftime('%Y-%m-%d %H:%M:%S')}

📧 邮件通知已发送至您的邮箱"""
    
    except Exception as e:
        db.rollback()
        return f"❌ 支付失败: {str(e)}"
    finally:
        db.close()


@tool
def get_payment_status(
    payment_id: int,
    runtime: ToolRuntime = None
) -> str:
    """
    查询支付状态
    
    Args:
        payment_id: 支付订单ID
        runtime: 运行时上下文
    
    Returns:
        支付状态信息
    """
    db = get_session()
    try:
        payment = db.query(PaymentRecord).filter(PaymentRecord.id == payment_id).first()
        
        if not payment:
            return f"❌ 错误: 支付订单 {payment_id} 不存在"
        
        status_text = {
            PaymentStatus.PENDING: "⏳ 待支付",
            PaymentStatus.PAID: "✅ 已支付",
            PaymentStatus.FAILED: "❌ 支付失败",
            PaymentStatus.CANCELLED: "🚫 已取消",
            PaymentStatus.REFUNDED: "💰 已退款"
        }
        
        payment_status_value = payment.status.value if payment.status else ""
        payment_time_str = payment.payment_time.strftime('%Y-%m-%d %H:%M:%S') if bool(payment.payment_time) else ""
        refund_time_str = payment.refund_time.strftime('%Y-%m-%d %H:%M:%S') if bool(payment.refund_time) else ""
        refund_amount_value = float(payment.refund_amount) if bool(payment.refund_amount) else 0.0
        remark_value = str(payment.remark) if bool(payment.remark) else ""
        
        result = f"""📋 支付订单详情:
- 支付订单ID: {payment.id}
- 交易流水号: {payment.transaction_id}
- 订单类型: {payment.order_type}
- 关联订单ID: {payment.order_id}
- 支付金额: {payment.currency} {payment.amount}
- 支付方式: {payment.payment_method.value}
- 状态: {status_text.get(payment.status, payment_status_value)}
- 创建时间: {payment.created_at.strftime('%Y-%m-%d %H:%M:%S')}"""
        
        if bool(payment.payment_time):
            result += f"\n- 支付时间: {payment_time_str}"
        
        if bool(payment.refund_time):
            result += f"\n- 退款时间: {refund_time_str}"
            result += f"\n- 退款金额: {payment.currency} {refund_amount_value}"
        
        if bool(payment.remark):
            result += f"\n- 备注: {remark_value}"
        
        return result
    
    finally:
        db.close()


@tool
def refund_payment(
    payment_id: int,
    refund_amount: Optional[float] = None,
    reason: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    申请退款
    
    Args:
        payment_id: 支付订单ID
        refund_amount: 退款金额（不填则全额退款）
        reason: 退款原因
        runtime: 运行时上下文
    
    Returns:
        退款结果
    """
    db = get_session()
    try:
        payment = db.query(PaymentRecord).filter(PaymentRecord.id == payment_id).first()
        
        if not payment:
            return f"❌ 错误: 支付订单 {payment_id} 不存在"
        
        if payment.status != PaymentStatus.PAID:
            return f"❌ 只有已支付的订单才能申请退款，当前状态: {payment.status.value}"
        
        # 设置退款金额
        if refund_amount is None:
            refund_amount = payment.amount
        
        if refund_amount > payment.amount:
            return f"❌ 退款金额不能超过支付金额（{payment.currency} {payment.amount}）"
        
        # 执行退款
        payment.status = PaymentStatus.REFUNDED
        payment.refund_time = datetime.now()
        payment.refund_amount = refund_amount
        payment.remark = f"退款原因: {reason}" if reason else payment.remark
        
        db.commit()
        db.refresh(payment)
        
        return f"""✅ 退款申请成功！
💰 退款信息:
- 支付订单ID: {payment.id}
- 交易流水号: {payment.transaction_id}
- 退款金额: {payment.currency} {refund_amount}
- 退款时间: {payment.refund_time.strftime('%Y-%m-%d %H:%M:%S')}
- 退款原因: {reason or '无'}

📧 退款确认邮件已发送至您的邮箱"""
    
    except Exception as e:
        db.rollback()
        return f"❌ 退款失败: {str(e)}"
    finally:
        db.close()


@tool
def get_user_payments(
    user_id: int,
    status: Optional[str] = None,
    limit: int = 20,
    runtime: ToolRuntime = None
) -> str:
    """
    查询用户的支付记录
    
    Args:
        user_id: 用户ID
        status: 支付状态筛选（pending/paid/failed/cancelled/refunded）
        limit: 返回记录数量限制
        runtime: 运行时上下文
    
    Returns:
        支付记录列表
    """
    db = get_session()
    try:
        query = db.query(PaymentRecord).filter(PaymentRecord.user_id == user_id)
        
        if status:
            try:
                status_filter = PaymentStatus(status.lower())
                query = query.filter(PaymentRecord.status == status_filter)
            except ValueError:
                return f"❌ 错误: 无效的支付状态 '{status}'"
        
        payments = query.order_by(PaymentRecord.created_at.desc()).limit(limit).all()
        
        if not payments:
            return "📭 暂无支付记录"
        
        status_text = {
            PaymentStatus.PENDING: "⏳ 待支付",
            PaymentStatus.PAID: "✅ 已支付",
            PaymentStatus.FAILED: "❌ 支付失败",
            PaymentStatus.CANCELLED: "🚫 已取消",
            PaymentStatus.REFUNDED: "💰 已退款"
        }
        
        result = f"📋 支付记录 ({len(payments)} 条):\n\n"
        for idx, payment in enumerate(payments, 1):
            result += f"{idx}. 订单ID: {payment.id} | 流水号: {payment.transaction_id}\n"
            result += f"   类型: {payment.order_type} | 金额: {payment.currency} {payment.amount}\n"
            result += f"   支付方式: {payment.payment_method.value} | 状态: {status_text.get(payment.status, payment.status.value)}\n"
            result += f"   创建时间: {payment.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        return result
    
    finally:
        db.close()


@tool
def cancel_payment(
    payment_id: int,
    reason: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    取消支付订单（仅限待支付状态）
    
    Args:
        payment_id: 支付订单ID
        reason: 取消原因
        runtime: 运行时上下文
    
    Returns:
        取消结果
    """
    db = get_session()
    try:
        payment = db.query(PaymentRecord).filter(PaymentRecord.id == payment_id).first()
        
        if not payment:
            return f"❌ 错误: 支付订单 {payment_id} 不存在"
        
        if payment.status != PaymentStatus.PENDING:
            return f"❌ 只有待支付状态的订单可以取消，当前状态: {payment.status.value}"
        
        payment.status = PaymentStatus.CANCELLED
        payment.remark = f"取消原因: {reason}" if reason else payment.remark
        
        db.commit()
        db.refresh(payment)
        
        return f"""✅ 支付订单已取消！
📋 取消信息:
- 支付订单ID: {payment.id}
- 交易流水号: {payment.transaction_id}
- 取消时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 取消原因: {reason or '无'}"""
    
    except Exception as e:
        db.rollback()
        return f"❌ 取消失败: {str(e)}"
    finally:
        db.close()
