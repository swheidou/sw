#!/usr/bin/env python3
"""
Remote Agent 项目自动设置脚本
将项目完整搬迁到指定目录
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def create_directory_structure(base_path):
    """创建项目目录结构"""
    directories = [
        "app",
        "app/models",
        "app/services", 
        "app/integrations",
        "app/utils"
    ]
    
    for directory in directories:
        dir_path = base_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录: {dir_path}")

def copy_project_files(source_path, target_path):
    """复制项目文件"""
    files_to_copy = [
        "README.md",
        "LOCAL_SETUP.md", 
        "requirements.txt",
        "Dockerfile",
        "docker-compose.yml",
        "start.bat",
        "start.sh",
        "start_local.py",
        "test_demo.py",
        "performance_test.py",
        "debug_dashboard.py",
        "monitor.py",
        "open_debug.py",
        "verify_deployment.py",
        "debug.html",
        ".gitignore"
    ]
    
    app_files = [
        ("app/__init__.py", "app/__init__.py"),
        ("app/main.py", "app/main.py"),
        ("app/models/__init__.py", "app/models/__init__.py"),
        ("app/models/schemas.py", "app/models/schemas.py"),
        ("app/services/__init__.py", "app/services/__init__.py"),
        ("app/services/order_service.py", "app/services/order_service.py"),
        ("app/services/inventory_service.py", "app/services/inventory_service.py"),
        ("app/services/pricing_service.py", "app/services/pricing_service.py"),
        ("app/integrations/__init__.py", "app/integrations/__init__.py"),
        ("app/integrations/payment_gateway.py", "app/integrations/payment_gateway.py"),
        ("app/integrations/logistics_service.py", "app/integrations/logistics_service.py"),
        ("app/integrations/notification_service.py", "app/integrations/notification_service.py"),
        ("app/integrations/external_apis.py", "app/integrations/external_apis.py"),
        ("app/utils/__init__.py", "app/utils/__init__.py"),
        ("app/utils/database.py", "app/utils/database.py")
    ]
    
    # 复制根目录文件
    for file_name in files_to_copy:
        source_file = source_path / file_name
        target_file = target_path / file_name
        
        if source_file.exists():
            shutil.copy2(source_file, target_file)
            print(f"✅ 复制文件: {file_name}")
        else:
            print(f"⚠️  文件不存在: {file_name}")
    
    # 复制app目录文件
    for source_rel, target_rel in app_files:
        source_file = source_path / source_rel
        target_file = target_path / target_rel
        
        if source_file.exists():
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, target_file)
            print(f"✅ 复制文件: {source_rel}")
        else:
            print(f"⚠️  文件不存在: {source_rel}")

def setup_project(target_directory):
    """设置项目"""
    print("🚀 Remote Agent 项目自动设置")
    print("=" * 60)
    
    # 转换为Path对象
    target_path = Path(target_directory).resolve()
    source_path = Path.cwd()
    
    print(f"📂 源目录: {source_path}")
    print(f"📁 目标目录: {target_path}")
    
    # 创建目标目录
    target_path.mkdir(parents=True, exist_ok=True)
    
    # 创建目录结构
    print("\n📁 创建目录结构...")
    create_directory_structure(target_path)
    
    # 复制文件
    print("\n📄 复制项目文件...")
    copy_project_files(source_path, target_path)
    
    # 设置权限（Linux/macOS）
    if os.name != 'nt':
        start_sh = target_path / "start.sh"
        if start_sh.exists():
            os.chmod(start_sh, 0o755)
            print("✅ 设置start.sh执行权限")
    
    print(f"\n🎉 项目设置完成！")
    print(f"📍 项目位置: {target_path}")
    print(f"\n🚀 启动项目:")
    print(f"   cd {target_path}")
    print(f"   # Windows: start.bat")
    print(f"   # Linux/macOS: ./start.sh")
    print(f"   # 跨平台: python start_local.py")
    
    return target_path

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python setup_project.py <目标目录>")
        print("示例: python setup_project.py D:/AI_Projects/remote-agent")
        sys.exit(1)
    
    target_directory = sys.argv[1]
    
    try:
        project_path = setup_project(target_directory)
        
        # 询问是否立即启动
        response = input("\n🚀 是否立即启动项目? (y/n): ").lower().strip()
        if response in ['y', 'yes', '']:
            print("\n启动项目...")
            os.chdir(project_path)
            
            if os.name == 'nt':  # Windows
                subprocess.run(["start.bat"], shell=True)
            else:  # Linux/macOS
                subprocess.run(["python", "start_local.py"])
                
    except Exception as e:
        print(f"❌ 设置失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
