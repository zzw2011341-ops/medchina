# 🚀 Railway 部署速查卡片

> 打印此页面，按照步骤操作，5分钟完成部署！

---

## 📋 准备清单（部署前）

```bash
□ GitHub 账号已注册
□ MedChina 代码已推送到 GitHub
□ 仓库包含：Dockerfile、requirements.txt、railway.toml、.env.example
□ 生成了 SECRET_KEY（64位随机字符串）
```

---

## ⚡ 快速部署（10步）

### 第 1 步：访问 Railway
```
https://railway.app
```
→ 点击右上角 **"Login"** → **"Continue with GitHub"** → **"Authorize railwayapp"**

---

### 第 2 步：创建新项目
→ 点击 **"+ New Project"** → 点击 **"Deploy from GitHub repo"**

---

### 第 3 步：选择仓库
→ 在列表中找到您的 MedChina 仓库
→ 点击仓库名称（复选框变为 ☑）
→ 点击右下角 **"Next"** 按钮

**如果找不到仓库？**
→ 点击 **"Configure GitHub"**
→ 勾选您的 MedChina 仓库
→ 点击 **"Save"**
→ 刷新页面，重新选择

---

### 第 4 步：配置项目

| 配置项 | 填写内容 |
|--------|---------|
| **Project Name** | `medchina-app` |
| **Region** | `US East (Virginia)` 或 `Asia Northeast (Tokyo)` |
| **Root Directory** | `/` (不要修改) |
| **Dockerfile Path** | `./Dockerfile` (不要修改) |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` (不要修改) |

→ 检查确认无误
→ **先不要点击 Deploy！**

---

### 第 5 步：配置环境变量

在配置页面底部找到 **"Environment Variables"** 区域
→ 点击 **"+ New Variable"**

按顺序添加以下变量：

#### 变量 1：SECRET_KEY
```
Name:   SECRET_KEY
Value:  <粘贴您的64位随机字符串>
```

**生成 SECRET_KEY：**
```bash
# 方法1：访问 https://www.uuidgenerator.net
# 方法2：Python
import secrets; print(secrets.token_hex(32))
```

---

#### 变量 2：ALGORITHM
```
Name:   ALGORITHM
Value:  HS256
```

---

#### 变量 3：ACCESS_TOKEN_EXPIRE_MINUTES
```
Name:   ACCESS_TOKEN_EXPIRE_MINUTES
Value:  1440
```

---

#### 变量 4：COZE_INTEGRATION_MODEL_BASE_URL
```
Name:   COZE_INTEGRATION_MODEL_BASE_URL
Value:  https://api.coze.com
```

---

#### 变量 5：COZE_WORKLOAD_IDENTITY_API_KEY（可选）
```
Name:   COZE_WORKLOAD_IDENTITY_API_KEY
Value:  <您的 Coze API Key，如没有则不填>
```

---

### 第 6 步：开始部署

→ 点击页面右下角的 **"Deploy"** 按钮
→ **等待 3-5 分钟**

**正在部署时：**
- 不要关闭浏览器
- 可以滚动查看日志
- 看到 "Active" 状态即为成功

---

### 第 7 步：验证部署

部署成功后，页面会显示访问 URL：

```
📍 URL: https://medchina-app-up.railway.app
```

**依次测试以下地址：**

| 地址 | 说明 | 预期结果 |
|------|------|---------|
| `https://xxx.up.railway.app/` | 前台页面 | 看到首页内容 |
| `https://xxx.up.railway.app/admin/` | 后台页面 | 看到登录页面 |
| `https://xxx.up.railway.app/docs` | API文档 | 看到Swagger UI |
| `https://xxx.up.railway.app/health` | 健康检查 | 显示 `{"status": "healthy"}` |

---

### 第 8 步：初始化数据库

**方法 A：使用 Railway Console（推荐）**

1. 在项目页面，点击 **"Deployments"** 标签
2. 点击正在运行的部署
3. 在右侧面板，找到 **"Console"** 区域
4. 点击 **"New Shell"**
5. 等待 Shell 启动（提示符为 `/app $`）
6. 执行：
   ```bash
   bash /app/scripts/init_db.sh
   ```
