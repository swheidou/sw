"""
数据模型定义
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class OrderItemRequest(BaseModel):
    """订单商品请求模型"""
    product_id: str = Field(..., description="商品ID")
    quantity: int = Field(..., gt=0, description="数量")


class OrderRequest(BaseModel):
    """创建订单请求模型"""
    customer_id: str = Field(..., description="客户ID")
    items: List[OrderItemRequest] = Field(..., description="订单商品列表")
    delivery_address: Optional[str] = Field(None, description="配送地址")
    notes: Optional[str] = Field(None, description="订单备注")


class OrderResponse(BaseModel):
    """订单响应模型"""
    order_id: str = Field(..., description="订单ID")
    status: str = Field(..., description="订单状态")
    total_amount: float = Field(..., description="订单总金额")
    currency: str = Field(..., description="货币类型")
    estimated_delivery: Optional[str] = Field(None, description="预计配送时间")


class OrderStatusEnum(str, Enum):
    """订单状态枚举"""
    CREATED = "created"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    PAYMENT_FAILED = "payment_failed"
    ERROR = "error"


class OrderStatus(BaseModel):
    """订单状态查询响应"""
    order_id: str = Field(..., description="订单ID")
    status: OrderStatusEnum = Field(..., description="订单状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    tracking_number: Optional[str] = Field(None, description="物流跟踪号")


class InventoryItem(BaseModel):
    """库存商品模型"""
    product_id: str = Field(..., description="商品ID")
    product_name: str = Field(..., description="商品名称")
    available_quantity: int = Field(..., description="可用库存")
    reserved_quantity: int = Field(..., description="预留库存")
    unit_price: float = Field(..., description="单价")
    currency: str = Field(..., description="货币类型")


class PricingResult(BaseModel):
    """定价结果模型"""
    product_id: str = Field(..., description="商品ID")
    base_price: float = Field(..., description="基础价格")
    dynamic_price: float = Field(..., description="动态价格")
    discount_rate: float = Field(..., description="折扣率")
    currency: str = Field(..., description="货币类型")
    factors: dict = Field(..., description="定价因素")


class PaymentRequest(BaseModel):
    """支付请求模型"""
    order_id: str = Field(..., description="订单ID")
    amount: float = Field(..., description="支付金额")
    currency: str = Field(..., description="货币类型")
    payment_method: str = Field(..., description="支付方式")


class PaymentResponse(BaseModel):
    """支付响应模型"""
    payment_id: str = Field(..., description="支付ID")
    status: str = Field(..., description="支付状态")
    transaction_id: Optional[str] = Field(None, description="交易ID")
    message: str = Field(..., description="响应消息")


class LogisticsRequest(BaseModel):
    """物流请求模型"""
    order_id: str = Field(..., description="订单ID")
    delivery_address: str = Field(..., description="配送地址")
    items: List[OrderItemRequest] = Field(..., description="商品列表")
    priority: str = Field(default="normal", description="配送优先级")


class LogisticsResponse(BaseModel):
    """物流响应模型"""
    tracking_number: str = Field(..., description="跟踪号")
    carrier: str = Field(..., description="承运商")
    estimated_delivery: str = Field(..., description="预计配送时间")
    shipping_cost: float = Field(..., description="运费")


class NotificationRequest(BaseModel):
    """通知请求模型"""
    recipient: str = Field(..., description="接收者")
    message_type: str = Field(..., description="消息类型")
    content: dict = Field(..., description="消息内容")
    channels: List[str] = Field(..., description="通知渠道")


class WeatherInfo(BaseModel):
    """天气信息模型"""
    location: str = Field(..., description="位置")
    temperature: float = Field(..., description="温度")
    humidity: float = Field(..., description="湿度")
    weather_condition: str = Field(..., description="天气状况")
    wind_speed: float = Field(..., description="风速")
    suitable_for_delivery: bool = Field(..., description="是否适合配送")


class ExchangeRate(BaseModel):
    """汇率信息模型"""
    from_currency: str = Field(..., description="源货币")
    to_currency: str = Field(..., description="目标货币")
    rate: float = Field(..., description="汇率")
    timestamp: datetime = Field(..., description="更新时间")
