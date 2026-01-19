#!/bin/bash

echo "===== 快速诊断 admin 路由问题 ====="
echo ""

# 1. 检查环境变量
echo "1. 环境变量检查:"
echo "   PGDATABASE_URL: ${PGDATABASE_URL:+已设置}"
echo "   PYTHONPATH: $PYTHONPATH"
echo "   COZE_PROJECT_TYPE: $COZE_PROJECT_TYPE"
echo ""

# 2. 测试数据库连接
echo "2. 数据库连接测试:"
cd /app && python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    from storage.database.db import get_engine
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute('SELECT 1')
    print('   ✓ 数据库连接成功')
except Exception as e:
    print(f'   ✗ 数据库连接失败: {type(e).__name__}: {e}')
" 2>&1
echo ""

# 3. 检查 admin 路由
echo "3. Admin 路由测试:"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/admin/login)
echo "   /admin/login: HTTP $HTTP_CODE"
if [ "$HTTP_CODE" = "404" ]; then
    echo "   ⚠ 路由未注册"
fi
echo ""

# 4. 获取所有 admin 路由
echo "4. 所有 admin 路由:"
cd /app && python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    from main import app
    admin_routes = [r.path for r in app.routes if hasattr(r, 'path') and 'admin' in r.path]
    if admin_routes:
        for r in sorted(set(admin_routes)):
            print(f'   - {r}')
    else:
        print('   (没有找到 admin 路由)')
except Exception as e:
    print(f'   错误: {e}')
" 2>&1
echo ""

echo "===== 诊断完成 ====="
