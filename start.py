"""
一键启动脚本 - 同时启动后端和前端服务
"""

import sys
import subprocess
import threading
import webbrowser
import time
import os
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"


def start_backend():
    """启动后端服务"""
    print("🚀 启动后端服务...")
    
    # 检查虚拟环境
    venv_dir = BACKEND_DIR / "venv"
    if venv_dir.exists():
        # 使用虚拟环境的 Python
        if os.name == 'nt':  # Windows
            python_exe = venv_dir / "Scripts" / "python.exe"
        else:  # Linux/macOS
            python_exe = venv_dir / "bin" / "python3"
    else:
        # 使用系统 Python
        print("⚠️  未检测到虚拟环境，使用系统 Python")
        python_exe = sys.executable
    
    # 切换到后端目录
    os.chdir(BACKEND_DIR)
    cmd = [str(python_exe), "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
    subprocess.run(cmd, check=True)


def start_frontend():
    """启动前端开发服务器"""
    print("🎨 启动前端服务...")
    
    # 检查 node_modules
    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        print("❌ 前端依赖未安装，请先运行:")
        print("   cd frontend")
        print("   npm install")
        return
    
    # 启动前端
    os.chdir(FRONTEND_DIR)
    subprocess.run("npm run dev", shell=True)


def install_dependencies():
    """安装依赖"""
    print("📦 安装依赖...")
    
    # 安装后端依赖
    print("\n--- 安装后端依赖 ---")
    venv_dir = BACKEND_DIR / "venv"
    
    if not venv_dir.exists():
        print("创建虚拟环境...")
        os.chdir(BACKEND_DIR)
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    
    # 根据操作系统选择正确的 Python 可执行文件路径
    if os.name == 'nt':  # Windows
        python_cmd = str(venv_dir / "Scripts" / "python.exe")
    else:  # Linux/macOS
        python_cmd = str(venv_dir / "bin" / "python")
    
    # 使用虚拟环境的 Python 直接安装依赖
    os.chdir(BACKEND_DIR)
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    # 检测 Python 版本，如果是 3.14+ 使用 PyPI 官方源（有预编译包）
    python_version = sys.version_info
    if python_version >= (3, 14):
        print("检测到 Python 3.14+，使用 PyPI 官方源")
        subprocess.run([
            python_cmd, "-m", "pip", "install", "-r", "requirements.txt",
            "-i", "https://pypi.org/simple"
        ], encoding='utf-8', env=env, check=True)
    else:
        print("使用清华镜像源加速")
        subprocess.run([
            python_cmd, "-m", "pip", "install", "-r", "requirements.txt",
            "-i", "https://pypi.tuna.tsinghua.edu.cn/simple",
            "--trusted-host", "pypi.tuna.tsinghua.edu.cn"
        ], encoding='utf-8', env=env, check=True)
    
    print("✅ 后端依赖安装完成")
    
    # 安装前端依赖
    print("\n--- 安装前端依赖 ---")
    os.chdir(FRONTEND_DIR)
    subprocess.run(["npm", "install","--registry=https://registry.npmmirror.com"], encoding='utf-8', check=True)
    print("✅ 前端依赖安装完成")


def main():
    """主函数"""
    print("=" * 50)
    print("  寒假工具集 - 一键启动脚本")
    print("=" * 50)
    
    # 检查是否需要安装依赖
    venv_exists = (BACKEND_DIR / "venv").exists()
    node_modules_exists = (FRONTEND_DIR / "node_modules").exists()
    
    if not venv_exists or not node_modules_exists:
        print("\n📦 正在检查依赖...")
        install_dependencies()
        print("\n✅ 依赖安装完成！")
    
    print("\n🚀 启动服务...")
    print("后端地址: http://localhost:8000")
    print("前端地址: http://localhost:5173")
    print("API 文档: http://localhost:8000/docs")
    print("\n按 Ctrl+C 停止服务\n")
    
    # 等待用户确认
    input("按 Enter 键开始启动...")
    
    # 创建线程启动后端
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # 等待后端启动
    time.sleep(2)
    
    # 启动前端（在主线程中）
    try:
        # 自动打开浏览器
        time.sleep(3)
        webbrowser.open("http://localhost:5173")
        print("✅ 已自动打开浏览器")
        
        # 启动前端
        start_frontend()
    except KeyboardInterrupt:
        print("\n\n👋 服务已停止")


if __name__ == "__main__":
    main()
