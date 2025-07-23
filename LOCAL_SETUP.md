# Remote Agent 本地部署指南

## 🚀 快速开始

### 方式一：一键启动（推荐）

```bash
# 克隆仓库
git clone https://github.com/swheidou/sw.git
cd sw

# Windows用户
start.bat

# Linux/macOS用户
chmod +x start.sh
./start.sh

# 或使用Python脚本（跨平台）
python start_local.py
```

### 方式二：手动部署

#### 1. 克隆项目

```bash
# 克隆仓库
git clone https://github.com/swheidou/sw.git

# 进入项目目录
cd sw
```

### 2. 环境准备

#### Python 环境要求
- Python 3.8+
- pip 包管理器

#### 检查Python版本
```bash
python --version
# 或
python3 --version
```

### 3. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装项目依赖
pip install -r requirements.txt
```

### 4. 启动服务

```bash
# 启动Remote Agent服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后，您将看到类似输出：
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxx] using WatchFiles
INFO:     Started server process [xxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## 🔧 调试和测试

### 访问调试页面

1. **Swagger UI (推荐)**
   ```
   http://localhost:8000/docs
   ```

2. **ReDoc 文档**
   ```
   http://localhost:8000/redoc
   ```

3. **健康检查**
   ```
   http://localhost:8000/health
   ```

### 运行测试脚本

```bash
# 运行完整功能演示
python test_demo.py

# 运行性能测试
python performance_test.py

# 启动调试仪表板
python debug_dashboard.py

# 启动实时监控
python monitor.py

# 快速打开所有调试页面
python open_debug.py
```

## 📊 API 测试示例

### 1. 创建订单

```bash
curl -X POST "http://localhost:8000/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "local_user",
    "items": [
      {"product_id": "prod001", "quantity": 2},
      {"product_id": "prod002", "quantity": 1}
    ],
    "delivery_address": "本地测试地址",
    "notes": "本地调试订单"
  }'
```

### 2. 查询订单状态

```bash
# 替换 {order_id} 为实际订单ID
curl "http://localhost:8000/orders/{order_id}/status"
```

### 3. 查询库存

```bash
curl "http://localhost:8000/inventory/prod001"
```

### 4. 获取动态定价

```bash
curl "http://localhost:8000/pricing/prod001"
```

### 5. 查看天气信息

```bash
curl "http://localhost:8000/external/weather"
```

### 6. 获取汇率信息

```bash
curl "http://localhost:8000/external/exchange-rate"
```

## 🛠️ 开发调试

### 热重载开发

服务启动时使用了 `--reload` 参数，修改代码后会自动重启服务。

### 查看日志

服务运行时会在终端显示详细的结构化日志：
- 订单处理流程
- 支付处理状态
- 库存变化
- 物流安排
- 通知发送

### 代码结构

```
sw/
├── app/
│   ├── main.py                     # FastAPI应用入口
│   ├── models/schemas.py           # 数据模型
│   ├── services/                   # 业务逻辑服务
│   │   ├── order_service.py        # 订单服务
│   │   ├── inventory_service.py    # 库存服务
│   │   └── pricing_service.py      # 定价服务
│   ├── integrations/               # 外部系统集成
│   │   ├── payment_gateway.py      # 支付网关
│   │   ├── logistics_service.py    # 物流服务
│   │   ├── notification_service.py # 通知服务
│   │   └── external_apis.py        # 外部API
│   └── utils/database.py           # 数据库工具
├── requirements.txt                # 依赖列表
├── test_demo.py                    # 功能演示
├── performance_test.py             # 性能测试
├── debug_dashboard.py              # 调试仪表板
├── monitor.py                      # 实时监控
└── debug.html                      # Web调试界面
```

## 🔍 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 使用其他端口
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
   ```

2. **依赖安装失败**
   ```bash
   # 升级pip
   pip install --upgrade pip
   
   # 重新安装依赖
   pip install -r requirements.txt --force-reinstall
   ```

3. **Python版本不兼容**
   ```bash
   # 检查Python版本
   python --version
   
   # 确保使用Python 3.8+
   ```

### 验证安装

运行健康检查确认服务正常：
```bash
curl http://localhost:8000/health
```

预期响应：
```json
{
  "status": "healthy",
  "services": {
    "database": true,
    "inventory": true,
    "payment": true,
    "logistics": true,
    "notification": true
  },
  "timestamp": "2025-07-23T06:45:41.478259"
}
```

## 🎯 下一步

1. 在Swagger UI中测试各个API端点
2. 运行演示脚本查看完整业务流程
3. 修改代码体验热重载功能
4. 查看实时日志了解系统运行状态

## 🐳 Docker 部署

### 使用 Docker Compose（推荐）

```bash
# 构建并启动服务
docker-compose up --build

# 后台运行
docker-compose up -d --build

# 停止服务
docker-compose down
```

### 使用 Docker

```bash
# 构建镜像
docker build -t remote-agent .

# 运行容器
docker run -p 8000:8000 remote-agent

# 后台运行
docker run -d -p 8000:8000 --name remote-agent-container remote-agent
```

## 📞 技术支持

如果遇到问题，请检查：
1. Python版本是否为3.8+
2. 所有依赖是否正确安装
3. 端口8000是否被占用
4. 防火墙是否阻止了端口访问

### 常见启动方式

| 方式 | 命令 | 适用场景 |
|------|------|----------|
| 一键启动 | `start.bat` (Windows) | 新手推荐 |
| 一键启动 | `./start.sh` (Linux/macOS) | 新手推荐 |
| Python脚本 | `python start_local.py` | 跨平台 |
| 手动启动 | `uvicorn app.main:app --reload` | 开发调试 |
| Docker | `docker-compose up` | 生产环境 |
