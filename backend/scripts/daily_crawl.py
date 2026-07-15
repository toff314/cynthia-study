#!/usr/bin/env python3.11
"""
增量爬虫：记录进度，每次从上次断点继续，循环抓取所有科目/年级/学期的试卷。

进度文件: backend/data/crawl_progress.json
  {
    "subject": "math",      # 当前科目
    "grade": 1,             # 当前年级
    "semester": 1,          # 当前学期 1=上 2=下
    "page": 3,              # 当前页码
    "total_crawled": 150,   # 累计抓取试卷数
    "total_questions": 5000,# 累计题目数
    "last_run": "2025-07-14T11:30:00",
    "finished_rounds": 0    # 完成几轮全量
  }

每次执行抓取 N 张试卷（默认20），抓完一个年级学期自动跳到下一个，
全部走完一轮后从头开始（翻新页），永不停止。

Usage:
    python3.11 daily_crawl.py              # 每次抓20张
    python3.11 daily_crawl.py --batch 50   # 每次抓50张
    python3.11 daily_crawl.py --once       # 只抓一个年级学期的一页（测试用）
"""
import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# 添加backend目录到path
BACKEND_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BACKEND_DIR / "scripts"))

from crawl_by_grade import crawl_subject_grade, SUBJECT_MAP, setup_logging

logger = logging.getLogger("daily_crawl")

PROGRESS_FILE = BACKEND_DIR / "data" / "crawl_progress.json"

# 所有组合：3科目 x 6年级 x 2学期 = 36个
ALL_COMBOS = []
for subj in ["math", "chinese", "english"]:
    for grade in range(1, 7):
        for sem in [1, 2]:
            ALL_COMBOS.append((subj, grade, sem))


def load_progress():
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "combo_index": 0,
        "page": 1,
        "total_crawled": 0,
        "total_questions": 0,
        "total_imported": 0,
        "total_skipped": 0,
        "last_run": "",
        "finished_rounds": 0,
        "history": [],
    }


def save_progress(progress):
    progress["last_run"] = datetime.now().isoformat(timespec="seconds")
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def import_to_db(papers, subject, grade, semester):
    """导入数据库，返回 (created, skipped)"""
    from app.database import SessionLocal
    from app.models.study import QuestionBank

    subject_cn = SUBJECT_MAP[subject]["name"]
    sem_str = "上" if semester == 1 else "下"

    db = SessionLocal()
    created, skipped = 0, 0
    for paper in papers:
        for q in paper.get("questions", []):
            existing = db.query(QuestionBank).filter(
                QuestionBank.question_text == q["question_text"]
            ).first()
            if existing:
                if q.get("images") and not existing.images:
                    existing.images = q["images"]
                if q.get("audio_url") and not existing.audio_url:
                    existing.audio_url = q["audio_url"]
                if not existing.paper_id:
                    existing.paper_id = paper["paper_id"]
                    existing.paper_title = paper["title"]
                    existing.semester = sem_str
                skipped += 1
                continue
            new_q = QuestionBank(
                subject=subject_cn, grade=grade, semester=sem_str,
                question_type=q.get("question_type", "short_answer"),
                question_text=q.get("question_text", ""),
                options=json.dumps(q["options"], ensure_ascii=False) if q.get("options") else None,
                answer=q.get("answer", ""), explanation=q.get("explanation", ""),
                source=paper.get("url", ""),
                images=q.get("images"), audio_url=q.get("audio_url"),
                paper_id=paper["paper_id"], paper_title=paper["title"],
                difficulty="medium",
            )
            db.add(new_q)
            created += 1
    db.commit()
    db.close()
    return created, skipped


