"""
旅游景点查询工具
"""
from langchain.tools import tool, ToolRuntime
from typing import Optional
from coze_coding_dev_sdk.database import get_session
from storage.database.shared.model import TouristAttraction


def _format_attraction(attraction: TouristAttraction, include_details: bool = False) -> dict:
    """格式化景点信息"""
    result = {
        "id": attraction.id,
        "name": attraction.name,
        "name_en": attraction.name_en,
        "city": attraction.city,
        "province": attraction.province,
        "category": attraction.category,
        "rating": attraction.rating,
        "review_count": attraction.review_count,
        "is_featured": attraction.is_featured,
    }
    
    if include_details:
        ticket_price_str = "免费"
        if attraction.ticket_price is not None:
            ticket_price_str = f"${attraction.ticket_price}"
        
        result.update({
            "address": attraction.address,
            "description": attraction.description,
            "highlights": attraction.highlights,
            "ticket_price": ticket_price_str,
            "opening_hours": attraction.opening_hours,
            "recommended_duration": attraction.recommended_duration,
            "best_visit_season": attraction.best_visit_season,
            "image_urls": attraction.image_urls,
        })
    
    return result


@tool
def search_attractions(
    keyword: Optional[str] = None,
    city: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 10,
    runtime: ToolRuntime = None
) -> str:
    """
    查询旅游景点信息
    
    Args:
        keyword: 搜索关键词（景点名称）
        city: 城市（可选）
        category: 景点类别（可选，如"自然风光"、"历史人文"）
        limit: 返回结果数量限制
        runtime: 运行时上下文
    
    Returns:
        JSON格式的景点列表
    """
    db = get_session()
    try:
        query = db.query(TouristAttraction).filter(TouristAttraction.is_active == True)
        
        if keyword:
            query = query.filter(
                TouristAttraction.name.ilike(f"%{keyword}%") |
                TouristAttraction.name_en.ilike(f"%{keyword}%")
            )
        
        if city:
            query = query.filter(TouristAttraction.city.ilike(f"%{city}%"))
        
        if category:
            query = query.filter(TouristAttraction.category.ilike(f"%{category}%"))
        
        # 优先显示推荐的景点
        query = query.order_by(TouristAttraction.is_featured.desc(), TouristAttraction.rating.desc())
        
        attractions = query.limit(limit).all()
        result = [_format_attraction(a, include_details=False) for a in attractions]
        
        return f"找到 {len(result)} 个景点:\n{result}"
    
    finally:
        db.close()


@tool
def get_attraction_detail(
    attraction_id: int,
    runtime: ToolRuntime = None
) -> str:
    """
    获取景点详细信息
    
    Args:
        attraction_id: 景点ID
        runtime: 运行时上下文
    
    Returns:
        JSON格式的景点详细信息
    """
    db = get_session()
    try:
        attraction = db.query(TouristAttraction).filter(
            TouristAttraction.id == attraction_id
        ).first()
        
        if not attraction:
            return "未找到该景点信息"
        
        result = _format_attraction(attraction, include_details=True)
        
        return f"景点详细信息:\n{result}"
    
    finally:
        db.close()


@tool
def get_featured_attractions(
    limit: int = 5,
    runtime: ToolRuntime = None
) -> str:
    """
    获取推荐的旅游景点列表
    
    Args:
        limit: 返回结果数量限制
        runtime: 运行时上下文
    
    Returns:
        JSON格式的推荐景点列表
    """
    db = get_session()
    try:
        query = db.query(TouristAttraction).filter(
            TouristAttraction.is_featured == True,
            TouristAttraction.is_active == True
        )
        
        attractions = query.order_by(TouristAttraction.rating.desc()).limit(limit).all()
        result = [_format_attraction(a, include_details=True) for a in attractions]
        
        return f"推荐景点 ({len(attractions)} 个):\n{result}"
    
    finally:
        db.close()


@tool
def get_attractions_by_city(
    city: str,
    limit: int = 10,
    runtime: ToolRuntime = None
) -> str:
    """
    根据城市查询景点
    
    Args:
        city: 城市名称
        limit: 返回结果数量限制
        runtime: 运行时上下文
    
    Returns:
        JSON格式的景点列表
    """
    db = get_session()
    try:
        query = db.query(TouristAttraction).filter(
            TouristAttraction.city.ilike(f"%{city}%"),
            TouristAttraction.is_active == True
        )
        
        attractions = query.order_by(TouristAttraction.rating.desc()).limit(limit).all()
        result = [_format_attraction(a, include_details=True) for a in attractions]
        
        return f"{city}的景点 ({len(attractions)} 个):\n{result}"
    
    finally:
        db.close()
