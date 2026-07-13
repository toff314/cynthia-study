#!/bin/bash
# 每日增量爬取试卷并导入数据库
# crontab: 0 3 * * * /home/yuanwu/cynthia-study/backend/scripts/daily_crawl.sh >> /var/log/crawl.log 2>&1

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
cd "$BACKEND_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始每日爬取..."

# 爬取同步教学试卷（语文 1-3年级上册）
python3 scripts/crawl_sync_papers.py --subject chinese --grade 1 --semester 1 --max-papers 100 2>&1 || true
python3 scripts/crawl_sync_papers.py --subject chinese --grade 2 --semester 1 --max-papers 100 2>&1 || true
python3 scripts/crawl_sync_papers.py --subject chinese --grade 3 --semester 1 --max-papers 100 2>&1 || true

# 爬取JDC基础达标（数学+英语）
python3 scripts/crawl_questions.py --subject math --category jdcs --pages 2 2>&1 || true
python3 scripts/crawl_questions.py --subject chinese --category jdcs --pages 2 2>&1 || true
python3 scripts/crawl_questions.py --subject english --category jdcs --pages 2 2>&1 || true

# 导入到数据库
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 导入数据库..."
python3 << 'PYEOF'
import json, sys
from pathlib import Path
from app.database import SessionLocal
from app.models.study import QuestionBank

all_papers = []
for fname in ["sync_papers.json", "crawled_papers.json"]:
    fp = Path("data") / fname
    if fp.exists():
        data = json.load(open(fp, 'r', encoding='utf-8'))
        all_papers.extend(data["papers"])

if not all_papers:
    print("无试卷数据")
    sys.exit(0)

db = SessionLocal()
created, skipped = 0, 0
smap = {"math": "数学", "chinese": "语文", "english": "英语"}

def infer_subject(paper):
    s = paper.get("subject") or paper.get("subject_name")
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

db.close()
print(f"导入: +{created} 跳过{skipped}")
PYEOF

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 每日爬取完成"
