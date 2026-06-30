#!/usr/bin/env python3
"""
一键部署脚本
参考: /home/yuanwu/zhihu-wiki/scripts/deploy.sh

用法:
    sudo python deploy.py build     # 仅构建前端
    sudo python deploy.py nginx     # 安装/配置/启动 nginx
    sudo python deploy.py start     # 启动后端 + nginx
    sudo python deploy.py stop      # 停止后端 + nginx
    sudo python deploy.py restart   # 重启后端 + nginx
    sudo python deploy.py reload    # 重载 nginx + 重启后端
    sudo python deploy.py status    # 查看状态
    sudo python deploy.py serve     # 完整部署: build + nginx + start
"""

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# 项目路径
ROOT = Path(__file__).parent.resolve()
FRONTEND_DIR = ROOT / "frontend"
BACKEND_DIR = ROOT / "backend"
VENV_DIR = ROOT / "venv"
NGINX_CONF_SRC = ROOT / "deploy" / "nginx-cynthia.conf"
NGINX_CONF_DST = Path("/etc/nginx/conf.d/cynthia-study.conf")

SERVICE_NAME = "cynthia-study"
DOMAIN = "cynthia.askfount.com"


def run(cmd, cwd=None, check=True):
    """执行命令并打印"""
    cmd_str = " ".join(str(c) for c in cmd)
    print(f"==> {cmd_str}")
    return subprocess.run(cmd, cwd=cwd, check=check)


def build():
    """构建前端"""
    print("==> Building frontend...")
    if not (FRONTEND_DIR / "node_modules").exists():
        print("==> Installing frontend dependencies...")
        run(
            ["npm", "install", "--registry=https://registry.npmmirror.com"],
            cwd=FRONTEND_DIR,
        )
    run(["npm", "run", "build"], cwd=FRONTEND_DIR)
    print("==> Frontend built successfully.")


def nginx_install():
    """安装 nginx（如未安装）"""
    if shutil.which("nginx"):
        print("==> nginx already installed.")
        return

    print("==> Installing nginx...")
    if shutil.which("yum"):
        run(["yum", "install", "-y", "-q", "nginx"])
    elif shutil.which("apt"):
        run(["apt", "update", "-y"])
        run(["apt", "install", "-y", "nginx"])
    else:
        raise RuntimeError("Unsupported package manager. Please install nginx manually.")


def nginx_configure():
    """配置 nginx"""
    print(f"==> Configuring nginx for {DOMAIN}...")
    if not NGINX_CONF_SRC.exists():
        raise FileNotFoundError(f"nginx config not found: {NGINX_CONF_SRC}")
    shutil.copy(NGINX_CONF_SRC, NGINX_CONF_DST)
    run(["nginx", "-t"])


def nginx_start():
    """启动/重启 nginx"""
    print("==> Starting nginx...")
    run(["systemctl", "enable", "nginx"])
    run(["systemctl", "restart", "nginx"])


def install_backend_service():
    """安装后端 systemd 服务"""
    service_path = Path(f"/etc/systemd/system/{SERVICE_NAME}.service")
    if service_path.exists():
        return

    print(f"==> Installing {SERVICE_NAME} systemd service...")
    venv_python = VENV_DIR / "bin" / "python"
    if not venv_python.exists():
        raise FileNotFoundError(f"Backend venv not found: {venv_python}")

    service_content = f"""[Unit]
Description={SERVICE_NAME} FastAPI backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={BACKEND_DIR}
ExecStart={venv_python} -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
    service_path.write_text(service_content, encoding="utf-8")
    run(["systemctl", "daemon-reload"])


def backend_is_running():
    """检查后端是否运行"""
    result = subprocess.run(
        ["systemctl", "is-active", "--quiet", SERVICE_NAME],
        capture_output=True,
    )
    return result.returncode == 0


def backend_start():
    """启动后端"""
    install_backend_service()
    print(f"==> Starting {SERVICE_NAME}...")
    run(["systemctl", "enable", SERVICE_NAME])
    run(["systemctl", "restart", SERVICE_NAME])

    time.sleep(2)
    if backend_is_running():
        print(f"==> {SERVICE_NAME} is running.")
    else:
        print(f"==> ERROR: {SERVICE_NAME} failed to start!")
        run(
            ["journalctl", "-u", SERVICE_NAME, "--no-pager", "-n", "20"],
            check=False,
        )
        sys.exit(1)


def backend_stop():
    """停止后端"""
    print(f"==> Stopping {SERVICE_NAME}...")
    run(["systemctl", "stop", SERVICE_NAME], check=False)


def start():
    """启动后端 + nginx"""
    nginx_configure()
    backend_start()
    nginx_start()
    print(f"==> Services started. Visit http://{DOMAIN}")


def stop():
    """停止后端 + nginx"""
    backend_stop()
    print("==> Stopping nginx...")
    run(["systemctl", "stop", "nginx"], check=False)


def restart():
    """重启后端 + nginx"""
    stop()
    time.sleep(1)
    start()


def reload():
    """重载 nginx 配置并重启后端"""
    nginx_configure()
    print("==> Reloading nginx...")
    run(["nginx", "-s", "reload"], check=False)
    backend_start()


def status():
    """查看服务状态"""
    print("--- nginx ---")
    run(["systemctl", "status", "nginx"], check=False)
    print(f"--- {SERVICE_NAME} ---")
    run(["systemctl", "status", SERVICE_NAME], check=False)


def serve():
    """完整部署"""
    build()
    nginx_install()
    start()
    print("============================================")
    print(f"  http://{DOMAIN}  -> nginx -> static files")
    print(f"  /api/*          -> backend localhost:8000")
    print("============================================")


def main():
    parser = argparse.ArgumentParser(description="Cynthia Study deployment script")
    parser.add_argument(
        "command",
        choices=["build", "nginx", "start", "stop", "restart", "reload", "status", "serve"],
        help="部署命令",
    )
    args = parser.parse_args()

    commands = {
        "build": build,
        "nginx": lambda: (nginx_install(), nginx_configure(), nginx_start()),
        "start": start,
        "stop": stop,
        "restart": restart,
        "reload": reload,
        "status": status,
        "serve": serve,
    }

    try:
        commands[args.command]()
    except subprocess.CalledProcessError as e:
        print(f"==> Command failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"==> Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
