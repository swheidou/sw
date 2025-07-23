#!/usr/bin/env python3
"""
Remote Agent 实时监控脚本
"""

import requests
import time
import json
from datetime import datetime
import os

BASE_URL = "http://localhost:8000"

def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_system_status():
    """获取系统状态"""
    try:
        # 健康检查
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        health_data = health_response.json() if health_response.status_code == 200 else {}
        
        # 库存状态
        inventory_data = {}
        for product_id in ["prod001", "prod002", "prod003"]:
            try:
                inv_response = requests.get(f"{BASE_URL}/inventory/{product_id}", timeout=3)
                if inv_response.status_code == 200:
                    inventory_data[product_id] = inv_response.json()
            except:
                pass
        
        # 外部服务状态
        external_status = {}
        try:
            weather_response = requests.get(f"{BASE_URL}/external/weather", timeout=5)
            external_status['weather'] = weather_response.status_code == 200
        except:
            external_status['weather'] = False
            
        try:
            rate_response = requests.get(f"{BASE_URL}/external/exchange-rate", timeout=5)
            external_status['exchange_rate'] = rate_response.status_code == 200
        except:
            external_status['exchange_rate'] = False
        
        return {
            'health': health_data,
            'inventory': inventory_data,
            'external': external_status,
            'timestamp': datetime.now()
        }
    except Exception as e:
        return {
            'error': str(e),
            'timestamp': datetime.now()
        }

def display_status(status_data):
    """显示状态信息"""
    clear_screen()
    
    print("🚀 Remote Agent 实时监控")
    print("=" * 80)
    print(f"⏰ 更新时间: {status_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    if 'error' in status_data:
        print(f"❌ 连接错误: {status_data['error']}")
        print("请确保Remote Agent服务正在运行")
        return
    
    # 系统健康状态
    health = status_data.get('health', {})
    overall_status = health.get('status', 'unknown')
    
    print(f"\n🏥 系统健康状态: ", end="")
    if overall_status == 'healthy':
        print("✅ 健康")
    else:
        print("❌ 异常")
    
    services = health.get('services', {})
    for service, status in services.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {service}: {'正常' if status else '异常'}")
    
    # 库存状态
    print(f"\n📦 库存状态:")
    inventory = status_data.get('inventory', {})
    if inventory:
        for product_id, data in inventory.items():
            available = data.get('available_quantity', 0)
            reserved = data.get('reserved_quantity', 0)
            name = data.get('product_name', product_id)
            price = data.get('unit_price', 0)
            
            # 库存警告
            warning = ""
            if available < 10:
                warning = " ⚠️ 库存不足"
            elif available < 5:
                warning = " 🚨 库存严重不足"
            
            print(f"   📱 {name} ({product_id})")
            print(f"      可用: {available} | 预留: {reserved} | 价格: ¥{price}{warning}")
    else:
        print("   ❌ 无法获取库存信息")
    
    # 外部服务状态
    print(f"\n🌐 外部服务状态:")
    external = status_data.get('external', {})
    
    weather_status = "✅ 正常" if external.get('weather') else "❌ 异常"
    rate_status = "✅ 正常" if external.get('exchange_rate') else "❌ 异常"
    
    print(f"   🌤️  天气服务: {weather_status}")
    print(f"   💱 汇率服务: {rate_status}")
    
    # 快捷操作提示
    print(f"\n🔧 快捷操作:")
    print(f"   • 按 Ctrl+C 退出监控")
    print(f"   • API文档: http://localhost:8000/docs")
    print(f"   • 健康检查: http://localhost:8000/health")
    
    print("\n" + "=" * 80)

def main():
    """主监控循环"""
    print("🚀 启动Remote Agent实时监控...")
    print("按 Ctrl+C 退出")
    time.sleep(2)
    
    try:
        while True:
            status_data = get_system_status()
            display_status(status_data)
            
            # 等待10秒后刷新
            for i in range(10, 0, -1):
                print(f"\r下次刷新: {i}秒", end="", flush=True)
                time.sleep(1)
            
    except KeyboardInterrupt:
        clear_screen()
        print("\n👋 Remote Agent监控已停止")
        print("感谢使用!")

if __name__ == "__main__":
    main()
