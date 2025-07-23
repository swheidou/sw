@echo off
REM Remote Agent 项目搬迁到D盘脚本

echo ================================================================================
echo 🚀 Remote Agent 项目搬迁到 D:/AI_Projects/
echo ================================================================================

REM 设置目标目录
set TARGET_DIR=D:\AI_Projects\remote-agent

echo 📁 目标目录: %TARGET_DIR%
echo.

REM 创建目标目录
echo 📂 创建目标目录...
if not exist "D:\AI_Projects" mkdir "D:\AI_Projects"
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

REM 检查Git是否可用
git --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Git未安装，使用文件复制方式...
    goto COPY_FILES
) else (
    echo ✅ Git已安装，使用Git克隆...
    goto GIT_CLONE
)

:GIT_CLONE
echo.
echo 📥 从GitHub克隆项目...
cd /d D:\AI_Projects
git clone https://github.com/swheidou/sw.git remote-agent
if errorlevel 1 (
    echo ❌ Git克隆失败，尝试文件复制方式...
    goto COPY_FILES
) else (
    echo ✅ Git克隆成功
    goto SETUP_COMPLETE
)

:COPY_FILES
echo.
echo 📄 复制项目文件...

REM 创建目录结构
mkdir "%TARGET_DIR%\app" 2>nul
mkdir "%TARGET_DIR%\app\models" 2>nul
mkdir "%TARGET_DIR%\app\services" 2>nul
mkdir "%TARGET_DIR%\app\integrations" 2>nul
mkdir "%TARGET_DIR%\app\utils" 2>nul

REM 复制文件（如果存在）
if exist "README.md" copy "README.md" "%TARGET_DIR%\" >nul
if exist "LOCAL_SETUP.md" copy "LOCAL_SETUP.md" "%TARGET_DIR%\" >nul
if exist "requirements.txt" copy "requirements.txt" "%TARGET_DIR%\" >nul
if exist "Dockerfile" copy "Dockerfile" "%TARGET_DIR%\" >nul
if exist "docker-compose.yml" copy "docker-compose.yml" "%TARGET_DIR%\" >nul
if exist "start.bat" copy "start.bat" "%TARGET_DIR%\" >nul
if exist "start.sh" copy "start.sh" "%TARGET_DIR%\" >nul
if exist "start_local.py" copy "start_local.py" "%TARGET_DIR%\" >nul
if exist "test_demo.py" copy "test_demo.py" "%TARGET_DIR%\" >nul
if exist "performance_test.py" copy "performance_test.py" "%TARGET_DIR%\" >nul
if exist "debug_dashboard.py" copy "debug_dashboard.py" "%TARGET_DIR%\" >nul
if exist "monitor.py" copy "monitor.py" "%TARGET_DIR%\" >nul
if exist "open_debug.py" copy "open_debug.py" "%TARGET_DIR%\" >nul
if exist "verify_deployment.py" copy "verify_deployment.py" "%TARGET_DIR%\" >nul
if exist "debug.html" copy "debug.html" "%TARGET_DIR%\" >nul
if exist ".gitignore" copy ".gitignore" "%TARGET_DIR%\" >nul

REM 复制app目录
if exist "app\*" xcopy "app\*" "%TARGET_DIR%\app\" /E /I /Y >nul

echo ✅ 文件复制完成

:SETUP_COMPLETE
echo.
echo 🎉 项目搬迁完成！
echo 📍 项目位置: %TARGET_DIR%
echo.

REM 切换到项目目录
cd /d "%TARGET_DIR%"

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 请从 https://python.org 下载并安装Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python已安装

REM 检查项目文件
if not exist "requirements.txt" (
    echo ❌ 项目文件不完整，正在创建基础文件...
    goto CREATE_BASIC_FILES
)

echo ✅ 项目文件完整

REM 安装依赖
echo.
echo 📦 安装Python依赖...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo ✅ 依赖安装完成

REM 启动项目
echo.
echo 🚀 启动Remote Agent项目...
echo 📍 服务地址: http://localhost:8000
echo 📚 API文档: http://localhost:8000/docs
echo 💡 按 Ctrl+C 停止服务
echo ----------------------------------------------------------------

REM 延迟3秒后打开浏览器
start "" /min cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:8000/docs"

REM 启动服务
if exist "start_local.py" (
    python start_local.py
) else if exist "app\main.py" (
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
) else (
    echo ❌ 找不到启动文件
    pause
    exit /b 1
)

goto END

:CREATE_BASIC_FILES
echo 创建基础requirements.txt...
echo fastapi==0.104.1> "%TARGET_DIR%\requirements.txt"
echo uvicorn[standard]==0.24.0>> "%TARGET_DIR%\requirements.txt"
echo pydantic==2.5.0>> "%TARGET_DIR%\requirements.txt"
echo httpx==0.25.2>> "%TARGET_DIR%\requirements.txt"
echo structlog==23.2.0>> "%TARGET_DIR%\requirements.txt"

echo ⚠️  项目文件不完整，建议从GitHub重新下载
echo 📍 GitHub地址: https://github.com/swheidou/sw
pause

:END
pause
