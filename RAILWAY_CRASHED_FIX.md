# Railway 应用崩溃（Crashed）问题排查

## 问题分析

```
✅ Redeploy 成功
→ 很快显示 Crashed
→ 有 Restart 选项
```

这说明：
- ✅ **构建成功**（requirements.txt 修复成功，依赖安装正常）
- ❌ **应用启动后崩溃**（运行时错误）

---

## 🔍 立即查看崩溃原因

### 步骤 1：查看运行日志

1. 在 Railway 项目页面，点击 **"Deployments"**
2. 找到显示 **"Crashed"** 的部署
3. 点击进入详情
4. 查看 **"Logs"** 或 **"Console"** 标签
5. **复制最后的错误信息**发给我

**关键信息点**：
```
[复制最后一行开始的错误信息]
例如：KeyError: SECRET_KEY
      或：Database connection failed
      或：ModuleNotFoundError
```

---

## 🚨 最常见的崩溃原因

### 原因 1: 环境变量缺失（概率最高：⭐⭐⭐⭐⭐）

**错误信息**：
```
KeyError: SECRET_KEY
或
KeyError: JWT_SECRET_KEY
```

**解决方法**：
1. 在 Railway 项目点击 **"Variables"**
2. 添加以下变量：

```
SECRET_KEY=<用 openssl rand -hex 32 生成>
JWT_SECRET_KEY=<用 openssl rand -hex 32 生成>
```

**生成密钥**：
```bash
openssl rand -hex 32
```

---

### 原因 2: 端口未配置（概率：⭐⭐⭐⭐）

**错误信息**：
```
Port 8000 is not exposed
或
Network unreachable
```

**解决方法**：
1. 在 Railway 项目点击 **"Settings"**
2. 找到 **"Networking"** 或 **"Ports"**
3. 添加端口：`8000`
4. 启用公开访问 ✅
5. 点击 **"Redeploy"**

---

### 原因 3: 数据库连接失败（概率：⭐⭐⭐）

**错误信息**：
```
Connection refused
或
Authentication failed
或
DATABASE_URL not set
```

**解决方法**：
1. 在 Railway 项目点击 **"Variables"**
2. 确认 `DATABASE_URL` 存在
3. Railway PostgreSQL 会自动提供这个变量
4. 如果没有，在 Railway 添加一个 PostgreSQL 服务

**添加 PostgreSQL 服务**：
1. 在 Railway 项目点击 **"New Service"**
2. 选择 **"PostgreSQL"**
3. 等待创建完成
4. Railway 会自动配置 `DATABASE_URL`

---

### 原因 4: 启动命令错误（概率：⭐⭐）

**错误信息**：
```
Command not found: uvicorn
或
Module src.main not found
```

**解决方法**：
1. 在 Railway 项目点击 **"Settings"**
2. 找到 **"Start Command"**
3. 设置为：
   ```
   uvicorn src.main:app --host 0.0.0.0 --port 8000
   ```

---

## 🔧 快速修复步骤

### 第一步：检查环境变量（最重要！）

在 Railway 项目中：

1. 点击 **"Variables"**
2. 确认有这三个变量：
   - `SECRET_KEY` ✅
   - `DATABASE_URL` ✅
   - `JWT_SECRET_KEY` ✅

3. 如果缺少，立即添加：
   ```
   SECRET_KEY=<生成的随机密钥>
   JWT_SECRET_KEY=<生成的随机密钥>
   ```

**生成密钥**：
```bash
# 在本地终端执行
openssl rand -hex 32
# 会输出类似：a1b2c3d4e5f6...
# 复制这个值作为 SECRET_KEY
# 再执行一次生成 JWT_SECRET_KEY
```

### 第二步：检查端口配置

1. 点击 **"Settings"** → **"Networking"**
2. 确认有端口：`8000`
3. 确认已启用公开访问

### 第三步：添加 PostgreSQL（如果还没有）

1. 在项目页面点击 **"New Service"**
2. 选择 **"PostgreSQL"**
3. 等待创建完成
4. Railway 会自动配置 `DATABASE_URL`

### 第四步：重新部署

1. 在项目页面点击 **"Redeploy"**
2. 等待构建完成
3. 观察是否还崩溃

---

## 🌐 关于 Custom Domain

### 什么是 Custom Domain？

**Custom Domain（自定义域名）** 是让你的应用使用自己的域名，而不是 Railway 提供的临时域名。

### 需要配置吗？

**答案：测试阶段不需要！**

- ❌ **不需要配置** 如果只是测试应用
- ✅ **需要配置** 如果要正式上线使用

### 如何配置 Custom Domain？

**当你需要时，按以下步骤操作**：

#### 第一步：拥有域名

你需要有自己的域名，例如：
- `medchina.com`
- `your-domain.com`
- `subdomain.example.com`

#### 第二步：在 Railway 添加自定义域名

1. 在 Railway 项目点击 **"Settings"**
2. 找到 **"Domains"** 或 **"Custom Domain"**
3. 点击 **"Add Domain"**
4. 输入你的域名，例如：`medchina.yourdomain.com`
5. Railway 会显示 DNS 配置信息

#### 第三步：配置 DNS

 Railway 会给你两个 DNS 记录，例如：

```
Type: CNAME
Name: medchina
Value: medchina-production.up.railway.app

或

Type: A
Name: medchina
Value: 123.45.67.89
```

到你的域名注册商（阿里云、腾讯云、GoDaddy 等）添加这个 DNS 记录。

#### 第四步：等待生效

DNS 生效需要：
- 快：5-10 分钟
- 慢：最长 24 小时

#### 第五步：启用 HTTPS

DNS 生效后，在 Railway 上点击 **"Generate Certificate"** 自动启用 HTTPS。

### 示例

假设你有域名 `example.com`，想用 `medchina.example.com`：

1. 在 Railway 添加域名：`medchina.example.com`
2. Railway 给你 DNS 记录：
   ```
   Type: CNAME
   Name: medchina
   Value: medchina-production.up.railway.app
   ```
3. 到域名注册商添加这个 CNAME 记录
4. 等待 10 分钟
5. 在 Railway 点击 "Generate Certificate"
6. 完成！现在可以访问 `https://medchina.example.com`

---

## 📋 现在请你做

### 1. 查看崩溃日志（最重要！）

```
[请复制 Railway 上最后的错误信息发给我]
```

### 2. 检查配置

| 检查项 | 状态 |
|--------|------|
| SECRET_KEY | ☐ 已设置  ☐ 未设置 |
| JWT_SECRET_KEY | ☐ 已设置  ☐ 未设置 |
| DATABASE_URL | ☐ 已设置  ☐ 未设置 |
| Port 8000 | ☐ 已配置  ☐ 未配置 |
| PostgreSQL 服务 | ☐ 已添加  ☐ 未添加 |

### 3. 告诉我

- 你看到了什么错误信息？
- 上面 5 个检查项哪些是 ☐ 未设置/未配置？

---

## 🆘 帮助我帮你解决

把以下信息发给我：

1. **错误日志**（复制文字）
2. **配置检查**（上面表格的结果）
3. **截图**（如果方便）

我会立即给出精确的解决方案！

---

**出品方**: 山东和拾方信息科技有限公司
**项目**: MedChina - 走！到中国去看病！
