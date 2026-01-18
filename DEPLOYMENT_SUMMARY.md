# 📦 MedChina 部署文件总结

## ✅ 已创建的部署文件

### 核心部署文件

1. **Dockerfile** - Docker 镜像构建文件
   - 基于 Python 3.11-slim
   - 安装所有依赖
   - 配置工作目录和环境
   - 暴露 8000 端口

2. **docker-compose.yml** - 本地 Docker 编排文件
   - 包含 PostgreSQL 数据库服务
   - 包含 FastAPI 应用服务
   - 自动配置网络和存储卷
   - 健康检查配置

3. **.dockerignore** - Docker 构建忽略文件
   - 优化构建速度
   - 减小镜像体积

### 云平台配置文件

4. **deployment/render.yaml** - Render 平台配置
   - Web 服务配置
   - PostgreSQL 数据库配置
   - 环境变量配置
   - 存储挂载配置

5. **deployment/railway.toml** - Railway 平台配置
   - Docker 构建配置
   - 环境变量配置
   - 数据库集成
   - 健康检查配置

6. **deployment/fly.toml** - Fly.io 平台配置
   - 区域配置
   - 健康检查配置
   - 资源限制配置
   - HTTPS 配置

### 脚本文件

7. **scripts/init_db.sh** - 数据库初始化脚本
   - 等待数据库就绪
   - 运行数据库迁移
   - 创建数据库表

8. **scripts/health_check.py** - 健康检查脚本
   - 检查应用状态
   - 检查数据库连接
   - 输出健康报告

9. **scripts/deploy.sh** - 本地快速部署脚本
   - 环境检查
   - 自动构建和启动
   - 健康检查
   - 访问地址提示

### 文档文件

10. **DEPLOYMENT.md** - 详细部署文档
    - 4 种部署方案详解
    - 环境配置说明
    - 常见问题解答
    - 故障排查指南

11. **QUICKSTART.md** - 快速部署指南
    - 5 分钟快速部署
    - Railway 平台详细步骤
    - 常见问题速查

12. **.env.example** - 环境变量模板
    - 所有必需的环境变量
    - 示例配置值
    - 配置说明

---

## 🚀 如何使用这些文件

### 方案一：部署到 Railway（推荐）

**适合人群**：新手、快速测试、个人项目

