#!/usr/bin/env python3
"""
快速打开Remote Agent调试页面
"""

import webbrowser
import time
import requests
import sys

BASE_URL = "http://localhost:8000"

def check_service():
    """检查服务是否运行"""
    try:
        response = requests.get(BASE_URL, timeout=3)
        return response.status_code == 200
    except:
        return False

def open_pages():
    """打开所有调试页面"""
    print("🚀 Remote Agent 调试页面启动器")
    print("=" * 50)
    
    # 检查服务状态
    print("🔍 检查服务状态...")
    if not check_service():
        print("❌ Remote Agent 服务未运行!")
        print("请先启动服务: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    print("✅ 服务运行正常")
    print()
    
    # 定义要打开的页面
    pages = [
        ("📚 API文档 (Swagger UI)", f"{BASE_URL}/docs"),
        ("📖 ReDoc文档", f"{BASE_URL}/redoc"),
        ("💚 健康检查", f"{BASE_URL}/health"),
        ("🔧 OpenAPI规范", f"{BASE_URL}/openapi.json")
    ]
    
    print("🌐 正在打开调试页面...")
    
    for name, url in pages:
        print(f"  {name}: {url}")
        try:
            webbrowser.open(url)
            time.sleep(1)  # 避免同时打开太多页面
        except Exception as e:
            print(f"    ⚠️  无法打开: {e}")
    
    print()
    print("✅ 所有调试页面已打开!")
    print()
    print("🎯 主要功能:")
    print("  • Swagger UI: 交互式API测试")
    print("  • ReDoc: 美观的API文档")
    print("  • 健康检查: 实时系统状态")
    print("  • OpenAPI: API规范下载")
    print()
    print("🧪 快速测试命令:")
    print("  # 创建测试订单")
    print(f"  curl -X POST '{BASE_URL}/orders' \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"customer_id\": \"test\", \"items\": [{\"product_id\": \"prod001\", \"quantity\": 1}]}'")
    print()
    print("  # 查看库存")
    print(f"  curl '{BASE_URL}/inventory/prod001'")
    print()
    print("  # 获取动态定价")
    print(f"  curl '{BASE_URL}/pricing/prod001'")

if __name__ == "__main__":
    open_pages()
