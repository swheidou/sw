# Remote Agent 项目搬迁到D盘 PowerShell脚本

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "🚀 Remote Agent 项目搬迁到 D:/AI_Projects/" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan

$targetDir = "D:\AI_Projects\remote-agent"

Write-Host "📁 目标目录: $targetDir" -ForegroundColor Yellow
Write-Host ""

# 创建目标目录
Write-Host "📂 创建目标目录..." -ForegroundColor Blue
New-Item -ItemType Directory -Path "D:\AI_Projects" -Force | Out-Null
New-Item -ItemType Directory -Path $targetDir -Force | Out-Null

# 检查Git
try {
    git --version | Out-Null
    Write-Host "✅ Git已安装，使用Git克隆..." -ForegroundColor Green
    
    Set-Location "D:\AI_Projects"
    
    # 如果目录已存在且不为空，先删除
    if (Test-Path $targetDir) {
        Remove-Item $targetDir -Recurse -Force
    }
    
    git clone https://github.com/swheidou/sw.git remote-agent
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Git克隆成功" -ForegroundColor Green
    } else {
        throw "Git克隆失败"
    }
} catch {
    Write-Host "⚠️  Git不可用，请手动下载项目" -ForegroundColor Yellow
    Write-Host "📍 GitHub地址: https://github.com/swheidou/sw" -ForegroundColor Cyan
    Write-Host "💡 或者下载ZIP: https://github.com/swheidou/sw/archive/refs/heads/master.zip" -ForegroundColor Cyan
    
    # 打开GitHub页面
    Start-Process "https://github.com/swheidou/sw"
    
    Read-Host "请手动下载并解压到 $targetDir 后按回车继续"
}

# 切换到项目目录
Set-Location $targetDir

# 检查Python
try {
    python --version | Out-Null
    Write-Host "✅ Python已安装" -ForegroundColor Green
} catch {
    Write-Host "❌ Python未安装或未添加到PATH" -ForegroundColor Red
    Write-Host "请从 https://python.org 下载并安装Python 3.8+" -ForegroundColor Yellow
    Start-Process "https://python.org/downloads/"
    Read-Host "安装Python后按回车继续"
    exit 1
}

# 检查项目文件
if (Test-Path "requirements.txt") {
    Write-Host "✅ 项目文件完整" -ForegroundColor Green
} else {
    Write-Host "❌ 项目文件不完整" -ForegroundColor Red
    Write-Host "请确保从GitHub正确下载了完整项目" -ForegroundColor Yellow
    exit 1
}

# 安装依赖
Write-Host ""
Write-Host "📦 安装Python依赖..." -ForegroundColor Blue
python -m pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 依赖安装完成" -ForegroundColor Green
} else {
    Write-Host "❌ 依赖安装失败" -ForegroundColor Red
    Read-Host "按回车退出"
    exit 1
}

# 启动项目
Write-Host ""
Write-Host "🚀 启动Remote Agent项目..." -ForegroundColor Green
Write-Host "📍 服务地址: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API文档: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "💡 按 Ctrl+C 停止服务" -ForegroundColor Yellow
Write-Host "----------------------------------------------------------------" -ForegroundColor Gray

# 延迟3秒后打开浏览器
Start-Job -ScriptBlock {
    Start-Sleep 3
    Start-Process "http://localhost:8000/docs"
} | Out-Null

# 启动服务
if (Test-Path "start_local.py") {
    python start_local.py
} elseif (Test-Path "app\main.py") {
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
} else {
    Write-Host "❌ 找不到启动文件" -ForegroundColor Red
    Read-Host "按回车退出"
}

Read-Host "按回车退出"
