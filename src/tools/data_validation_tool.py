"""
数据验证工具
提供电话号码、护照号、电子邮箱等数据的验证功能
"""
import re
from typing import Optional, Dict, Any
from langchain.tools import tool, ToolRuntime
from storage.database.db import get_session

@tool
def validate_phone_number(phone: str, country_code: str = "US") -> str:
    """
    验证电话号码的有效性
    
    Args:
        phone: 电话号码
        country_code: 国家代码（如：US, UK, DE, FR, CN等），默认为US
    
    Returns:
        验证结果（JSON格式字符串）
    """
    result = {
        "is_valid": False,
        "phone": phone,
        "country_code": country_code,
        "message": "",
        "formatted": None
    }
    
    if not phone:
        result["message"] = "电话号码不能为空"
        return str(result)
    
    # 移除所有非数字字符
    cleaned_phone = re.sub(r'[^\d+]', '', phone)
    
    # 根据国家代码验证电话号码格式
    patterns = {
        "US": r'^\+?1?[2-9]\d{2}[2-9]\d{2}\d{4}$',  # 美国：10位数字，可选+1前缀
        "UK": r'^\+?44[1-9]\d{8,9}$',  # 英国：+44后接9-10位数字
        "DE": r'^\+?49[1-9]\d{8,11}$',  # 德国：+49后接9-12位数字
        "FR": r'^\+?33[1-9]\d{8}$',  # 法国：+33后接9位数字
        "CN": r'^\+?86[1-9]\d{10}$',  # 中国：+86后接11位数字
    }
    
    pattern = patterns.get(country_code.upper(), patterns["US"])
    
    if re.match(pattern, cleaned_phone):
        result["is_valid"] = True
        result["formatted"] = cleaned_phone
        result["message"] = "电话号码格式正确"
    else:
        result["message"] = f"电话号码格式不正确，请检查{country_code}国家/地区的电话号码格式"
    
    return str(result)

@tool
def validate_passport_number(passport_number: str, country_code: str = None) -> str:
    """
    验证护照号码的有效性
    
    Args:
        passport_number: 护照号码
        country_code: 国家代码（可选），用于特定国家验证
    
    Returns:
        验证结果（JSON格式字符串）
    """
    result = {
        "is_valid": False,
        "passport_number": passport_number,
        "country_code": country_code,
        "message": "",
        "formatted": None
    }
    
    if not passport_number:
        result["message"] = "护照号码不能为空"
        return str(result)
    
    # 移除空格
    cleaned = passport_number.strip().upper()
    
    # 通用护照号码验证规则
    # 通常为字母和数字的组合，长度6-12位
    if not re.match(r'^[A-Z0-9]{6,12}$', cleaned):
        result["message"] = "护照号码格式不正确，应为6-12位字母和数字的组合"
        return str(result)
    
    # 特定国家的护照号码验证（可选）
    if country_code:
        country_patterns = {
            "US": r'^[A-Z]{2}[0-9]{7}$',  # 美国：2字母+7数字
            "UK": r'^[0-9]{9}$',  # 英国：9位数字
            "CN": r'^[GE][0-9]{8}$',  # 中国：G或E开头+8位数字
        }
        
        pattern = country_patterns.get(country_code.upper())
        if pattern and not re.match(pattern, cleaned):
            result["message"] = f"护照号码格式不符合{country_code}国家护照规范"
            return str(result)
    
    result["is_valid"] = True
    result["formatted"] = cleaned
    result["message"] = "护照号码格式正确"
    
    return str(result)

@tool
def validate_email(email: str) -> str:
    """
    验证电子邮箱的有效性
    
    Args:
        email: 电子邮箱地址
    
    Returns:
        验证结果（JSON格式字符串）
    """
    result = {
        "is_valid": False,
        "email": email,
        "message": "",
        "formatted": None
    }
    
    if not email:
        result["message"] = "电子邮箱不能为空"
        return str(result)
    
    # 电子邮箱验证正则表达式
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(pattern, email):
        # 检查邮箱长度
        if len(email) > 255:
            result["message"] = "电子邮箱地址过长"
        else:
            result["is_valid"] = True
            result["formatted"] = email.lower()  # 统一转为小写
            result["message"] = "电子邮箱格式正确"
    else:
        result["message"] = "电子邮箱格式不正确"
    
    return str(result)

@tool
def validate_user_data(user_data: str, runtime: ToolRuntime = None) -> str:
    """
    综合验证用户数据（电话、邮箱、护照号）
    
    Args:
        user_data: 用户数据JSON字符串，包含phone, email, passport_number等字段
        runtime: 工具运行时上下文
    
    Returns:
        综合验证结果（JSON格式字符串）
    """
    import json
    
    try:
        data = json.loads(user_data)
    except json.JSONDecodeError:
        return str({
            "is_valid": False,
            "message": "用户数据格式错误，请提供有效的JSON格式"
        })
    
    validation_results = {
        "phone": None,
        "email": None,
        "passport_number": None
    }
    
    overall_valid = True
    
    # 验证电话号码
    if "phone" in data and data["phone"]:
        phone_result = json.loads(validate_phone_number(data["phone"], data.get("country_code", "US")))
        validation_results["phone"] = phone_result
        if not phone_result["is_valid"]:
            overall_valid = False
    
    # 验证电子邮箱
    if "email" in data and data["email"]:
        email_result = json.loads(validate_email(data["email"]))
        validation_results["email"] = email_result
        if not email_result["is_valid"]:
            overall_valid = False
    
    # 验证护照号码
    if "passport_number" in data and data["passport_number"]:
        passport_result = json.loads(validate_passport_number(
            data["passport_number"], 
            data.get("country_code")
        ))
        validation_results["passport_number"] = passport_result
        if not passport_result["is_valid"]:
            overall_valid = False
    
    return str({
        "is_valid": overall_valid,
        "validation_results": validation_results,
        "message": "用户数据验证通过" if overall_valid else "用户数据验证失败，请检查无效字段"
    })
