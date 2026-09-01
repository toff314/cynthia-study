"""
批量爬取所有年级/科目/学期的同步教学试卷，并导入数据库

Usage:
    python batch_crawl_all.py           # 爬取所有
    python batch_crawl_all.py --dry-run  # 仅预览
    python batch_crawl_all.py --import   # 爬取并导入
"""
import argparse
import json
import logging
import sys
from pathlib import Path
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from crawl_sync_papers import crawl_sync_papers, setup_logging as setup_sync_logging
from crawl_questions import crawl_papers as crawl_jdcs_papers, setup_logging as setup_jdcs_logging

logger = logging.getLogger("batch_crawl")
DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_FILE = DATA_DIR / "all_papers.json"
DB_FILE = DATA_DIR / "cynthia.db"

SUBJECTS = ["math", "chinese", "english"]
GRADES = [1, 2, 3, 4, 5, 6]
SEMESTERS = [1, 2]  # 1=上册, 2=下册

CATEGORIES = ["jdcs", "zqjm"]  # 基础达标, 期中期末

TYPES = ["t1", "t2", "t31"]  # 课后练习, 单元测验, 课前预习


def crawl_all_sync():
    """爬取所有同步教学试卷"""
    all_papers = []
    total = len(SUBJECTS) * len(GRADES) * len(SEMESTERS)

    i = 0
    for subject in SUBJECTS:
        for grade in GRADES:
            for semester in SEMESTERS:
                i += 1
                logger.info(f"[{i}/{total}] 同步: {subject} {grade}年级 {'上册' if semester == 1 else '下册'}")

                try:
                    papers = crawl_sync_papers(
                        subject=subject,
                        grade=grade,
                        semester=semester,
                        max_papers=0,
                    )

                    for p in papers:
                        p["subject"] = subject
                        p["grade"] = grade

                    all_papers.extend(papers)
                    logger.info(f"  -> 获取 {len(papers)} 张试卷")

                except Exception as e:
                    logger.error(f"  -> 失败: {e}")

    return all_papers


def crawl_all_jdcs():
    """爬取所有基础达标/期中期末试卷（不限制年级）"""
    all_papers = []

    for subject in SUBJECTS:
        for category in CATEGORIES:
            logger.info(f"JDC: {subject} {category}")

            try:
                papers = crawl_jdcs_papers(
                    subject=subject,
                    category=category,
                    pages=2,
                    grade=0,
                    max_papers=0,
                )

                for p in papers:
                    p["subject"] = subject
                    p["category"] = category

                all_papers.extend(papers)
                logger.info(f"  -> 获取 {len(papers)} 张试卷")

            except Exception as e:
                logger.error(f"  -> 失败: {e}")

    return all_papers


def import_to_db(papers: list):
    """导入试卷到数据库"""
    from app.database import SessionLocal
    from app.models.study import QuestionBank
    from clean_question_bank import clean_question_dict

    db = SessionLocal()
    created = 0
    skipped = 0

    subject_map = {
        "math": "数学", "chinese": "语文", "english": "英语",
    }

    for paper in papers:
        subject = subject_map.get(paper.get("subject", ""), "数学")
        grade = paper.get("grade", 4)
        url = paper.get("url", "")

        for q in paper.get("questions", []):
            q = clean_question_dict(q)
            existing = db.query(QuestionBank).filter(
                QuestionBank.question_text == q["question_text"]
            ).first()

            if existing:
                skipped += 1
                continue

            new_q = QuestionBank(
                subject=subject,
                grade=grade,
                question_type=q.get("question_type", "short_answer"),
                question_text=q.get("question_text", ""),
                options=json.dumps(q.get("options")) if q.get("options") else None,
                answer=q.get("answer", ""),
                explanation=q.get("explanation", ""),
                source=url,
                difficulty=paper.get("difficulty", "medium"),
            )
            db.add(new_q)
            created += 1

    db.commit()
    db.close()
    logger.info(f"导入完成: {created} 新增, {skipped} 跳过")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync-only", action="store_true", help="仅爬取同步教学")
    parser.add_argument("--jdcs-only", action="store_true", help="仅爬取基础达标/期中期末")
    parser.add_argument("--import", dest="do_import", action="store_true", help="导入到数据库")
    parser.add_argument("--dry-run", action="store_true", help="仅预览不爬取")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

    if args.dry_run:
        total = len(SUBJECTS) * len(GRADES) * len(SEMESTERS)
        logger.info(f"将爬取 {total} 个同步教学组合 (3科目 x 6年级 x 2学期)")
        return

    all_papers = []

    if not args.jdcs_only:
        setup_sync_logging(args.verbose)
        sync_papers = crawl_all_sync()
        all_papers.extend(sync_papers)

    if not args.sync_only:
        setup_jdcs_logging(args.verbose)
        jdcs_papers = crawl_all_jdcs()
        all_papers.extend(jdcs_papers)

    # 保存到文件
    data = {
        "crawled_at": datetime.now().isoformat(),
        "total_papers": len(all_papers),
        "papers": all_papers,
    }
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"总计 {len(all_papers)} 张试卷 -> {OUTPUT_FILE}")

    # 按科目统计
    subjects = {}
    for p in all_papers:
        s = p.get("subject", "unknown")
        subjects[s] = subjects.get(s, 0) + 1
    logger.info(f"按科目: {subjects}")

    # 导入数据库
    if args.do_import and all_papers:
        import_to_db(all_papers)

    logger.info("全部完成!")


if __name__ == "__main__":
    main()
