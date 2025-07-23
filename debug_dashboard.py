#!/usr/bin/env python3
"""
Remote Agent 调试仪表板
提供系统状态监控和调试信息
"""

import requests
import json
import time
import webbrowser
import threading
from datetime import datetime
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def print_header():
    """打印调试仪表板标题"""
    print("=" * 80)
    print("🔧 Remote Agent 调试仪表板")
    print("=" * 80)
    print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 服务地址: {BASE_URL}")
    print("=" * 80)

def check_service_status():
    """检查服务状态"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ 服务状态: 正常运行")
            print(f"📝 消息: {data.get('message', 'N/A')}")
            print(f"⏱️  响应时间: {data.get('timestamp', 'N/A')}")
            return True
        else:
            print(f"❌ 服务状态: 异常 (HTTP {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 服务状态: 无法连接")
        return False
    except Exception as e:
        print(f"❌ 服务状态: 错误 - {e}")
        return False

def get_health_status():
    """获取详细健康状态"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("\n🏥 系统健康状态:")
            print(f"  总体状态: {data.get('status', 'unknown')}")
            
            services = data.get('services', {})
            for service, status in services.items():
                status_icon = "✅" if status else "❌"
                print(f"  {status_icon} {service}: {'正常' if status else '异常'}")
            
            return data.get('status') == 'healthy'
        else:
            print(f"❌ 健康检查失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查错误: {e}")
        return False

def get_system_metrics():
    """获取系统指标"""
    print("\n📊 系统指标:")
    
    # 获取库存状态
    products = ["prod001", "prod002", "prod003"]
    for product_id in products:
        try:
            response = requests.get(f"{BASE_URL}/inventory/{product_id}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"  📦 {data['product_name']} ({product_id}):")
                print(f"     可用库存: {data['available_quantity']}")
                print(f"     预留库存: {data['reserved_quantity']}")
                print(f"     单价: ¥{data['unit_price']}")
        except Exception as e:
            print(f"  ❌ {product_id}: 获取失败 - {e}")

def get_external_services_status():
    """获取外部服务状态"""
    print("\n🌐 外部服务状态:")
    
    # 天气服务
    try:
        response = requests.get(f"{BASE_URL}/external/weather", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"  🌤️  天气服务: 正常")
            print(f"     位置: {data['location']}")
            print(f"     温度: {data['temperature']}°C")
            print(f"     天气: {data['weather_condition']}")
            print(f"     适合配送: {'是' if data['suitable_for_delivery'] else '否'}")
        else:
            print(f"  ❌ 天气服务: HTTP {response.status_code}")
    except Exception as e:
        print(f"  ❌ 天气服务: {e}")
    
    # 汇率服务
    try:
        response = requests.get(f"{BASE_URL}/external/exchange-rate", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"  💱 汇率服务: 正常")
            print(f"     USD/CNY: {data['usd_to_cny']}")
        else:
            print(f"  ❌ 汇率服务: HTTP {response.status_code}")
    except Exception as e:
        print(f"  ❌ 汇率服务: {e}")

def open_debug_pages():
    """打开调试页面"""
    print("\n🌐 正在打开调试页面...")
    
    pages = [
        ("API文档 (Swagger UI)", f"{BASE_URL}/docs"),
        ("API规范 (OpenAPI JSON)", f"{BASE_URL}/openapi.json"),
        ("ReDoc文档", f"{BASE_URL}/redoc")
    ]
    
    for name, url in pages:
        print(f"  📄 {name}: {url}")
        try:
            # 在新线程中打开浏览器，避免阻塞
            threading.Thread(target=lambda u=url: webbrowser.open(u), daemon=True).start()
            time.sleep(1)  # 避免同时打开太多页面
        except Exception as e:
            print(f"     ⚠️  无法自动打开浏览器: {e}")
            print(f"     请手动访问: {url}")

def create_test_order():
    """创建测试订单"""
    print("\n🧪 创建测试订单...")
    
    test_order = {
        "customer_id": "debug_user",
        "items": [
            {"product_id": "prod001", "quantity": 1}
        ],
        "delivery_address": "调试测试地址",
        "notes": "调试仪表板测试订单"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/orders",
            json=test_order,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ 测试订单创建成功!")
            print(f"     订单ID: {data['order_id']}")
            print(f"     状态: {data['status']}")
            print(f"     金额: ¥{data['total_amount']}")
            
            # 等待一下异步处理
            time.sleep(3)
            
            # 查询订单状态
            status_response = requests.get(f"{BASE_URL}/orders/{data['order_id']}/status")
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"     当前状态: {status_data['status']}")
            
            return data['order_id']
        else:
            print(f"  ❌ 测试订单创建失败: HTTP {response.status_code}")
            print(f"     错误: {response.text}")
            return None
    except Exception as e:
        print(f"  ❌ 测试订单创建错误: {e}")
        return None

def monitor_system():
    """系统监控模式"""
    print("\n🔄 进入系统监控模式 (按 Ctrl+C 退出)")
    
    try:
        while True:
            print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - 系统状态检查")
            
            # 快速健康检查
            health_ok = get_health_status()
            
            if health_ok:
                print("  ✅ 系统运行正常")
            else:
                print("  ⚠️  系统状态异常，请检查日志")
            
            # 等待30秒
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n👋 退出监控模式")

def show_menu():
    """显示菜单"""
    print("\n📋 调试选项:")
    print("  1. 📊 查看系统状态")
    print("  2. 🌐 打开调试页面")
    print("  3. 🧪 创建测试订单")
    print("  4. 🔄 系统监控模式")
    print("  5. 📈 查看性能指标")
    print("  6. 🚪 退出")
    print("-" * 40)

def show_performance_metrics():
    """显示性能指标"""
    print("\n📈 性能指标测试...")
    
    # 简单的响应时间测试
    endpoints = [
        ("健康检查", "/health"),
        ("库存查询", "/inventory/prod001"),
        ("动态定价", "/pricing/prod001"),
        ("天气信息", "/external/weather")
    ]
    
    for name, endpoint in endpoints:
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
            
            if response.status_code == 200:
                print(f"  ✅ {name}: {response_time:.2f}ms")
            else:
                print(f"  ❌ {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"  ❌ {name}: 错误 - {e}")

def main():
    """主函数"""
    print_header()
    
    # 初始状态检查
    if not check_service_status():
        print("\n❌ 服务未运行，请先启动Remote Agent服务:")
        print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    get_health_status()
    get_system_metrics()
    get_external_services_status()
    
    while True:
        show_menu()
        try:
            choice = input("请选择操作 (1-6): ").strip()
            
            if choice == "1":
                print_header()
                check_service_status()
                get_health_status()
                get_system_metrics()
                get_external_services_status()
            
            elif choice == "2":
                open_debug_pages()
            
            elif choice == "3":
                create_test_order()
            
            elif choice == "4":
                monitor_system()
            
            elif choice == "5":
                show_performance_metrics()
            
            elif choice == "6":
                print("\n👋 感谢使用Remote Agent调试仪表板!")
                break
            
            else:
                print("❌ 无效选择，请输入1-6")
                
        except KeyboardInterrupt:
            print("\n\n👋 感谢使用Remote Agent调试仪表板!")
            break
        except Exception as e:
            print(f"❌ 操作错误: {e}")

if __name__ == "__main__":
    main()
