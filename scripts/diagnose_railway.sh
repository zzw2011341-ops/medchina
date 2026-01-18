#!/bin/bash

echo "===== Railway 部署诊断脚本 ====="
echo ""

echo "1. 检查进程状态:"
ps aux | grep -E "(uvicorn|python)" | grep -v grep
echo ""

echo "2. 检查端口 8000 监听状态:"
netstat -tlnp 2>/dev/null | grep 8000 || ss -tlnp 2>/dev/null | grep 8000 || echo "无法检查端口"
echo ""

echo "3. 检查环境变量:"
echo "PYTHONPATH=$PYTHONPATH"
echo "COZE_PROJECT_TYPE=$COZE_PROJECT_TYPE"
if [ -n "$PGDATABASE_URL" ]; then
    echo "PGDATABASE_URL=${PGDATABASE_URL:0:30}..."
else
    echo "PGDATABASE_URL=(未设置)"
fi
echo ""

echo "4. 检查应用健康状态:"
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
echo "HTTP Status: $HEALTH_STATUS"
if [ "$HEALTH_STATUS" = "200" ]; then
    echo "响应内容:"
    curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/health
fi
echo ""

echo "5. 检查 admin 路由:"
ADMIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/admin/login)
echo "HTTP Status: $ADMIN_STATUS"
if [ "$ADMIN_STATUS" = "404" ]; then
    echo "警告: admin 路由未找到 (404)"
    echo "可能原因: admin 模块导入失败或路由未注册"
elif [ "$ADMIN_STATUS" = "200" ]; then
    echo "成功: admin 路由可访问"
fi
echo ""

echo "6. 列出所有注册的路由:"
curl -s http://localhost:8000/docs 2>/dev/null | grep -o '"/[^"]*"' | sort -u | head -20
echo ""

echo "7. 检查应用启动日志（最后50行）:"
if [ -f logs/app.log ]; then
    tail -n 50 logs/app.log
else
    echo "日志文件不存在"
fi
echo ""

echo "8. 测试数据库连接:"
python3 -c "
import sys
sys.path.insert(0, '/app/src')
try:
    from storage.database.db import get_engine
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute('SELECT 1')
        print('数据库连接成功')
except Exception as e:
    print(f'数据库连接失败: {e}')
" 2>&1
echo ""

echo "===== 诊断完成 ====="
