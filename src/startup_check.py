"""
应用启动时输出关键诊断信息"""
import os
import sys

print("=" * 60)
print("MedChina 应用启动诊断")
print("=" * 60)
print(f"Python 版本: {sys.version}")
print(f"工作目录: {os.getcwd()}")
print(f"PYTHONPATH: {os.getenv('PYTHONPATH', 'NOT SET')}")
print(f"COZE_PROJECT_TYPE: {os.getenv('COZE_PROJECT_TYPE', 'NOT SET')}")
print(f"PGDATABASE_URL 设置: {'YES' if os.getenv('PGDATABASE_URL') else 'NO'}")
print("=" * 60)

# 尝试导入关键模块
try:
    from src.admin.routes import router
    print("✓ src.admin.routes 导入成功")
except Exception as e:
    print(f"✗ src.admin.routes 导入失败: {e}")
    sys.exit(1)

try:
    from src.storage.database.db import get_engine
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute('SELECT 1')
    print("✓ 数据库连接成功")
except Exception as e:
    print(f"✗ 数据库连接失败: {e}")
    sys.exit(1)

try:
    from src.debug_routes import register_debug_routes
    print("✓ debug_routes 导入成功")
except Exception as e:
    print(f"✗ debug_routes 导入失败: {e}")
    sys.exit(1)

print("=" * 60)
print("所有检查通过，应用准备就绪")
print("=" * 60)
