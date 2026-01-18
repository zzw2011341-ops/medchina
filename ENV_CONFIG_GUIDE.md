# 🔧 环境变量配置完整指南

## 📋 环境变量清单

在 Railway 上部署 MedChina 需要配置以下环境变量：

| 变量名 | 是否必需 | 示例值 | 说明 |
|--------|---------|--------|------|
| `SECRET_KEY` | ✅ 必需 | `a1b2c3d4e5f6g7h8i9j0...` | JWT 签名密钥（64位随机字符串） |
| `ALGORITHM` | ✅ 必需 | `HS256` | 加密算法 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ✅ 必需 | `1440` | Token 过期时间（分钟） |
| `COZE_INTEGRATION_MODEL_BASE_URL` | ✅ 必需 | `https://api.coze.com` | Coze API 地址 |
| `COZE_WORKLOAD_IDENTITY_API_KEY` | ❌ 可选 | `your-api-key` | Coze API 密钥 |

---

## 🎯 在 Railway 上配置环境变量

### 步骤 1：进入项目页面

1. 访问 https://railway.app
2. 登录您的账号
3. 在 Dashboard 中找到 `medchina-app` 项目
4. 点击项目名称进入项目页面

### 步骤 2：打开 Variables 标签页

**方法 A：通过侧边栏**
1. 在项目页面左侧，找到 **"Variables"** 标签
2. 点击进入 Variables 页面

**方法 B：通过设置菜单**
1. 在项目页面右上角，点击 **"Settings"** 或齿轮图标
2. 在设置页面中，找到 **"Variables"** 标签
3. 点击进入

**页面布局：**
```
┌─────────────────────────────────────┐
│  medchina-app  Settings / Variables │
├─────────────────────────────────────┤
│                                     │
│  Environment Variables              │
│  ──────────────────────────────     │
│                                     │
│  + New Variable                     │  ← 点击这里添加变量
│                                     │
│  Key                      Value     │
│  ──────────────────────────────     │
│  SECRET_KEY      ********************│  ← 已配置的变量
│  ALGORITHM        HS256              │
│  ...                                │
│                                     │
│  💡 Tips:                           │
│  - 点击变量名编辑                   │
│  - 点击垃圾桶图标删除               │
│  - 变量会自动保存                   │
│                                     │
└─────────────────────────────────────┘
```

### 步骤 3：添加环境变量

点击 **"+ New Variable"** 按钮，会出现添加变量的表单：

**表单布局：**
```
┌─────────────────────────────────────┐
│  Add Variable                       │
├─────────────────────────────────────┤
│                                     │
│  Key:                    [输入框]   │  ← 变量名
│                                     │
│  Value:                  [输入框]   │  ← 变量值
│                                     │
│  Type:                    [Plain ▾] │  ← 类型（保持 Plain）
│                                     │
│           [Cancel]  [Add Variable]  │
└─────────────────────────────────────┘
```

---

## 📝 详细配置步骤（逐个变量）

### 变量 1：SECRET_KEY（最重要！）

**说明：**
- 用于 JWT Token 签名
- 必须是长随机字符串
- 不要使用简单密码
- 不要泄露给他人

**如何生成 SECRET_KEY：**

#### 方法 A：在线生成（推荐）

1. **访问 UUID 生成器**：
   ```
   https://www.uuidgenerator.net/api/version4
   ```

2. **复制生成的 UUID**（如：`550e8400-e29b-41d4-a716-446655440000`）

3. **或者使用更长的随机字符串生成器**：
   - 访问：https://www.random.org/strings/
   - 设置：
     - Length: `64`
     - Characters: `All alphanumeric characters`
   - 点击 "Generate"
   - 复制结果

#### 方法 B：使用 Python 生成

```python
import secrets

# 生成 32 字节的随机字符串（64 个十六进制字符）
secret_key = secrets.token_hex(32)
print(secret_key)
```

**示例输出：**
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

#### 方法 C：使用命令行（如果有 openssl）

```bash
# Linux/Mac
openssl rand -hex 32

# 输出示例：
# a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

**填写到 Railway：**

1. 在 "Key" 输入框输入：`SECRET_KEY`
2. 在 "Value" 输入框粘贴生成的字符串（64位）
3. 点击 **"Add Variable"** 按钮

**示例：**
```
Key:    SECRET_KEY
Value:  a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

**⚠️ 重要提示：**
- 立即保存这个密钥！
- 不要使用上面的示例值！
- 每个项目应该使用不同的密钥

---

### 变量 2：ALGORITHM

**说明：**
- JWT 加密算法
- 必须是 `HS256`
- 不要修改

**填写到 Railway：**

1. 点击 **"+ New Variable"**
2. 在 "Key" 输入框输入：`ALGORITHM`
3. 在 "Value" 输入框输入：`HS256`
4. 点击 **"Add Variable"**

**示例：**
```
Key:    ALGORITHM
Value:  HS256
```

---

### 变量 3：ACCESS_TOKEN_EXPIRE_MINUTES

**说明：**
- 用户登录 Token 的过期时间（分钟）
- 1440 = 24 小时
- 可以根据需要调整

**填写到 Railway：**

1. 点击 **"+ New Variable"**
2. 在 "Key" 输入框输入：`ACCESS_TOKEN_EXPIRE_MINUTES`
3. 在 "Value" 输入框输入：`1440`
4. 点击 **"Add Variable"**

**示例：**
```
Key:    ACCESS_TOKEN_EXPIRE_MINUTES
Value:  1440
```

**可选值：**
- `30` - 30 分钟
- `60` - 1 小时
- `1440` - 24 小时（推荐）
- `4320` - 3 天
- `10080` - 1 周

---

