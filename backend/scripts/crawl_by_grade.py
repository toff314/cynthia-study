"""
按年级学期抓取基础达标试卷（jdcs），含图片和音频

URL格式: https://zujuan.xkw.com/{prefix}/shijuan/jdcs/g{grade}_{semester}
  xxsx=数学, xxyw=语文, xxyy=英语
  g1_1=一年级上, g1_2=一年级下, ... g6_2=六年级下

Usage:
    python3.11 crawl_by_grade.py --subject math --grade 1 --semester 1
    python3.11 crawl_by_grade.py --all --import
    python3.11 crawl_by_grade.py --all --import --max-papers 3
"""
import argparse
import json
import logging
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

logger = logging.getLogger("crawl_by_grade")

SUBJECT_MAP = {
    "math": {"name": "数学", "prefix": "xxsx", "bank_id": "23"},
    "chinese": {"name": "语文", "prefix": "xxyw", "bank_id": "24"},
    "english": {"name": "英语", "prefix": "xxyy", "bank_id": "25"},
}

BASE_URL = "https://zujuan.xkw.com"
DATA_DIR = Path(__file__).parent.parent / "data"


def setup_logging(verbose=False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")


def build_url(subject: str, grade: int, semester: int, page: int = 1) -> str:
    prefix = SUBJECT_MAP[subject]["prefix"]
    if page == 1:
        return f"{BASE_URL}/{prefix}/shijuan/jdcs/g{grade}_{semester}"
    return f"{BASE_URL}/{prefix}/shijuan/jdcs/g{grade}_{semester}/{page}/"


def extract_paper_links(page) -> list[dict]:
    papers = []
    seen = set()
    for link in page.query_selector_all('a[href]'):
        href = (link.get_attribute("href") or "").strip()
        if not href or href.startswith("javascript"):
            continue
        href = urljoin(BASE_URL, href)
        m = re.search(r"/(\d+)p(\d+)\.html", href)
        if not m:
            continue
        bank_id, paper_id = m.group(1), m.group(2)
        if paper_id in seen:
            continue
        title = link.inner_text().strip()
        if len(title) < 5 or title in ("删除", "收藏", "加入试卷篮"):
            continue
        seen.add(paper_id)
        papers.append({"paper_id": paper_id, "bank_id": bank_id, "title": re.sub(r"\s+", " ", title), "url": href})
    return papers


def extract_questions(page) -> list[dict]:
    questions = []
    blocks = page.query_selector_all(".tk-quest-item")
    logger.debug(f"  找到 {len(blocks)} 个题目区块")

    for block in blocks:
        try:
            # 图片
            images = []
            for img in block.query_selector_all("img"):
                src = (img.get_attribute("src") or "").strip()
                if not src:
                    continue
                if src.startswith("//"):
                    src = "https:" + src
                elif src.startswith("/"):
                    src = BASE_URL + src
                w = img.get_attribute("width") or ""
                if w and int(w) < 50:
                    continue
                images.append(src)

            # 音频
            audio_url = None
            for el in block.query_selector_all("audio source, audio"):
                src = el.get_attribute("src") or ""
                if not src:
                    src = el.get_attribute("data-src") or ""
                if src:
                    if src.startswith("//"):
                        src = "https:" + src
                    elif src.startswith("/"):
                        src = BASE_URL + src
                    audio_url = src
                    break
            if not audio_url:
                for btn in block.query_selector_all("[data-audio], [data-src*='.mp3'], [onclick*='audio'], [onclick*='play']"):
                    for attr in ["data-src", "data-audio"]:
                        val = btn.get_attribute(attr) or ""
                        if val and (".mp3" in val or ".m4a" in val):
                            audio_url = urljoin(BASE_URL, val) if val.startswith("/") else val
                            break
                    if audio_url:
                        break

            # 文本 + 噪音清理
            full_text = block.inner_text().strip()
            if not full_text or len(full_text) < 5:
                continue

            lines = full_text.split("\n")
            clean = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if re.match(r"\d{4}/\d{2}/\d{2}", line):
                    break
                if "次组卷" in line or "卷引用" in line:
                    break
                if line in ("相似题", "纠错", "详情", "收藏", "加入试题篮"):
                    continue
                if line.startswith("整体分析") or line.startswith("类文阅读"):
                    continue
                if re.match(r"^\d+\.\s*(整体分析|类文阅读)", line):
                    continue
                if re.match(r"^[_\s]{5,}$", line):
                    continue
                if re.match(r"^第[一二三四五六七八九十]+单元", line) and "课" in line:
                    continue
                clean.append(line)

            text = "\n".join(clean)
            if not text or len(text) < 5:
                if not images:
                    continue
                text = "（看图作答）"

            # 题型判断
            opt_matches = re.findall(r"([A-E])[\s.．、]*(.*?)(?=\s*[A-E][\s.．、]|\t[A-E][\s.．、]|$)", text, re.DOTALL)
            if len(opt_matches) >= 2:
                options = [{"label": m[0].strip(), "text": m[1].strip()} for m in opt_matches if m[1].strip()]
                q_type = "choice"
            elif "判断" in text or re.search(r"[（(]\s{2,}[）)]", text):
                options, q_type = None, "true_false"
            elif "填空" in text or "（" in text:
                options, q_type = None, "fill_blank"
            elif any(k in text for k in ("解答", "计算", "简答", "应用", "操作")):
                options, q_type = None, "short_answer"
            else:
                options, q_type = None, "short_answer"

            questions.append({
                "question_text": text,
                "question_type": q_type,
                "options": options,
                "answer": "",
                "explanation": "",
                "images": images or None,
                "audio_url": audio_url,
            })
        except Exception as e:
            logger.debug(f"  解析题目失败: {e}")

    return questions


def crawl_paper_detail(page, paper: dict) -> dict | None:
    url = paper["url"]
    logger.info(f"  爬取: {paper['title'][:50]}...")
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        for attempt in range(3):
            try:
                page.wait_for_selector(".tk-quest-item", state="attached", timeout=20000)
                break
            except PlaywrightTimeout:
                if attempt < 2:
                    time.sleep(2)
                else:
                    logger.warning(f"  试卷 {paper['paper_id']} 加载超时")
                    return None
        time.sleep(2)

        body_text = page.inner_text("body")
        page_title = page.title().replace("-组卷网", "").strip()

        cn = {"一":1,"二":2,"三":3,"四":4,"五":5,"六":6}
        grade = 0
        gm = re.search(r"(\d)年级", body_text) or re.search(r"(\d)年级", page_title)
        if gm:
            grade = int(gm.group(1))
        else:
            gm = re.search(r"([一二三四五六])年级", body_text) or re.search(r"([一二三四五六])年级", page_title)
            if gm:
                grade = cn.get(gm.group(1), 0)

        semester = "下" if ("下册" in body_text or "下" in body_text) else "上"
        questions = extract_questions(page)

        return {
            "paper_id": paper["paper_id"],
            "title": page_title or paper["title"],
            "url": url,
            "grade": grade,
            "semester": semester,
            "questions": questions,
            "question_count": len(questions),
        }
    except Exception as e:
        logger.error(f"  爬取失败: {e}")
        return None


def crawl_subject_grade(subject, grade, semester, max_papers=0, max_pages=3):
    all_papers = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        )
        context.add_cookies([{"name": "bankId", "value": SUBJECT_MAP[subject]["bank_id"], "domain": ".xkw.com", "path": "/"}])
        page = context.new_page()

        for p in range(1, max_pages + 1):
            if max_papers and len(all_papers) >= max_papers:
                break
            url = build_url(subject, grade, semester, p)
            logger.info(f"第{p}页: {url}")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                time.sleep(random.uniform(2, 4))
                if "请先登录" in page.content():
                    logger.warning("需要登录，跳过")
                    break
                papers = extract_paper_links(page)
                logger.info(f"  找到 {len(papers)} 张试卷")
                for paper in papers:
                    if max_papers and len(all_papers) >= max_papers:
                        break
                    detail = crawl_paper_detail(page, paper)
                    if detail:
                        detail["subject"] = subject
                        all_papers.append(detail)
                if p < max_pages:
                    time.sleep(random.uniform(2, 4))
            except PlaywrightTimeout:
                logger.error(f"第{p}页超时")
            except Exception as e:
                logger.error(f"第{p}页失败: {e}")

        context.close()
        browser.close()
    return all_papers


