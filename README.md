# Remote Agent 智能订单处理系统

这是一个展示Remote Agent功能的简易案例，包含云端运行、复杂任务处理和系统交互能力。

## 功能特性

### 1. 云端运行能力
- 基于FastAPI的RESTful API服务
- 支持异步处理和并发请求
- 容器化部署支持

### 2. 复杂任务处理
- **订单处理流程**：订单验证、库存检查、价格计算、支付处理
- **库存管理**：实时库存更新、预警机制
- **智能定价**：基于库存量和历史数据的动态定价
- **异步任务队列**：处理耗时操作

### 3. 系统交互能力
- **数据库集成**：SQLite/PostgreSQL数据持久化
- **支付系统**：模拟第三方支付接口
- **物流系统**：自动分配配送方式
- **通知系统**：邮件和短信通知
- **外部API**：天气、汇率等数据获取

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

## 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 启动服务：
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. 访问API文档：
```
http://localhost:8000/docs
```

## API示例

### 创建订单
```bash
curl -X POST "http://localhost:8000/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "user123",
    "items": [
      {"product_id": "prod001", "quantity": 2},
      {"product_id": "prod002", "quantity": 1}
    ]
  }'
```

### 查询订单状态
```bash
curl "http://localhost:8000/orders/order123/status"
```

## 技术栈

- **Web框架**：FastAPI
- **数据库**：SQLAlchemy + SQLite/PostgreSQL
- **异步任务**：Celery + Redis
- **容器化**：Docker
- **测试**：pytest
- **日志**：structlog
