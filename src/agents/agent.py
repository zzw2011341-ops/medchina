"""
中国医疗旅游智能体
出品方: 山东和拾方信息科技有限公司
Slogan: 走！到中国去看病！
"""
import os
import json
from typing import Annotated
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage
from coze_coding_utils.runtime_ctx.context import default_headers
from storage.memory.memory_saver import get_memory_saver

# 导入工具
from tools.medical_query_tool import (
    search_doctors, get_doctor_detail, search_hospitals, 
    get_hospital_detail, search_diseases, get_featured_doctors, get_featured_hospitals,
    book_doctor_appointment, book_appointment_with_payment, get_appointment_detail
)
from tools.tourism_tool import (
    search_attractions, get_attraction_detail, 
    get_featured_attractions, get_attractions_by_city
)
from tools.travel_plan_tool import (
    create_travel_plan, update_travel_plan, confirm_travel_plan, 
    get_travel_plan, generate_sample_plan
)
from tools.message_tool import (
    send_message, get_messages, mark_message_as_read, 
    get_unread_count, get_conversation_list
)
from tools.payment_tool import (
    create_payment, process_payment, get_payment_status, 
    refund_payment, get_user_payments, cancel_payment
)
from tools.flight_booking_tool import (
    search_flights, book_flight, book_flight_with_payment, 
    get_flight_order_detail, cancel_flight_order
)
from tools.hotel_booking_tool import (
    search_hotels, book_hotel, book_hotel_with_payment, 
    get_hotel_order_detail, cancel_hotel_order
)
from tools.train_booking_tool import (
    search_trains, book_train_ticket, book_train_ticket_with_payment, 
    get_train_ticket_order_detail, cancel_train_ticket_order
)
from tools.attraction_ticket_tool import (
    book_attraction_ticket, book_attraction_ticket_with_payment, 
    get_attraction_ticket_order_detail, cancel_attraction_ticket_order
)

LLM_CONFIG = "config/agent_llm_config.json"

# 默认保留最近 20 轮对话 (40 条消息)
MAX_MESSAGES = 40

def _windowed_messages(old, new):
    """滑动窗口: 只保留最近 MAX_MESSAGES 条消息"""
    return add_messages(old, new)[-MAX_MESSAGES:] # type: ignore

class AgentState(MessagesState):
    messages: Annotated[list[AnyMessage], _windowed_messages]

def build_agent(ctx=None):
    """
    构建中国医疗旅游智能体
    
    这个智能体专门为欧美患者到中国就医和旅游提供全方位服务：
    - 多语言沟通（支持英语、德语、法语等）
    - 医疗信息查询（名医名院、病种、治疗方案）
    - 旅游景点推荐
    - 个性化出行方案生成
    - 用户间消息沟通
    - 支付通道（微信支付、VISA、MasterCard、支付宝、PayPal、银联等）
    - 医生预约和支付
    - 机票预定和支付
    - 酒店预定和支付
    - 车票预定和支付
    - 景点门票预定和支付
    """
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, LLM_CONFIG)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")
    
    llm = ChatOpenAI(
        model=cfg['config'].get("model"),
        api_key=api_key,
        base_url=base_url,
        temperature=cfg['config'].get('temperature', 0.7),
        streaming=True,
        timeout=cfg['config'].get('timeout', 600),
        extra_body={
            "thinking": {
                "type": cfg['config'].get('thinking', 'disabled')
            }
        },
        default_headers=default_headers(ctx) if ctx else {}
    )
    
    # 注册所有工具
    tools = [
        # 医疗查询工具
        search_doctors,
        get_doctor_detail,
        search_hospitals,
        get_hospital_detail,
        search_diseases,
        get_featured_doctors,
        get_featured_hospitals,
        
        # 医生预约工具（含支付）
        book_doctor_appointment,
        book_appointment_with_payment,
        get_appointment_detail,
        
        # 旅游景点工具
        search_attractions,
        get_attraction_detail,
        get_featured_attractions,
        get_attractions_by_city,
        
        # 出行方案工具
        create_travel_plan,
        update_travel_plan,
        confirm_travel_plan,
        get_travel_plan,
        generate_sample_plan,
        
        # 支付工具
        create_payment,
        process_payment,
        get_payment_status,
        refund_payment,
        get_user_payments,
        cancel_payment,
        
        # 机票预定工具
        search_flights,
        book_flight,
        book_flight_with_payment,
        get_flight_order_detail,
        cancel_flight_order,
        
        # 酒店预定工具
        search_hotels,
        book_hotel,
        book_hotel_with_payment,
        get_hotel_order_detail,
        cancel_hotel_order,
        
        # 车票预定工具
        search_trains,
        book_train_ticket,
        book_train_ticket_with_payment,
        get_train_ticket_order_detail,
        cancel_train_ticket_order,
        
        # 景点门票预定工具
        book_attraction_ticket,
        book_attraction_ticket_with_payment,
        get_attraction_ticket_order_detail,
        cancel_attraction_ticket_order,
        
        # 消息沟通工具
        send_message,
        get_messages,
        mark_message_as_read,
        get_unread_count,
        get_conversation_list,
    ]
    
    return create_agent(
        model=llm,
        system_prompt=cfg.get("sp"),
        tools=tools,
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )
