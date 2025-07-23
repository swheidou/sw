#!/usr/bin/env python3
"""
Remote Agent 部署验证脚本
验证本地部署是否成功
"""

import requests
import time
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_header():
    """打印验证标题"""
    print("=" * 80)
    print("🔍 Remote Agent 部署验证")
    print("=" * 80)
    print(f"⏰ 验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 服务地址: {BASE_URL}")
    print("=" * 80)

def check_service_connectivity():
    """检查服务连通性"""
    print("\n1. 🔗 检查服务连通性...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 服务正常运行")
            print(f"   📝 消息: {data.get('message', 'N/A')}")
            return True
        else:
            print(f"   ❌ 服务响应异常: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ 无法连接到服务")
        print(f"   💡 请确保服务正在运行: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"   ❌ 连接错误: {e}")
        return False

def check_health_status():
    """检查健康状态"""
    print("\n2. 🏥 检查系统健康状态...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            overall_status = data.get('status', 'unknown')
            
            if overall_status == 'healthy':
                print(f"   ✅ 系统健康状态: {overall_status}")
            else:
                print(f"   ⚠️  系统健康状态: {overall_status}")
            
            services = data.get('services', {})
            for service, status in services.items():
                status_icon = "✅" if status else "❌"
                print(f"   {status_icon} {service}: {'正常' if status else '异常'}")
            
            return overall_status == 'healthy'
        else:
            print(f"   ❌ 健康检查失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 健康检查错误: {e}")
        return False

def check_api_endpoints():
    """检查API端点"""
    print("\n3. 🔌 检查API端点...")
    
    endpoints = [
        ("库存查询", "/inventory/prod001"),
        ("动态定价", "/pricing/prod001"),
        ("天气信息", "/external/weather"),
        ("汇率信息", "/external/exchange-rate")
    ]
    
    success_count = 0
    for name, endpoint in endpoints:
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                print(f"   ✅ {name}: {response_time:.0f}ms")
                success_count += 1
            else:
                print(f"   ❌ {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name}: 错误 - {e}")
    
    print(f"   📊 成功率: {success_count}/{len(endpoints)} ({success_count/len(endpoints)*100:.0f}%)")
    return success_count == len(endpoints)

def test_order_creation():
    """测试订单创建"""
    print("\n4. 🛒 测试订单创建...")
    
    test_order = {
        "customer_id": "verify_user",
        "items": [
            {"product_id": "prod001", "quantity": 1}
        ],
        "delivery_address": "验证测试地址",
        "notes": "部署验证测试订单"
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/orders",
            json=test_order,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 订单创建成功: {response_time:.0f}ms")
            print(f"   📋 订单ID: {data.get('order_id')}")
            print(f"   💰 订单金额: ¥{data.get('total_amount')}")
            
            # 等待异步处理
            time.sleep(3)
            
            # 查询订单状态
            order_id = data.get('order_id')
            if order_id:
                status_response = requests.get(f"{BASE_URL}/orders/{order_id}/status", timeout=5)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"   📊 订单状态: {status_data.get('status')}")
                    return True
            
            return True
        else:
            print(f"   ❌ 订单创建失败: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   📝 错误详情: {error_data.get('detail', '未知错误')}")
            except:
                pass
            return False
    except Exception as e:
        print(f"   ❌ 订单创建错误: {e}")
        return False

def check_documentation():
    """检查文档页面"""
    print("\n5. 📚 检查文档页面...")
    
    doc_pages = [
        ("Swagger UI", "/docs"),
        ("ReDoc", "/redoc"),
        ("OpenAPI规范", "/openapi.json")
    ]
    
    success_count = 0
    for name, endpoint in doc_pages:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {name}: 可访问")
                success_count += 1
            else:
                print(f"   ❌ {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name}: 错误 - {e}")
    
    return success_count == len(doc_pages)

def print_summary(results):
    """打印验证总结"""
    print("\n" + "=" * 80)
    print("📋 验证总结")
    print("=" * 80)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {status} {test_name}")
    
    print(f"\n📊 总体结果: {passed_tests}/{total_tests} 项测试通过")
    
    if passed_tests == total_tests:
        print("🎉 恭喜！Remote Agent 部署验证成功！")
        print("\n🌐 可用的访问地址:")
        print(f"   • Swagger UI: {BASE_URL}/docs")
        print(f"   • ReDoc文档: {BASE_URL}/redoc")
        print(f"   • 健康检查: {BASE_URL}/health")
        print("\n🛠️  调试工具:")
        print("   • python test_demo.py          # 功能演示")
        print("   • python performance_test.py   # 性能测试")
        print("   • python debug_dashboard.py    # 调试仪表板")
        print("   • python monitor.py            # 实时监控")
        return True
    else:
        print("⚠️  部分测试失败，请检查服务状态")
        print("\n🔧 故障排除建议:")
        print("   1. 确保服务正在运行")
        print("   2. 检查端口8000是否被占用")
        print("   3. 验证所有依赖是否正确安装")
        print("   4. 查看服务日志获取详细错误信息")
        return False

def main():
    """主验证函数"""
    print_header()
    
    # 执行各项验证
    results = {
        "服务连通性": check_service_connectivity(),
        "系统健康状态": check_health_status(),
        "API端点": check_api_endpoints(),
        "订单创建": test_order_creation(),
        "文档页面": check_documentation()
    }
    
    # 打印总结
    success = print_summary(results)
    
    # 返回适当的退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
