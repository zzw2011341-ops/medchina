"""
财务管理工具
提供财务统计、中介费管理、账单明细生成等功能
"""
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from langchain.tools import tool, ToolRuntime
from coze_coding_dev_sdk.database import get_session
from sqlalchemy import func, and_

@tool
def get_finance_statistics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    获取财务统计数据（后台管理用）
    
    Args:
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）
        runtime: 工具运行时上下文
    
    Returns:
        财务统计数据（JSON格式）
    """
    from storage.database.shared.model import (
        PaymentRecord, IncomeRecord, ExpenseRecord, 
        PaymentStatus, BillDetail
    )
    
    try:
        db = get_session()
        
        # 处理日期范围
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        
        # 统计总收入
        total_income = db.query(func.sum(IncomeRecord.amount)).filter(
            IncomeRecord.transaction_date >= start_dt,
            IncomeRecord.transaction_date < end_dt,
            IncomeRecord.status == "settled"
        ).scalar() or 0
        
        # 统计总中介费
        total_service_fee = db.query(func.sum(IncomeRecord.service_fee_amount)).filter(
            IncomeRecord.transaction_date >= start_dt,
            IncomeRecord.transaction_date < end_dt,
            IncomeRecord.status == "settled"
        ).scalar() or 0
        
        # 统计净收入
        total_net_income = db.query(func.sum(IncomeRecord.net_amount)).filter(
            IncomeRecord.transaction_date >= start_dt,
            IncomeRecord.transaction_date < end_dt,
            IncomeRecord.status == "settled"
        ).scalar() or 0
        
        # 统计总支出
        total_expense = db.query(func.sum(ExpenseRecord.amount)).filter(
            ExpenseRecord.expense_date >= start_dt,
            ExpenseRecord.expense_date < end_dt,
            ExpenseRecord.status == "approved"
        ).scalar() or 0
        
        # 统计总订单数
        total_orders = db.query(func.count(PaymentRecord.id)).filter(
            PaymentRecord.created_at >= start_dt,
            PaymentRecord.created_at < end_dt,
            PaymentRecord.status == PaymentStatus.PAID
        ).scalar() or 0
        
        # 按类型统计收入
        income_by_type = db.query(
            IncomeRecord.income_type,
            func.sum(IncomeRecord.amount).label("total"),
            func.count(IncomeRecord.id).label("count")
        ).filter(
            IncomeRecord.transaction_date >= start_dt,
            IncomeRecord.transaction_date < end_dt
        ).group_by(IncomeRecord.income_type).all()
        
        income_by_type_dict = []
        for item in income_by_type:
            income_by_type_dict.append({
                "type": item[0],
                "total": float(item[1]) if item[1] else 0,
                "count": item[2]
            })
        
        return str({
            "success": True,
            "data": {
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "summary": {
                    "total_income": float(total_income),
                    "total_service_fee": float(total_service_fee),
                    "total_net_income": float(total_net_income),
                    "total_expense": float(total_expense),
                    "total_orders": total_orders,
                    "profit": float(total_net_income - total_expense)
                },
                "income_by_type": income_by_type_dict
            }
        })
    except Exception as e:
        return str({
            "success": False,
            "message": f"获取财务统计数据失败: {str(e)}"
        })

@tool
def get_commission_rate(runtime: ToolRuntime = None) -> str:
    """
    获取当前中介费率
    
    Args:
        runtime: 工具运行时上下文
    
    Returns:
        中介费率信息（JSON格式）
    """
    from storage.database.shared.model import FinanceConfig
    
    try:
        db = get_session()
        config = db.query(FinanceConfig).filter(
            FinanceConfig.config_key == "commission_rate"
        ).first()
        
        rate = 0.05  # 默认5%
        if config and config.config_value:  # type: ignore
            try:
                rate = float(config.config_value)
            except ValueError:
                pass
        
        return str({
            "success": True,
            "data": {
                "commission_rate": rate,
                "percentage": f"{rate * 100}%"
            }
        })
    except Exception as e:
        return str({
            "success": False,
            "message": f"获取中介费率失败: {str(e)}"
        })

@tool
def update_commission_rate(rate: float, runtime: ToolRuntime = None) -> str:
    """
    更新中介费率（后台管理用）
    
    Args:
        rate: 新的中介费率（如0.05表示5%），范围0-1
        runtime: 工具运行时上下文
    
    Returns:
        更新结果（JSON格式）
    """
    from storage.database.shared.model import FinanceConfig
    
    try:
        if not (0 <= rate <= 1):
            return str({
                "success": False,
                "message": "中介费率必须在0到1之间"
            })
        
        db = get_session()
        config = db.query(FinanceConfig).filter(
            FinanceConfig.config_key == "commission_rate"
        ).first()
        
        if config:
            config.config_value = str(rate)  # type: ignore
            config.updated_at = datetime.now()  # type: ignore
        else:
            config = FinanceConfig(
                config_key="commission_rate",
                config_value=str(rate),
                config_type="float",
                description="中介费率，用于计算订单的中介费用"
            )
            db.add(config)
        
        db.commit()
        
        return str({
            "success": True,
            "message": f"中介费率已更新为 {rate * 100}%",
            "data": {
                "commission_rate": rate,
                "percentage": f"{rate * 100}%"
            }
        })
    except Exception as e:
        db.rollback()
        return str({
            "success": False,
            "message": f"更新中介费率失败: {str(e)}"
        })

@tool
def create_bill_detail(bill_data: str, runtime: ToolRuntime = None) -> str:
    """
    创建账单明细
    
    Args:
        bill_data: 账单数据JSON字符串
            必需字段：user_id, bill_type, item_name, unit_price
            可选字段：payment_id, travel_plan_id, item_description, quantity, currency, discount, reference_order_id, reference_order_type
        runtime: 工具运行时上下文
    
    Returns:
        创建结果（JSON格式）
    """
    from storage.database.shared.model import BillDetail, BillType
    
    try:
        data = json.loads(bill_data)
        
        # 必填字段验证
        required_fields = ["user_id", "bill_type", "item_name", "unit_price"]
        for field in required_fields:
            if field not in data or data[field] is None:
                return str({
                    "success": False,
                    "message": f"缺少必填字段: {field}"
                })
        
        # 验证账单类型
        try:
            bill_type = BillType(data["bill_type"])
        except ValueError:
            return str({
                "success": False,
                "message": f"无效的账单类型: {data['bill_type']}"
            })
        
        # 获取中介费率
        commission_rate = 0.05
        try:
            commission_result = json.loads(get_commission_rate())
            if commission_result.get("success"):
                commission_rate = commission_result["data"]["commission_rate"]
        except:
            pass
        
        # 计算金额
        quantity = data.get("quantity", 1)
        discount = data.get("discount", 0.0)
        unit_price = float(data["unit_price"])
        
        total_price = unit_price * quantity
        actual_amount = total_price - discount
        service_fee = actual_amount * commission_rate
        
        # 创建账单明细
        new_bill = BillDetail(
            user_id=data["user_id"],
            payment_id=data.get("payment_id"),
            travel_plan_id=data.get("travel_plan_id"),
            bill_type=bill_type,
            item_name=data["item_name"],
            item_description=data.get("item_description"),
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price,
            currency=data.get("currency", "USD"),
            discount=discount,
            actual_amount=actual_amount,
            service_fee_rate=commission_rate,
            service_fee=service_fee,
            reference_order_id=data.get("reference_order_id"),
            reference_order_type=data.get("reference_order_type"),
            notes=data.get("notes")
        )
        
        db = get_session()
        db.add(new_bill)
        db.commit()
        db.refresh(new_bill)
        
        return str({
            "success": True,
            "message": "账单明细创建成功",
            "data": {
                "id": new_bill.id,
                "item_name": new_bill.item_name,
                "total_price": new_bill.total_price,
                "actual_amount": new_bill.actual_amount,
                "service_fee": new_bill.service_fee
            }
        })
    except json.JSONDecodeError:
        return str({
            "success": False,
            "message": "账单数据格式错误，请提供有效的JSON格式"
        })
    except Exception as e:
        return str({
            "success": False,
            "message": f"创建账单明细失败: {str(e)}"
        })

@tool
def get_bill_details(
    user_id: int,
    payment_id: Optional[int] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    获取账单明细列表
    
    Args:
        user_id: 用户ID
        payment_id: 支付记录ID（可选，用于筛选特定支付的账单）
        runtime: 工具运行时上下文
    
    Returns:
        账单明细列表（JSON格式）
    """
    from storage.database.shared.model import BillDetail
    
    try:
        db = get_session()
        query = db.query(BillDetail).filter(BillDetail.user_id == user_id)
        
        if payment_id:
            query = query.filter(BillDetail.payment_id == payment_id)
        
        bill_details = query.order_by(BillDetail.created_at.desc()).all()
        
        # 序列化结果
        bill_list = []
        total_amount = 0.0
        total_service_fee = 0.0
        
        for bill in bill_details:
            bill_dict = {
                "id": bill.id,
                "bill_type": bill.bill_type.value if bill.bill_type else None,  # type: ignore
                "item_name": bill.item_name,
                "item_description": bill.item_description,
                "quantity": bill.quantity,
                "unit_price": bill.unit_price,
                "total_price": bill.total_price,
                "currency": bill.currency,
                "discount": bill.discount,
                "actual_amount": bill.actual_amount,
                "service_fee_rate": bill.service_fee_rate,
                "service_fee": bill.service_fee,
                "is_confirmed": bill.is_confirmed,
                "created_at": bill.created_at.isoformat() if bill.created_at else None  # type: ignore
            }
            bill_list.append(bill_dict)
            total_amount += bill.actual_amount
            total_service_fee += bill.service_fee
        
        return str({
            "success": True,
            "data": {
                "bill_details": bill_list,
                "summary": {
                    "total_items": len(bill_list),
                    "total_amount": total_amount,
                    "total_service_fee": total_service_fee,
                    "grand_total": total_amount + total_service_fee
                }
            }
        })
    except Exception as e:
        return str({
            "success": False,
            "message": f"获取账单明细失败: {str(e)}"
        })

