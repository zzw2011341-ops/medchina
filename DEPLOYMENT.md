# MedChina 部署指南

本指南将帮助您将 MedChina 医疗旅游智能体系统部署到免费服务器上。

## 📋 目录

- [快速开始](#快速开始)
- [部署平台选择](#部署平台选择)
- [部署方案](#部署方案)
  - [方案一：Render（推荐新手）](#方案一-render推荐新手)
  - [方案二：Railway（推荐）](#方案二-railway推荐)
  - [方案三：Fly.io（功能强大）](#方案三-flyio功能强大)
  - [方案四：本地 Docker 部署](#方案四本地-docker-部署)
- [环境配置](#环境配置)
- [数据库初始化](#数据库初始化)
- [常见问题](#常见问题)

## 🚀 快速开始

### 前置条件

1. 一个 GitHub 账号
2. 本地安装 Git
3. （可选）已申请 Coze API Key

### 最简部署步骤（推荐使用 Railway）

1. 访问 https://railway.app 并登录
2. 点击 "New Project" → "Deploy from GitHub repo"
3. 选择您的 MedChina 仓库
4. Railway 会自动检测 Dockerfile 并开始部署
5. 等待约 3-5 分钟，部署完成
6. 点击生成的 URL 访问您的应用

## 🎯 部署平台选择

| 平台 | 免费额度 | 数据库 | 自定义域名 | 难度 | 推荐指数 |
|------|---------|--------|----------|------|---------|
| **Railway** | $5/月额度 | ✅ 免费 PostgreSQL | ✅ | ⭐ | ⭐⭐⭐⭐⭐ |
| **Render** | 750小时/月 | ✅ 免费实例 | ✅ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Fly.io** | $5/月额度 | ✅ 挂载卷需付费 | ✅ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Vercel** | 无限制 | ❌ 需外部数据库 | ✅ | ⭐ | ⭐⭐⭐ |

## 📦 部署方案

---

## 方案一：Render（推荐新手）

### 优点
- 完全免费（750 小时/月）
- 内置 PostgreSQL 数据库
- 自动 HTTPS
- 操作简单

### 缺点
- 冷启动较慢（首次访问需 30-60 秒）
- 免费版限制较多

### 部署步骤

#### 1. 注册并登录 Render
访问 https://render.com 注册账号（建议使用 GitHub 登录）

#### 2. 创建数据库服务
1. 点击 Dashboard → "New +"
2. 选择 "PostgreSQL"
3. 填写配置：
   - Name: `medchina-db`
   - Database: `medchina`
   - User: `meduser`
   - Region: `Oregon (US West)`
4. 点击 "Create Database"
5. 等待数据库创建完成（约 2-3 分钟）
6. 记下 `Internal Database URL`

#### 3. 创建 Web 服务
1. 点击 "New +" → "Web Service"
2. 连接您的 GitHub 仓库
3. 配置服务：
   - Name: `medchina-web`
   - Region: `Oregon (US West)`
   - Branch: `main`
   - Runtime: `Docker`
   - Docker Context: `/`
   - Dockerfile Path: `./Dockerfile`

4. 配置环境变量（从数据库复制）：
   ```
   DATABASE_URL=<从数据库服务复制的 Internal Database URL>
   SECRET_KEY=<生成一个随机字符串>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   COZE_WORKLOAD_IDENTITY_API_KEY=<您的 Coze API Key>
   COZE_INTEGRATION_MODEL_BASE_URL=https://api.coze.com
   ```

5. 点击 "Create Web Service"
6. 等待部署完成（约 5-10 分钟）

#### 4. 访问应用
- 部署成功后，Render 会提供一个 HTTPS URL
- 访问: `https://medchina-web.onrender.com`

---

## 方案二：Railway（推荐）

### 优点
- $5/月免费额度（够用）
- 自动配置数据库
- 实时日志
- 性能较好

### 缺点
- 免费额度用完会暂停服务

### 部署步骤

#### 1. 注册并登录 Railway
访问 https://railway.app 注册账号

#### 2. 创建新项目
1. 点击 "New Project" → "Deploy from GitHub repo"
2. 选择您的 MedChina 仓库
3. Railway 会自动识别 Dockerfile 和 `railway.toml`

#### 3. 配置环境变量
在项目设置中添加以下环境变量：

```bash
SECRET_KEY=<生成随机字符串>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
COZE_WORKLOAD_IDENTITY_API_KEY=<您的 Coze API Key>
COZE_INTEGRATION_MODEL_BASE_URL=https://api.coze.com
```

Railway 会自动配置 DATABASE_URL。

#### 4. 部署
点击 "Deploy"，Railway 会自动：
- 创建 PostgreSQL 数据库
- 构建并部署应用
- 配置域名和 HTTPS

#### 5. 访问应用
- 部署完成后，Railway 会提供访问 URL
- 格式: `https://medchina-app.up.railway.app`

---

## 方案三：Fly.io（功能强大）

### 优点
- 全球部署
- 更好的性能
- 支持 Docker

### 缺点
- 配置较复杂
- 数据库需单独配置

### 部署步骤

#### 1. 安装 Fly CLI
```bash
# macOS
brew install flyctl

# Linux
curl -L https://fly.io/install.sh | sh

# Windows (使用 PowerShell)
iwr https://fly.io/install.ps1 -useb | iex
```

#### 2. 登录 Fly.io
```bash
flyctl auth login
```

#### 3. 启动应用
```bash
# 在项目根目录执行
flyctl launch
```

按照提示完成配置，或使用预配置的 `fly.toml`。

#### 4. 配置环境变量
```bash
flyctl secrets set SECRET_KEY="your-secret-key"
flyctl secrets set COZE_WORKLOAD_IDENTITY_API_KEY="your-api-key"
```

#### 5. 创建数据库
```bash
flyctl postgres create --name medchina-db
flyctl postgres attach --app medchina-app medchina-db
```

#### 6. 部署
```bash
flyctl deploy
```

---

## 方案四：本地 Docker 部署

### 适用场景
- 本地开发测试
- 演示环境
- 服务器自托管

### 部署步骤

#### 1. 安装 Docker 和 Docker Compose
访问 https://docs.docker.com/get-docker/ 下载安装

#### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入必要配置
```

#### 3. 启动服务
```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

#### 4. 初始化数据库
```bash
docker-compose exec app bash /app/scripts/init_db.sh
```

#### 5. 访问应用
- 前台: http://localhost:8000
- 后台管理: http://localhost:8000/admin/
- API 文档: http://localhost:8000/docs

---

## ⚙️ 环境配置

### 必需的环境变量

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `DATABASE_URL` | PostgreSQL 数据库连接字符串 | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | JWT 签名密钥 | `your-long-random-secret-key-here` |
| `ALGORITHM` | 加密算法 | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token 过期时间（分钟） | `1440` (24小时) |
| `COZE_WORKLOAD_IDENTITY_API_KEY` | Coze API 密钥 | 从 Coze 平台获取 |
| `COZE_INTEGRATION_MODEL_BASE_URL` | Coze API 地址 | `https://api.coze.com` |

### 生成 SECRET_KEY
```bash
# Linux/Mac
openssl rand -hex 32

# Python
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🗄️ 数据库初始化

首次部署后，需要创建数据库表：

### 方法一：使用初始化脚本
```bash
# Docker 环境
docker-compose exec app bash scripts/init_db.sh

# Railway（在 Railway Console 的终端中执行）
python scripts/init_db.sh
```

### 方法二：手动运行迁移
```bash
# 安装 Alembic（如果使用）
pip install alembic

# 运行迁移
alembic upgrade head
```

### 方法三：通过 API 创建
访问健康检查端点，应用会自动创建表：
```bash
curl http://your-domain/health
```

---

## 🔍 常见问题

### Q1: 部署后无法访问？
**A**: 检查以下几点：
1. 服务是否正常运行（查看平台日志）
2. 防火墙是否开放 8000 端口
3. 域名 DNS 解析是否正确

### Q2: 数据库连接失败？
**A**: 确认：
1. DATABASE_URL 格式正确
2. 数据库服务已启动
3. 网络连接正常

### Q3: 如何查看日志？
**平台日志查看方式：**
- **Render**: Dashboard → Logs
- **Railway**: Project → Logs tab
- **Fly.io**: `flyctl logs`
- **Docker**: `docker-compose logs -f`

### Q4: 如何更新应用？
**自动部署：**
1. 推送代码到 GitHub
2. 平台会自动检测并重新部署

**手动部署：**
```bash
# Fly.io
flyctl deploy

# Docker
docker-compose up -d --build
```

### Q5: 免费额度用完了怎么办？
**A**: 免费平台每月有限额：
- **Render**: 750 小时/月（约每天 24 小时）
- **Railway**: $5/月
- **Fly.io**: $5/月

用完会自动暂停，下月重置，或升级付费。

### Q6: 如何添加自定义域名？
**各平台配置：**
- **Render**: Settings → Custom Domains
- **Railway**: Settings → Networking
- **Fly.io**: `flyctl certs add your-domain.com`

---

## 📞 获取帮助

- **文档**: 查看项目 README.md
- **问题反馈**: 在 GitHub 提交 Issue
- **技术支持**: 联系山东和拾方信息科技有限公司

---

## 🎉 部署成功后

### 访问地址

1. **用户端**: `https://your-domain/`
2. **后台管理**: `https://your-domain/admin/`
3. **API 文档**: `https://your-domain/docs`

### 默认管理员账号

首次使用需要创建管理员账号，访问 `/admin/register/` 注册：
- 用户名: `admin`
- 密码: （自定义）
- Email: （你的邮箱）

### 下一步

1. 登录后台管理系统
2. 添加医生、医院、病种数据
3. 配置景点信息
4. 设置财务管理参数
5. 开始接待用户咨询

---

**祝您部署顺利！如有问题，请随时反馈。**