def import_to_db(papers, subject, grade, semester):
    sys.path.insert(0, str(Path(__file__).parent.parent))
    sys.path.insert(0, str(Path(__file__).parent))
    from app.database import SessionLocal
    from app.models.study import QuestionBank
    from clean_question_bank import clean_question_dict

    subject_cn = SUBJECT_MAP[subject]["name"]
    sem_str = "上" if semester == 1 else "下"

    db = SessionLocal()
    created, skipped = 0, 0
    for paper in papers:
        for q in paper.get("questions", []):
            q = clean_question_dict(q)
            existing = db.query(QuestionBank).filter(QuestionBank.question_text == q["question_text"]).first()
            if existing:
                # 更新已有记录的图片和音频
                if q.get("images") and not existing.images:
                    existing.images = q["images"]
                    db.commit()
                if q.get("audio_url") and not existing.audio_url:
                    existing.audio_url = q["audio_url"]
                    db.commit()
                if not existing.paper_id:
                    existing.paper_id = paper["paper_id"]
                    existing.paper_title = paper["title"]
                    existing.semester = sem_str
                    db.commit()
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
    logger.info(f"  导入: 新增{created} 跳过{skipped}")
    return created, skipped


def main():
    parser = argparse.ArgumentParser(description="按年级学期抓取基础达标试卷")
    parser.add_argument("--subject", choices=["math", "chinese", "english"], help="科目")
    parser.add_argument("--grade", type=int, choices=range(1,7), help="年级1-6")
    parser.add_argument("--semester", type=int, choices=[1,2], help="1=上 2=下")
    parser.add_argument("--all", action="store_true", help="抓取全部")
    parser.add_argument("--import", dest="do_import", action="store_true", help="导入数据库")
    parser.add_argument("--max-papers", type=int, default=0, help="每个年级最多抓几张(0=不限)")
    parser.add_argument("--max-pages", type=int, default=3, help="每个列表最多翻几页")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    setup_logging(args.verbose)

    if args.all:
        tasks = [(s, g, sem) for s in ["math","chinese","english"] for g in range(1,7) for sem in [1,2]]
    elif args.subject and args.grade and args.semester:
        tasks = [(args.subject, args.grade, args.semester)]
    else:
        parser.error("需要 --all 或 --subject+--grade+--semester")
        return

    total = len(tasks)
    all_papers = []
    total_created = 0
    total_skipped = 0

    for i, (subject, grade, semester) in enumerate(tasks, 1):
        logger.info(f"[{i}/{total}] {SUBJECT_MAP[subject]['name']} {grade}年级{'上' if semester==1 else '下'}")
        try:
            papers = crawl_subject_grade(subject, grade, semester, args.max_papers, args.max_pages)
            for p in papers:
                p["subject"] = subject
                p["grade"] = grade
            all_papers.extend(papers)
            logger.info(f"  获取 {len(papers)} 张试卷, {sum(len(p.get('questions',[])) for p in papers)} 道题")

            if args.do_import and papers:
                c, s = import_to_db(papers, subject, grade, semester)
                total_created += c
                total_skipped += s
        except Exception as e:
            logger.error(f"  失败: {e}")

    # 保存JSON备份
    output = DATA_DIR / "crawled_jdcs_papers.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump({"crawled_at": datetime.now().isoformat(), "total": len(all_papers), "papers": all_papers}, f, ensure_ascii=False, indent=2)
    logger.info(f"总计 {len(all_papers)} 张试卷, 导入新增{total_created}跳过{total_skipped} -> {output}")


if __name__ == "__main__":
    main()
