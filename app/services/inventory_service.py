"""
库存服务 - 处理库存管理相关业务逻辑
"""

import asyncio
from typing import Dict, List, Optional, Any
import structlog
from datetime import datetime

from app.models.schemas import OrderItemRequest, InventoryItem

logger = structlog.get_logger()


class InventoryService:
    """库存服务类"""
    
    def __init__(self):
        # 模拟库存数据
        self.inventory: Dict[str, Dict] = {
            "prod001": {
                "product_id": "prod001",
                "product_name": "智能手机",
                "available_quantity": 100,
                "reserved_quantity": 0,
                "unit_price": 2999.00,
                "currency": "CNY",
                "reorder_level": 20,
                "last_updated": datetime.now()
            },
            "prod002": {
                "product_id": "prod002",
                "product_name": "无线耳机",
                "available_quantity": 50,
                "reserved_quantity": 0,
                "unit_price": 299.00,
                "currency": "CNY",
                "reorder_level": 10,
                "last_updated": datetime.now()
            },
            "prod003": {
                "product_id": "prod003",
                "product_name": "智能手表",
                "available_quantity": 30,
                "reserved_quantity": 0,
                "unit_price": 1999.00,
                "currency": "CNY",
                "reorder_level": 5,
                "last_updated": datetime.now()
            }
        }
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            await asyncio.sleep(0.1)
            return True
        except Exception as e:
            logger.error("库存服务健康检查失败", error=str(e))
            return False
    
    async def get_inventory(self, product_id: str) -> Optional[InventoryItem]:
        """获取商品库存信息"""
        try:
            inventory_data = self.inventory.get(product_id)
            if not inventory_data:
                return None
            
            return InventoryItem(**inventory_data)
            
        except Exception as e:
            logger.error("获取库存信息失败", product_id=product_id, error=str(e))
            raise
    
    async def check_availability(self, items: List[OrderItemRequest]) -> Dict[str, Any]:
        """检查商品库存可用性"""
        try:
            available = True
            unavailable_items = []
            availability_details = []
            
            for item in items:
                inventory_data = self.inventory.get(item.product_id)
                
                if not inventory_data:
                    available = False
                    unavailable_items.append({
                        "product_id": item.product_id,
                        "reason": "商品不存在"
                    })
                    continue
                
                available_qty = inventory_data["available_quantity"]
                
                if available_qty < item.quantity:
                    available = False
                    unavailable_items.append({
                        "product_id": item.product_id,
                        "requested": item.quantity,
                        "available": available_qty,
                        "reason": "库存不足"
                    })
                
                availability_details.append({
                    "product_id": item.product_id,
                    "product_name": inventory_data["product_name"],
                    "requested": item.quantity,
                    "available": available_qty,
                    "sufficient": available_qty >= item.quantity
                })
            
            result = {
                "available": available,
                "unavailable_items": unavailable_items,
                "details": availability_details
            }
            
            logger.info("库存检查完成", available=available, items_count=len(items))
            return result
            
        except Exception as e:
            logger.error("库存检查失败", error=str(e))
            raise
    
    async def reserve_items(self, items: List[Dict[str, Any]]) -> bool:
        """预留库存"""
        try:
            for item in items:
                product_id = item["product_id"]
                quantity = item["quantity"]
                
                if product_id not in self.inventory:
                    logger.error("预留库存失败：商品不存在", product_id=product_id)
                    return False
                
                inventory_data = self.inventory[product_id]
                
                if inventory_data["available_quantity"] < quantity:
                    logger.error("预留库存失败：库存不足", 
                               product_id=product_id, 
                               available=inventory_data["available_quantity"],
                               requested=quantity)
                    return False
                
                # 扣减可用库存，增加预留库存
                inventory_data["available_quantity"] -= quantity
                inventory_data["reserved_quantity"] += quantity
                inventory_data["last_updated"] = datetime.now()
                
                logger.info("库存预留成功", 
                          product_id=product_id, 
                          quantity=quantity,
                          remaining=inventory_data["available_quantity"])
            
            return True
            
        except Exception as e:
            logger.error("预留库存失败", error=str(e))
            raise
    
    async def release_reserved_items(self, items: List[Dict[str, Any]]) -> bool:
        """释放预留库存"""
        try:
            for item in items:
                product_id = item["product_id"]
                quantity = item["quantity"]
                
                if product_id not in self.inventory:
                    continue
                
                inventory_data = self.inventory[product_id]
                
                # 从预留库存中释放，回到可用库存
                release_qty = min(quantity, inventory_data["reserved_quantity"])
                inventory_data["reserved_quantity"] -= release_qty
                inventory_data["available_quantity"] += release_qty
                inventory_data["last_updated"] = datetime.now()
                
                logger.info("库存释放成功", 
                          product_id=product_id, 
                          quantity=release_qty)
            
            return True
            
        except Exception as e:
            logger.error("释放库存失败", error=str(e))
            raise
    
    async def confirm_shipment(self, items: List[Dict[str, Any]]) -> bool:
        """确认发货，从预留库存中扣减"""
        try:
            for item in items:
                product_id = item["product_id"]
                quantity = item["quantity"]
                
                if product_id not in self.inventory:
                    continue
                
                inventory_data = self.inventory[product_id]
                
                # 从预留库存中扣减
                shipped_qty = min(quantity, inventory_data["reserved_quantity"])
                inventory_data["reserved_quantity"] -= shipped_qty
                inventory_data["last_updated"] = datetime.now()
                
                logger.info("发货确认成功", 
                          product_id=product_id, 
                          quantity=shipped_qty)
            
            return True
            
        except Exception as e:
            logger.error("确认发货失败", error=str(e))
            raise
    
    async def get_low_stock_alerts(self) -> List[Dict[str, Any]]:
        """获取低库存预警"""
        try:
            low_stock_items = []
            
            for product_id, inventory_data in self.inventory.items():
                total_available = inventory_data["available_quantity"]
                reorder_level = inventory_data["reorder_level"]
                
                if total_available <= reorder_level:
                    low_stock_items.append({
                        "product_id": product_id,
                        "product_name": inventory_data["product_name"],
                        "current_stock": total_available,
                        "reorder_level": reorder_level,
                        "urgency": "critical" if total_available == 0 else "warning"
                    })
            
            return low_stock_items
            
        except Exception as e:
            logger.error("获取低库存预警失败", error=str(e))
            raise
    
    async def update_inventory(self, product_id: str, quantity_change: int, reason: str = "") -> bool:
        """更新库存数量"""
        try:
            if product_id not in self.inventory:
                logger.error("更新库存失败：商品不存在", product_id=product_id)
                return False
            
            inventory_data = self.inventory[product_id]
            new_quantity = inventory_data["available_quantity"] + quantity_change
            
            if new_quantity < 0:
                logger.error("更新库存失败：库存不能为负数", 
                           product_id=product_id, 
                           current=inventory_data["available_quantity"],
                           change=quantity_change)
                return False
            
            inventory_data["available_quantity"] = new_quantity
            inventory_data["last_updated"] = datetime.now()
            
            logger.info("库存更新成功", 
                      product_id=product_id, 
                      change=quantity_change,
                      new_quantity=new_quantity,
                      reason=reason)
            
            return True
            
        except Exception as e:
            logger.error("更新库存失败", product_id=product_id, error=str(e))
            raise
