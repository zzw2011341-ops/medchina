#!/bin/bash

# 快速部署脚本
# 用于本地 Docker 部署测试

set -e

echo "================================"
echo "MedChina 快速部署脚本"
echo "================================"
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    echo "   访问: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

echo "✅ Docker 和 Docker Compose 已安装"
echo ""

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  .env 文件不存在，从 .env.example 创建..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件，请编辑配置后重新运行"
    echo ""
    echo "需要配置的环境变量："
    echo "  - DATABASE_URL"
    echo "  - SECRET_KEY"
    echo "  - COZE_WORKLOAD_IDENTITY_API_KEY"
    echo ""
    echo "运行以下命令编辑配置："
    echo "  nano .env  # 或使用其他编辑器"
    exit 1
fi

echo "✅ 找到 .env 配置文件"
echo ""

# 询问是否启动服务
read -p "是否启动服务？(y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 部署已取消"
    exit 1
fi

echo ""
echo "🚀 开始部署..."
echo ""

# 停止旧容器（如果存在）
echo "📦 停止旧容器..."
docker-compose down 2>/dev/null || true

# 构建镜像
echo "🔨 构建 Docker 镜像..."
docker-compose build

# 启动服务
echo "▶️  启动服务..."
docker-compose up -d

# 等待数据库启动
echo "⏳ 等待数据库启动..."
sleep 10

# 初始化数据库
echo "🗄️  初始化数据库..."
docker-compose exec -T app bash scripts/init_db.sh 2>/dev/null || echo "⚠️  数据库初始化可能在后台进行..."

# 等待应用启动
echo "⏳ 等待应用启动..."
sleep 5

# 健康检查
echo "🔍 健康检查..."
sleep 5

if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
    echo ""
    echo "================================"
    echo "🎉 部署成功！"
    echo "================================"
    echo ""
    echo "📍 访问地址："
    echo "  - 前台: http://localhost:8000/"
    echo "  - 后台: http://localhost:8000/admin/"
    echo "  - API 文档: http://localhost:8000/docs"
    echo "  - 健康检查: http://localhost:8000/health"
    echo ""
    echo "📊 查看日志："
    echo "  docker-compose logs -f"
    echo ""
    echo "🛑 停止服务："
    echo "  docker-compose down"
    echo ""
    echo "♻️  重启服务："
    echo "  docker-compose restart"
    echo ""
else
    echo ""
    echo "⚠️  服务可能还在启动中，请稍后访问"
    echo "   查看日志: docker-compose logs -f"
fi

echo ""
echo "================================"
