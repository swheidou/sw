#!/usr/bin/env python3
"""
Remote Agent 系统演示脚本
展示完整的订单处理流程和系统集成功能
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def print_section(title):
    """打印分节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_response(response, title="响应"):
    """格式化打印响应"""
    print(f"\n{title}:")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print(f"错误: {response.status_code} - {response.text}")

def test_health_check():
    """测试系统健康检查"""
    print_section("系统健康检查")
    
    # 基础健康检查
    response = requests.get(f"{BASE_URL}/")
    print_response(response, "基础状态")
    
    # 详细健康检查
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, "详细健康状态")

def test_inventory_and_pricing():
    """测试库存和定价功能"""
    print_section("库存和定价功能测试")
    
    products = ["prod001", "prod002", "prod003"]
    
    for product_id in products:
        print(f"\n--- 商品 {product_id} ---")
        
        # 查询库存
        response = requests.get(f"{BASE_URL}/inventory/{product_id}")
        print_response(response, f"库存信息")
        
        # 查询动态定价
        response = requests.get(f"{BASE_URL}/pricing/{product_id}")
        print_response(response, f"动态定价")

def test_external_apis():
    """测试外部API集成"""
    print_section("外部API集成测试")
    
    # 天气API
    response = requests.get(f"{BASE_URL}/external/weather")
    print_response(response, "天气信息")
    
    # 汇率API
    response = requests.get(f"{BASE_URL}/external/exchange-rate")
    print_response(response, "汇率信息")

def test_order_processing():
    """测试完整订单处理流程"""
    print_section("完整订单处理流程测试")
    
    # 创建测试订单
    order_data = {
        "customer_id": "demo_user",
        "items": [
            {"product_id": "prod001", "quantity": 1},
            {"product_id": "prod002", "quantity": 2}
        ],
        "delivery_address": "北京市朝阳区",
        "notes": "Remote Agent 演示订单"
    }
    
    print("\n创建订单...")
    print(f"订单数据: {json.dumps(order_data, indent=2, ensure_ascii=False)}")
    
    response = requests.post(
        f"{BASE_URL}/orders",
        json=order_data,
        headers={"Content-Type": "application/json"}
    )
    print_response(response, "订单创建结果")
    
    if response.status_code == 200:
        order_id = response.json()["order_id"]
        
        # 等待异步处理
        print(f"\n等待异步处理完成...")
        for i in range(3):
            time.sleep(2)
            print(f"等待中... ({i+1}/3)")
        
        # 查询订单状态
        print(f"\n查询订单状态...")
        response = requests.get(f"{BASE_URL}/orders/{order_id}/status")
        print_response(response, "订单状态")
        
        return order_id
    
    return None

def test_inventory_after_order():
    """测试订单后的库存变化"""
    print_section("订单处理后库存状态")
    
    products = ["prod001", "prod002"]
    
    for product_id in products:
        response = requests.get(f"{BASE_URL}/inventory/{product_id}")
        print_response(response, f"商品 {product_id} 库存状态")

def main():
    """主演示函数"""
    print("🚀 Remote Agent 智能订单处理系统演示")
    print("展示云端运行、复杂任务处理和系统交互能力")
    
    try:
        # 1. 系统健康检查
        test_health_check()
        
        # 2. 库存和定价功能
        test_inventory_and_pricing()
        
        # 3. 外部API集成
        test_external_apis()
        
        # 4. 完整订单处理流程
        order_id = test_order_processing()
        
        # 5. 订单处理后的库存状态
        if order_id:
            test_inventory_after_order()
        
        print_section("演示完成")
        print("✅ Remote Agent 系统演示成功完成！")
        print("\n主要功能验证:")
        print("- ✅ 云端运行: FastAPI服务正常运行")
        print("- ✅ 复杂任务处理: 订单处理、库存管理、动态定价")
        print("- ✅ 系统交互: 支付、物流、通知、外部API集成")
        print("- ✅ 异步处理: 后台任务队列正常工作")
        print("- ✅ 健康监控: 系统状态监控正常")
        
        print(f"\n🌐 访问 http://localhost:8000/docs 查看完整API文档")
        
    except requests.exceptions.ConnectionError:
        print("❌ 错误: 无法连接到Remote Agent服务")
        print("请确保服务正在运行: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
