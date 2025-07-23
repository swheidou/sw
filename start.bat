@echo off
REM Remote Agent Windows 启动脚本

echo ================================================================================
echo 🚀 Remote Agent 智能订单处理系统 - Windows 启动器
echo ================================================================================
echo 📍 项目地址: https://github.com/swheidou/sw
echo 📖 本地文档: LOCAL_SETUP.md
echo ================================================================================

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 请从 https://python.org 下载并安装Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python已安装

REM 检查项目文件
if not exist "app\main.py" (
    echo ❌ 项目文件缺失，请确保在项目根目录运行
    echo 请运行以下命令:
    echo   git clone https://github.com/swheidou/sw.git
    echo   cd sw
    echo   start.bat
    pause
    exit /b 1
)

echo ✅ 项目结构完整

REM 安装依赖
echo 📦 检查并安装依赖...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo ✅ 依赖安装完成

REM 显示信息
echo.
echo 🚀 启动Remote Agent服务...
echo 📍 服务地址: http://localhost:8000
echo 📚 API文档: http://localhost:8000/docs
echo 💡 按 Ctrl+C 停止服务
echo ----------------------------------------------------------------

REM 延迟3秒后打开浏览器
start "" /min cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:8000/docs"

REM 启动服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
