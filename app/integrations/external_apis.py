"""
外部API集成 - 天气和汇率数据
"""

import asyncio
import random
from typing import Dict, Any
from datetime import datetime
import structlog

from app.models.schemas import WeatherInfo, ExchangeRate

logger = structlog.get_logger()


class WeatherAPI:
    """天气API集成类"""
    
    def __init__(self):
        self.api_config = {
            "api_key": "weather_api_key_12345",
            "base_url": "https://api.weather.com/v1",
            "timeout": 10
        }
    
    async def get_current_weather(self, location: str = "北京") -> WeatherInfo:
        """获取当前天气信息"""
        try:
            logger.info("获取天气信息", location=location)
            
            # 模拟API调用延迟
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # 模拟天气数据
            weather_conditions = ["晴天", "多云", "小雨", "中雨", "大雨", "雪", "雾"]
            condition = random.choice(weather_conditions)
            
            temperature = random.uniform(-10, 35)
            humidity = random.uniform(30, 90)
            wind_speed = random.uniform(0, 20)
            
            # 判断是否适合配送
            suitable_for_delivery = self._is_suitable_for_delivery(
                condition, temperature, wind_speed
            )
            
            weather_info = WeatherInfo(
                location=location,
                temperature=round(temperature, 1),
                humidity=round(humidity, 1),
                weather_condition=condition,
                wind_speed=round(wind_speed, 1),
                suitable_for_delivery=suitable_for_delivery
            )
            
            logger.info("天气信息获取成功", 
                      location=location,
                      condition=condition,
                      temperature=weather_info.temperature,
                      suitable_for_delivery=suitable_for_delivery)
            
            return weather_info
            
        except Exception as e:
            logger.error("获取天气信息失败", location=location, error=str(e))
            # 返回默认天气信息
            return WeatherInfo(
                location=location,
                temperature=20.0,
                humidity=60.0,
                weather_condition="多云",
                wind_speed=5.0,
                suitable_for_delivery=True
            )
    
    async def get_weather_for_delivery(self, location: str = "北京") -> WeatherInfo:
        """获取配送相关的天气信息"""
        try:
            weather_info = await self.get_current_weather(location)
            
            # 记录配送相关的天气判断
            logger.info("配送天气评估", 
                      location=location,
                      condition=weather_info.weather_condition,
                      suitable=weather_info.suitable_for_delivery)
            
            return weather_info
            
        except Exception as e:
            logger.error("获取配送天气信息失败", location=location, error=str(e))
            raise
    
    def _is_suitable_for_delivery(self, condition: str, temperature: float, wind_speed: float) -> bool:
        """判断天气是否适合配送"""
        try:
            # 恶劣天气条件
            bad_conditions = ["大雨", "暴雨", "雪", "暴雪", "台风"]
            
            if condition in bad_conditions:
                return False
            
            # 极端温度
            if temperature < -15 or temperature > 40:
                return False
            
            # 强风
            if wind_speed > 15:
                return False
            
            # 中雨时需要特别注意
            if condition == "中雨" and wind_speed > 10:
                return False
            
            return True
            
        except Exception as e:
            logger.error("天气适宜性判断失败", error=str(e))
            return True  # 默认适合配送
    
    async def get_weather_forecast(self, location: str = "北京", days: int = 7) -> List[WeatherInfo]:
        """获取天气预报"""
        try:
            logger.info("获取天气预报", location=location, days=days)
            
            forecast = []
            for i in range(days):
                # 模拟每天的天气数据
                await asyncio.sleep(0.1)  # 模拟API调用
                
                weather_info = await self.get_current_weather(location)
                forecast.append(weather_info)
            
            return forecast
            
        except Exception as e:
            logger.error("获取天气预报失败", location=location, error=str(e))
            return []