### 变量 4：COZE_INTEGRATION_MODEL_BASE_URL

**说明：**
- Coze AI 模型的 API 地址
- 必须是 `https://api.coze.com`
- 不要修改

**填写到 Railway：**

1. 点击 **"+ New Variable"**
2. 在 "Key" 输入框输入：`COZE_INTEGRATION_MODEL_BASE_URL`
3. 在 "Value" 输入框输入：`https://api.coze.com`
4. 点击 **"Add Variable"**

**示例：**
```
Key:    COZE_INTEGRATION_MODEL_BASE_URL
Value:  https://api.coze.com
```

---

### 变量 5：COZE_WORKLOAD_IDENTITY_API_KEY（可选）

**说明：**
- Coze API 密钥
- 如果没有，可以暂时不配置
- 不配置会使用免费额度

**如何获取 API Key：**

1. 访问 Coze 平台（如果有账号）
2. 进入 API 管理页面
3. 创建新的 API Key
4. 复制 API Key

**填写到 Railway（如果有）：**

1. 点击 **"+ New Variable"**
2. 在 "Key" 输入框输入：`COZE_WORKLOAD_IDENTITY_API_KEY`
3. 在 "Value" 输入框粘贴您的 API Key
4. 点击 **"Add Variable"**

**示例：**
```
Key:    COZE_WORKLOAD_IDENTITY_API_KEY
Value:  pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**如果没有：**
- 可以跳过此变量
- 应用仍能正常运行
- 可能会有调用次数限制

---

## ✅ 完成配置

### 验证环境变量

添加完所有变量后，Variables 页面应该显示：

```
Key                                    Value
──────────────────────────────────────────────────────────
SECRET_KEY                             a1b2c3d4e5f6g7h8i9j0...
ALGORITHM                              HS256
ACCESS_TOKEN_EXPIRE_MINUTES            1440
COZE_INTEGRATION_MODEL_BASE_URL        https://api.coze.com
COZE_WORKLOAD_IDENTITY_API_KEY         pat_xxxxxxxxxxxxxxxx (可选)
```

### 配置检查清单

在开始部署前，请确认：

- [ ] `SECRET_KEY` 已配置，使用 64 位随机字符串
- [ ] `ALGORITHM` 已配置为 `HS256`
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` 已配置为 `1440`
- [ ] `COZE_INTEGRATION_MODEL_BASE_URL` 已配置为 `https://api.coze.com`
- [ ] `COZE_WORKLOAD_IDENTITY_API_KEY` 已配置（可选）

### 自动生成的变量（无需配置）

Railway 会自动创建以下变量，您**不需要**手动配置：

- `DATABASE_URL` - 数据库连接字符串（自动生成）
- `PORT` - 应用端口（自动生成）
- `PYTHONPATH` - Python 路径（自动生成）

---

## 🔄 修改环境变量

如果需要修改已配置的变量：

### 修改值

1. 在 Variables 页面，找到要修改的变量
2. 点击变量的 **Value** 列
3. 修改值
4. 点击保存或按 Enter 键
5. Railway 会自动重启应用

### 删除变量

1. 找到要删除的变量
2. 点击变量右侧的 **垃圾桶图标**
3. 确认删除
4. Railway 会自动重启应用

---

## ⚠️ 常见错误

### 错误 1：SECRET_KEY 太短

**错误信息：**
```
Invalid SECRET_KEY: must be at least 32 bytes
```

**解决方法：**
- 重新生成 64 位的随机字符串
- 确保长度至少 64 个字符

### 错误 2：变量名拼写错误

**错误信息：**
```
Environment variable not found: SECRET_KEY
```

**解决方法：**
- 检查变量名是否正确（区分大小写）
- 变量名应该是：`SECRET_KEY`（全大写，下划线连接）

### 错误 3：COZE_INTEGRATION_MODEL_BASE_URL 错误

**错误信息：**
```
Connection refused: api.coze.com
```

**解决方法：**
- 确保值为：`https://api.coze.com`
- 不要加斜杠：`https://api.coze.com/`（错误）
- 必须包含 `https://`

---

## 🎯 快速配置清单（复制粘贴）

为了方便，我为您准备好了可以直接复制的内容：

### 生成 SECRET_KEY
```bash
# 使用 Python 生成
python3 -c "import secrets; print(secrets.token_hex(32))"

# 或使用在线生成
# 访问：https://www.uuidgenerator.net/api/version4
```

### 配置列表（按顺序添加）

**第 1 个：**
```
Key:    SECRET_KEY
Value:  <粘贴生成的 64 位字符串>
```

**第 2 个：**
```
Key:    ALGORITHM
Value:  HS256
```

**第 3 个：**
```
Key:    ACCESS_TOKEN_EXPIRE_MINUTES
Value:  1440
```

**第 4 个：**
```
Key:    COZE_INTEGRATION_MODEL_BASE_URL
Value:  https://api.coze.com
```

**第 5 个（可选）：**
```
Key:    COZE_WORKLOAD_IDENTITY_API_KEY
Value:  <您的 Coze API Key>
```

---

## 📞 获取帮助

如果配置过程中遇到问题：

1. **查看变量**：确保所有必需变量都已配置
2. **查看日志**：在 Railway Deployments 页面查看应用日志
3. **重启应用**：点击应用服务的 "Restart" 按钮
4. **重新部署**：点击 "Redeploy" 按钮

---

## 🎉 配置完成！

配置完所有环境变量后：

1. 回到 **"Deployments"** 标签页
2. 点击 **"Deploy"** 或 **"Redeploy"** 按钮
3. 等待 3-5 分钟
4. 访问生成的 URL 验证部署

**走！到中国去看病！** 🏥✈️🇨🇳
