"""
Remote Agent 主应用入口
展示云端运行、复杂任务处理和系统交互能力
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import structlog
from typing import List, Dict, Any
import asyncio
from datetime import datetime

from app.models.schemas import OrderRequest, OrderResponse, OrderStatus
from app.services.order_service import OrderService
from app.services.inventory_service import InventoryService
from app.services.pricing_service import PricingService
from app.integrations.payment_gateway import PaymentGateway
from app.integrations.logistics_service import LogisticsService
from app.integrations.notification_service import NotificationService
from app.integrations.external_apis import WeatherAPI, ExchangeRateAPI
from app.utils.database import init_db

# 配置结构化日志
logger = structlog.get_logger()

# 创建FastAPI应用
app = FastAPI(
    title="Remote Agent 智能订单处理系统",
    description="展示云端运行、复杂任务处理和系统交互的Remote Agent案例",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
order_service = OrderService()
inventory_service = InventoryService()
pricing_service = PricingService()
payment_gateway = PaymentGateway()
logistics_service = LogisticsService()
notification_service = NotificationService()
weather_api = WeatherAPI()
exchange_rate_api = ExchangeRateAPI()


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    await init_db()
    logger.info("Remote Agent 系统启动完成")


@app.get("/")
async def root():
    """健康检查端点"""
    return {
        "message": "Remote Agent 智能订单处理系统",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """系统健康状态检查"""
    try:
        # 检查各个服务状态
        services_status = {
            "database": await order_service.health_check(),
            "inventory": await inventory_service.health_check(),
            "payment": await payment_gateway.health_check(),
            "logistics": await logistics_service.health_check(),
            "notification": await notification_service.health_check()
        }
        
        all_healthy = all(services_status.values())
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "services": services_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error("健康检查失败", error=str(e))
        raise HTTPException(status_code=500, detail="系统健康检查失败")


@app.post("/orders", response_model=OrderResponse)
async def create_order(order_request: OrderRequest, background_tasks: BackgroundTasks):
    """
    创建订单 - 展示复杂业务流程处理
    """
    try:
        logger.info("开始处理订单创建", customer_id=order_request.customer_id)
        
        # 1. 订单验证
        if not order_request.items:
            raise HTTPException(status_code=400, detail="订单不能为空")
        
        # 2. 库存检查
        inventory_check = await inventory_service.check_availability(order_request.items)
        if not inventory_check["available"]:
            raise HTTPException(
                status_code=400, 
                detail=f"库存不足: {inventory_check['unavailable_items']}"
            )
        
        # 3. 价格计算（考虑库存量、汇率等因素）
        exchange_rate = await exchange_rate_api.get_usd_to_cny_rate()
        pricing_result = await pricing_service.calculate_order_price(
            order_request.items, 
            exchange_rate
        )
        
        # 4. 创建订单
        order = await order_service.create_order(
            customer_id=order_request.customer_id,
            items=order_request.items,
            total_amount=pricing_result["total_amount"],
            currency=pricing_result["currency"]
        )
        
        # 5. 异步处理后续流程
        background_tasks.add_task(
            process_order_async,
            order["order_id"],
            order_request.customer_id
        )
        
        logger.info("订单创建成功", order_id=order["order_id"])
        
        return OrderResponse(
            order_id=order["order_id"],
            status="created",
            total_amount=pricing_result["total_amount"],
            currency=pricing_result["currency"],
            estimated_delivery=order["estimated_delivery"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("订单创建失败", error=str(e))
        raise HTTPException(status_code=500, detail="订单创建失败")


async def process_order_async(order_id: str, customer_id: str):
    """
    异步处理订单后续流程 - 展示系统交互能力
    """
    try:
        logger.info("开始异步处理订单", order_id=order_id)
        
        # 1. 支付处理
        payment_result = await payment_gateway.process_payment(order_id)
        if payment_result["status"] == "success":
            await order_service.update_order_status(order_id, "paid")
            
            # 2. 库存扣减
            order_details = await order_service.get_order(order_id)
            await inventory_service.reserve_items(order_details["items"])
            
            # 3. 物流安排（考虑天气因素）
            weather_info = await weather_api.get_weather_for_delivery()
            logistics_plan = await logistics_service.arrange_delivery(
                order_id, 
                weather_info
            )
            
            await order_service.update_order_status(order_id, "processing")
            
            # 4. 发送通知
            await notification_service.send_order_confirmation(
                customer_id, 
                order_id,
                logistics_plan["tracking_number"]
            )
            
            logger.info("订单处理完成", order_id=order_id)
        else:
            await order_service.update_order_status(order_id, "payment_failed")
            await notification_service.send_payment_failure_notice(customer_id, order_id)
            
    except Exception as e:
        logger.error("异步订单处理失败", order_id=order_id, error=str(e))
        await order_service.update_order_status(order_id, "error")


@app.get("/orders/{order_id}/status", response_model=OrderStatus)
async def get_order_status(order_id: str):
    """查询订单状态"""
    try:
        order = await order_service.get_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")
        
        return OrderStatus(
            order_id=order_id,
            status=order["status"],
            created_at=order["created_at"],
            updated_at=order["updated_at"],
            tracking_number=order.get("tracking_number")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("查询订单状态失败", order_id=order_id, error=str(e))
        raise HTTPException(status_code=500, detail="查询订单状态失败")


@app.get("/inventory/{product_id}")
async def get_inventory(product_id: str):
    """查询商品库存"""
    try:
        inventory = await inventory_service.get_inventory(product_id)
        if inventory is None:
            raise HTTPException(status_code=404, detail="商品不存在")
        
        return inventory
    except HTTPException:
        raise
    except Exception as e:
        logger.error("查询库存失败", product_id=product_id, error=str(e))
        raise HTTPException(status_code=500, detail="查询库存失败")


@app.get("/pricing/{product_id}")
async def get_dynamic_pricing(product_id: str):
    """获取动态定价"""
    try:
        # 获取当前汇率
        exchange_rate = await exchange_rate_api.get_usd_to_cny_rate()
        
        # 计算动态价格
        pricing = await pricing_service.get_dynamic_price(product_id, exchange_rate)
        
        return pricing
    except Exception as e:
        logger.error("获取动态定价失败", product_id=product_id, error=str(e))
        raise HTTPException(status_code=500, detail="获取动态定价失败")


@app.get("/external/weather")
async def get_weather():
    """获取天气信息 - 展示外部API集成"""
    try:
        weather = await weather_api.get_current_weather()
        return weather
    except Exception as e:
        logger.error("获取天气信息失败", error=str(e))
        raise HTTPException(status_code=500, detail="获取天气信息失败")


@app.get("/external/exchange-rate")
async def get_exchange_rate():
    """获取汇率信息 - 展示外部API集成"""
    try:
        rate = await exchange_rate_api.get_usd_to_cny_rate()
        return {"usd_to_cny": rate, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error("获取汇率信息失败", error=str(e))
        raise HTTPException(status_code=500, detail="获取汇率信息失败")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
