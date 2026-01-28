"""
后台一键启动脚本 - 支持启动、停止、重启和状态检查
"""

import os
import sys
import subprocess
import time
import signal
import psutil
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"

# PID 文件路径
BACKEND_PID_FILE = ROOT_DIR / ".backend.pid"
FRONTEND_PID_FILE = ROOT_DIR / ".frontend.pid"

# 日志文件路径
BACKEND_LOG = ROOT_DIR / "logs" / "backend.log"
FRONTEND_LOG = ROOT_DIR / "logs" / "frontend.log"


def ensure_log_dir():
    """确保日志目录存在"""
    log_dir = ROOT_DIR / "logs"
    if not log_dir.exists():
        log_dir.mkdir(parents=True)


def get_process_by_pid(pid):
    """根据 PID 获取进程对象"""
    try:
        return psutil.Process(pid)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None


def is_backend_running():
    """检查后端是否运行"""
    if not BACKEND_PID_FILE.exists():
        return False
    with open(BACKEND_PID_FILE, 'r') as f:
        pid = int(f.read().strip())
    proc = get_process_by_pid(pid)
    return proc is not None


def is_frontend_running():
    """检查前端是否运行"""
    if not FRONTEND_PID_FILE.exists():
        return False
    with open(FRONTEND_PID_FILE, 'r') as f:
        pid = int(f.read().strip())
    proc = get_process_by_pid(pid)
    return proc is not None


