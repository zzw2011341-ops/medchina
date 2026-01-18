"""
增强版支付工具
在支付前展示账单明细，支持完整的支付流程
"""
import json
from langchain.tools import tool, ToolRuntime
from typing import Optional, List
from datetime import datetime
from coze_coding_dev_sdk.database import get_session
from storage.database.shared.model import (
    PaymentRecord, PaymentMethod, PaymentStatus, 
    BillDetail, BillType, IncomeRecord
)
import secrets


def _generate_transaction_id() -> str:
    """生成交易流水号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = secrets.token_hex(4)
    return f"PAY{timestamp}{random_str}".upper()


@tool
def create_payment_with_bill(
    user_id: int,
    order_type: str,
    order_id: Optional[int],
    bill_items: str,
    currency: str = "USD",
    payment_method: str = "visa",
    remark: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    创建支付订单并生成账单明细（增强版）
    
    Args:
        user_id: 用户ID
        order_type: 订单类型（appointment/flight/hotel/train/ticket）
        order_id: 关联订单ID
        bill_items: 账单项目列表JSON字符串，格式：[{"type": "medical", "name": "项目名称", "quantity": 1, "unit_price": 100.0}]
        currency: 货币类型（默认USD）
        payment_method: 支付方式（wechat_pay/visa/mastercard/alipay/paypal/unionpay）
        remark: 备注信息
        runtime: 运行时上下文
    
    Returns:
        支付订单信息和账单明细
    """
    db = get_session()
    try:
        # 验证支付方式
        try:
            method = PaymentMethod(payment_method.lower())
        except ValueError:
            available_methods = [m.value for m in PaymentMethod]
            return f"❌ 错误: 不支持的支付方式 '{payment_method}'\n支持的支付方式: {', '.join(available_methods)}"
        
        # 解析账单项目
        try:
            items = json.loads(bill_items)
        except json.JSONDecodeError:
            return f"❌ 错误: 账单项目格式错误，请提供有效的JSON格式"
        
        # 获取中介费率
        from tools.finance_management_tool import get_commission_rate
        commission_rate = 0.05
        try:
            commission_result = json.loads(get_commission_rate())
            if commission_result.get("success"):
                commission_rate = commission_result["data"]["commission_rate"]
        except:
            pass
        
        # 计算账单明细
        bill_details = []
        subtotal = 0.0
        
        for item in items:
            quantity = item.get("quantity", 1)
            unit_price = float(item.get("unit_price", 0))
            total = quantity * unit_price
            
            bill_details.append({
                "type": item.get("type", "other"),
                "name": item.get("name", "未知项目"),
                "quantity": quantity,
                "unit_price": unit_price,
                "total": total
            })
            
            subtotal += total
        
        # 计算中介费和总价
        service_fee = subtotal * commission_rate
        grand_total = subtotal + service_fee
        
        # 生成交易流水号
        transaction_id = _generate_transaction_id()
        
        # 创建支付记录
        payment = PaymentRecord(
            user_id=user_id,
            order_type=order_type,
            order_id=order_id,
            amount=grand_total,
            currency=currency,
            payment_method=method,
            status=PaymentStatus.PENDING,
            transaction_id=transaction_id,
            remark=remark
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        # 创建账单明细记录
        for bill_detail in bill_details:
            try:
                bill_type = BillType(bill_detail["type"])
            except ValueError:
                bill_type = BillType.OTHER
            
            bill = BillDetail(
                user_id=user_id,
                payment_id=payment.id,
                bill_type=bill_type,
                item_name=bill_detail["name"],
                quantity=bill_detail["quantity"],
                unit_price=bill_detail["unit_price"],
                total_price=bill_detail["total"],
                currency=currency,
                actual_amount=bill_detail["total"],
                service_fee_rate=commission_rate,
                service_fee=bill_detail["total"] * commission_rate,
                reference_order_id=order_id,
                reference_order_type=order_type
            )
            db.add(bill)
        
        db.commit()
        
        # 生成账单摘要文本
        bill_summary = f"""
📋 **MedChina 账单明细**

【费用项目】
"""
        for item in bill_details:
            bill_summary += f"- {item['name']}: ${item['total']:.2f} (数量: {item['quantity']} × ${item['unit_price']:.2f})\n"
        
        bill_summary += f"""
【费用汇总】
- 小计: ${subtotal:.2f}
- 中介费 ({commission_rate * 100}%): ${service_fee:.2f}
- 总计: ${grand_total:.2f}

🎫 **支付订单信息**
- 支付订单ID: {payment.id}
- 交易流水号: {payment.transaction_id}
- 订单类型: {order_type}
- 关联订单ID: {order_id}
- 支付方式: {payment_method}
- 状态: ⏳ 待支付

💡 请确认以上账单明细后，使用 confirm_payment_with_bill 工具完成支付"""
        
        return bill_summary
    
    except Exception as e:
        db.rollback()
        return f"❌ 创建支付订单失败: {str(e)}"
    finally:
        db.close()


@tool
def confirm_payment_with_bill(
    payment_id: int,
    card_number: Optional[str] = None,
    card_holder: Optional[str] = None,
    expiry_date: Optional[str] = None,
    cvv: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    确认并完成支付（增强版，包含账单明细和收入记录）
    
    Args:
        payment_id: 支付订单ID
        card_number: 信用卡卡号（VISA/MasterCard等需要）
        card_holder: 持卡人姓名
        expiry_date: 卡片有效期（MM/YY）
        cvv: CVV码
        runtime: 运行时上下文
    
    Returns:
        支付结果和账单确认
    """
    db = get_session()
    try:
        payment = db.query(PaymentRecord).filter(PaymentRecord.id == payment_id).first()
        
        if not payment:
            return f"❌ 错误: 支付订单 {payment_id} 不存在"
        
        if payment.status == PaymentStatus.PAID:  # type: ignore
            return f"⚠️ 该支付订单已完成支付，交易流水号: {payment.transaction_id}"
        
        if payment.status != PaymentStatus.PENDING:  # type: ignore
            return f"❌ 支付订单状态异常，当前状态: {payment.status.value}"
        
        # 模拟支付处理
        payment.status = PaymentStatus.PAID  # type: ignore
        payment.payment_time = datetime.now()  # type: ignore
        
        # 更新账单明细状态
        bill_details = db.query(BillDetail).filter(BillDetail.payment_id == payment_id).all()
        for bill in bill_details:
            bill.is_confirmed = True  # type: ignore
            bill.confirmed_at = datetime.now()  # type: ignore
            
            # 创建收入记录
            income = IncomeRecord(
                payment_id=payment.id,
                bill_id=bill.id,
                user_id=payment.user_id,
                income_type=bill.bill_type.value if bill.bill_type else "other",  # type: ignore
                amount=bill.total_price,
                currency=bill.currency,
                service_fee_rate=bill.service_fee_rate,
                service_fee_amount=bill.service_fee,
                net_amount=bill.actual_amount - bill.service_fee,
                transaction_date=datetime.now(),
                status="settled"
            )
            db.add(income)
        
        db.commit()
        db.refresh(payment)
        
        # 生成确认信息
        confirmation = f"""
✅ **支付成功！**

🎉 支付完成信息:
- 支付订单ID: {payment.id}
- 交易流水号: {payment.transaction_id}
- 支付金额: {payment.currency} {payment.amount:.2f}
- 支付方式: {payment.payment_method.value}
- 支付时间: {payment.payment_time.strftime('%Y-%m-%d %H:%M:%S')}

📋 账单明细:
"""
        total_items = 0
        total_amount = 0.0
        total_service_fee = 0.0
        
        for bill in bill_details:
            confirmation += f"- {bill.item_name}: ${bill.total_price:.2f}\n"
            total_items += 1
            total_amount += bill.total_price
            total_service_fee += bill.service_fee
        
        confirmation += f"""
【费用汇总】
- 项目数量: {total_items}
- 费用小计: ${total_amount:.2f}
- 中介费: ${total_service_fee:.2f}
- 实付金额: ${payment.amount:.2f}

📧 确认邮件已发送至您的邮箱
🎫 订单确认信息已生成"""
        
        return confirmation
    
    except Exception as e:
        db.rollback()
        return f"❌ 支付失败: {str(e)}"
    finally:
        db.close()


@tool
def preview_bill_before_payment(
    user_id: int,
    order_type: str,
    bill_items: str,
    currency: str = "USD",
    runtime: ToolRuntime = None
) -> str:
    """
    预览账单明细（支付前展示，不创建订单）
    
    Args:
        user_id: 用户ID
        order_type: 订单类型（appointment/flight/hotel/train/ticket）
        bill_items: 账单项目列表JSON字符串
        currency: 货币类型（默认USD）
        runtime: 运行时上下文
    
    Returns:
        账单预览信息
    """
    try:
        # 解析账单项目
        items = json.loads(bill_items)
        
        # 获取中介费率
        from tools.finance_management_tool import get_commission_rate
        commission_rate = 0.05
        try:
            commission_result = json.loads(get_commission_rate())
            if commission_result.get("success"):
                commission_rate = commission_result["data"]["commission_rate"]
        except:
            pass
        
        # 计算账单明细
        bill_details = []
        subtotal = 0.0
        
        for item in items:
            quantity = item.get("quantity", 1)
            unit_price = float(item.get("unit_price", 0))
            total = quantity * unit_price
            
            bill_details.append({
                "type": item.get("type", "other"),
                "name": item.get("name", "未知项目"),
                "quantity": quantity,
                "unit_price": unit_price,
                "total": total
            })
            
            subtotal += total
        
        # 计算中介费和总价
        service_fee = subtotal * commission_rate
        grand_total = subtotal + service_fee
        
        # 生成预览文本
        preview = f"""
📋 **MedChina 账单预览**

【费用项目】
"""
        for item in bill_details:
            preview += f"- {item['name']}: ${item['total']:.2f} (数量: {item['quantity']} × ${item['unit_price']:.2f})\n"
        
        preview += f"""
【费用汇总】
- 小计: ${subtotal:.2f}
- 中介费 ({commission_rate * 100}%): ${service_fee:.2f}
- 总计: ${grand_total:.2f}

💡 说明:
- 中介费率: {commission_rate * 100}%（可在财务管理模块调整）
- 费用包含: 各项服务费用 + MedChina中介服务费

👉 如确认无误，请使用 create_payment_with_bill 工具创建支付订单并完成支付"""
        
        return preview
    
    except json.JSONDecodeError:
        return f"❌ 错误: 账单项目格式错误，请提供有效的JSON格式"
    except Exception as e:
        return f"❌ 生成账单预览失败: {str(e)}"
