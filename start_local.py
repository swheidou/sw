#!/usr/bin/env python3
"""
Remote Agent 本地一键启动脚本
"""

import os
import sys
import subprocess
import time
import webbrowser
import platform
from pathlib import Path

def print_banner():
    """打印启动横幅"""
    print("=" * 80)
    print("🚀 Remote Agent 智能订单处理系统 - 本地启动器")
    print("=" * 80)
    print("📍 项目地址: https://github.com/swheidou/sw")
    print("📖 本地文档: LOCAL_SETUP.md")
    print("=" * 80)

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python版本过低，需要Python 3.8+")
        print(f"   当前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
    return True

def check_requirements():
    """检查并安装依赖"""
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("❌ requirements.txt 文件不存在")
        return False
    
    print("📦 检查依赖包...")
    
    try:
        # 检查是否已安装FastAPI
        import fastapi
        print("✅ 依赖包已安装")
        return True
    except ImportError:
        print("📥 正在安装依赖包...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], check=True, capture_output=True)
            print("✅ 依赖包安装完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 依赖包安装失败: {e}")
            print("请手动运行: pip install -r requirements.txt")
            return False

def check_project_structure():
    """检查项目结构"""
    required_files = [
        "app/main.py",
        "app/models/schemas.py",
        "app/services/order_service.py",
        "requirements.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 项目文件缺失:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ 项目结构完整")
    return True

def start_server():
    """启动服务器"""
    print("\n🚀 启动Remote Agent服务...")
    print("📍 服务地址: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("💡 按 Ctrl+C 停止服务")
    print("-" * 60)
    
    try:
        # 启动uvicorn服务器
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except FileNotFoundError:
        print("❌ uvicorn未安装，请运行: pip install uvicorn")
        return False
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False

def open_browser_pages():
    """打开浏览器页面"""
    pages = [
        ("API文档", "http://localhost:8000/docs"),
        ("健康检查", "http://localhost:8000/health")
    ]
    
    print("\n🌐 正在打开调试页面...")
    for name, url in pages:
        try:
            webbrowser.open(url)
            print(f"  📄 {name}: {url}")
            time.sleep(1)
        except Exception as e:
            print(f"  ⚠️  无法打开 {name}: {e}")

def show_quick_commands():
    """显示快速命令"""
    print("\n🔧 快速测试命令:")
    print("# 创建测试订单")
    print('curl -X POST "http://localhost:8000/orders" \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"customer_id": "test", "items": [{"product_id": "prod001", "quantity": 1}]}\'')
    
    print("\n# 查看库存")
    print('curl "http://localhost:8000/inventory/prod001"')
    
    print("\n# 获取动态定价")
    print('curl "http://localhost:8000/pricing/prod001"')
    
    print("\n🛠️  调试工具:")
    print("python test_demo.py          # 功能演示")
    print("python performance_test.py   # 性能测试")
    print("python debug_dashboard.py    # 调试仪表板")
    print("python monitor.py            # 实时监控")

def main():
    """主函数"""
    print_banner()
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 检查项目结构
    if not check_project_structure():
        print("\n💡 请确保在项目根目录运行此脚本")
        print("   git clone https://github.com/swheidou/sw.git")
        print("   cd sw")
        print("   python start_local.py")
        sys.exit(1)
    
    # 检查并安装依赖
    if not check_requirements():
        sys.exit(1)
    
    # 显示快速命令
    show_quick_commands()
    
    # 询问是否打开浏览器
    try:
        open_browser = input("\n🌐 是否自动打开调试页面? (y/n): ").lower().strip()
        if open_browser in ['y', 'yes', '']:
            # 延迟打开浏览器
            import threading
            timer = threading.Timer(3.0, open_browser_pages)
            timer.start()
    except KeyboardInterrupt:
        print("\n")
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()
