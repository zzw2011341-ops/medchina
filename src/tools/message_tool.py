"""
用户消息沟通工具
"""
from langchain.tools import tool, ToolRuntime
from typing import Optional
from datetime import datetime
from storage.database.db import get_session
from storage.database.shared.model import Message, User
from sqlalchemy import or_, and_

# Type hints
from typing import Any, cast


@tool
def send_message(
    sender_id: int,
    content: str,
    receiver_id: Optional[int] = None,
    message_type: str = "text",
    attachments: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    发送消息
    
    Args:
        sender_id: 发送者用户ID
        content: 消息内容
        receiver_id: 接收者用户ID（NULL为系统消息）
        message_type: 消息类型（text/image/file）
        attachments: 附件信息（JSON字符串）
        runtime: 运行时上下文
    
    Returns:
        发送结果
    """
    import json
    
    db = get_session()
    try:
        # 检查发送者是否存在
        sender = db.query(User).filter(User.id == sender_id).first()
        if not sender:
            return f"错误: 发送者ID {sender_id} 不存在"
        
        # 如果指定了接收者，检查接收者是否存在
        if receiver_id:
            receiver = db.query(User).filter(User.id == receiver_id).first()
            if not receiver:
                return f"错误: 接收者ID {receiver_id} 不存在"
        
        # 解析附件信息
        attachments_data = None
        if attachments:
            try:
                attachments_data = json.loads(attachments)
            except json.JSONDecodeError:
                attachments_data = [{"description": attachments}]
        
        # 创建消息
        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            message_type=message_type,
            attachments=attachments_data,
            is_read=False
        )
        
        db.add(message)
        db.commit()
        db.refresh(message)
        
        if receiver_id:
            return f"✅ 消息发送成功！\n消息ID: {message.id}\n接收者: {receiver_id}"
        else:
            return f"✅ 系统消息发送成功！\n消息ID: {message.id}"
    
    except Exception as e:
        db.rollback()
        return f"发送失败: {str(e)}"
    finally:
        db.close()


@tool
def get_messages(
    user_id: int,
    conversation_with: Optional[int] = None,
    limit: int = 20,
    runtime: ToolRuntime = None
) -> str:
    """
    获取消息列表
    
    Args:
        user_id: 用户ID
        conversation_with: 与指定用户的消息（可选）
        limit: 返回结果数量限制
        runtime: 运行时上下文
    
    Returns:
        消息列表
    """
    db = get_session()
    try:
        from sqlalchemy import or_
        
        query = db.query(Message)
        
        # 获取发送和接收的消息
        query = query.filter(
            or_(
                Message.sender_id == user_id,
                Message.receiver_id == user_id
            )
        )
        
        # 如果指定了对话用户
        if conversation_with:
            query = query.filter(
                or_(
                    and_(
                        Message.sender_id == user_id,
                        Message.receiver_id == conversation_with
                    ),
                    and_(
                        Message.sender_id == conversation_with,
                        Message.receiver_id == user_id
                    )
                )
            )
        
        # 按时间倒序排列
        messages = query.order_by(Message.created_at.desc()).limit(limit).all()
        
        result = []
        for msg in reversed(messages):
            msg_sender_id: int = int(msg.sender_id) if msg.sender_id is not None else 0
            msg_receiver_id: Optional[int] = int(msg.receiver_id) if msg.receiver_id is not None else None
            msg_is_read: bool = bool(msg.is_read) if msg.is_read is not None else False
            
            sender = db.query(User).filter(User.id == msg_sender_id).first()
            
            if msg_receiver_id:
                receiver = db.query(User).filter(User.id == msg_receiver_id).first()
            else:
                receiver = None
            
            sender_name = sender.name if sender else "系统"
            receiver_name = receiver.name if receiver else "所有人"
            
            result.append({
                "id": msg.id,
                "sender": sender_name,
                "receiver": receiver_name,
                "content": msg.content,
                "type": msg.message_type,
                "is_read": msg_is_read,
                "time": msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return f"消息列表 ({len(result)} 条):\n{result}"
    
    except Exception as e:
        return f"获取失败: {str(e)}"
    finally:
        db.close()


@tool
def mark_message_as_read(
    message_id: int,
    user_id: int,
    runtime: ToolRuntime = None
) -> str:
    """
    标记消息为已读
    
    Args:
        message_id: 消息ID
        user_id: 用户ID（用于验证权限）
        runtime: 运行时上下文
    
    Returns:
        操作结果
    """
    db = get_session()
    try:
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            return f"错误: 消息ID {message_id} 不存在"
        
        # 验证用户是否为接收者
        msg_receiver_id: Optional[int] = int(message.receiver_id) if message.receiver_id is not None else None
        if msg_receiver_id != user_id:
            return f"错误: 您无权标记此消息为已读"
        
        # 使用正确的赋值方式
        db.query(Message).filter(Message.id == message_id).update({
            Message.is_read: True
        })
        db.commit()
        
        return f"✅ 消息已标记为已读"
    
    except Exception as e:
        db.rollback()
        return f"操作失败: {str(e)}"
    finally:
        db.close()


@tool
def get_unread_count(
    user_id: int,
    runtime: ToolRuntime = None
) -> str:
    """
    获取未读消息数量
    
    Args:
        user_id: 用户ID
        runtime: 运行时上下文
    
    Returns:
        未读消息数量
    """
    db = get_session()
    try:
        count = db.query(Message).filter(
            Message.receiver_id == user_id,
            Message.is_read == False
        ).count()
        
        return f"您有 {count} 条未读消息"
    
    except Exception as e:
        return f"获取失败: {str(e)}"
    finally:
        db.close()


@tool
def get_conversation_list(
    user_id: int,
    runtime: ToolRuntime = None
) -> str:
    """
    获取用户的对话列表（最近联系的人）
    
    Args:
        user_id: 用户ID
        runtime: 运行时上下文
    
    Returns:
        对话列表
    """
    db = get_session()
    try:
        from sqlalchemy import or_
        
        # 获取所有相关的消息
        messages = db.query(Message).filter(
            or_(
                Message.sender_id == user_id,
                Message.receiver_id == user_id
            )
        ).order_by(Message.created_at.desc()).all()
        
        # 收集对话用户
        conversation_users = {}
        for msg in messages:
            msg_sender_id: int = int(msg.sender_id) if msg.sender_id is not None else 0
            msg_receiver_id: Optional[int] = int(msg.receiver_id) if msg.receiver_id is not None else None
            msg_is_read: bool = bool(msg.is_read) if msg.is_read is not None else False
            
            sender = db.query(User).filter(User.id == msg_sender_id).first()
            
            if msg_receiver_id:
                receiver = db.query(User).filter(User.id == msg_receiver_id).first()
            else:
                receiver = None
            
            if msg_sender_id != user_id and msg_sender_id not in conversation_users:
                conversation_users[msg_sender_id] = {
                    "user_id": msg_sender_id,
                    "name": sender.name if sender else "系统",
                    "last_message": msg.content,
                    "last_time": msg.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "unread_count": 0
                }
            elif msg_receiver_id and msg_receiver_id != user_id and msg_receiver_id not in conversation_users:
                conversation_users[msg_receiver_id] = {
                    "user_id": msg_receiver_id,
                    "name": receiver.name if receiver else "系统",
                    "last_message": msg.content,
                    "last_time": msg.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "unread_count": 0
                }
            
            # 计算未读数量
            if msg_receiver_id == user_id and not msg_is_read:
                conversation_users[msg_sender_id]["unread_count"] += 1
        
        result = list(conversation_users.values())
        
        return f"对话列表 ({len(result)} 个):\n{result}"
    
    except Exception as e:
        return f"获取失败: {str(e)}"
    finally:
        db.close()
