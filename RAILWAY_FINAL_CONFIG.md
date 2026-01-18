# Railway 最终配置指南

## ✅ 问题 1：端口配置

### 你的理解是正确的！

**是的，在 "Enter the port your app is listening on" 这里填 `8000`**

### 端口配置步骤：

1. 在 Railway 项目点击 **Settings**
2. 找到 **Networking** 或 **Ports**
3. 在输入框中填写：`8000`
4. 启用公开访问 ✅
5. 保存

---

## 🔧 问题 2：JWT_SECRET_KEY 环境变量

### 为什么没有看到 JWT_SECRET_KEY？

Railway 不会自动创建 `JWT_SECRET_KEY`，你需要**手动添加**它！

### 如何添加 JWT_SECRET_KEY？

#### 步骤 1：生成密钥

在你的本地电脑打开终端，执行：

```bash
openssl rand -hex 32
```

会输出类似这样的随机字符串：
```
a3f8b2c9d4e7f1a6b5c8d2e9f3a7b1c5d8e2f4a7b9c3d6e1f5a8b2c4d7e9f3a
```

**复制这个字符串**

#### 步骤 2：添加到 Railway

1. 在 Railway 项目点击 **Variables**（或 Environment）
2. 点击 **"New Variable"** 或 **"+"** 按钮
3. 在 "Name" 或 "Key" 输入：`JWT_SECRET_KEY`
4. 在 "Value" 粘贴刚才生成的密钥
5. 点击保存或 "Add"

#### 步骤 3：确认 SECRET_KEY 也已设置

用同样的方法确保 `SECRET_KEY` 也已设置：

1. 点击 **"New Variable"**
2. Name: `SECRET_KEY`
3. Value: 再次运行 `openssl rand -hex 32` 生成新的密钥
4. 保存

---

## 📋 完整配置清单

请逐项检查并配置：

### 1. 端口配置（必须）

| 设置项 | 位置 | 值 |
|--------|------|-----|
| Port | Settings → Networking | `8000` |
| Public Access | Settings → Networking | ✅ 启用 |

### 2. 启动命令（必须）

| 设置项 | 位置 | 值 |
|--------|------|-----|
| Start Command | Settings → Start Command | `uvicorn src.main:app --host 0.0.0.0 --port 8000` |

### 3. 环境变量（必须）

| 变量名 | 来源 | 值 |
|--------|------|-----|
| SECRET_KEY | 手动添加 | 用 `openssl rand -hex 32` 生成 |
| JWT_SECRET_KEY | 手动添加 | 用 `openssl rand -hex 32` 生成 |
| DATABASE_URL | Railway 自动提供 | Railway PostgreSQL 自动配置 |

---

## 🚀 配置完成后

### 步骤 1：确认配置

在 Railway 上检查：
- ✅ Port 8000 已配置
- ✅ Start Command 已设置
- ✅ SECRET_KEY 已添加
- ✅ JWT_SECRET_KEY 已添加
- ✅ DATABASE_URL 存在（Railway 自动）

### 步骤 2：重新部署

1. 在 Railway 项目点击 **Redeploy**
2. 等待 3-5 分钟
3. 查看部署日志

### 步骤 3：验证成功

部署成功后，访问：
```
https://your-app.railway.app/health
```

应该返回：
```json
{
  "status": "healthy"
}
```

---

## 🔍 如果还显示 "Could not import module main"

请检查：

1. ✅ Start Command 是否是：
   ```
   uvicorn src.main:app --host 0.0.0.0 --port 8000
   ```
   
   **注意**：是 `src.main` 不是 `main`

2. ✅ Port 是否是 `8000`

3. ✅ 是否点击了 **Redeploy**

---

## 💡 常见问题

### Q: 生成密钥后忘记了怎么办？

A: 没关系，重新生成一个即可。每次部署都可以用新的密钥。

### Q: SECRET_KEY 和 JWT_SECRET_KEY 必须不同吗？

A: 不是必须，但建议使用不同的密钥以增加安全性。

### Q: DATABASE_URL 在哪里？

A: 如果你在 Railway 中添加了 PostgreSQL 服务，Railway 会自动创建 `DATABASE_URL` 环境变量。如果没有添加 PostgreSQL 服务，需要先添加。

---

## 📸 配置截图参考

### Variables 页面应该显示：

```
Key                Value
----------------------------------------
SECRET_KEY         a3f8b2c9d4e7f1a6...
JWT_SECRET_KEY     b4g9c3d7e8f2a5b1...
DATABASE_URL       postgres://...
```

### Settings 页面应该显示：

```
Port: 8000
Start Command: uvicorn src.main:app --host 0.0.0.0 --port 8000
```

---

## 🎯 现在请按顺序操作

### 第一步：配置端口（1 分钟）
- Settings → Networking → Port: `8000`

### 第二步：配置启动命令（1 分钟）
- Settings → Start Command: `uvicorn src.main:app --host 0.0.0.0 --port 8000`

### 第三步：生成并添加密钥（2 分钟）
```bash
# 在本地终端执行
openssl rand -hex 32  # 复制输出作为 SECRET_KEY
openssl rand -hex 32  # 再执行一次作为 JWT_SECRET_KEY
```

### 第四步：添加环境变量（1 分钟）
- Variables → New Variable
- 添加 SECRET_KEY
- 添加 JWT_SECRET_KEY

### 第五步：重新部署（3-5 分钟）
- 点击 Redeploy
- 等待完成

### 第六步：验证（1 分钟）
- 访问健康检查端点
- 确认返回成功

---

## 🆘 需要帮助？

如果完成上述步骤后还有问题，请提供：

1. ✅ 端口已设置为 8000
2. ✅ 启动命令已设置为 `uvicorn src.main:app --host 0.0.0.0 --port 8000`
3. ✅ SECRET_KEY 已添加
4. ✅ JWT_SECRET_KEY 已添加
5. ✅ 已点击 Redeploy
6. ❓ **最新的错误日志**

把最新的错误信息发给我！

---

**出品方**: 山东和拾方信息科技有限公司
**项目**: MedChina - 走！到中国去看病！
