#!/bin/bash

echo "=========================================="
echo "Railway 诊断脚本"
echo "=========================================="
echo ""

echo "1. 检查容器进程"
ps aux | grep -E "(uvicorn|python)" | grep -v grep
echo ""

echo "2. 检查监听端口"
netstat -tlnp 2>/dev/null || ss -tlnp 2>/dev/null || echo "无法查看端口"
echo ""

echo "3. 测试本地健康检查"
curl -v http://localhost:8000/health 2>&1
echo ""

echo "4. 测试首页"
curl -I http://localhost:8000/ 2>&1
echo ""

echo "5. 检查环境变量"
echo "PYTHONPATH: $PYTHONPATH"
echo "COZE_PROJECT_TYPE: $COZE_PROJECT_TYPE"
echo "PORT: $PORT"
echo ""

echo "6. 检查日志文件"
if [ -f logs/app.log ]; then
    echo "最近的日志："
    tail -20 logs/app.log
else
    echo "日志文件不存在"
fi
echo ""

echo "7. 测试 Python 导入"
cd /app
python -c "
import sys
print('Python 路径:')
for p in sys.path[:5]:
    print(f'  {p}')
print()

try:
    from src.main import app, service
    print('✓ app 和 service 导入成功')
    print(f'✓ app 类型: {type(app)}')
    print(f'✓ service 类型: {type(service)}')
except Exception as e:
    print(f'✗ 导入失败: {e}')
    import traceback
    traceback.print_exc()
"
echo ""

echo "=========================================="
echo "诊断完成"
echo "=========================================="
