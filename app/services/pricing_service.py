"""
定价服务 - 处理动态定价相关业务逻辑
"""

import asyncio
import random
from typing import Dict, List, Any
import structlog
from datetime import datetime

from app.models.schemas import OrderItemRequest, PricingResult

logger = structlog.get_logger()


class PricingService:
    """定价服务类"""
    
    def __init__(self):
        # 基础价格配置
        self.base_prices = {
            "prod001": {"price": 2999.00, "currency": "CNY"},
            "prod002": {"price": 299.00, "currency": "CNY"},
            "prod003": {"price": 1999.00, "currency": "CNY"}
        }
        
        # 定价策略配置
        self.pricing_config = {
            "inventory_factor": 0.1,  # 库存影响因子
            "demand_factor": 0.05,    # 需求影响因子
            "exchange_rate_factor": 0.02,  # 汇率影响因子
            "time_factor": 0.03,      # 时间影响因子
            "max_discount": 0.3,      # 最大折扣
            "max_markup": 0.2         # 最大加价
        }
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            await asyncio.sleep(0.1)
            return True
        except Exception as e:
            logger.error("定价服务健康检查失败", error=str(e))
            return False
    
    async def get_dynamic_price(self, product_id: str, exchange_rate: float = 7.0) -> PricingResult:
        """获取商品动态价格"""
        try:
            if product_id not in self.base_prices:
                raise ValueError(f"商品 {product_id} 不存在")
            
            base_price_info = self.base_prices[product_id]
            base_price = base_price_info["price"]
            
            # 计算各种定价因素
            factors = await self._calculate_pricing_factors(product_id, exchange_rate)
            
            # 计算动态价格
            price_adjustment = 0.0
            
            # 库存因素：库存低时价格上涨
            price_adjustment += factors["inventory_impact"]
            
            # 需求因素：需求高时价格上涨
            price_adjustment += factors["demand_impact"]
            
            # 汇率因素：汇率变化影响价格
            price_adjustment += factors["exchange_rate_impact"]
            
            # 时间因素：特定时间段的价格调整
            price_adjustment += factors["time_impact"]
            
            # 限制价格调整范围
            price_adjustment = max(
                -self.pricing_config["max_discount"],
                min(self.pricing_config["max_markup"], price_adjustment)
            )
            
            dynamic_price = base_price * (1 + price_adjustment)
            discount_rate = -price_adjustment if price_adjustment < 0 else 0
            
            result = PricingResult(
                product_id=product_id,
                base_price=base_price,
                dynamic_price=round(dynamic_price, 2),
                discount_rate=round(discount_rate, 4),
                currency=base_price_info["currency"],
                factors=factors
            )
            
            logger.info("动态定价计算完成", 
                      product_id=product_id,
                      base_price=base_price,
                      dynamic_price=result.dynamic_price,
                      adjustment=price_adjustment)
            
            return result
            
        except Exception as e:
            logger.error("动态定价计算失败", product_id=product_id, error=str(e))
            raise
    
    async def calculate_order_price(
        self, 
        items: List[OrderItemRequest], 
        exchange_rate: float = 7.0
    ) -> Dict[str, Any]:
        """计算订单总价"""
        try:
            total_amount = 0.0
            item_prices = []
            
            for item in items:
                # 获取商品动态价格
                pricing_result = await self.get_dynamic_price(item.product_id, exchange_rate)
                
                item_total = pricing_result.dynamic_price * item.quantity
                total_amount += item_total
                
                item_prices.append({
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": pricing_result.dynamic_price,
                    "total_price": item_total,
                    "discount_rate": pricing_result.discount_rate
                })
            
            # 计算订单级别的优惠
            order_discount = await self._calculate_order_discount(total_amount, len(items))
            final_amount = total_amount * (1 - order_discount)
            
            result = {
                "subtotal": round(total_amount, 2),
                "order_discount": round(order_discount, 4),
                "total_amount": round(final_amount, 2),
                "currency": "CNY",
                "item_prices": item_prices,
                "exchange_rate": exchange_rate
            }
            
            logger.info("订单价格计算完成", 
                      items_count=len(items),
                      subtotal=result["subtotal"],
                      total_amount=result["total_amount"])
            
            return result
            
        except Exception as e:
            logger.error("订单价格计算失败", error=str(e))
            raise
    
    async def _calculate_pricing_factors(self, product_id: str, exchange_rate: float) -> Dict[str, Any]:
        """计算定价因素"""
        try:
            # 模拟库存水平（实际应该从库存服务获取）
            inventory_level = random.uniform(0.1, 1.0)  # 0.1-1.0 表示库存水平
            
            # 模拟需求水平
            demand_level = random.uniform(0.5, 1.5)  # 0.5-1.5 表示需求倍数
            
            # 计算各因素影响
            inventory_impact = (1 - inventory_level) * self.pricing_config["inventory_factor"]
            demand_impact = (demand_level - 1) * self.pricing_config["demand_factor"]
            
            # 汇率影响（假设基准汇率为7.0）
            exchange_rate_impact = (exchange_rate - 7.0) / 7.0 * self.pricing_config["exchange_rate_factor"]
            
            # 时间影响（模拟节假日、促销期等）
            current_hour = datetime.now().hour
            if 9 <= current_hour <= 21:  # 营业时间
                time_impact = 0.01
            else:  # 非营业时间小幅优惠
                time_impact = -0.02
            
            return {
                "inventory_level": round(inventory_level, 3),
                "demand_level": round(demand_level, 3),
                "inventory_impact": round(inventory_impact, 4),
                "demand_impact": round(demand_impact, 4),
                "exchange_rate_impact": round(exchange_rate_impact, 4),
                "time_impact": round(time_impact, 4),
                "exchange_rate": exchange_rate
            }
            
        except Exception as e:
            logger.error("计算定价因素失败", product_id=product_id, error=str(e))
            raise
    
    async def _calculate_order_discount(self, total_amount: float, item_count: int) -> float:
        """计算订单级别折扣"""
        try:
            discount = 0.0
            
            # 满额折扣
            if total_amount >= 5000:
                discount += 0.05  # 5%折扣
            elif total_amount >= 3000:
                discount += 0.03  # 3%折扣
            elif total_amount >= 1000:
                discount += 0.01  # 1%折扣
            
            # 多件商品折扣
            if item_count >= 3:
                discount += 0.02  # 额外2%折扣
            
            # 限制最大折扣
            discount = min(discount, 0.1)  # 最大10%折扣
            
            return discount
            
        except Exception as e:
            logger.error("计算订单折扣失败", error=str(e))
            return 0.0
    
    async def get_price_history(self, product_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """获取价格历史（模拟数据）"""
        try:
            if product_id not in self.base_prices:
                raise ValueError(f"商品 {product_id} 不存在")
            
            base_price = self.base_prices[product_id]["price"]
            price_history = []
            
            # 生成模拟的价格历史数据
            for i in range(days):
                date = datetime.now().date()
                # 模拟价格波动
                price_variation = random.uniform(-0.1, 0.1)
                price = base_price * (1 + price_variation)
                
                price_history.append({
                    "date": date.isoformat(),
                    "price": round(price, 2),
                    "currency": self.base_prices[product_id]["currency"]
                })
            
            return price_history
            
        except Exception as e:
            logger.error("获取价格历史失败", product_id=product_id, error=str(e))
            raise
