#!/bin/bash

# 数据库初始化脚本
# 用于在首次部署时创建数据库表

set -e

echo "Waiting for database to be ready..."
until pg_isready -h db -U meduser -d medchina; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "Database is ready, running migrations..."
cd /app

# 如果有 alembic 迁移，使用 alembic
if [ -d "alembic" ]; then
    echo "Running Alembic migrations..."
    alembic upgrade head
else
    echo "No Alembic migrations found, creating tables from models..."
    # 直接从模型创建表（如果有初始化脚本）
    python -c "
from storage.database.shared.model import Base, engine
print('Creating database tables...')
Base.metadata.create_all(bind=engine)
print('Database tables created successfully!')
"
fi

echo "Database initialization completed!"
