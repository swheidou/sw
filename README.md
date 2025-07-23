# 🚀 Remote Agent 智能订单处理系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

这是一个展示Remote Agent功能的完整案例，包含云端运行、复杂任务处理和系统交互能力。

## ⚡ 快速开始

### 一键启动（推荐）

```bash
# 克隆项目
git clone https://github.com/swheidou/sw.git
cd sw

# Windows 用户
start.bat

# Linux/macOS 用户
chmod +x start.sh && ./start.sh

# 跨平台 Python 脚本
python start_local.py
```

### 手动启动

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker 部署

```bash
# 使用 Docker Compose
docker-compose up --build

# 或使用 Docker
docker build -t remote-agent .
docker run -p 8000:8000 remote-agent
```

## 🎯 功能特性

### 1. 云端运行能力
- 基于FastAPI的RESTful API服务
- 支持异步处理和并发请求
- 容器化部署支持
- 实时健康监控

### 2. 复杂任务处理
- **订单处理流程**：订单验证、库存检查、价格计算、支付处理
- **库存管理**：实时库存更新、预警机制、库存预留/释放
- **智能定价**：基于库存量、需求和汇率的动态定价
- **异步任务队列**：处理耗时操作的后台任务

### 3. 系统交互能力
- **数据库集成**：SQLite/PostgreSQL数据持久化
- **支付系统**：模拟第三方支付接口集成
- **物流系统**：智能承运商选择和配送安排
- **通知系统**：邮件和短信多渠道通知
- **外部API**：天气、汇率等实时数据获取

## 项目结构

```
remote-agent-demo/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── models/              # 数据模型
│   ├── services/            # 业务逻辑服务
│   ├── integrations/        # 外部系统集成
│   └── utils/               # 工具函数
├── tests/                   # 测试文件
├── docker/                  # Docker配置
├── requirements.txt         # Python依赖
└── README.md
```

## 🌐 访问调试页面

启动服务后，访问以下页面：

- **Swagger UI**: http://localhost:8000/docs （推荐）
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health
- **系统状态**: http://localhost:8000/

## 🧪 快速测试

### 使用测试脚本

```bash
# 完整功能演示
python test_demo.py

# 性能测试
python performance_test.py

# 调试仪表板
python debug_dashboard.py

# 实时监控
python monitor.py
```

### API 测试示例

#### 创建订单
```bash
curl -X POST "http://localhost:8000/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "user123",
    "items": [
      {"product_id": "prod001", "quantity": 2},
      {"product_id": "prod002", "quantity": 1}
    ],
    "delivery_address": "北京市朝阳区",
    "notes": "测试订单"
  }'
```

#### 查询订单状态
```bash
curl "http://localhost:8000/orders/{order_id}/status"
```

#### 查看库存
```bash
curl "http://localhost:8000/inventory/prod001"
```

#### 获取动态定价
```bash
curl "http://localhost:8000/pricing/prod001"
```

#### 查看天气信息
```bash
curl "http://localhost:8000/external/weather"
```

## 🛠️ 技术栈

- **Web框架**：FastAPI (异步高性能)
- **数据验证**：Pydantic
- **日志系统**：structlog (结构化日志)
- **HTTP客户端**：httpx (异步HTTP请求)
- **任务队列**：Celery + Redis
- **容器化**：Docker + Docker Compose
- **测试框架**：pytest + pytest-asyncio

## 📊 性能指标

| 测试类型 | 并发数 | 成功率 | 平均响应时间 | QPS |
|---------|--------|--------|-------------|-----|
| 健康检查 | 50 | 100% | ~640ms | 77+ |
| 订单创建 | 10 | 100% | ~715ms | 10+ |
| 混合负载 | 20 | 100% | - | 32+ |

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │    │   API Gateway   │    │  Load Balancer  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌───────────────────────▼───────────────────────┐
         │              FastAPI Application              │
         └───────────────────────┬───────────────────────┘
                                 │
    ┌────────────┬───────────────┼───────────────┬────────────┐
    │            │               │               │            │
    ▼            ▼               ▼               ▼            ▼
┌────────┐ ┌──────────┐ ┌─────────────┐ ┌──────────┐ ┌──────────┐
│Order   │ │Inventory │ │   Pricing   │ │ Payment  │ │Logistics │
│Service │ │ Service  │ │   Service   │ │ Gateway  │ │ Service  │
└────────┘ └──────────┘ └─────────────┘ └──────────┘ └──────────┘
     │           │              │              │           │
     └───────────┼──────────────┼──────────────┼───────────┘
                 │              │              │
         ┌───────▼──────────────▼──────────────▼───────┐
         │           External Integrations            │
         │  ┌─────────┐ ┌─────────┐ ┌─────────────┐   │
         │  │Weather  │ │Exchange │ │Notification │   │
         │  │   API   │ │Rate API │ │   Service   │   │
         │  └─────────┘ └─────────┘ └─────────────┘   │
         └─────────────────────────────────────────────┘
```
