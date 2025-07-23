"""
通知服务集成 - 邮件和短信通知
"""

import asyncio
import uuid
from typing import Dict, Any, List
from datetime import datetime
import structlog

from app.models.schemas import NotificationRequest

logger = structlog.get_logger()


class NotificationService:
    """通知服务类"""
    
    def __init__(self):
        # 通知配置
        self.notification_config = {
            "email": {
                "smtp_server": "smtp.example.com",
                "smtp_port": 587,
                "username": "noreply@example.com",
                "enabled": True
            },
            "sms": {
                "api_endpoint": "https://sms-api.example.com",
                "api_key": "sms_api_key_12345",
                "enabled": True
            },
            "push": {
                "fcm_server_key": "fcm_key_12345",
                "enabled": False
            }
        }
        
        # 通知模板
        self.templates = {
            "order_confirmation": {
                "email": {
                    "subject": "订单确认 - 订单号: {order_id}",
                    "body": """
亲爱的客户，

您的订单已成功创建！

订单详情：
- 订单号：{order_id}
- 订单金额：¥{total_amount}
- 预计配送时间：{estimated_delivery}
- 物流跟踪号：{tracking_number}

感谢您的购买！

此致
客服团队
                    """
                },
                "sms": "【商城】您的订单{order_id}已确认，金额¥{total_amount}，预计{estimated_delivery}送达。跟踪号：{tracking_number}"
            },
            "payment_failure": {
                "email": {
                    "subject": "支付失败通知 - 订单号: {order_id}",
                    "body": """
亲爱的客户，

很抱歉，您的订单支付失败。

订单详情：
- 订单号：{order_id}
- 失败原因：{reason}

请重新尝试支付或联系客服。

此致
客服团队
                    """
                },
                "sms": "【商城】订单{order_id}支付失败：{reason}。请重新支付或联系客服。"
            },
            "shipping_update": {
                "email": {
                    "subject": "配送状态更新 - 订单号: {order_id}",
                    "body": """
亲爱的客户，

您的订单配送状态已更新：

- 订单号：{order_id}
- 当前状态：{status}
- 当前位置：{location}
- 跟踪号：{tracking_number}

您可以通过跟踪号查询详细配送信息。

此致
客服团队
                    """
                },
                "sms": "【商城】订单{order_id}状态更新：{status}，当前位置：{location}。"
            }
        }
        
        # 通知记录
        self.notification_records: Dict[str, Dict] = {}
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            await asyncio.sleep(0.1)
            return True
        except Exception as e:
            logger.error("通知服务健康检查失败", error=str(e))
            return False
    
    async def send_order_confirmation(self, customer_id: str, order_id: str, tracking_number: str) -> bool:
        """发送订单确认通知"""
        try:
            # 模拟获取客户联系信息
            customer_info = await self._get_customer_info(customer_id)
            
            # 模拟订单信息
            order_info = {
                "order_id": order_id,
                "total_amount": "299.00",
                "estimated_delivery": "2024-01-15",
                "tracking_number": tracking_number
            }
            
            # 发送邮件通知
            email_sent = await self._send_email_notification(
                customer_info["email"],
                "order_confirmation",
                order_info
            )
            
            # 发送短信通知
            sms_sent = await self._send_sms_notification(
                customer_info["phone"],
                "order_confirmation",
                order_info
            )
            
            logger.info("订单确认通知发送完成", 
                      customer_id=customer_id,
                      order_id=order_id,
                      email_sent=email_sent,
                      sms_sent=sms_sent)
            
            return email_sent or sms_sent
            
        except Exception as e:
            logger.error("发送订单确认通知失败", 
                       customer_id=customer_id, 
                       order_id=order_id, 
                       error=str(e))
            return False
    
    async def send_payment_failure_notice(self, customer_id: str, order_id: str) -> bool:
        """发送支付失败通知"""
        try:
            customer_info = await self._get_customer_info(customer_id)
            
            notification_data = {
                "order_id": order_id,
                "reason": "银行卡余额不足"
            }
            
            # 发送邮件通知
            email_sent = await self._send_email_notification(
                customer_info["email"],
                "payment_failure",
                notification_data
            )
            
            # 发送短信通知
            sms_sent = await self._send_sms_notification(
                customer_info["phone"],
                "payment_failure",
                notification_data
            )
            
            logger.info("支付失败通知发送完成", 
                      customer_id=customer_id,
                      order_id=order_id,
                      email_sent=email_sent,
                      sms_sent=sms_sent)
            
            return email_sent or sms_sent
            
        except Exception as e:
            logger.error("发送支付失败通知失败", 
                       customer_id=customer_id, 
                       order_id=order_id, 
                       error=str(e))
            return False
    
    async def send_shipping_update(self, customer_id: str, order_id: str, status: str, location: str, tracking_number: str) -> bool:
        """发送配送状态更新通知"""
        try:
            customer_info = await self._get_customer_info(customer_id)
            
            notification_data = {
                "order_id": order_id,
                "status": status,
                "location": location,
                "tracking_number": tracking_number
            }
            
            # 发送邮件通知
            email_sent = await self._send_email_notification(
                customer_info["email"],
                "shipping_update",
                notification_data
            )
            
            # 发送短信通知（仅重要状态更新）
            important_statuses = ["shipped", "out_for_delivery", "delivered"]
            sms_sent = False
            
            if status in important_statuses:
                sms_sent = await self._send_sms_notification(
                    customer_info["phone"],
                    "shipping_update",
                    notification_data
                )
            
            logger.info("配送状态通知发送完成", 
                      customer_id=customer_id,
                      order_id=order_id,
                      status=status,
                      email_sent=email_sent,
                      sms_sent=sms_sent)
            
            return email_sent or sms_sent
            
        except Exception as e:
            logger.error("发送配送状态通知失败", 
                       customer_id=customer_id, 
                       order_id=order_id, 
                       error=str(e))
            return False
    
    async def _get_customer_info(self, customer_id: str) -> Dict[str, str]:
        """获取客户联系信息（模拟）"""
        # 模拟客户数据
        customer_data = {
            "user123": {
                "email": "user123@example.com",
                "phone": "+86-138-0013-8000",
                "name": "张三"
            },
            "user456": {
                "email": "user456@example.com",
                "phone": "+86-139-0013-9000",
                "name": "李四"
            }
        }
        
        return customer_data.get(customer_id, {
            "email": "default@example.com",
            "phone": "+86-138-0000-0000",
            "name": "客户"
        })
    
    async def _send_email_notification(self, email: str, template_name: str, data: Dict) -> bool:
        """发送邮件通知"""
        try:
            if not self.notification_config["email"]["enabled"]:
                logger.info("邮件通知已禁用")
                return False
            
            template = self.templates[template_name]["email"]
            subject = template["subject"].format(**data)
            body = template["body"].format(**data)
            
            # 模拟邮件发送
            await asyncio.sleep(0.5)  # 模拟网络延迟
            
            notification_id = f"EMAIL-{uuid.uuid4().hex[:8].upper()}"
            
            # 记录通知
            self.notification_records[notification_id] = {
                "id": notification_id,
                "type": "email",
                "recipient": email,
                "template": template_name,
                "subject": subject,
                "status": "sent",
                "sent_at": datetime.now()
            }
            
            logger.info("邮件发送成功", 
                      email=email, 
                      template=template_name,
                      notification_id=notification_id)
            
            return True
            
        except Exception as e:
            logger.error("邮件发送失败", email=email, template=template_name, error=str(e))
            return False
    
    async def _send_sms_notification(self, phone: str, template_name: str, data: Dict) -> bool:
        """发送短信通知"""
        try:
            if not self.notification_config["sms"]["enabled"]:
                logger.info("短信通知已禁用")
                return False
            
            template = self.templates[template_name]["sms"]
            message = template.format(**data)
            
            # 模拟短信发送
            await asyncio.sleep(0.3)  # 模拟网络延迟
            
            notification_id = f"SMS-{uuid.uuid4().hex[:8].upper()}"
            
            # 记录通知
            self.notification_records[notification_id] = {
                "id": notification_id,
                "type": "sms",
                "recipient": phone,
                "template": template_name,
                "message": message,
                "status": "sent",
                "sent_at": datetime.now()
            }
            
            logger.info("短信发送成功", 
                      phone=phone, 
                      template=template_name,
                      notification_id=notification_id)
            
            return True
            
        except Exception as e:
            logger.error("短信发送失败", phone=phone, template=template_name, error=str(e))
            return False
    
    async def get_notification_history(self, customer_id: str) -> List[Dict[str, Any]]:
        """获取通知历史"""
        try:
            # 模拟根据客户ID筛选通知记录
            customer_notifications = []
            
            for notification in self.notification_records.values():
                # 简化的筛选逻辑
                customer_notifications.append(notification)
            
            # 按时间倒序排列
            customer_notifications.sort(
                key=lambda x: x["sent_at"], 
                reverse=True
            )
            
            return customer_notifications[:10]  # 返回最近10条
            
        except Exception as e:
            logger.error("获取通知历史失败", customer_id=customer_id, error=str(e))
            return []