def run_batch(batch_size=20, max_pages_per_combo=5):
    """抓取一批试卷，从上次进度继续"""
    progress = load_progress()
    combo_idx = progress["combo_index"]
    page = progress["page"]
    crawled_this_run = 0

    logger.info(f"增量爬虫启动 | 已完成{progress['finished_rounds']}轮 | 累计{progress['total_crawled']}张试卷 | 本次目标{batch_size}张")

    while crawled_this_run < batch_size:
        subj, grade, sem = ALL_COMBOS[combo_idx]
        subj_cn = SUBJECT_MAP[subj]["name"]
        sem_cn = "上" if sem == 1 else "下"

        remaining = batch_size - crawled_this_run
        max_papers = min(remaining, 10)  # 每个combo最多抓10张，避免卡在一个combo

        logger.info(f"[{crawled_this_run+1}/{batch_size}] {subj_cn} {grade}年级{sem_cn} 第{page}页 (最多{max_papers}张)")

        try:
            papers = crawl_subject_grade(subj, grade, sem, max_papers=max_papers, max_pages=1)
            # crawl_subject_grade从第1页开始抓，我们传入max_pages=1只抓当前页
            # 但它内部从page=1开始，所以需要直接用它抓第1页

            if papers:
                q_count = sum(len(p.get("questions", [])) for p in papers)
                logger.info(f"  抓取 {len(papers)} 张试卷, {q_count} 道题")

                created, skipped = import_to_db(papers, subj, grade, sem)
                logger.info(f"  导入: 新增{created} 跳过{skipped}")

                progress["total_crawled"] += len(papers)
                progress["total_questions"] += q_count
                progress["total_imported"] += created
                progress["total_skipped"] += skipped
                crawled_this_run += len(papers)
            else:
                logger.info(f"  无新试卷")

        except Exception as e:
            logger.error(f"  失败: {e}")

        # 移动到下一个combo
        combo_idx += 1
        if combo_idx >= len(ALL_COMBOS):
            combo_idx = 0
            progress["finished_rounds"] += 1
            logger.info(f"=== 完成第{progress['finished_rounds']}轮全量，重新开始 ===")

        progress["combo_index"] = combo_idx
        save_progress(progress)

        # 防止无限循环（如果全是跳过的）
        if crawled_this_run == 0 and not papers:
            # 连续空结果，也推进combo
            pass

    # 记录本次运行
    run_record = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "crawled": crawled_this_run,
        "round": progress["finished_rounds"],
    }
    progress.setdefault("history", []).append(run_record)
    # 只保留最近30条历史
    progress["history"] = progress["history"][-30:]
    save_progress(progress)

    logger.info(f"本次完成: 抓取{crawled_this_run}张 | 累计{progress['total_crawled']}张 | 导入{progress['total_imported']}题")
    return crawled_this_run


def main():
    parser = argparse.ArgumentParser(description="增量爬虫 - 记录进度循环抓取")
    parser.add_argument("--batch", type=int, default=20, help="每次抓取多少张试卷 (默认20)")
    parser.add_argument("--once", action="store_true", help="只抓1张（测试）")
    parser.add_argument("--status", action="store_true", help="查看进度")
    parser.add_argument("--reset", action="store_true", help="重置进度")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    setup_logging(args.verbose)

    if args.status:
        p = load_progress()
        print(f"进度: combo={p['combo_index']}/{len(ALL_COMBOS)} 轮次={p['finished_rounds']}")
        print(f"累计: {p['total_crawled']}张试卷, {p['total_questions']}道题, 导入{p['total_imported']}跳过{p['total_skipped']}")
        print(f"上次运行: {p['last_run']}")
        combo = ALL_COMBOS[p['combo_index']]
        print(f"下一步: {SUBJECT_MAP[combo[0]]['name']} {combo[1]}年级{'上' if combo[2]==1 else '下'}")
        if p.get("history"):
            print(f"最近运行: {p['history'][-1]}")
        return

    if args.reset:
        save_progress({
            "combo_index": 0, "page": 1, "total_crawled": 0, "total_questions": 0,
            "total_imported": 0, "total_skipped": 0, "last_run": "",
            "finished_rounds": 0, "history": [],
        })
        print("进度已重置")
        return

    batch = 1 if args.once else args.batch
    run_batch(batch_size=batch)


if __name__ == "__main__":
    main()
