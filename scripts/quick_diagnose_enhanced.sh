#!/bin/bash

echo "========================================="
echo "MedChina 应用启动诊断"
echo "========================================="
echo ""

# 设置环境变量
export PYTHONPATH="/workspace/projects:/workspace/projects/src"
export COZE_PROJECT_TYPE="agent"

echo "1️⃣  检查 Python 版本..."
python --version

echo ""
echo "2️⃣  检查 PYTHONPATH..."
echo "PYTHONPATH=$PYTHONPATH"

echo ""
echo "3️⃣  测试模块导入..."
echo "  - 测试 main 模块..."
python -c "import src.main; print('  ✓ src.main imported')" 2>&1 | grep -E "(✓|Error|Traceback)"

echo ""
echo "  - 测试 admin 模块..."
python -c "import src.admin.routes; print('  ✓ src.admin.routes imported')" 2>&1 | grep -E "(✓|Error|Traceback)"

echo ""
echo "  - 测试数据库连接..."
python -c "from src.storage.database.db import get_engine; engine = get_engine(); print('  ✓ Database connected')" 2>&1 | grep -E "(✓|Error|Traceback)"

echo ""
echo "4️⃣  列出所有已注册的路由..."
python -c "from src.main import app; routes = [{'path': r.path if hasattr(r, 'path') else str(r), 'methods': list(r.methods) if hasattr(r, 'methods') else []} for r in app.routes]; admin_routes = [r for r in routes if 'admin' in r['path']]; print(f'Total routes: {len(routes)}'); print(f'Admin routes: {len(admin_routes)}'); [print(f\"  - {r['path']} ({r['methods']})\") for r in admin_routes[:10]]" 2>&1 | grep -E "(Total|Admin|  -)"

echo ""
echo "5️⃣  测试应用启动..."
echo "  启动应用（10秒超时）..."
timeout 10 python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 2>&1 &
APP_PID=$!
sleep 5

if kill -0 $APP_PID 2>/dev/null; then
    echo "  ✓ 应用成功启动 (PID: $APP_PID)"
    echo ""
    echo "  测试端点..."
    echo "    - /health"
    curl -s -o /dev/null -w "      HTTP Status: %{http_code}\n" http://localhost:8001/health 2>/dev/null
    echo "    - /admin/login"
    curl -s -o /dev/null -w "      HTTP Status: %{http_code}\n" http://localhost:8001/admin/login 2>/dev/null
    echo "    - /debug/routes"
    curl -s -o /dev/null -w "      HTTP Status: %{http_code}\n" http://localhost:8001/debug/routes 2>/dev/null

    kill $APP_PID 2>/dev/null
    echo "  ✓ 应用已停止"
else
    echo "  ❌ 应用启动失败"
fi

echo ""
echo "========================================="
echo "诊断完成"
echo "========================================="
