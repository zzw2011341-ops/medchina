# 在 Railway 上直接编辑 requirements.txt

## 方法一：使用 Railway Web 界面（推荐）

### 步骤 1：打开 Railway 项目
1. 访问 https://railway.app
2. 登录你的账号
3. 找到并点击你的 `medchina` 项目

### 步骤 2：进入代码编辑器
1. 在项目页面顶部，找到并点击 **"Source"** 或 **"Code"** 标签
2. 这会打开 Railway 内置的代码编辑器

### 步骤 3：找到并编辑 requirements.txt
1. 在左侧文件树中，找到 `requirements.txt` 文件
2. 点击打开文件

### 步骤 4：删除不必要的依赖
找到并删除以下两行：
```txt
dbus-python==1.3.2
PyGObject==3.48.2
```

### 步骤 5：保存更改
1. 点击编辑器右上角的 **"Save"** 或 **"Commit"** 按钮
2. 输入提交信息（可选）：`fix: remove unnecessary desktop libraries`
3. 点击确认

### 步骤 6：触发重新部署
1. Railway 会自动检测到文件变更
2. 点击 **"Redeploy"** 或 **"Deploy"** 按钮
3. 等待构建完成（约 3-5 分钟）

---

## 方法二：使用 Railway CLI

如果你已安装 Railway CLI，可以使用命令行操作：

```bash
# 登录 Railway
railway login

# 选择项目
railway link

# 拉取最新代码
railway up

# 编辑 requirements.txt
nano requirements.txt
# 或者使用 vim
vim requirements.txt

# 删除以下两行：
# dbus-python==1.3.2
# PyGObject==3.48.2

# 保存并退出后，推送更改
railway up

# 触发重新部署
railway deploy
```

---

## 方法三：使用 GitHub 网页编辑

如果你有 GitHub 访问权限：

### 步骤 1：打开 GitHub 仓库
1. 访问 https://github.com/zzw2011341-ops/medchina
2. 登录你的账号

### 步骤 2：找到 requirements.txt
1. 在文件列表中找到 `requirements.txt`
2. 点击文件名

### 步骤 3：编辑文件
1. 点击文件右上角的 **铅笔图标** ✏️（Edit）
2. 找到并删除以下两行：
   ```txt
   dbus-python==1.3.2
   PyGObject==3.48.2
   ```

### 步骤 4：提交更改
1. 在页面底部的提交信息框中输入：
   ```
   fix: remove unnecessary desktop libraries (dbus-python, PyGObject) to fix Railway deployment
   ```
2. 点击 **"Commit changes"** 按钮

### 步骤 5：Railway 自动部署
- Railway 会自动检测到 GitHub 的新提交
- 开始重新构建和部署
- 约 3-5 分钟后完成

---

## 验证部署是否成功

### 1. 查看构建日志
1. 访问 Railway 项目页面
2. 点击 **"Deployments"** 标签
3. 查看最新的构建状态
4. 点击构建查看详细日志

### 2. 检查应用状态
- ✅ **构建成功**: 日志显示 "Build completed successfully"
- ✅ **应用启动**: 日志显示 "App is running"
- ❌ **构建失败**: 查看错误日志，如有需要请提供给我

### 3. 访问健康检查端点
在浏览器中访问：
```
https://your-app.railway.app/health
```

应该返回：
```json
{
  "status": "healthy",
  "message": "MedChina is running"
}
```

### 4. 访问应用主页
```
https://your-app.railway.app/
```

---

## 常见问题

### Q: 找不到 "Source" 标签？
A: Railway 界面可能因版本不同而有所变化，尝试查找：
- "Code"
- "Repository"
- "Files"
- 或者在项目设置中找到相关选项

### Q: 编辑后没有保存按钮？
A: 试试：
- 按 `Ctrl + S`（Windows）或 `Cmd + S`（Mac）
- 查看右上角是否有 "Commit" 或 "Save" 选项
- 有些版本可能需要手动提交

### Q: 保存后没有自动部署？
A: 手动触发：
1. 在项目主页找到 **"Redeploy"** 按钮
2. 或者进入 **"Settings"** → **"Deployments"**
3. 点击 **"Create new deployment"**

---

## 需要帮助？

如果在操作过程中遇到问题，请提供：
1. Railway 界面截图
2. 错误信息
3. 你尝试的步骤

我会帮你继续解决。

---

**出品方**: 山东和拾方信息科技有限公司
**项目**: MedChina - 走！到中国去看病！
