# 🚀 快速部署指南

本指南帮助您在 **5 分钟内** 将 MedChina 部署到免费服务器。

## 🎯 推荐方案：Railway（最简单）

### 为什么选择 Railway？
- ✅ 完全免费（每月 $5 额度，足够使用）
- ✅ 自动配置 PostgreSQL 数据库
- ✅ 自动 HTTPS 和域名
- ✅ 一键部署，无需复杂配置
- ✅ 实时日志和监控

---

## 📋 部署步骤（仅需 5 步）

### 第一步：准备 GitHub 仓库

1. 确保您的项目代码已推送到 GitHub
2. 仓库中必须包含：
   - `Dockerfile`（已在项目中）
   - `requirements.txt`（已在项目中）
   - `railway.toml`（已在项目中）
   - `.env.example`（已在项目中）

### 第二步：注册 Railway

1. 访问 [railway.app](https://railway.app)
2. 点击右上角 "Login" 或 "Sign up"
3. 建议使用 **GitHub 登录**（最方便）
4. 首次登录需要授权 Railway 访问您的 GitHub 仓库

### 第三步：创建新项目

1. 登录后，点击 **"New Project"** 按钮
2. 选择 **"Deploy from GitHub repo"**
3. 在列表中找到您的 MedChina 项目并点击

### 第四步：配置环境变量

Railway 会自动识别配置文件，但需要设置以下变量：

1. 点击进入项目，选择 **"Variables"** 标签页
2. 点击 **"New Variable"** 添加以下变量：

```bash
# 必需配置
SECRET_KEY=your-long-random-secret-key-here-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
COZE_INTEGRATION_MODEL_BASE_URL=https://api.coze.com

# 可选配置（如果有 Coze API Key）
COZE_WORKLOAD_IDENTITY_API_KEY=your-coze-api-key-here
```

**生成 SECRET_KEY 的方法：**
- 访问 https://www.uuidgenerator.net/api/guid 生成一个 UUID
- 或使用 Python: `import secrets; print(secrets.token_hex(32))`

### 第五步：开始部署

1. 回到 **"Deployments"** 标签页
2. 点击 **"Deploy"** 按钮（或 "Redeploy"）
3. Railway 会自动：
   - 创建 PostgreSQL 数据库
   - 构建应用
   - 配置环境
   - 分配域名
   - 启动服务

4. 等待约 **3-5 分钟**（首次部署较慢）

---

## ✅ 部署成功

### 如何知道部署成功？

1. 看到 **绿色的 "Active"** 标识
2. 点击生成的 URL（如 `https://medchina-app.up.railway.app`）
3. 能看到页面内容

### 访问地址

Railway 会自动生成以下地址：

- **前台**: `https://medchina-app.up.railway.app/`
- **后台**: `https://medchina-app.up.railway.app/admin/`
- **API 文档**: `https://medchina-app.up.railway.app/docs`

---

## 🎯 下一步操作

### 1. 创建管理员账号

1. 访问后台管理页面：`https://medchina-app.up.railway.app/admin/`
2. 点击注册页面
3. 填写信息创建第一个管理员账号

### 2. 初始化数据

登录后台后，添加以下基础数据：
- ✅ 医生信息
- ✅ 医院信息
- ✅ 病种分类
- ✅ 景点介绍

### 3. 测试功能

- ✅ 测试用户注册登录
- ✅ 测试对话功能
- ✅ 测试预约流程
- ✅ 测试支付流程

---

## 🔧 常见问题速查

### Q1: 部署失败？
**A**: 检查以下几点：
- [ ] Dockerfile 是否正确
- [ ] requirements.txt 是否完整
- [ ] 环境变量是否都设置了
- [ ] 点击 "View logs" 查看详细错误日志

### Q2: 数据库连接失败？
**A**:
- Railway 会自动创建数据库，无需手动配置
- 等待数据库服务启动完成（约 2 分钟）
- 查看日志确认 DATABASE_URL 是否正确

### Q3: 如何查看日志？
**A**: 在 Railway 项目页面：
1. 点击 "Deployments" 标签
2. 点击正在运行的部署
3. 向下滚动查看实时日志

### Q4: 如何更新代码？
**A**: 推送新代码到 GitHub 后：
- Railway 会自动检测并重新部署
- 或手动点击 "Redeploy" 按钮

### Q5: 免费额度用完了？
**A**: Railway 免费额度为 **每月 $5**
- 正常使用完全足够
- 用完会暂停，下月自动恢复
- 可选择升级付费计划

---

## 🎉 恭喜！

您的 MedChina 医疗旅游智能体系统已成功部署！

### 获取支持

- 📖 查看详细文档：[DEPLOYMENT.md](./DEPLOYMENT.md)
- 🐛 遇到问题？在 GitHub 提交 Issue
- 📧 联系技术支持：山东和拾方信息科技有限公司

---

## 📊 其他部署方案

如果 Railway 不适合您，可以尝试：

| 平台 | 推荐度 | 操作难度 | 免费额度 |
|------|--------|---------|---------|
| **Railway** | ⭐⭐⭐⭐⭐ | 简单 | $5/月 |
| **Render** | ⭐⭐⭐⭐ | 简单 | 750小时/月 |
| **Fly.io** | ⭐⭐⭐ | 中等 | $5/月 |
| **本地Docker** | ⭐⭐⭐⭐⭐ | 简单 | 免费 |

查看详细部署方案：[DEPLOYMENT.md](./DEPLOYMENT.md)

---

**祝您使用愉快！走！到中国去看病！**
