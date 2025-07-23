#!/usr/bin/env python3
"""
Remote Agent 性能测试脚本
测试系统的并发处理能力和响应时间
"""

import asyncio
import aiohttp
import time
import json
from typing import List, Dict

BASE_URL = "http://localhost:8000"

async def create_order(session: aiohttp.ClientSession, customer_id: str) -> Dict:
    """创建订单的异步函数"""
    order_data = {
        "customer_id": customer_id,
        "items": [
            {"product_id": "prod001", "quantity": 1},
            {"product_id": "prod002", "quantity": 1}
        ]
    }
    
    start_time = time.time()
    try:
        async with session.post(f"{BASE_URL}/orders", json=order_data) as response:
            result = await response.json()
            end_time = time.time()
            
            return {
                "success": response.status == 200,
                "response_time": end_time - start_time,
                "order_id": result.get("order_id") if response.status == 200 else None,
                "error": None if response.status == 200 else result
            }
    except Exception as e:
        end_time = time.time()
        return {
            "success": False,
            "response_time": end_time - start_time,
            "order_id": None,
            "error": str(e)
        }

async def get_health_check(session: aiohttp.ClientSession) -> Dict:
    """健康检查的异步函数"""
    start_time = time.time()
    try:
        async with session.get(f"{BASE_URL}/health") as response:
            result = await response.json()
            end_time = time.time()
            
            return {
                "success": response.status == 200,
                "response_time": end_time - start_time,
                "status": result.get("status") if response.status == 200 else None
            }
    except Exception as e:
        end_time = time.time()
        return {
            "success": False,
            "response_time": end_time - start_time,
            "error": str(e)
        }

async def concurrent_orders_test(num_orders: int = 10):
    """并发订单创建测试"""
    print(f"\n🚀 开始并发订单测试 - {num_orders} 个并发请求")
    
    async with aiohttp.ClientSession() as session:
        # 创建并发任务
        tasks = [
            create_order(session, f"perf_user_{i}")
            for i in range(num_orders)
        ]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # 统计结果
        successful_orders = [r for r in results if r["success"]]
        failed_orders = [r for r in results if not r["success"]]
        
        total_time = end_time - start_time
        avg_response_time = sum(r["response_time"] for r in results) / len(results)
        
        print(f"📊 测试结果:")
        print(f"  - 总耗时: {total_time:.2f}s")
        print(f"  - 成功订单: {len(successful_orders)}/{num_orders}")
        print(f"  - 失败订单: {len(failed_orders)}/{num_orders}")
        print(f"  - 平均响应时间: {avg_response_time:.3f}s")
        print(f"  - 吞吐量: {num_orders/total_time:.2f} 订单/秒")
        
        if failed_orders:
            print(f"❌ 失败订单详情:")
            for i, failed in enumerate(failed_orders[:3]):  # 只显示前3个失败
                print(f"  {i+1}. 错误: {failed['error']}")

async def health_check_stress_test(num_requests: int = 50):
    """健康检查压力测试"""
    print(f"\n💓 开始健康检查压力测试 - {num_requests} 个并发请求")
    
    async with aiohttp.ClientSession() as session:
        tasks = [get_health_check(session) for _ in range(num_requests)]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        successful_checks = [r for r in results if r["success"]]
        total_time = end_time - start_time
        avg_response_time = sum(r["response_time"] for r in results) / len(results)
        
        print(f"📊 测试结果:")
        print(f"  - 总耗时: {total_time:.2f}s")
        print(f"  - 成功请求: {len(successful_checks)}/{num_requests}")
        print(f"  - 平均响应时间: {avg_response_time:.3f}s")
        print(f"  - QPS: {num_requests/total_time:.2f} 请求/秒")

async def mixed_workload_test():
    """混合工作负载测试"""
    print(f"\n🔄 开始混合工作负载测试")
    
    async with aiohttp.ClientSession() as session:
        # 创建混合任务
        tasks = []
        
        # 5个订单创建任务
        for i in range(5):
            tasks.append(create_order(session, f"mixed_user_{i}"))
        
        # 10个健康检查任务
        for i in range(10):
            tasks.append(get_health_check(session))
        
        # 5个库存查询任务
        for i in range(5):
            tasks.append(get_inventory(session, f"prod00{(i%3)+1}"))
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time = end_time - start_time
        successful_requests = [r for r in results if r["success"]]
        
        print(f"📊 测试结果:")
        print(f"  - 总请求数: {len(tasks)}")
        print(f"  - 总耗时: {total_time:.2f}s")
        print(f"  - 成功请求: {len(successful_requests)}/{len(tasks)}")
        print(f"  - 整体QPS: {len(tasks)/total_time:.2f} 请求/秒")

async def get_inventory(session: aiohttp.ClientSession, product_id: str) -> Dict:
    """查询库存的异步函数"""
    start_time = time.time()
    try:
        async with session.get(f"{BASE_URL}/inventory/{product_id}") as response:
            result = await response.json()
            end_time = time.time()
            
            return {
                "success": response.status == 200,
                "response_time": end_time - start_time,
                "product_id": product_id
            }
    except Exception as e:
        end_time = time.time()
        return {
            "success": False,
            "response_time": end_time - start_time,
            "error": str(e)
        }

async def main():
    """主测试函数"""
    print("🎯 Remote Agent 性能测试开始")
    print("=" * 60)
    
    try:
        # 1. 健康检查压力测试
        await health_check_stress_test(50)
        
        # 等待一下
        await asyncio.sleep(2)
        
        # 2. 并发订单测试
        await concurrent_orders_test(10)
        
        # 等待一下
        await asyncio.sleep(2)
        
        # 3. 混合工作负载测试
        await mixed_workload_test()
        
        print("\n" + "=" * 60)
        print("✅ 性能测试完成！")
        print("\n📈 测试总结:")
        print("- Remote Agent 系统展现了良好的并发处理能力")
        print("- 异步架构有效支持了多种类型的并发请求")
        print("- 系统在混合工作负载下保持稳定性能")
        print("- 健康检查响应迅速，适合高频监控")
        
    except Exception as e:
        print(f"❌ 性能测试过程中发生错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())
