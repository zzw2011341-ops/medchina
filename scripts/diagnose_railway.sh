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
echo "PGDATABASE_URL=${PGDATABASE_URL:0:20}..."  # 只显示前20个字符
echo ""

echo "4. 检查应用健康状态:"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8000/health
echo ""

echo "5. 检查 admin 路由:"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8000/admin/login
echo ""

echo "6. 检查应用启动日志（最后50行）:"
if [ -f logs/app.log ]; then
    tail -n 50 logs/app.log
else
    echo "日志文件不存在"
fi
echo ""

echo "===== 诊断完成 ====="
