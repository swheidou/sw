#!/bin/bash
# Remote Agent Linux/macOS 启动脚本

echo "================================================================================"
echo "🚀 Remote Agent 智能订单处理系统 - Linux/macOS 启动器"
echo "================================================================================"
echo "📍 项目地址: https://github.com/swheidou/sw"
echo "📖 本地文档: LOCAL_SETUP.md"
echo "================================================================================"

# 检查Python是否安装
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python未安装"
    echo "请安装Python 3.8+:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "  macOS: brew install python3"
    exit 1
fi

# 确定Python命令
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PIP_CMD="pip"
fi

echo "✅ Python已安装 ($($PYTHON_CMD --version))"

# 检查项目文件
if [ ! -f "app/main.py" ]; then
    echo "❌ 项目文件缺失，请确保在项目根目录运行"
    echo "请运行以下命令:"
    echo "  git clone https://github.com/swheidou/sw.git"
    echo "  cd sw"
    echo "  chmod +x start.sh"
    echo "  ./start.sh"
    exit 1
fi

echo "✅ 项目结构完整"

# 创建虚拟环境（可选）
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    $PYTHON_CMD -m venv venv
fi

# 激活虚拟环境
if [ -d "venv" ]; then
    echo "🔄 激活虚拟环境..."
    source venv/bin/activate
fi

# 安装依赖
echo "📦 检查并安装依赖..."
$PIP_CMD install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi

echo "✅ 依赖安装完成"

# 显示信息
echo ""
echo "🚀 启动Remote Agent服务..."
echo "📍 服务地址: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo "💡 按 Ctrl+C 停止服务"
echo "----------------------------------------------------------------"

# 延迟打开浏览器
(sleep 3 && open http://localhost:8000/docs 2>/dev/null || xdg-open http://localhost:8000/docs 2>/dev/null) &

# 启动服务
$PYTHON_CMD -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
