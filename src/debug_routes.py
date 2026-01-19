"""添加路由调试端点"""
from fastapi import APIRouter

def register_debug_routes():
    """注册调试路由到应用"""
    from main import app

    debug_router = APIRouter(prefix="/debug", tags=["Debug"])

    @debug_router.get("/routes")
    async def list_all_routes():
        """列出所有注册的路由"""
        routes = []
        for route in app.routes:
            route_info = {"path": getattr(route, 'path', str(route))}
            if hasattr(route, 'methods'):
                route_info['methods'] = list(route.methods)
            if hasattr(route, 'tags'):
                route_info['tags'] = getattr(route, 'tags', [])
            routes.append(route_info)

        admin_routes = [r for r in routes if 'admin' in r.get('path', '')]

        return {
            "total_routes": len(routes),
            "admin_routes": len(admin_routes),
            "admin_routes_list": admin_routes,
            "all_routes": routes
        }

    @debug_router.get("/health-detailed")
    async def health_detailed():
        """详细的健康检查"""
        import os
        from storage.database.db import get_engine

        db_status = "ok"
        db_error = None
        try:
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute('SELECT 1')
        except Exception as e:
            db_status = "error"
            db_error = str(e)

        return {
            "status": "ok",
            "database": {
                "status": db_status,
                "url_set": bool(os.getenv('PGDATABASE_URL')),
                "error": db_error
            },
            "environment": {
                "pythonpath": os.getenv('PYTHONPATH', ''),
                "project_type": os.getenv('COZE_PROJECT_TYPE', '')
            }
        }

    # 注册调试路由
    app.include_router(debug_router)
    print("✓ Debug routes registered: /debug/routes, /debug/health-detailed")