7. 看到 "Database initialization completed!" 表示成功

---

**方法 B：通过 API（如果 Console 不好用）**

1. 访问健康检查：
   ```
   https://xxx.up.railway.app/health
   ```
2. 应用会自动创建表（如果配置了）
3. 访问 `/docs` 测试创建用户 API

---

### 第 9 步：创建管理员账号

1. 访问后台注册页面：
   ```
   https://xxx.up.railway.app/admin/register/
   ```

2. 填写信息：
   ```
   Username: admin
   Email:    your-email@example.com
   Password: <设置强密码>
   Confirm:  <再次输入密码>
   ```

3. 点击 **"Register"**

4. 注册成功后自动登录后台

---

### 第 10 步：添加基础数据

在后台依次添加：

| 菜单项 | 操作 |
|--------|------|
| **病种管理** | 添加 3-5 个病种（心血管、神经科、骨科等） |
| **医生管理** | 添加 5-10 位医生 |
| **医院管理** | 添加 3-5 家医院 |
| **景点管理** | 添加 5-10 个景点 |

---

## ✅ 成功标志

完成以上 10 步后，您应该看到：

- [ ] Railway 显示应用状态为 **Active** ✅
- [ ] 能访问前台页面 ✅
- [ ] 能访问后台管理 ✅
- [ ] 数据库表已创建 ✅
- [ ] 管理员账号已创建 ✅
- [ ] 基础数据已添加 ✅

---

## 📍 重要链接保存

**Railway 项目地址：**
```
https://railway.app/project/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**应用访问地址：**
```
前台:  https://medchina-app.up.railway.app/
后台:  https://medchina-app.up.railway.app/admin/
API:   https://medchina-app.up.railway.app/docs
```

**Railway 文档：**
```
https://docs.railway.app
```

---

## 🆘 快速故障排除

| 问题 | 解决方法 |
|------|---------|
| 找不到仓库 | 点击 "Configure GitHub"，勾选仓库，保存 |
| Dockerfile not found | 检查文件名（Dockerfile，不是 dockerfile），提交到 GitHub |
| requirements.txt not found | 运行 `pip freeze > requirements.txt`，提交到 GitHub |
| 数据库连接失败 | 检查 Variables 中是否有 DATABASE_URL，重启应用 |
| 访问 404 | 查看日志，检查应用是否正常启动 |
| 部署失败 | 查看 "Logs" 区域，阅读错误信息，参考完整文档 |

---

## 🔄 如何更新代码

**自动更新（推荐）：**
```bash
# 本地修改代码
git add .
git commit -m "更新代码"
git push origin main
# Railway 会自动检测并重新部署
```

**手动更新：**
→ Railway 项目 → Deployments → 点击 **"Redeploy"**

---

## 📊 常用命令速查

### 本地开发
```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
python -m uvicorn main:app --reload

# 运行测试
pytest tests/
```

### Docker 本地部署
```bash
# 复制配置
cp .env.example .env
# 编辑 .env 文件

# 启动服务
bash scripts/deploy.sh

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### Railway 命令
```bash
# 安装 CLI
npm install -g @railway/cli

# 登录
railway login

# 查看日志
railway logs

# 打开项目
railway open

# 重启应用
railway up
```

---

## 📞 获取帮助

- **详细文档**：`DETAILED_DEPLOYMENT_GUIDE.md`
- **常见问题**：`DEPLOYMENT.md` - "常见问题解决" 部分
- **项目仓库**：您的 GitHub 仓库
- **技术支持**：山东和拾方信息科技有限公司

---

## 💡 提示

1. **保存 SECRET_KEY**：将其保存在安全的地方
2. **定期备份**：定期导出数据库备份
3. **监控日志**：定期查看应用日志，及时发现异常
4. **测试功能**：每次更新后测试核心功能
5. **更新依赖**：定期更新依赖，保持安全性

---

## 🎉 完成部署！

恭喜您完成 MedChina 系统的部署！

**走！到中国去看病！** 🏥✈️🇨🇳

---

**打印提示：** 建议打印此页面，在部署过程中按步骤操作
