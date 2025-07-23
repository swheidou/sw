"""
订单服务 - 处理订单相关业务逻辑
"""

import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import structlog

from app.models.schemas import OrderItemRequest, OrderStatusEnum

logger = structlog.get_logger()


class OrderService:
    """订单服务类"""
    
    def __init__(self):
        # 模拟数据库存储
        self.orders: Dict[str, Dict] = {}
        self.order_items: Dict[str, List[Dict]] = {}
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            # 模拟数据库连接检查
            await asyncio.sleep(0.1)
            return True
        except Exception as e:
            logger.error("订单服务健康检查失败", error=str(e))
            return False
    
    async def create_order(
        self, 
        customer_id: str, 
        items: List[OrderItemRequest],
        total_amount: float,
        currency: str = "CNY"
    ) -> Dict[str, Any]:
        """创建订单"""
        try:
            order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            now = datetime.now()
            
            # 计算预计配送时间（3-7天）
            estimated_delivery = (now + timedelta(days=5)).strftime("%Y-%m-%d")
            
            order = {
                "order_id": order_id,
                "customer_id": customer_id,
                "status": OrderStatusEnum.CREATED.value,
                "total_amount": total_amount,
                "currency": currency,
                "created_at": now,
                "updated_at": now,
                "estimated_delivery": estimated_delivery,
                "tracking_number": None
            }
            
            # 存储订单
            self.orders[order_id] = order
            
            # 存储订单商品
            order_items = []
            for item in items:
                order_items.append({
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": 0.0  # 将在定价服务中计算
                })
            
            self.order_items[order_id] = order_items
            
            logger.info("订单创建成功", order_id=order_id, customer_id=customer_id)
            return order
            
        except Exception as e:
            logger.error("创建订单失败", error=str(e))
            raise
    
    async def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """获取订单信息"""
        try:
            order = self.orders.get(order_id)
            if order:
                # 添加订单商品信息
                order["items"] = self.order_items.get(order_id, [])
            return order
        except Exception as e:
            logger.error("获取订单失败", order_id=order_id, error=str(e))
            raise
    
    async def update_order_status(self, order_id: str, status: str) -> bool:
        """更新订单状态"""
        try:
            if order_id not in self.orders:
                logger.warning("订单不存在", order_id=order_id)
                return False
            
            self.orders[order_id]["status"] = status
            self.orders[order_id]["updated_at"] = datetime.now()
            
            # 如果是发货状态，生成跟踪号
            if status == OrderStatusEnum.SHIPPED.value:
                tracking_number = f"TRK-{uuid.uuid4().hex[:10].upper()}"
                self.orders[order_id]["tracking_number"] = tracking_number
            
            logger.info("订单状态更新成功", order_id=order_id, status=status)
            return True
            
        except Exception as e:
            logger.error("更新订单状态失败", order_id=order_id, error=str(e))
            raise
    
    async def get_orders_by_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """获取客户的所有订单"""
        try:
            customer_orders = []
            for order in self.orders.values():
                if order["customer_id"] == customer_id:
                    order_with_items = order.copy()
                    order_with_items["items"] = self.order_items.get(order["order_id"], [])
                    customer_orders.append(order_with_items)
            
            # 按创建时间倒序排列
            customer_orders.sort(key=lambda x: x["created_at"], reverse=True)
            return customer_orders
            
        except Exception as e:
            logger.error("获取客户订单失败", customer_id=customer_id, error=str(e))
            raise
    
    async def cancel_order(self, order_id: str, reason: str = "") -> bool:
        """取消订单"""
        try:
            if order_id not in self.orders:
                logger.warning("订单不存在", order_id=order_id)
                return False
            
            current_status = self.orders[order_id]["status"]
            
            # 只有特定状态的订单可以取消
            cancellable_statuses = [
                OrderStatusEnum.CREATED.value,
                OrderStatusEnum.PAID.value,
                OrderStatusEnum.PROCESSING.value
            ]
            
            if current_status not in cancellable_statuses:
                logger.warning("订单状态不允许取消", order_id=order_id, status=current_status)
                return False
            
            self.orders[order_id]["status"] = OrderStatusEnum.CANCELLED.value
            self.orders[order_id]["updated_at"] = datetime.now()
            self.orders[order_id]["cancel_reason"] = reason
            
            logger.info("订单取消成功", order_id=order_id, reason=reason)
            return True
            
        except Exception as e:
            logger.error("取消订单失败", order_id=order_id, error=str(e))
            raise
    
    async def get_order_statistics(self) -> Dict[str, Any]:
        """获取订单统计信息"""
        try:
            total_orders = len(self.orders)
            status_counts = {}
            total_revenue = 0.0
            
            for order in self.orders.values():
                status = order["status"]
                status_counts[status] = status_counts.get(status, 0) + 1
                
                if status in [OrderStatusEnum.PAID.value, OrderStatusEnum.PROCESSING.value, 
                             OrderStatusEnum.SHIPPED.value, OrderStatusEnum.DELIVERED.value]:
                    total_revenue += order["total_amount"]
            
            return {
                "total_orders": total_orders,
                "status_distribution": status_counts,
                "total_revenue": total_revenue,
                "average_order_value": total_revenue / max(total_orders, 1)
            }
            
        except Exception as e:
            logger.error("获取订单统计失败", error=str(e))
            raise
