#!/bin/bash

echo "========================================="
echo "MedChina Railway 部署诊断脚本"
echo "========================================="
echo ""

# 检查 Railway CLI 是否已安装
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI 未安装"
    echo "请安装: npm install -g @railway/cli"
    exit 1
fi

echo "1️⃣  检查 Railway 登录状态..."
railway status > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 已登录 Railway"
else
    echo "❌ 未登录 Railway"
    echo "请运行: railway login"
    exit 1
fi

echo ""
echo "2️⃣  获取项目 URL..."
PROJECT_URL=$(railway domain 2>/dev/null | head -1)
if [ -z "$PROJECT_URL" ]; then
    echo "⚠️  无法获取项目 URL，尝试从项目配置中获取..."
    PROJECT_ID=$(railway project 2>/dev/null | grep "ID" | awk '{print $2}')
    if [ -z "$PROJECT_ID" ]; then
        echo "❌ 无法获取项目信息"
        exit 1
    fi
    PROJECT_URL="https://$PROJECT_ID.railway.app"
fi
echo "🌐 项目 URL: $PROJECT_URL"

echo ""
echo "3️⃣  检查服务状态..."
railway status 2>/dev/null

echo ""
echo "4️⃣  检查部署状态..."
LATEST_DEPLOYMENT=$(railway logs --limit 1 2>/dev/null | tail -20)
echo "最新部署日志:"
echo "$LATEST_DEPLOYMENT"

echo ""
echo "5️⃣  测试健康检查端点..."
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $PROJECT_URL/health 2>/dev/null)
if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo "✅ /health 端点正常 (HTTP $HEALTH_RESPONSE)"
else
    echo "❌ /health 端点异常 (HTTP $HEALTH_RESPONSE)"
fi

echo ""
echo "6️⃣  测试调试路由端点..."
DEBUG_ROUTES_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $PROJECT_URL/debug/routes 2>/dev/null)
if [ "$DEBUG_ROUTES_RESPONSE" = "200" ]; then
    echo "✅ /debug/routes 端点正常 (HTTP $DEBUG_ROUTES_RESPONSE)"
    echo ""
    echo "📋 注册的路由列表:"
    curl -s $PROJECT_URL/debug/routes 2>/dev/null | jq '.admin_routes_list' 2>/dev/null || echo "无法解析 JSON"
else
    echo "❌ /debug/routes 端点异常 (HTTP $DEBUG_ROUTES_RESPONSE)"
fi

echo ""
echo "7️⃣  测试详细健康检查端点..."
HEALTH_DETAILED_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $PROJECT_URL/debug/health-detailed 2>/dev/null)
if [ "$HEALTH_DETAILED_RESPONSE" = "200" ]; then
    echo "✅ /debug/health-detailed 端点正常 (HTTP $HEALTH_DETAILED_RESPONSE)"
    echo ""
    echo "📊 详细健康状态:"
    curl -s $PROJECT_URL/debug/health-detailed 2>/dev/null | jq '.' 2>/dev/null || echo "无法解析 JSON"
else
    echo "❌ /debug/health-detailed 端点异常 (HTTP $HEALTH_DETAILED_RESPONSE)"
fi

echo ""
echo "8️⃣  测试 Admin 登录页面..."
ADMIN_LOGIN_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $PROJECT_URL/admin/login 2>/dev/null)
if [ "$ADMIN_LOGIN_RESPONSE" = "200" ]; then
    echo "✅ /admin/login 端点正常 (HTTP $ADMIN_LOGIN_RESPONSE)"
else
    echo "❌ /admin/login 端点异常 (HTTP $ADMIN_LOGIN_RESPONSE)"
fi

echo ""
echo "========================================="
echo "诊断完成"
echo "========================================="