@tool
def generate_bill_summary(user_id: int, order_items: str, runtime: ToolRuntime = None) -> str:
    """
    生成账单摘要（用于支付前展示给用户）
    
    Args:
        user_id: 用户ID
        order_items: 订单项目列表JSON字符串
            格式：[{"type": "medical/flight/hotel等", "name": "项目名称", "quantity": 1, "unit_price": 100.0}]
        runtime: 工具运行时上下文
    
    Returns:
        账单摘要（JSON格式）
    """
    try:
        items = json.loads(order_items)
        
        # 获取中介费率
        commission_rate = 0.05
        try:
            commission_result = json.loads(get_commission_rate())
            if commission_result.get("success"):
                commission_rate = commission_result["data"]["commission_rate"]
        except:
            pass
        
        # 计算账单明细
        bill_items = []
        subtotal = 0.0
        
        for item in items:
            quantity = item.get("quantity", 1)
            unit_price = float(item.get("unit_price", 0))
            total = quantity * unit_price
            
            bill_items.append({
                "type": item.get("type", "other"),
                "name": item.get("name", "未知项目"),
                "quantity": quantity,
                "unit_price": unit_price,
                "total": total
            })
            
            subtotal += total
        
        # 计算中介费
        service_fee = subtotal * commission_rate
        grand_total = subtotal + service_fee
        
        # 格式化账单摘要
        summary = {
            "user_id": user_id,
            "bill_items": bill_items,
            "cost_breakdown": {
                "subtotal": subtotal,
                "service_fee": service_fee,
                "service_fee_rate": commission_rate,
                "grand_total": grand_total
            },
            "display_text": f"""
📋 **MedChina 账单明细**

【费用项目】
"""
        }
        
        for item in bill_items:
            summary["display_text"] += f"- {item['name']}: ${item['total']:.2f} (数量: {item['quantity']} × ${item['unit_price']:.2f})\n"
        
        summary["display_text"] += f"""
【费用汇总】
- 小计: ${subtotal:.2f}
- 中介费 ({commission_rate * 100}%): ${service_fee:.2f}
- 总计: ${grand_total:.2f}

请确认以上费用明细后，再进行支付。
"""
        
        return str({
            "success": True,
            "data": summary
        })
    except json.JSONDecodeError:
        return str({
            "success": False,
            "message": "订单项目格式错误，请提供有效的JSON格式"
        })
    except Exception as e:
        return str({
            "success": False,
            "message": f"生成账单摘要失败: {str(e)}"
        })

