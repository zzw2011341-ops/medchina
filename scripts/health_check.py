#!/usr/bin/env python3
"""
健康检查脚本
用于部署后验证应用状态
"""
import os
import sys
import requests
import time

def check_health(url: str, timeout: int = 30) -> bool:
    """检查应用健康状态"""
    try:
        response = requests.get(f"{url}/health", timeout=timeout)
        if response.status_code == 200:
            print(f"✅ 健康检查通过: {url}/health")
            return True
        else:
            print(f"❌ 健康检查失败: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def check_database(url: str, timeout: int = 30) -> bool:
    """检查数据库连接"""
    try:
        response = requests.get(f"{url}/api/db-check", timeout=timeout)
        if response.status_code == 200:
            print(f"✅ 数据库连接正常")
            return True
        else:
            print(f"❌ 数据库连接异常: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 数据库检查失败: {e}")
        return False

def main():
    # 获取应用 URL
    base_url = os.getenv("APP_URL", "http://localhost:8000")
    base_url = base_url.rstrip("/")

    print(f"🔍 检查应用状态: {base_url}")
    print("-" * 50)

    # 执行检查
    health_ok = check_health(base_url)
    db_ok = check_database(base_url)

    print("-" * 50)
    if health_ok and db_ok:
        print("🎉 所有检查通过！应用运行正常。")
        print(f"\n📍 访问地址:")
        print(f"  - 前台: {base_url}/")
        print(f"  - 后台: {base_url}/admin/")
        print(f"  - API 文档: {base_url}/docs")
        return 0
    else:
        print("⚠️  部分检查失败，请查看日志排查问题。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
