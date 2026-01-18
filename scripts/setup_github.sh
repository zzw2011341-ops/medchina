#!/bin/bash

# GitHub 仓库快速设置脚本
# 使用方法：bash scripts/setup_github.sh YOUR_GITHUB_USERNAME

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}================================${NC}"
echo -e "${YELLOW}MedChina GitHub 仓库设置脚本${NC}"
echo -e "${YELLOW}================================${NC}"
echo ""

# 检查参数
if [ -z "$1" ]; then
    echo -e "${RED}错误：请提供您的 GitHub 用户名${NC}"
    echo ""
    echo "使用方法："
    echo "  bash scripts/setup_github.sh YOUR_GITHUB_USERNAME"
    echo ""
    echo "示例："
    echo "  bash scripts/setup_github.sh zhangsan"
    exit 1
fi

GITHUB_USERNAME=$1
REPO_NAME="medchina"

echo -e "${GREEN}📊 当前状态检查${NC}"
echo ""

# 检查 Git 仓库
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ 当前目录不是 Git 仓库${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Git 仓库已初始化${NC}"

# 检查工作区状态
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  工作区有未提交的更改${NC}"
    echo ""
    echo "未提交的文件："
    git status --short
    echo ""
    read -p "是否先提交这些更改？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}📝 提交更改...${NC}"
        git add .
        git commit -m "chore: 更新部署文件和文档"
        echo -e "${GREEN}✅ 更改已提交${NC}"
    fi
fi

# 检查远程仓库
if git remote get-url origin > /dev/null 2>&1; then
    CURRENT_REMOTE=$(git remote get-url origin)
    echo -e "${YELLOW}⚠️  已存在远程仓库：${CURRENT_REMOTE}${NC}"
    echo ""
    read -p "是否要更新远程仓库地址？(y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}✅ 保持现有远程仓库配置${NC}"
        exit 0
    fi
fi

# 生成仓库 URL
REPO_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

echo ""
echo -e "${GREEN}🔧 配置远程仓库${NC}"
echo ""
echo -e "仓库 URL：${REPO_URL}"
echo ""

# 确认
read -p "是否继续配置此远程仓库？(y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}❌ 操作已取消${NC}"
    exit 0
fi

# 添加/更新远程仓库
if git remote get-url origin > /dev/null 2>&1; then
    git remote set-url origin $REPO_URL
    echo -e "${GREEN}✅ 远程仓库地址已更新${NC}"
else
    git remote add origin $REPO_URL
    echo -e "${GREEN}✅ 远程仓库已添加${NC}"
fi

# 验证
echo ""
echo -e "${GREEN}🔍 验证远程仓库配置${NC}"
git remote -v

echo ""
echo -e "${YELLOW}================================${NC}"
echo -e "${GREEN}📝 下一步操作指南${NC}"
echo -e "${YELLOW}================================${NC}"
echo ""
echo "1️⃣  在 GitHub 上创建仓库："
echo "   访问：https://github.com/new"
echo "   仓库名：${REPO_NAME}"
echo "   描述：MedChina 医疗旅游智能体系统"
echo "   可见性：Public（推荐）或 Private"
echo "   ⚠️  不要勾选 README、.gitignore、license"
echo ""
echo "2️⃣  推送代码到 GitHub："
echo "   git push -u origin main"
echo ""
echo "   ⚠️  如果提示认证，使用 Personal Access Token 而不是密码"
echo "   Token 获取：https://github.com/settings/tokens"
echo ""
echo "3️⃣  验证推送："
echo "   访问：https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
echo ""
echo -e "${GREEN}🎉 配置完成！按照上述步骤推送代码即可。${NC}"
echo ""
