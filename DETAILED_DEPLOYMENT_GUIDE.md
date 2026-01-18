# 🎯 Railway 超详细部署指南

> 按照本文档，您可以**零经验**完成部署，每一步都有详细说明和截图位置提示

---

## 📋 目录

1. [准备工作](#准备工作)
2. [第一步：注册 Railway 账号](#第一步注册-railway-账号)
3. [第二步：连接 GitHub 仓库](#第二步连接-github-仓库)
4. [第三步：配置项目](#第三步配置项目)
5. [第四步：配置环境变量](#第四步配置环境变量)
6. [第五步：部署应用](#第五步部署应用)
7. [第六步：验证部署](#第六步验证部署)
8. [第七步：初始化数据](#第七步初始化数据)
9. [常见问题解决](#常见问题解决)
10. [如何更新应用](#如何更新应用)

---

## 📦 准备工作

在开始之前，请确保您已完成以下准备：

### ✅ 必须准备的事项

1. **GitHub 账号**
   - 访问 https://github.com 注册（如果还没有）
   - 必须已登录 GitHub

2. **MedChina 代码已推送到 GitHub**
   - 代码必须在 GitHub 仓库中
   - 仓库必须包含这些文件：
     - `Dockerfile`
     - `requirements.txt`
     - `railway.toml`
     - `.env.example`
   
3. **一个用于生成密钥的工具**
   - 推荐使用在线工具：https://www.uuidgenerator.net
   - 或使用 Python：`import secrets; print(secrets.token_hex(32))`

### 📝 检查您的 GitHub 仓库

在开始之前，确认您的仓库包含这些文件：

```bash
# 在您的项目根目录执行
ls -la | grep -E "(Dockerfile|requirements|railway|env)"
```

应该看到：
- `Dockerfile` ✅
- `requirements.txt` ✅
- `railway.toml` ✅
- `.env.example` ✅

如果缺少这些文件，请先确保代码已提交并推送到 GitHub：

```bash
git add .
git commit -m "准备部署文件"
git push origin main
```

---

## 第一步：注册 Railway 账号

### 1.1 访问 Railway 官网

打开浏览器，访问：
```
https://railway.app
```

**页面说明：**
- 页面顶部有 "Login" 和 "Sign up" 按钮
- 页面中部有 Railway 的介绍和功能说明

### 1.2 注册账号

#### 方式 A：使用 GitHub 注册（推荐）⭐

1. 点击页面右上角的 **"Login"** 按钮
2. 页面跳转到登录页面
3. 点击 **"Continue with GitHub"** 按钮
   - 位置：登录表单下方，有一个 GitHub 图标的蓝色按钮
4. GitHub 会弹出授权窗口
5. 点击 **"Authorize railwayapp"** 按钮
   - 这会让 Railway 访问您的 GitHub 仓库
6. 授权成功后，自动跳转到 Railway Dashboard

#### 方式 B：使用邮箱注册

1. 点击页面右上角的 **"Sign up"** 按钮
2. 填写注册表单：
   - **Full Name**: 填写您的姓名（如：Zhang San）
   - **Email Address**: 填写您的邮箱
   - **Password**: 设置密码（至少8位）
3. 点击 **"Create Account"** 按钮
4. 检查邮箱，点击验证邮件中的链接
5. 验证成功后，自动跳转到 Railway Dashboard

### 1.3 首次登录后的页面

登录成功后，您会看到 Railway 的 Dashboard：

**页面布局说明：**
```
┌─────────────────────────────────────┐
│  Railway Logo         + New Project │  ← 顶部导航栏
├─────────────────────────────────────┤
│                                     │
│   🚀 Start a new project            │
│                                     │
│   [ Deploy from GitHub repo ]       │  ← 重点：点击这里
│   [ Deploy from a CLI template ]    │
│   [ Create a new project ]          │
│                                     │
└─────────────────────────────────────┘
```

**重要提示：**
- 如果您之前创建过项目，Dashboard 会显示项目列表
- 点击左上角的 **"+ New Project"** 按钮也可以创建新项目

---

## 第二步：连接 GitHub 仓库

### 2.1 开始创建新项目

在 Railway Dashboard 页面：

1. 找到 **"Start a new project"** 区域
2. 点击 **"Deploy from GitHub repo"** 按钮
   - 这个按钮上有 GitHub 的图标
   - 通常在页面中央最显眼的位置

### 2.2 选择 GitHub 仓库

点击后会进入仓库选择页面：

**页面说明：**
```
┌─────────────────────────────────────┐
│  < Back   Select GitHub Repository  │
├─────────────────────────────────────┤
│                                     │
│  🔍 Search repositories...          │  ← 搜索框
│                                     │
│  Your Repositories                  │
│  ──────────────────────────────     │
│  □ my-project-1                    │
│  ☑ medchina-2025                   │  ← 您的MedChina仓库
│  □ another-repo                    │
│                                     │
└─────────────────────────────────────┘
```

**操作步骤：**

1. **搜索您的仓库**（可选）
   - 在搜索框中输入 "medchina"
   - 页面会过滤显示相关仓库

2. **选择 MedChina 仓库**
   - 在列表中找到您的 MedChina 仓库
   - 点击仓库名称或复选框
   - 选中后，复选框会变为 ☑

3. **点击 "Next" 按钮**
   - 位置：页面右下角
   - 按钮文字：**"Next"** 或 **"Continue"**
   - 颜色：蓝色或紫色

### 2.3 如果仓库未显示

**可能原因：**
- Railway 还没有权限访问该仓库
- 仓库是私有的，需要额外授权

**解决方法：**

1. 点击页面上的 **"Configure GitHub"** 链接
   - 位置：搜索框下方或页面顶部
2. 跳转到 GitHub 的应用授权页面
3. 在 "Repository access" 部分：
   - 选择 **"Only select repositories"**
   - 在列表中找到并勾选您的 MedChina 仓库
4. 点击页面底部的 **"Save"** 按钮
5. 返回 Railway，刷新页面
6. 重新尝试选择仓库

---

## 第三步：配置项目

选择仓库后，Railway 会自动检测项目配置并进入项目配置页面：

### 3.1 自动配置确认页面

**页面布局：**
```
┌─────────────────────────────────────┐
│  < Back   Configure New Project     │
├─────────────────────────────────────┤
│                                     │
│  Project Name:                      │
│  [ medchina-app              ]      │  ← 项目名称
│                                     │
│  Region:                            │
│  [ US East (Virginia)        ▾ ]    │  ← 区域选择
│                                     │
│  Root Directory:                    │
│  [ /                         ]      │  ← 根目录
│                                     │
│  Dockerfile Path:                   │
│  [ ./Dockerfile              ]      │  ← 自动检测
│                                     │
│  Build Command:                     │
│  [ (auto-detected)           ]      │  ← 自动检测
│                                     │
│  Start Command:                     │
│  [ uvicorn main:app         ]      │  ← 自动检测
│                                     │
│  ⚠️  We detected Dockerfile...      │  ← 提示信息
│                                     │
│           [ Cancel ]  [ Deploy ]    │  ← 底部按钮
└─────────────────────────────────────┘
```

### 3.2 配置各个选项

#### 1️⃣ Project Name（项目名称）

**默认值：** `medchina-app` 或仓库名称

**建议设置：**
- 保持默认：`medchina-app`
- 或使用您的命名：`medchina-medical-tourism`

**操作：**
- 在输入框中输入项目名称
- 名称只能包含小写字母、数字和连字符
- 不能有空格或特殊字符

#### 2️⃣ Region（区域）

**选项列表：**
- `US East (Virginia)` - 美国东部（推荐）
- `US West (Oregon)` - 美国西部
- `EU West (London)` - 欧洲西部
- `EU Central (Frankfurt)` - 欧洲中部
- `Asia Southeast (Singapore)` - 亚洲东南（新加坡）
- `Asia Northeast (Tokyo)` - 亚洲东北（东京）

**建议选择：**
- 如果主要服务欧美用户：`US East (Virginia)` ⭐
- 如果需要中国用户访问：`Asia Northeast (Tokyo)` ⭐

**操作：**
- 点击下拉框
- 在列表中选择合适的区域
- 选择后自动关闭下拉框

#### 3️⃣ Root Directory（根目录）

**默认值：** `/`

**说明：**
- 指定 Dockerfile 和代码所在的目录
- 如果您的 Dockerfile 在项目根目录，保持 `/` 即可

**操作：**
- 保持默认值 `/`
- 不要修改

#### 4️⃣ Dockerfile Path（Dockerfile 路径）

**默认值：** `./Dockerfile`

**说明：**
- Railway 自动检测到项目中的 Dockerfile
- 如果显示正确，无需修改

**操作：**
- 确认显示 `./Dockerfile`
- 不要修改

#### 5️⃣ Build Command（构建命令）

**默认值：** `docker build -f $RAILWAY_DOCKERFILE_PATH -t $RAILWAY_BUILD_IMAGE_NAME .`

**说明：**
- 这是 Docker 构建命令
- Railway 自动生成的

**操作：**
- 保持默认，不要修改

#### 6️⃣ Start Command（启动命令）

**默认值：** `uvicorn main:app --host 0.0.0.0 --port $PORT`

**说明：**
- 这是应用启动命令
- Railway 会自动注入 `$PORT` 环境变量

**操作：**
- 确认显示 `uvicorn main:app --host 0.0.0.0 --port $PORT`
- 不要修改

### 3.3 检查配置

在点击部署之前，请确认：

- [ ] Project Name 已填写
- [ ] Region 已选择（推荐 US East）
- [ ] Root Directory 是 `/`
- [ ] Dockerfile Path 是 `./Dockerfile`
- [ ] Start Command 是 `uvicorn main:app...`
- [ ] 页面底部没有红色的错误提示

### 3.4 开始部署

**重要提示：**
此时还**不要**点击 "Deploy" 按钮！
我们需要先配置环境变量。

**但 Railway 会自动创建两个服务：**
1. **PostgreSQL 数据库服务**（自动创建）
2. **Web 应用服务**（您刚配置的）

所以我们可以点击 **"Deploy"**，Railway 会：
1. 创建项目
2. 自动添加 PostgreSQL
3. 配置环境变量
4. 开始部署

---

## 第四步：配置环境变量

部署开始后，我们需要配置环境变量。有两种方式：

### 方式 A：在部署前配置（推荐）⭐

**在配置页面（第三步的页面）添加环境变量：**

1. 在配置页面底部，找到 **"Environment Variables"** 区域
2. 点击 **"+ New Variable"** 按钮
3. 依次添加以下变量：

#### 变量 1：SECRET_KEY

```
Name:   SECRET_KEY
Value:  <生成一个长随机字符串>
```

**如何生成 SECRET_KEY：**

**方法 1：使用在线工具**
1. 访问 https://www.uuidgenerator.net/api/version4
2. 复制生成的 UUID
3. 或访问 https://www.random.org/strings/
4. 生成 64 个字符的随机字符串

**方法 2：使用 Python**
```python
# 在 Python REPL 中执行
import secrets
print(secrets.token_hex(32))
```
复制输出的 64 个字符的字符串

**填写示例：**
```
Name:   SECRET_KEY
Value:  a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

**重要提示：**
- 保存好这个密钥！
- 不要使用简单的密码
- 不要泄露给他人

#### 变量 2：ALGORITHM

```
Name:   ALGORITHM
Value:  HS256
```

**说明：**
- JWT 加密算法
- 必须是 `HS256`
- 不要修改

#### 变量 3：ACCESS_TOKEN_EXPIRE_MINUTES

```
Name:   ACCESS_TOKEN_EXPIRE_MINUTES
Value:  1440
```

**说明：**
- Token 过期时间（分钟）
- 1440 = 24 小时
- 可以根据需要调整

#### 变量 4：COZE_INTEGRATION_MODEL_BASE_URL

```
Name:   COZE_INTEGRATION_MODEL_BASE_URL
Value:  https://api.coze.com
```

**说明：**
- Coze API 地址
- 必须是 `https://api.coze.com`
- 不要修改

#### 变量 5：COZE_WORKLOAD_IDENTITY_API_KEY（可选）

```
Name:   COZE_WORKLOAD_IDENTITY_API_KEY
Value:  <您的 Coze API Key>
```

**如果您有 Coze API Key：**
1. 从 Coze 平台获取 API Key
2. 填写此变量

**如果您没有：**
- 暂时不填
- 应用仍能运行，但可能有限制

### 方式 B：在部署后配置

如果您已经点击了 "Deploy"，也可以在项目创建后配置：

1. 部署开始后，等待项目创建完成
2. 在项目页面，点击左侧菜单的 **"Variables"** 标签
3. 点击右上角的 **"+ New Variable"** 按钮
4. 按照上面的说明添加变量
5. 添加完成后，Railway 会自动重启应用

---

## 第五步：部署应用

### 5.1 点击部署按钮

在配置页面（第三步的页面）：

1. 找到页面右下角的 **"Deploy"** 按钮
2. 点击 **"Deploy"** 按钮
   - 按钮颜色通常是蓝色或紫色
   - 按钮较大，容易找到

### 5.2 部署开始后的页面

点击后会进入部署进度页面：

**页面布局：**
```
┌─────────────────────────────────────┐
│  Railway Logo  medchina-app    ...  │
├─────────────────────────────────────┤
│                                     │
│  📦 Deployments                     │
│  ──────────────────────────────     │
│                                     │
│  🔄 Building...                     │  ← 正在构建
│  medchina-app (Build #1)            │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ → Cloning repository...     │   │
│  │ → Building Docker image...  │   │
│  │ → Deploying...              │   │
│  └─────────────────────────────┘   │
│                                     │
│  Services:                          │
│  ├─ medchina-app (Web)             │
│  └─ medchina-db (PostgreSQL)        │
│                                     │
└─────────────────────────────────────┘
```

### 5.3 部署过程详解

Railway 会自动执行以下步骤：

#### 步骤 1：克隆仓库（1-2 分钟）
```
→ Cloning repository from GitHub...
→ Checking out branch 'main'...
```

**显示信息：**
- "Cloning repository..."
- "Checking out..."

#### 步骤 2：构建 Docker 镜像（2-3 分钟）
```
→ Building Docker image...
→ Sending build context...
→ Installing dependencies...
```

**显示信息：**
- 构建进度百分比
- 依赖安装日志
- 可能会有很多 Python 包安装的输出

#### 步骤 3：部署应用（1-2 分钟）
```
→ Deploying containers...
→ Starting services...
→ Running health checks...
```

**显示信息：**
- 容器启动日志
- 健康检查结果
- 域名分配信息

#### 步骤 4：自动创建数据库

Railway 会自动检测 `railway.toml` 配置文件，并：

1. 创建 PostgreSQL 数据库服务
2. 配置数据库连接
3. 自动注入 `DATABASE_URL` 环境变量

**显示信息：**
- "Creating PostgreSQL service..."
- "Configuring database connection..."

### 5.4 等待部署完成

**预计时间：** 3-5 分钟（首次部署）

**您需要做的：**
- 耐心等待，不要关闭浏览器
- 可以滚动查看部署日志
- 如果出现错误，记录错误信息

**成功的标志：**
- 状态变为 **"Active"** 或 **"Success"**
- 有绿色的对勾图标 ✅
- 页面显示应用访问 URL

---

## 第六步：验证部署

### 6.1 查看部署状态

部署完成后，您会看到：

**成功页面：**
```
┌─────────────────────────────────────┐
│  🎉 Deployment Successful!          │
├─────────────────────────────────────┤
│                                     │
│  Your app is now live!              │
│                                     │
│  📍 URL:                            │
│  https://medchina-app.up.railway.app│  ← 点击这里访问
│                                     │
│  📊 Services:                       │
│  ✅ medchina-app (Web)              │
│  ✅ medchina-db (PostgreSQL)        │
│                                     │
│  [ View Logs ]  [ Redeploy ]        │
│                                     │
└─────────────────────────────────────┘
```

### 6.2 访问应用

1. 找到 **URL** 或 **域名** 区域
2. 点击生成的链接（如：`https://medchina-app.up.railway.app`）
3. 会打开新的浏览器标签页

**应该看到的页面：**
- 前台页面：MedChina 医疗旅游服务首页
- 如果看到页面内容，说明部署成功！
- 如果看到错误，请查看"常见问题解决"部分

### 6.3 访问后台管理

在 URL 后面加上 `/admin/`：

```
https://medchina-app.up.railway.app/admin/
```

**应该看到的页面：**
- 后台登录页面
- 有登录表单或注册链接

### 6.4 访问 API 文档

在 URL 后面加上 `/docs`：

```
https://medchina-app.up.railway.app/docs
```

**应该看到的页面：**
- Swagger UI API 文档页面
- 列出所有 API 端点

### 6.5 健康检查

在 URL 后面加上 `/health`：

```
https://medchina-app.up.railway.app/health
```

**应该看到：**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-01-18T10:30:00Z"
}
```

---

## 第七步：初始化数据

首次部署后，数据库中还没有表结构，需要初始化。

### 7.1 使用 Railway Console 初始化

#### 步骤 1：打开项目 Console

1. 在 Railway 项目页面
2. 点击左侧菜单的 **"Deployments"** 标签
3. 点击正在运行的部署（通常是顶部最新的）
4. 在右侧面板，找到 **"Console"** 或 **"Terminal"** 区域

#### 步骤 2：启动 Shell

1. 在 Console 区域，点击 **"New Shell"** 或 **"+"** 按钮
2. 选择 **"app"** 服务（Web 应用）
3. 等待 Shell 启动完成

**会看到类似这样的提示符：**
```
/app $
```

#### 步骤 3：运行初始化脚本

在 Shell 中执行：

```bash
bash /app/scripts/init_db.sh
```

**预期输出：**
```
Waiting for database to be ready...
Database is ready, running migrations...
Creating database tables...
Database tables created successfully!
Database initialization completed!
```

#### 步骤 4：验证数据库

在 Shell 中执行：

```bash
python -c "
from storage.database.shared.model import Base, engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()
print('Database tables:', tables)
"
```

**应该看到类似输出：**
```
Database tables: ['users', 'doctors', 'hospitals', 'diseases', 'tourist_attractions', ...]
```

### 7.2 通过 API 初始化（替代方法）

如果 Console 不好用，可以通过 API 触发初始化：

1. 访问健康检查端点：
   ```
   https://medchina-app.up.railway.app/health
   ```

2. 如果应用配置了自动创建表，第一次访问时会自动创建

3. 访问 API 文档测试数据库端点：
   ```
   https://medchina-app.up.railway.app/docs
   ```

4. 测试创建一个用户，看是否能成功

### 7.3 创建管理员账号

数据库初始化完成后，创建第一个管理员账号：

1. 访问后台注册页面：
   ```
   https://medchina-app.up.railway.app/admin/register/
   ```

2. 填写注册表单：
   - **Username**: `admin` 或您的用户名
   - **Email**: 您的邮箱
   - **Password**: 设置强密码
   - **Confirm Password**: 再次输入密码

3. 点击 **"Register"** 按钮

4. 注册成功后，会自动登录到后台

---

## 第八步：添加基础数据

登录后台后，添加必要的业务数据：

### 8.1 添加病种分类

1. 在后台左侧菜单，点击 **"病种管理"** 或 **"Diseases"**
2. 点击 **"新增病种"** 或 **"Add Disease"** 按钮
3. 填写病种信息：
   - **名称**: 心血管疾病
   - **英文名**: Cardiovascular Disease
   - **描述**: ...
   - **图标**: （可选）
4. 点击 **"保存"** 按钮

**添加几个示例病种：**
- 心血管疾病
- 神经科疾病
- 骨科疾病
- 肿瘤科疾病

### 8.2 添加医生信息

1. 在后台左侧菜单，点击 **"医生管理"** 或 **"Doctors"**
2. 点击 **"新增医生"** 按钮
3. 填写医生信息：
   - **姓名**: 张医生
   - **英文名**: Dr. Zhang
   - **所属医院**: 选择医院
   - **擅长领域**: 选择病种
   - **职称**: 主任医师
   - **简介**: ...
   - **图片**: （可选）
4. 点击 **"保存"** 按钮

### 8.3 添加医院信息

1. 在后台左侧菜单，点击 **"医院管理"** 或 **"Hospitals"**
2. 点击 **"新增医院"** 按钮
3. 填写医院信息：
   - **名称**: 北京协和医院
   - **英文名**: Peking Union Medical College Hospital
   - **地址**: 北京市东城区...
   - **等级**: 三甲
   - **简介**: ...
4. 点击 **"保存"** 按钮

### 8.4 添加景点信息

1. 在后台左侧菜单，点击 **"景点管理"** 或 **"Attractions"**
2. 点击 **"新增景点"** 按钮
3. 填写景点信息：
   - **名称**: 故宫
   - **英文名**: Forbidden City
   - **类型**: 历史景点
   - **地址**: 北京市东城区...
   - **门票**: 60元
   - **开放时间**: 8:30-17:00
   - **简介**: ...
4. 点击 **"保存"** 按钮

---

## 🆘 常见问题解决

### Q1: 点击 "Deploy from GitHub repo" 后没有看到我的仓库？

**症状：** GitHub 仓库列表为空或没有显示我的仓库

**原因：** Railway 还没有权限访问该仓库

**解决方法：**

1. 在仓库选择页面，找到 **"Configure GitHub"** 链接
2. 点击链接，跳转到 GitHub 授权页面
3. 在 "Repository access" 部分：
   - 选择 **"Only select repositories"**
   - 在列表中找到您的 MedChina 仓库
   - 勾选仓库名称
4. 点击页面底部的 **"Save"** 按钮
5. 返回 Railway，刷新页面（按 F5）
6. 重新尝试选择仓库

---

### Q2: 部署失败，提示 "Dockerfile not found"

**症状：** 部署日志中显示 "Dockerfile not found"

**原因：** Dockerfile 不在仓库根目录，或文件名错误

**解决方法：**

1. 检查您的 GitHub 仓库：
   ```bash
   # 在本地项目目录执行
   ls -la Dockerfile
   ```

2. 确认 Dockerfile 存在且名称正确：
   - 文件名必须是 `Dockerfile`（大写 D，小写其余）
   - 不能是 `dockerfile` 或 `Dockerfile.txt`

3. 如果文件存在但仍然报错：
   - 提交并推送文件到 GitHub：
     ```bash
     git add Dockerfile
     git commit -m "添加 Dockerfile"
     git push origin main
     ```

4. 在 Railway 重新部署：
   - 点击 "Redeploy" 按钮

---

### Q3: 部署失败，提示 "requirements.txt not found"

**症状：** 部署日志中显示 "requirements.txt not found"

**原因：** requirements.txt 不在仓库中

**解决方法：**

1. 检查 requirements.txt 是否存在：
   ```bash
   ls -la requirements.txt
   ```

2. 如果不存在，生成 requirements.txt：
   ```bash
   pip freeze > requirements.txt
   ```

3. 提交并推送：
   ```bash
   git add requirements.txt
   git commit -m "添加 requirements.txt"
   git push origin main
   ```

4. 在 Railway 重新部署

---

### Q4: 部署成功后访问 404 错误

**症状：** 访问 URL 显示 404 Not Found

**原因：** 应用路由配置问题

**解决方法：**

1. 检查应用日志：
   - 在 Railway 项目页面
   - 点击 "Deployments" 标签
   - 点击部署记录
   - 查看 "Logs" 区域

2. 确认应用是否正常启动：
   - 查找 "Uvicorn running" 或 "Application startup" 消息

3. 尝试访问根路径：
   - `https://your-app.up.railway.app/`
   - 或 `https://your-app.up.railway.app/docs`

4. 如果还是 404，检查 src/main.py 的路由配置

---

### Q5: 数据库连接失败

**症状：** 日志中显示 "Database connection failed" 或类似错误

**原因：** DATABASE_URL 配置问题或数据库未启动

**解决方法：**

1. 检查 PostgreSQL 服务状态：
   - 在 Railway 项目页面
   - 查看 "Services" 区域
   - 确认 `medchina-db` 服务状态是 **Active**

2. 检查环境变量：
   - 点击 "Variables" 标签
   - 查找 `DATABASE_URL` 变量
   - 确认变量存在且格式正确

3. 如果 DATABASE_URL 不存在：
   - Railway 应该自动创建
   - 如果没有，手动添加：
     ```
     Name:   DATABASE_URL
     Value:  postgresql://postgres:<password>@containers-us-west-1.railway.app:<port>/railway
     ```
   - 替换 `<password>` 和 `<port>` 为实际值

4. 重启应用：
   - 点击应用服务的 "Restart" 按钮

---

### Q6: 如何查看实时日志？

**方法 1：通过网页查看**

1. 在 Railway 项目页面
2. 点击 **"Deployments"** 标签
3. 点击正在运行的部署（顶部最新的）
4. 向下滚动找到 **"Logs"** 区域
5. 实时日志会自动滚动更新

**方法 2：通过 CLI 查看**

```bash
# 安装 Railway CLI
npm install -g @railway/cli

# 登录
railway login

# 进入项目
railway project cd medchina-app

# 查看日志
railway logs
```

---

### Q7: 应用启动慢怎么办？

**症状：** 每次访问都需要等 30-60 秒

**原因：** 这是 Railway 的冷启动特性（免费版）

**解释：**
- Railway 免费版会在无请求时休眠应用
- 下次访问需要重新启动应用
- 这是正常的，不是错误

**解决方法：**

1. **等待改进：** 首次访问等待 30-60 秒
2. **保持活跃：** 每隔几分钟访问一次，避免休眠
3. **升级付费：** Railway 付费版提供常驻实例
4. **使用 Render：** Render 的冷启动相对快一些

**优化方法：**

在 Dockerfile 中添加健康检查，缩短启动时间：

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

---

### Q8: 免费额度用完了怎么办？

**症状：** 应用暂停运行，Railway 提示额度不足

**原因：** 超过每月 $5 的免费额度

**解决方法：**

1. **等待下月重置：**
   - Railway 免费额度按月计算
   - 下个月自动重置

2. **升级付费：**
   - 在项目设置中升级到付费计划
   - 付费版提供更多资源和常驻实例

3. **优化使用：**
   - 减少不必要的请求
   - 优化代码减少资源消耗
   - 使用缓存减少数据库查询

4. **更换平台：**
   - Render 提供 750 小时/月免费额度
   - 适合需要长时间运行的应用

---

### Q9: 如何配置自定义域名？

**前提：** 您有一个域名（如：`medchina.com`）

**步骤：**

1. 在 Railway 项目页面
2. 点击 **"Settings"** 标签
3. 找到 **"Domains"** 或 **"Networking"** 部分
4. 点击 **"+ Add Domain"** 按钮
5. 输入您的域名：
   - `medchina.com`
   - 或 `www.medchina.com`
6. 点击 **"Add"** 按钮

7. **配置 DNS：**
   - Railway 会显示要添加的 DNS 记录
   - 登录您的域名注册商（如：阿里云、GoDaddy）
   - 添加 CNAME 记录：
     - **类型**: CNAME
     - **主机记录**: `www`
     - **记录值**: `<railway 提供的值>`
   - 保存 DNS 设置

8. **等待生效：**
   - DNS 生效需要 10 分钟到 48 小时
   - Railway 会自动申请 SSL 证书

9. **测试访问：**
   - 访问 `https://www.medchina.com`
   - 应该能看到您的应用

---

### Q10: 如何升级依赖或修改代码？

**方法 1：自动部署（推荐）**

1. 在本地修改代码
2. 提交到 GitHub：
   ```bash
   git add .
   git commit -m "更新代码"
   git push origin main
   ```

3. Railway 会自动检测到更新
4. 自动触发重新部署
5. 部署完成后，自动更新上线

**方法 2：手动重新部署**

1. 在 Railway 项目页面
2. 点击 **"Deployments"** 标签
3. 点击右上角的 **"Redeploy"** 按钮
4. 选择要重新部署的分支（通常是 `main`）
5. 点击 **"Deploy"** 按钮
6. 等待部署完成

---

## 🔄 如何更新应用

部署后，您可能需要更新代码或添加新功能。以下是详细的更新步骤：

### 场景 1：修改代码

**步骤：**

1. **本地修改代码**
   - 使用编辑器修改代码
   - 例如：修改 `src/agents/agent.py`

2. **测试本地修改**
   ```bash
   # 本地测试
   python -m pytest tests/
   ```

3. **提交到 GitHub**
   ```bash
   git add .
   git commit -m "修复 Bug"
   git push origin main
   ```

4. **Railway 自动部署**
   - Railway 检测到新的 commit
   - 自动触发重新部署
   - 部署完成后自动上线

5. **验证更新**
   - 访问应用
   - 测试新功能

### 场景 2：添加新依赖

**步骤：**

1. **安装新依赖**
   ```bash
   pip install new-package
   ```

2. **更新 requirements.txt**
   ```bash
   pip freeze > requirements.txt
   ```

3. **提交到 GitHub**
   ```bash
   git add requirements.txt
   git commit -m "添加新依赖 new-package"
   git push origin main
   ```

4. **Railway 自动重新构建**
   - Railway 检测到 requirements.txt 变化
   - 重新构建 Docker 镜像
   - 安装新依赖
   - 重新部署

### 场景 3：修改环境变量

**步骤：**

1. 在 Railway 项目页面
2. 点击 **"Variables"** 标签
3. 找到要修改的变量
4. 点击变量右侧的编辑图标（铅笔）
5. 修改值
6. 点击 **"Save"** 保存

7. **重启应用**
   - 修改环境变量后，应用会自动重启
   - 或手动点击应用服务的 **"Restart"** 按钮

### 场景 4：修改数据库结构

**步骤：**

1. **修改数据库模型**
   - 修改 `src/storage/database/shared/model.py`
   - 添加或修改表结构

2. **创建数据库迁移**（如果使用 Alembic）
   ```bash
   alembic revision --autogenerate -m "添加新表"
   ```

3. **提交代码**
   ```bash
   git add .
   git commit -m "修改数据库结构"
   git push origin main
   ```

4. **运行迁移**
   - 在 Railway Console 中执行：
     ```bash
     alembic upgrade head
     ```
   - 或通过 API 触发迁移

### 场景 5：回滚到旧版本

**步骤：**

1. 在 Railway 项目页面
2. 点击 **"Deployments"** 标签
3. 在部署列表中找到要回滚的版本
4. 点击部署记录右侧的 **"..."** 菜单
5. 选择 **"Promote to Production"** 或 **"Redeploy"**

---

## 📊 部署检查清单

在完成部署后，使用此清单确认所有步骤都已完成：

### ✅ 基础配置
- [ ] GitHub 仓库代码已推送
- [ ] Dockerfile 存在且正确
- [ ] requirements.txt 存在且完整
- [ ] railway.toml 存在

### ✅ Railway 配置
- [ ] 已注册 Railway 账号
- [ ] 已连接 GitHub 仓库
- [ ] 项目名称已填写
- [ ] 区域已选择

### ✅ 环境变量
- [ ] SECRET_KEY 已配置
- [ ] ALGORITHM 已配置
- [ ] ACCESS_TOKEN_EXPIRE_MINUTES 已配置
- [ ] COZE_INTEGRATION_MODEL_BASE_URL 已配置
- [ ] COZE_WORKLOAD_IDENTITY_API_KEY 已配置（如有）

### ✅ 部署状态
- [ ] 应用部署成功
- [ ] 状态显示 "Active"
- [ ] PostgreSQL 服务运行正常

### ✅ 访问测试
- [ ] 前台页面能访问
- [ ] 后台页面能访问
- [ ] API 文档能访问
- [ ] 健康检查通过

### ✅ 数据库
- [ ] 数据库表已创建
- [ ] 管理员账号已创建
- [ ] 基础数据已添加

### ✅ 功能测试
- [ ] 用户注册登录正常
- [ ] AI 对话功能正常
- [ ] 预约功能正常
- [ ] 支付功能正常
- [ ] 后台管理功能正常

---

## 🎉 恭喜！

如果您已经完成了以上所有步骤，您的 MedChina 医疗旅游智能体系统已经成功部署并运行了！

### 📍 您的访问地址

- **前台**: `https://medchina-app.up.railway.app/`
- **后台**: `https://medchina-app.up.railway.app/admin/`
- **API 文档**: `https://medchina-app.up.railway.app/docs`

### 📞 获取帮助

如果在部署过程中遇到问题：

1. **查看日志**：Railway 项目 → Deployments → Logs
2. **查看文档**：DEPLOYMENT.md、QUICKSTART.md
3. **提交 Issue**：在 GitHub 仓库提交问题
4. **联系支持**：山东和拾方信息科技有限公司

### 🚀 下一步

1. 添加更多医生、医院、景点数据
2. 配置财务管理参数
3. 测试所有功能
4. 邀请用户试用
5. 根据反馈优化功能

---

## 📚 其他资源

- **Railway 官方文档**: https://docs.railway.app
- **Railway 定价**: https://railway.app/pricing
- **GitHub 仓库**: 您的 MedChina 仓库链接

---

**祝您使用愉快！走！到中国去看病！**