@tool
def get_income_records(
    page: int = 1,
    page_size: int = 20,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    获取收入记录列表（后台管理用）
    
    Args:
        page: 页码
        page_size: 每页数量
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）
        runtime: 工具运行时上下文
    
    Returns:
        收入记录列表（JSON格式）
    """
    from storage.database.shared.model import IncomeRecord
    
    try:
        db = get_session()
        query = db.query(IncomeRecord)
        
        # 日期筛选
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(IncomeRecord.transaction_date >= start_dt)
        
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(IncomeRecord.transaction_date < end_dt)
        
        # 分页
        total = query.count()
        offset = (page - 1) * page_size
        records = query.order_by(IncomeRecord.transaction_date.desc()).offset(offset).limit(page_size).all()
        
        # 序列化结果
        record_list = []
        for record in records:
            record_dict = {
                "id": record.id,
                "income_type": record.income_type,
                "amount": record.amount,
                "currency": record.currency,
                "service_fee_rate": record.service_fee_rate,
                "service_fee_amount": record.service_fee_amount,
                "net_amount": record.net_amount,
                "transaction_date": record.transaction_date.isoformat() if record.transaction_date else None,  # type: ignore
                "status": record.status
            }
            record_list.append(record_dict)
        
        return str({
            "success": True,
            "data": {
                "records": record_list,
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
            "message": f"获取收入记录失败: {str(e)}"
        })

@tool
def get_expense_records(
    page: int = 1,
    page_size: int = 20,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    获取费用记录列表（后台管理用）
    
    Args:
        page: 页码
        page_size: 每页数量
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）
        runtime: 工具运行时上下文
    
    Returns:
        费用记录列表（JSON格式）
    """
    from storage.database.shared.model import ExpenseRecord
    
    try:
        db = get_session()
        query = db.query(ExpenseRecord)
        
        # 日期筛选
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(ExpenseRecord.expense_date >= start_dt)
        
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(ExpenseRecord.expense_date < end_dt)
        
        # 分页
        total = query.count()
        offset = (page - 1) * page_size
        records = query.order_by(ExpenseRecord.expense_date.desc()).offset(offset).limit(page_size).all()
        
        # 序列化结果
        record_list = []
        for record in records:
            record_dict = {
                "id": record.id,
                "expense_type": record.expense_type.value if record.expense_type else None,  # type: ignore
                "amount": record.amount,
                "currency": record.currency,
                "description": record.description,
                "expense_date": record.expense_date.isoformat() if record.expense_date else None,  # type: ignore
                "status": record.status,
                "approval_status": record.approval_status
            }
            record_list.append(record_dict)
        
        return str({
            "success": True,
            "data": {
                "records": record_list,
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
            "message": f"获取费用记录失败: {str(e)}"
        })
