#!/bin/bash

echo "===== Railway 诊断脚本 - 检查 admin 路由问题 ====="
echo ""

echo "1. 检查应用进程:"
ps aux | grep uvicorn | grep -v grep
echo ""

echo "2. 检查 admin 路由:"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8000/admin/login
echo ""

echo "3. 检查 OpenAPI 文档中的 admin 路由:"
curl -s http://localhost:8000/openapi.json | python3 -c "import sys, json; routes=[p for p in json.load(sys.stdin)['paths'].keys() if 'admin' in p]; print('\n'.join(routes))" 2>/dev/null || echo "无法获取 OpenAPI"
echo ""

echo "4. 检查环境变量:"
echo "PGDATABASE_URL=${PGDATABASE_URL:0:30}..."
echo "PYTHONPATH=$PYTHONPATH"
echo "COZE_PROJECT_TYPE=$COZE_PROJECT_TYPE"
echo ""

echo "5. 测试数据库连接:"
python3 -c "
import sys
sys.path.insert(0, '/app/src')
try:
    from storage.database.db import get_engine
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute('SELECT 1')
    print('✓ 数据库连接成功')
except Exception as e:
    print(f'✗ 数据库连接失败: {e}')
" 2>&1
echo ""

echo "6. 检查 admin 模块导入:"
python3 -c "
import sys
sys.path.insert(0, '/app/src')
try:
    from admin.routes import router
    print(f'✓ admin.routes 导入成功，路由数量: {len(router.routes)}')
    for route in router.routes[:5]:
        print(f'  - {route.path}')
except Exception as e:
    print(f'✗ admin.routes 导入失败: {e}')
" 2>&1
echo ""

echo "7. 检查 admin API 模块导入:"
python3 -c "
import sys
sys.path.insert(0, '/app/src')
try:
    from admin.api import auth
    print(f'✓ admin.api.auth 导入成功，路由数量: {len(auth.router.routes)}')
    for route in auth.router.routes:
        print(f'  - {route.path}')
except Exception as e:
    print(f'✗ admin.api.auth 导入失败: {e}')
" 2>&1
echo ""

echo "8. 检查应用启动日志（最后 50 行）:"
if [ -f logs/app.log ]; then
    tail -n 50 logs/app.log
else
    echo "日志文件不存在"
fi
echo ""

echo "===== 诊断完成 ====="