**步骤**：
1. 访问 [railway.app](https://railway.app)
2. 点击 "New Project" → "Deploy from GitHub repo"
3. 选择您的 MedChina 仓库
4. 配置环境变量（参考 QUICKSTART.md）
5. 点击 "Deploy"
6. 等待 3-5 分钟，访问生成的 URL

**参考文档**：[QUICKSTART.md](./QUICKSTART.md)

---

### 方案二：部署到 Render

**适合人群**：需要免费时长、长时间运行

**步骤**：
1. 注册 [render.com](https://render.com)
2. 创建 PostgreSQL 数据库服务
3. 创建 Web 服务（选择 Docker）
4. 配置环境变量
5. 等待部署完成

**参考文档**：[DEPLOYMENT.md](./DEPLOYMENT.md) - 方案一

---

### 方案三：部署到 Fly.io

**适合人群**：需要全球部署、性能要求高

**步骤**：
1. 安装 Fly CLI
2. 运行 `flyctl launch`
3. 配置环境变量
4. 创建数据库
5. 运行 `flyctl deploy`

**参考文档**：[DEPLOYMENT.md](./DEPLOYMENT.md) - 方案三

---

### 方案四：本地 Docker 部署

**适合人群**：本地开发、测试、演示

**步骤**：
1. 确保已安装 Docker 和 Docker Compose
2. 复制 `.env.example` 为 `.env` 并编辑配置
3. 运行 `bash scripts/deploy.sh`
4. 访问 http://localhost:8000

**参考文档**：[DEPLOYMENT.md](./DEPLOYMENT.md) - 方案四

---

## 📋 部署前检查清单

### 代码准备
- [x] 所有代码已推送到 GitHub
- [x] requirements.txt 包含所有依赖
- [x] Dockerfile 配置正确
- [x] .env.example 包含所有环境变量模板

### 环境变量
- [ ] SECRET_KEY（必需）
- [ ] DATABASE_URL（云平台自动配置，本地需配置）
- [ ] ALGORITHM（默认 HS256）
- [ ] ACCESS_TOKEN_EXPIRE_MINUTES（默认 1440）
- [ ] COZE_WORKLOAD_IDENTITY_API_KEY（如果有）
- [ ] COZE_INTEGRATION_MODEL_BASE_URL（默认 https://api.coze.com）

### 数据库
- [ ] 云平台：数据库会自动创建
- [ ] 本地：需要确保 PostgreSQL 已安装或使用 docker-compose

---

## 🔧 部署后操作

### 1. 健康检查
```bash
# 本地
curl http://localhost:8000/health

# 云平台
curl https://your-domain/health
```

### 2. 初始化数据
```bash
# Docker 环境
docker-compose exec app bash scripts/init_db.sh

# 云平台（在平台终端中执行）
python scripts/init_db.sh
```

### 3. 创建管理员账号
1. 访问 `/admin/`
2. 点击注册
3. 填写管理员信息

### 4. 添加基础数据
- 医生信息
- 医院信息
- 病种分类
- 景点介绍

### 5. 测试功能
- [ ] 用户注册登录
- [ ] AI 对话
- [ ] 预约功能
- [ ] 支付功能
- [ ] 后台管理

---

## 📊 部署平台对比

| 特性 | Railway | Render | Fly.io | 本地Docker |
|------|---------|--------|--------|-----------|
| **免费额度** | $5/月 | 750小时/月 | $5/月 | 免费 |
| **自动数据库** | ✅ | ✅ | ❌ | ✅ |
| **自动HTTPS** | ✅ | ✅ | ✅ | ❌ |
| **冷启动** | 快 | 慢(30-60s) | 快 | 无 |
| **难度** | 简单 | 简单 | 中等 | 简单 |
| **推荐指数** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🆘 常见问题

### Q1: 部署失败怎么办？
**A**:
1. 查看平台日志（GitHub Actions 或平台控制台）
2. 检查 Dockerfile 语法
3. 确认 requirements.txt 无错误
4. 检查环境变量配置

### Q2: 应用启动后无法访问？
**A**:
1. 等待 1-2 分钟（首次启动较慢）
2. 检查健康检查端点：`/health`
3. 查看应用日志
4. 确认防火墙设置

### Q3: 数据库连接失败？
**A**:
1. 确认 DATABASE_URL 格式正确
2. 检查数据库服务是否启动
3. 验证用户名密码
4. 查看数据库日志

### Q4: 如何更新应用？
**A**:
- **自动**：推送代码到 GitHub，云平台自动重新部署
- **手动**：在平台控制台点击 "Redeploy" 按钮
- **本地**：运行 `docker-compose up -d --build`

### Q5: 如何查看日志？
**A**:
- **Railway**: Project → Logs tab
- **Render**: Dashboard → Logs
- **Fly.io**: `flyctl logs`
- **Docker**: `docker-compose logs -f`

---

## 📞 获取帮助

- **完整文档**：[DEPLOYMENT.md](./DEPLOYMENT.md)
- **快速开始**：[QUICKSTART.md](./QUICKSTART.md)
- **问题反馈**：在 GitHub 提交 Issue
- **技术支持**：山东和拾方信息科技有限公司

---

## 🎉 开始部署吧！

选择一个平台，按照对应的文档步骤操作，几分钟内即可完成部署。

**推荐新手使用 Railway**，操作最简单，详见 [QUICKSTART.md](./QUICKSTART.md)

---

**祝您部署顺利！走！到中国去看病！**