def start_backend():
    """启动后端服务（后台运行）"""
    if is_backend_running():
        print("⚠️  后端服务已在运行中")
        return False
    
    print("🚀 启动后端服务...")
    
    # 检查虚拟环境
    venv_dir = BACKEND_DIR / "venv"
    if not venv_dir.exists():
        print("❌ 后端虚拟环境不存在，请先运行:")
        print("   cd backend")
        print("   python -m venv venv")
        print("   source venv/bin/activate")
        print("   pip install -r requirements.txt")
        return False
    
    # 确保日志目录存在
    ensure_log_dir()
    
    # 获取 Python 可执行文件路径
    python_exe = venv_dir / "bin" / "python"
    
    # 启动后端服务（后台运行）
    cmd = [
        str(python_exe), "-m", "uvicorn", 
        "app.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ]
    
    # 使用 nohup 创建独立进程
    creation_flags = 0
    
    with open(BACKEND_LOG, 'w', encoding='utf-8') as log_file:
        process = subprocess.Popen(
            cmd,
            cwd=BACKEND_DIR,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            creationflags=creation_flags
        )
    
    # 保存 PID
    with open(BACKEND_PID_FILE, 'w') as f:
        f.write(str(process.pid))
    
    # 等待并检查是否启动成功
    time.sleep(2)
    if is_backend_running():
        print(f"✅ 后端服务启动成功 (PID: {process.pid})")
        print(f"📝 后端日志: {BACKEND_LOG}")
        print(f"🌐 后端地址: http://localhost:8000")
        print(f"📚 API 文档: http://localhost:8000/docs")
        return True
    else:
        print("❌ 后端服务启动失败，请查看日志")
        return False


def start_frontend():
    """启动前端服务（后台运行）"""
    if is_frontend_running():
        print("⚠️  前端服务已在运行中")
        return False
    
    print("🎨 启动前端服务...")
    
    # 检查 node_modules
    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        print("❌ 前端依赖未安装，请先运行:")
        print("   cd frontend")
        print("   npm install --registry=https://registry.npmmirror.com")
        return False
    
    # 确保日志目录存在
    ensure_log_dir()
    
    # 启动前端服务（后台运行）
    # 使用 nohup 启动，不使用 shell=True 以便获取正确的子进程 PID
    cmd = ["npm", "run", "dev"]
    
    with open(FRONTEND_LOG, 'w', encoding='utf-8') as log_file:
        process = subprocess.Popen(
            cmd,
            cwd=FRONTEND_DIR,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True  # Unix: 创建新会话，使进程成为会话领导者
        )
    
    # 保存 PID
    with open(FRONTEND_PID_FILE, 'w') as f:
        f.write(str(process.pid))
    
    # 等待并检查是否启动成功
    time.sleep(3)
    if is_frontend_running():
        print(f"✅ 前端服务启动成功 (PID: {process.pid})")
        print(f"📝 前端日志: {FRONTEND_LOG}")
        print(f"🌐 前端地址: http://localhost:5173")
        return True
    else:
        print("❌ 前端服务启动失败，请查看日志")
        return False


def start_all():
    """启动所有服务"""
    print("=" * 50)
    print("  寒假工具集 - 后台启动服务")
    print("=" * 50)
    print()
    
    # 启动后端
    backend_ok = start_backend()
    
    # 等待后端启动
    if backend_ok:
        time.sleep(2)
    
    # 启动前端
    frontend_ok = start_frontend()
    
    print()
    print("=" * 50)
    if backend_ok and frontend_ok:
        print("✅ 所有服务启动成功！")
        print()
        print("访问地址:")
        print("  - 前端: http://localhost:5173")
        print("  - 后端: http://localhost:8000")
        print("  - API文档: http://localhost:8000/docs")
        print()
        print("查看日志:")
        print(f"  - 后端: {BACKEND_LOG}")
        print(f"  - 前端: {FRONTEND_LOG}")
    else:
        print("⚠️  部分服务启动失败")
        if not backend_ok:
            print("  ❌ 后端启动失败")
        if not frontend_ok:
            print("  ❌ 前端启动失败")
    print("=" * 50)


def stop_backend():
    """停止后端服务"""
    if not BACKEND_PID_FILE.exists():
        print("⚠️  后端服务未运行")
        return False
    
    with open(BACKEND_PID_FILE, 'r') as f:
        pid = int(f.read().strip())
    
    proc = get_process_by_pid(pid)
    if proc:
        print(f"🛑 停止后端服务 (PID: {pid})...")
        try:
            proc.terminate()
            proc.wait(timeout=5)
            print("✅ 后端服务已停止")
        except subprocess.TimeoutExpired:
            print("⚠️  后端服务未响应，强制终止...")
            proc.kill()
            print("✅ 后端服务已强制停止")
    else:
        print("⚠️  后端进程不存在")
    
    # 删除 PID 文件
    if BACKEND_PID_FILE.exists():
        BACKEND_PID_FILE.unlink()
    
    return True


def stop_frontend():
    """停止前端服务"""
    if not FRONTEND_PID_FILE.exists():
        print("⚠️  前端服务未运行")
        return False
    
    with open(FRONTEND_PID_FILE, 'r') as f:
        pid = int(f.read().strip())
    
    proc = get_process_by_pid(pid)
    if proc:
        print(f"🛑 停止前端服务 (PID: {pid})...")
        try:
            proc.terminate()
            proc.wait(timeout=5)
            print("✅ 前端服务已停止")
        except subprocess.TimeoutExpired:
            print("⚠️  前端服务未响应，强制终止...")
            proc.kill()
            print("✅ 前端服务已强制停止")
    else:
        print("⚠️  前端进程不存在")
    
    # 删除 PID 文件
    if FRONTEND_PID_FILE.exists():
        FRONTEND_PID_FILE.unlink()
    
    return True


def stop_all():
    """停止所有服务"""
    print("=" * 50)
    print("  停止服务")
    print("=" * 50)
    print()
    
    stop_frontend()
    stop_backend()
    
    print()
    print("=" * 50)
    print("✅ 所有服务已停止")
    print("=" * 50)


def restart_all():
    """重启所有服务"""
    print("=" * 50)
    print("  重启服务")
    print("=" * 50)
    print()
    
    stop_all()
    print()
    time.sleep(2)
    start_all()


def show_status():
    """显示服务状态"""
    print("=" * 50)
    print("  服务状态")
    print("=" * 50)
    print()
    
    # 后端状态
    if is_backend_running():
        with open(BACKEND_PID_FILE, 'r') as f:
            pid = f.read().strip()
        print(f"✅ 后端服务: 运行中 (PID: {pid})")
        print(f"   地址: http://localhost:8000")
    else:
        print("❌ 后端服务: 未运行")
    
    # 前端状态
    if is_frontend_running():
        with open(FRONTEND_PID_FILE, 'r') as f:
            pid = f.read().strip()
        print(f"✅ 前端服务: 运行中 (PID: {pid})")
        print(f"   地址: http://localhost:5173")
    else:
        print("❌ 前端服务: 未运行")
    
    print()
    print("=" * 50)


def show_logs(service='all'):
    """显示服务日志"""
    ensure_log_dir()
    
    print("=" * 50)
    if service == 'all':
        print("  所有服务日志")
    elif service == 'backend':
        print("  后端服务日志")
    elif service == 'frontend':
        print("  前端服务日志")
    print("=" * 50)
    print()
    
    if service in ['all', 'backend']:
        if BACKEND_LOG.exists():
            print(f"📝 {BACKEND_LOG}:")
            print("-" * 50)
            with open(BACKEND_LOG, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # 只显示最后 50 行
                for line in lines[-50:]:
                    print(line.rstrip())
        else:
            print("📝 后端日志文件不存在")
        print()
    
    if service in ['all', 'frontend']:
        if FRONTEND_LOG.exists():
            print(f"📝 {FRONTEND_LOG}:")
            print("-" * 50)
            with open(FRONTEND_LOG, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # 只显示最后 50 行
                for line in lines[-50:]:
                    print(line.rstrip())
        else:
            print("📝 前端日志文件不存在")
        print()


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python start_background.py start    - 启动所有服务")
        print("  python start_background.py stop     - 停止所有服务")
        print("  python start_background.py restart  - 重启所有服务")
        print("  python start_background.py status   - 查看服务状态")
        print("  python start_background.py logs     - 查看所有日志")
        print("  python start_background.py logs-backend  - 查看后端日志")
        print("  python start_background.py logs-frontend - 查看前端日志")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'start':
        start_all()
    elif command == 'stop':
        stop_all()
    elif command == 'restart':
        restart_all()
    elif command == 'status':
        show_status()
    elif command == 'logs':
        show_logs('all')
    elif command == 'logs-backend':
        show_logs('backend')
    elif command == 'logs-frontend':
        show_logs('frontend')
    else:
        print(f"❌ 未知命令: {command}")
        print("使用 'python start_background.py' 查看帮助")
        sys.exit(1)


if __name__ == "__main__":
    main()
