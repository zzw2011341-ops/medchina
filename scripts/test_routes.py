#!/usr/bin/env python3
"""测试路由是否正确注册"""
import sys
sys.path.insert(0, 'src')

# 设置环境变量
import os
os.environ['PYTHONPATH'] = '/app:/app/src'
os.environ['COZE_PROJECT_TYPE'] = 'agent'

try:
    # 导入应用
    from main import app
    print("✓ 主应用导入成功")
    
    # 获取所有路由
    routes = []
    for route in app.routes:
        if hasattr(route, 'path'):
            routes.append(route.path)
    
    print(f"\n总路由数: {len(routes)}")
    
    # 筛选 admin 路由
    admin_routes = [r for r in routes if 'admin' in r]
    
    print(f"\nAdmin 路由数: {len(admin_routes)}")
    print("Admin 路由列表:")
    for route in sorted(admin_routes):
        print(f"  - {route}")
    
    # 检查关键路由
    key_routes = [
        '/admin/login',
        '/admin/api/auth/login',
        '/health',
    ]
    
    print("\n关键路由检查:")
    for key_route in key_routes:
        exists = key_route in routes
        status = "✓" if exists else "✗"
        print(f"  {status} {key_route}")
        
except Exception as e:
    print(f"✗ 错误: {e}")
    import traceback
    traceback.print_exc()
