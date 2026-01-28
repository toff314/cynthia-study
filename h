[1mdiff --git a/start_background.py b/start_background.py[m
[1mindex 4c6bde3..1918dbd 100644[m
[1m--- a/start_background.py[m
[1m+++ b/start_background.py[m
[36m@@ -91,26 +91,38 @@[m [mdef start_backend():[m
         "--port", "8000"[m
     ][m
     [m
[31m-    # 使用 nohup 创建独立进程[m
[31m-    creation_flags = 0[m
[31m-    [m
     with open(BACKEND_LOG, 'w', encoding='utf-8') as log_file:[m
         process = subprocess.Popen([m
             cmd,[m
             cwd=BACKEND_DIR,[m
             stdout=log_file,[m
             stderr=subprocess.STDOUT,[m
[31m-            creationflags=creation_flags[m
[32m+[m[32m            start_new_session=True  # Unix: 创建新会话[m
         )[m
     [m
[32m+[m[32m    # 等待进程启动 fork 完成[m
[32m+[m[32m    time.sleep(2)[m
[32m+[m[41m    [m
[32m+[m[32m    # 尝试获取 uvicorn 子进程（python -m uvicorn 可能会 fork）[m
[32m+[m[32m    try:[m
[32m+[m[32m        parent_process = psutil.Process(process.pid)[m
[32m+[m[32m        children = parent_process.children(recursive=True)[m
[32m+[m[32m        # 如果有子进程，使用最新的子进程 PID[m
[32m+[m[32m        if children:[m
[32m+[m[32m            actual_pid = children[-1].pid[m
[32m+[m[32m        else:[m
[32m+[m[32m            actual_pid = process.pid[m
[32m+[m[32m    except (psutil.NoSuchProcess, psutil.AccessDenied):[m
[32m+[m[32m        actual_pid = process.pid[m
[32m+[m[41m    [m
     # 保存 PID[m
     with open(BACKEND_PID_FILE, 'w') as f:[m
[31m-        f.write(str(process.pid))[m
[32m+[m[32m        f.write(str(actual_pid))[m
     [m
     # 等待并检查是否启动成功[m
[31m-    time.sleep(2)[m
[32m+[m[32m    time.sleep(1)[m
     if is_backend_running():[m
[31m-        print(f"✅ 后端服务启动成功 (PID: {process.pid})")[m
[32m+[m[32m        print(f"✅ 后端服务启动成功 (PID: {actual_pid})")[m
         print(f"📝 后端日志: {BACKEND_LOG}")[m
         print(f"🌐 后端地址: http://localhost:8000")[m
         print(f"📚 API 文档: http://localhost:8000/docs")[m
