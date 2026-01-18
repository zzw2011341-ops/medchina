# Railway 部署修复指南

## 问题描述

在 Railway 上部署时遇到以下错误：
```
error: Preparing metadata (pyproject.toml) did not run successfully.
error: subprocess-exited-with-error
...
ERROR: Dependency lookup for dbus-1 with method 'pkgconfig' failed
```

## 原因分析

`dbus-python==1.3.2` 和 `PyGObject==3.48.2` 是 Linux 桌面环境相关的库，它们需要系统级依赖（`pkg-config` 和 `dbus-1`）。这些库在 Web 应用中完全不需要，但在 `requirements.txt` 中被误包含，导致构建失败。

## 解决方案

已从 `requirements.txt` 中删除这两个不必要的包：
- ✅ 删除 `dbus-python==1.3.2`
- ✅ 删除 `PyGObject==3.48.2`

## 如何应用修复

### 方式一：推送代码到 GitHub（推荐）

如果你有 GitHub 推送权限，请在你的本地电脑执行：

```bash
cd medchina
git pull origin main
git push origin main
```

Railway 会自动检测到新的提交并重新部署。

### 方式二：手动在 Railway 重新部署

1. 访问你的 Railway 项目页面
2. 点击 "Redeploy" 按钮
3. Railway 会重新拉取代码并构建

### 方式三：在 Railway 上直接编辑代码

1. 访问 Railway 项目页面
2. 打开 "Source" 标签
3. 找到 `requirements.txt` 文件
4. 删除以下两行：
   - `dbus-python==1.3.2`
   - `PyGObject==3.48.2`
5. 保存并重新部署

## 验证修复

部署成功后，你应该看到：
- ✅ 构建过程顺利完成
- ✅ 应用成功启动
- ✅ 访问 Railway 提供的域名可以看到应用界面

## 环境变量配置

确保在 Railway 上配置了以下环境变量：

```
SECRET_KEY=<生成的随机密钥>
DATABASE_URL=<Railway PostgreSQL 自动提供>
JWT_SECRET_KEY=<生成的随机密钥>
```

### 生成密钥的方法

```bash
# 生成 SECRET_KEY
openssl rand -hex 32

# 生成 JWT_SECRET_KEY
openssl rand -hex 32
```

## 访问应用

部署成功后，访问以下端点：

- **健康检查**: `https://your-app.railway.app/health`
- **主页**: `https://your-app.railway.app/`
- **后台登录**: `https://your-app.railway.app/admin/login`

## 默认管理员账号

如果这是第一次部署，需要先在数据库中创建管理员账号。可以使用以下 SQL：

```sql
INSERT INTO admin (username, password_hash, is_active, created_at)
VALUES ('admin', '$2b$12$...', true, NOW());
```

密码哈希需要使用 bcrypt 生成。

## 常见问题

### Q: 部署还是失败怎么办？
A: 查看 Railway 的构建日志，确认是否还有其他依赖问题。

### Q: 应用启动后访问 404？
A: 检查数据库是否正确初始化，环境变量是否配置正确。

### Q: 后台登录提示错误？
A: 确认数据库中已创建管理员账号，且密码哈希正确。

## 联系支持

如果遇到其他问题，请提供：
1. Railway 构建日志
2. 应用运行日志
3. 错误截图

---

**出品方**: 山东和拾方信息科技有限公司
**项目**: MedChina - 医疗旅游咨询平台