class ExchangeRateAPI:
    """汇率API集成类"""
    
    def __init__(self):
        self.api_config = {
            "api_key": "exchange_api_key_12345",
            "base_url": "https://api.exchangerate.com/v1",
            "timeout": 10
        }
        
        # 缓存汇率数据
        self.rate_cache: Dict[str, Dict] = {}
        self.cache_duration = 3600  # 1小时缓存
    
    async def get_usd_to_cny_rate(self) -> float:
        """获取美元对人民币汇率"""
        try:
            cache_key = "USD_CNY"
            
            # 检查缓存
            if self._is_cache_valid(cache_key):
                cached_rate = self.rate_cache[cache_key]["rate"]
                logger.info("使用缓存汇率", rate=cached_rate)
                return cached_rate
            
            logger.info("获取USD/CNY汇率")
            
            # 模拟API调用延迟
            await asyncio.sleep(random.uniform(0.3, 1.0))
            
            # 模拟汇率数据（基于真实汇率范围）
            base_rate = 7.2
            fluctuation = random.uniform(-0.3, 0.3)
            current_rate = base_rate + fluctuation
            
            # 缓存汇率
            self.rate_cache[cache_key] = {
                "rate": round(current_rate, 4),
                "timestamp": datetime.now(),
                "source": "exchange_api"
            }
            
            logger.info("USD/CNY汇率获取成功", rate=current_rate)
            
            return round(current_rate, 4)
            
        except Exception as e:
            logger.error("获取USD/CNY汇率失败", error=str(e))
            # 返回默认汇率
            return 7.2
    
    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> ExchangeRate:
        """获取指定货币对汇率"""
        try:
            cache_key = f"{from_currency}_{to_currency}"
            
            # 检查缓存
            if self._is_cache_valid(cache_key):
                cached_data = self.rate_cache[cache_key]
                return ExchangeRate(
                    from_currency=from_currency,
                    to_currency=to_currency,
                    rate=cached_data["rate"],
                    timestamp=cached_data["timestamp"]
                )
            
            logger.info("获取汇率", from_currency=from_currency, to_currency=to_currency)
            
            # 模拟API调用
            await asyncio.sleep(random.uniform(0.3, 1.0))
            
            # 模拟汇率计算
            rate = await self._calculate_exchange_rate(from_currency, to_currency)
            
            # 缓存汇率
            self.rate_cache[cache_key] = {
                "rate": rate,
                "timestamp": datetime.now(),
                "source": "exchange_api"
            }
            
            exchange_rate = ExchangeRate(
                from_currency=from_currency,
                to_currency=to_currency,
                rate=rate,
                timestamp=datetime.now()
            )
            
            logger.info("汇率获取成功", 
                      from_currency=from_currency,
                      to_currency=to_currency,
                      rate=rate)
            
            return exchange_rate
            
        except Exception as e:
            logger.error("获取汇率失败", 
                       from_currency=from_currency,
                       to_currency=to_currency,
                       error=str(e))
            
            # 返回默认汇率
            return ExchangeRate(
                from_currency=from_currency,
                to_currency=to_currency,
                rate=1.0,
                timestamp=datetime.now()
            )
    
    async def _calculate_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """计算汇率（模拟）"""
        try:
            # 模拟汇率数据
            rates = {
                "USD": {"CNY": 7.2, "EUR": 0.85, "JPY": 110.0},
                "CNY": {"USD": 0.139, "EUR": 0.118, "JPY": 15.3},
                "EUR": {"USD": 1.18, "CNY": 8.5, "JPY": 129.0},
                "JPY": {"USD": 0.009, "CNY": 0.065, "EUR": 0.008}
            }
            
            if from_currency == to_currency:
                return 1.0
            
            if from_currency in rates and to_currency in rates[from_currency]:
                base_rate = rates[from_currency][to_currency]
                # 添加小幅波动
                fluctuation = random.uniform(-0.02, 0.02)
                return round(base_rate * (1 + fluctuation), 6)
            
            # 如果没有直接汇率，通过USD中转
            if from_currency != "USD" and to_currency != "USD":
                usd_rate_from = rates.get(from_currency, {}).get("USD", 1.0)
                usd_rate_to = rates.get("USD", {}).get(to_currency, 1.0)
                return round(usd_rate_from * usd_rate_to, 6)
            
            return 1.0
            
        except Exception as e:
            logger.error("计算汇率失败", error=str(e))
            return 1.0
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """检查缓存是否有效"""
        try:
            if cache_key not in self.rate_cache:
                return False
            
            cached_time = self.rate_cache[cache_key]["timestamp"]
            elapsed_seconds = (datetime.now() - cached_time).total_seconds()
            
            return elapsed_seconds < self.cache_duration
            
        except Exception as e:
            logger.error("检查缓存有效性失败", error=str(e))
            return False
    
    async def get_supported_currencies(self) -> List[str]:
        """获取支持的货币列表"""
        try:
            # 模拟支持的货币
            currencies = ["USD", "CNY", "EUR", "JPY", "GBP", "AUD", "CAD", "CHF", "HKD", "SGD"]
            
            logger.info("获取支持货币列表", count=len(currencies))
            
            return currencies
            
        except Exception as e:
            logger.error("获取支持货币列表失败", error=str(e))
            return ["USD", "CNY"]
