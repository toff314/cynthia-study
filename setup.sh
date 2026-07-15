#!/bin/bash
# cynthia-study 项目初始化脚本
# 用法: ./setup.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "========================================"
echo " cynthia-study 项目初始化"
echo "========================================"

# 1. 检查 Python 环境
echo "[1/6] 检查 Python 环境..."
if ! command -v python3 &>/dev/null; then
    echo "错误: 需要 Python 3.10+"
    exit 1
fi

# 2. 安装后端依赖
echo "[2/6] 安装后端依赖..."
cd "$BACKEND_DIR"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt 2>/dev/null || pip install -q fastapi uvicorn sqlalchemy pydantic

# 安装 playwright (用于爬虫) - 可选，跳过安装失败
if ! python3 -c "import playwright" 2>/dev/null; then
    echo "  playwright 安装失败（跳过，不影响核心功能）"
fi

# 3. 初始化数据库 & 导入题库
echo "[3/6] 初始化数据库..."
python3 << 'PYEOF'
from app.database import init_db
init_db()
print("数据库初始化完成")
PYEOF

# 导入题库数据
echo "[4/6] 导入题库数据..."
python3 << 'PYEOF'
import json, sys
from pathlib import Path
from app.database import SessionLocal
from app.models.study import QuestionBank

DATA_FILES = ["data/crawled_papers.json", "data/sync_papers.json"]
all_papers = []
for fn in DATA_FILES:
    fp = Path(fn)
    if fp.exists():
        data = json.load(open(fp, 'r', encoding='utf-8'))
        all_papers.extend(data["papers"])
        print(f"  加载 {fn}: {len(data['papers'])} 张试卷")

if not all_papers:
    print("  无本地题库数据，请先运行爬虫")
    sys.exit(0)

db = SessionLocal()
created, skipped = 0, 0

def infer_subject(paper):
    s = paper.get("subject") or paper.get("subject_name")
    smap = {"math": "数学", "chinese": "语文", "english": "英语"}
    if s: return smap.get(s, s)
    bid = str(paper.get("bank_id", ""))
    if bid == "23": return "数学"
    if bid == "24": return "语文"
    if bid == "25": return "英语"
    url = paper.get("url", "")
    if "xxsx" in url: return "数学"
    if "xxyw" in url: return "语文"
    if "xxyy" in url: return "英语"
    return "数学"

for paper in all_papers:
    subject = infer_subject(paper)
    grade = paper.get("grade", 4)
    url = paper.get("url", "")
    for q in paper.get("questions", []):
        existing = db.query(QuestionBank).filter(
            QuestionBank.question_text == q["question_text"]
        ).first()
        if existing:
            skipped += 1
            continue
        new_q = QuestionBank(
            subject=subject, grade=grade,
            question_type=q.get("question_type", "short_answer"),
            question_text=q.get("question_text", ""),
            options=json.dumps(q.get("options")) if q.get("options") else None,
            answer=q.get("answer", ""), explanation=q.get("explanation", ""),
            source=url, difficulty=paper.get("difficulty", "medium"),
        )
        db.add(new_q)
        created += 1
db.commit()

total = db.query(QuestionBank).count()
print(f"  题目总数: {total} (新增 {created}, 跳过 {skipped})")
db.close()
PYEOF

# 5. 安装前端依赖 & 构建
echo "[5/6] 安装前端依赖..."
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    npm install 2>/dev/null || true
fi
npx vite build 2>&1 | tail -1

# 6. 启动服务
echo "[6/6] 启动服务..."
cd "$BACKEND_DIR"
source venv/bin/activate

# 杀掉旧进程
kill $(lsof -t -i:8000) 2>/dev/null || true

# 启动后端
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/cynthia-backend.log 2>&1 &
echo "后端已启动: http://0.0.0.0:8000"

# 启动前端dev server (可选，也可用 nginx 服务 dist/)
cd "$FRONTEND_DIR"
kill $(lsof -t -i:5173) 2>/dev/null || true
# 使用setsid确保进程在后台持续运行
setsid npx vite --host 0.0.0.0 > /tmp/cynthia-frontend.log 2>&1 &

# 等待前端启动并获取实际端口
sleep 3
FRONTEND_PORT=$(grep -oP "Network: http://[^:]+:\K\d+" /tmp/cynthia-frontend.log | head -1)
if [ -z "$FRONTEND_PORT" ]; then
    FRONTEND_PORT="5173"  # 默认端口
fi
echo "前端已启动: http://0.0.0.0:$FRONTEND_PORT"

# 7. 设置每日计划任务
echo ""
echo "设置每日增量爬取计划任务 (每天凌晨3点)..."
(crontab -l 2>/dev/null | grep -v "daily_crawl.sh"; echo "0 3 * * * $BACKEND_DIR/scripts/daily_crawl.sh >> /var/log/crawl.log 2>&1") | crontab -

echo ""
echo "========================================"
echo " 初始化完成!"
echo " 前端: http://0.0.0.0:$FRONTEND_PORT"
echo " 后端: http://0.0.0.0:8000"
echo " API文档: http://0.0.0.0:8000/docs"
echo "========================================"
