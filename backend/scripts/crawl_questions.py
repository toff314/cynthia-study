"""
学科网组卷 (zujuan.xkw.com) 试卷爬虫

爬取小学试卷列表和题目（不需要登录），不爬答案解析。

试卷分类：
- xxsx: 小学数学
- xxwx: 小学语文
- xxyx: 小学英语

分类标签：
- jdcs: 基础达标（月考/期中/期末）
- zqjm: 期中期末
- bk: 小升初

Usage:
    python crawl_questions.py --subject math --category jdcs --pages 5
    python crawl_questions.py --subject math --category zqjm --pages 3 --import
    python crawl_questions.py --all --pages 3
    python crawl_questions.py --subject chinese --category jdcs --grade 3 --pages 2

Requirements:
    pip install playwright
    playwright install chromium
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

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

logger = logging.getLogger("crawl_questions")

SUBJECT_MAP = {
    "math": {"name": "数学", "prefix": "xxsx", "bank_id": "23"},
    "chinese": {"name": "语文", "prefix": "xxyw", "bank_id": "24"},
    "english": {"name": "英语", "prefix": "xxyy", "bank_id": "25"},
}

CATEGORY_MAP = {
    "jdcs": "基础达标",
    "zqjm": "期中期末",
    "bk": "小升初",
}

GRADE_MAP = {1: "一年级", 2: "二年级", 3: "三年级", 4: "四年级", 5: "五年级", 6: "六年级"}
GRADE_SEMESTER = {1: "上学期", 2: "上学期", 3: "上学期", 4: "上学期", 5: "上学期", 6: "上学期"}

BASE_URL = "https://zujuan.xkw.com"
DEFAULT_OUTPUT = Path(__file__).parent.parent / "data" / "crawled_papers.json"
API_BASE = "http://localhost:8000"


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def build_paper_list_url(subject: str, category: str, grade: int = 0, page: int = 1) -> str:
    """构建试卷列表页 URL"""
    prefix = SUBJECT_MAP[subject]["prefix"]
    if grade > 0:
        return f"{BASE_URL}/{prefix}/shijuan/{category}/t{grade}/{page}/"
    return f"{BASE_URL}/{prefix}/shijuan/{category}/{page}/"


def extract_paper_links(page) -> list[dict[str, Any]]:
    """从试卷列表页提取试卷链接和基本信息"""
    papers = []
    seen = set()

    # 获取所有试卷链接（匹配 /23p\d+.html 格式）
    paper_links = page.query_selector_all('a[href^="/"]')

    for link in paper_links:
        href = (link.get_attribute("href") or "").strip()
        if not href or href.startswith("javascript"):
            continue

        # 统一为绝对路径
        if href.startswith("/"):
            href = f"{BASE_URL}{href}"
        elif not href.startswith("http"):
            href = f"{BASE_URL}/{href}"

        if href in seen:
            continue
        seen.add(href)

        # 提取试卷 ID: /23p2055802.html
        paper_id_match = re.search(r"/(\d+)p(\d+)\.html", href)
        if not paper_id_match:
            continue

        bank_id = paper_id_match.group(1)
        paper_id = paper_id_match.group(2)

        # 提取试卷标题
        title = link.inner_text().strip()
        # 过滤掉类型标签链接（如"期末"、"月考"等短文本）
        if len(title) < 10 or title in ("删除", "收藏", "加入试卷篮"):
            continue

        # 清理标题中的多余空白
        title = re.sub(r"\s+", " ", title)

        papers.append({
            "paper_id": paper_id,
            "bank_id": bank_id,
            "title": title,
            "url": href,
        })

    return papers


def extract_questions_from_page(page) -> list[dict[str, Any]]:
    """从试卷详情页提取题目"""
    questions = []

    # 获取所有题目区块
    question_blocks = page.query_selector_all(".tk-quest-item")
    logger.debug(f"页面中找到 {len(question_blocks)} 个题目区块")

    for block in question_blocks:
        try:
            # 提取完整文本
            full_text = block.inner_text().strip()
            if not full_text or len(full_text) < 5:
                continue

            # 清理文本：移除元数据行
            lines = full_text.split("\n")
            clean_lines = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # 跳过元数据行
                if re.match(r"\d{4}/\d{2}/\d{2}", line):
                    break
                if "次组卷" in line or "卷引用" in line:
                    break
                if line in ("相似题", "纠错", "详情", "收藏", "加入试题篮"):
                    continue
                clean_lines.append(line)

            question_text = " ".join(clean_lines)
            if not question_text or len(question_text) < 5:
                continue

            # 先尝试提取选项（支持全角/半角点号、空格、制表符分隔）
            option_matches = re.findall(r"([A-E])[\s.．、]*(.*?)(?=\s*[A-E][\s.．、]|\t[A-E][\s.．、]|$)", question_text, re.DOTALL)
            if len(option_matches) >= 2:
                options = [
                    {
                        "label": m[0].strip(),
                        "text": m[1].strip(),
                    }
                    for m in option_matches
                    if m[1].strip()
                ]
                q_type = "choice"
            elif "判断" in question_text or "（   ）" in question_text or "（    ）" in question_text or "(   )" in question_text or "(    )" in question_text:
                options = None
                q_type = "true_false"
            elif "填空" in question_text or "（" in question_text or "（" in question_text:
                options = None
                q_type = "fill_blank"
            elif "解答" in question_text or "计算" in question_text or "简答" in question_text or "应用" in question_text or "操作" in question_text:
                options = None
                q_type = "short_answer"
            else:
                options = None
                q_type = "short_answer"  # 默认简答题

            # 提取知识点
            knowledge = []
            know_el = block.query_selector(".knowlegde")
            if know_el:
                know_text = know_el.inner_text().strip()
                # 提取知识点名称
                know_matches = re.findall(r"【知识点】\s*(.+)", know_text)
                if know_matches:
                    knowledge = [k.strip() for k in know_matches[0].split() if k.strip()]

            questions.append({
                "question_text": question_text,
                "question_type": q_type,
                "options": options,
                "knowledge": knowledge,
                "answer": "",  # 不爬答案
                "explanation": "",  # 不爬解析
            })

        except Exception as e:
            logger.debug(f"解析题目失败: {e}")

    return questions


def crawl_paper_details(page, paper_id: str, bank_id: str, title: str) -> dict[str, Any] | None:
    """爬取单张试卷的详细信息和题目"""
    url = f"{BASE_URL}/{bank_id}p{paper_id}.html"
    logger.info(f"  爬取试卷详情: {title[:50]}...")

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)

        # 等待题目区块加载完成（只检测 DOM 存在，不要求可见）
        retries = 3
        for attempt in range(retries):
            try:
                page.wait_for_selector(".tk-quest-item", state="attached", timeout=20000)
                break
            except PlaywrightTimeout:
                if attempt < retries - 1:
                    logger.debug(f"  试卷 {paper_id} 题目未加载，重试 ({attempt + 1}/{retries})")
                    time.sleep(2)
                else:
                    logger.warning(f"  试卷 {paper_id} 题目加载超时")
                    return None

        # 额外等待确保内容渲染完成
        time.sleep(2)

        # 提取试卷元信息
        page_title = page.title().replace("-组卷网", "").strip()
        body_text = page.inner_text("body")

        # 提取年级（支持中文数字和阿拉伯数字）
        cn_to_num = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
        grade = 0
        grade_match = re.search(r"(\d+)年级", body_text)
        if not grade_match:
            grade_match = re.search(r"([一二三四五六七八九])年级", body_text)
            if grade_match:
                grade = cn_to_num.get(grade_match.group(1), 0)
        if not grade:
            grade_match = re.search(r"(\d+)年级", page_title)
            if not grade_match:
                grade_match = re.search(r"([一二三四五六七八九])年级", page_title)
                if grade_match:
                    grade = cn_to_num.get(grade_match.group(1), 0)
            else:
                grade = int(grade_match.group(1))

        # 提取学期
        semester = "下" if "下册" in body_text or "下" in body_text else "上"

        # 提取日期
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", body_text)
        date_str = date_match.group(1) if date_match else ""

        # 提取难度
        difficulty = "medium"
        if "容易" in body_text or "简单" in body_text:
            difficulty = "easy"
        elif "较难" in body_text or "困难" in body_text:
            difficulty = "hard"

        # 提取题目
        questions = extract_questions_from_page(page)

        return {
            "paper_id": paper_id,
            "title": page_title or title,
            "url": url,
            "grade": grade,
            "semester": semester,
            "date": date_str,
            "difficulty": difficulty,
            "questions": questions,
            "question_count": len(questions),
        }

    except Exception as e:
        logger.error(f"  爬取试卷 {paper_id} 失败: {e}")
        return None


def crawl_papers(
    subject: str,
    category: str,
    pages: int = 1,
    grade: int = 0,
    max_papers: int = 0,
) -> list[dict[str, Any]]:
    """爬取试卷列表和题目"""
    all_papers = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        # 预设置 bankId cookie，避免页面加载后需要切换学段
        context.add_cookies([
            {"name": "bankId", "value": SUBJECT_MAP[subject]["bank_id"], "domain": ".xkw.com", "path": "/"}
        ])
        page = context.new_page()

        for p in range(1, pages + 1):
            if max_papers and len(all_papers) >= max_papers:
                break

            url = build_paper_list_url(subject, category, grade=0, page=p)  # 不用 t{grade} URL
            logger.info(f"正在爬取第 {p} 页: {url}")

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                time.sleep(random.uniform(2, 4))

                # 如果指定了年级，点击年级过滤链接
                if grade > 0:
                    grade_name = GRADE_MAP[grade] + GRADE_SEMESTER.get(grade, "")
                    clicked = False
                    grade_links = page.query_selector_all('a')
                    for link in grade_links:
                        text = link.inner_text().strip()
                        if grade_name in text:
                            try:
                                link.click()
                                time.sleep(random.uniform(2, 4))
                                clicked = True
                                logger.info(f"  点击年级过滤: {text}")
                                break
                            except Exception:
                                continue
                    if not clicked:
                        logger.warning(f"  未找到 {grade_name} 过滤链接")

                # 检查是否需要登录
                if "请先登录" in page.content():
                    logger.warning("检测到需要登录")
                    break

                # 提取试卷列表
                papers = extract_paper_links(page)
                logger.info(f"第 {p} 页找到 {len(papers)} 张试卷")

                # 爬取每张试卷的详情
                for paper in papers:
                    if max_papers and len(all_papers) >= max_papers:
                        break

                    detail = crawl_paper_details(page, paper["paper_id"], paper["bank_id"], paper["title"])
                    if detail:
                        all_papers.append(detail)

                if p < pages:
                    delay = random.uniform(2, 4)
                    time.sleep(delay)

            except PlaywrightTimeout:
                logger.error(f"第 {p} 页加载超时")
            except Exception as e:
                logger.error(f"第 {p} 页爬取失败: {e}")

        context.close()
        browser.close()

    return all_papers


def save_papers(papers: list[dict[str, Any]], output_path: str):
    """保存爬取的试卷到 JSON 文件"""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "crawled_at": datetime.now().isoformat(timespec="seconds"),
        "total_papers": len(papers),
        "papers": papers,
    }

    with open(output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"已保存 {len(papers)} 张试卷到 {output}")
    return data


def import_to_api(papers: list[dict[str, Any]]):
    """导入试卷到后端 API"""
    if not papers:
        logger.warning("没有可导入的试卷")
        return

    # 转换为题目格式
    questions = []
    for paper in papers:
        for q in paper.get("questions", []):
            questions.append({
                "subject": paper.get("subject", ""),
                "grade": paper.get("grade", 0),
                "question_type": q.get("question_type", "choice"),
                "difficulty": paper.get("difficulty", "medium"),
                "question_text": q.get("question_text", ""),
                "options": q.get("options"),
                "answer": q.get("answer", ""),
                "explanation": q.get("explanation", ""),
                "source": paper.get("url", ""),
                "paper_id": paper.get("paper_id", ""),
                "paper_title": paper.get("title", ""),
            })

    if not questions:
        logger.warning("没有可导入的题目")
        return

    url = f"{API_BASE}/api/study/questions/batch"
    payload = {"questions": questions}

    logger.info(f"正在导入 {len(questions)} 道题目到 API: {url}")

    try:
        import requests
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()

        result = resp.json()
        if result.get("success"):
            logger.info(
                f"导入成功: 共 {result.get('total', 0)} 道，"
                f"新增 {result.get('created', 0)} 道，跳过 {result.get('skipped', 0)} 道"
            )
        else:
            logger.error(f"导入失败: {result}")

    except Exception as e:
        logger.error(f"导入失败: {e}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="学科网组卷试卷爬虫 - 爬取小学试卷和题目",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--subject",
        choices=["math", "chinese", "english"],
        help="科目: math(数学), chinese(语文), english(英语)",
    )
    parser.add_argument(
        "--category",
        choices=["jdcs", "zqjm", "bk"],
        default="jdcs",
        help="分类: jdcs(基础达标), zqjm(期中期末), bk(小升初) (默认: jdcs)",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="要爬取的页数 (默认: 1)",
    )
    parser.add_argument(
        "--grade",
        type=int,
        choices=range(0, 7),
        default=0,
        metavar="[0-6]",
        help="年级: 0(全部), 1-6 (默认: 0)",
    )
    parser.add_argument(
        "--max-papers",
        type=int,
        default=0,
        help="最大试卷数量 (0=不限制)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="爬取所有科目",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(DEFAULT_OUTPUT),
        help=f"输出 JSON 文件路径 (默认: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--import",
        dest="do_import",
        action="store_true",
        help="爬取完成后导入到后端数据库 API",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细日志",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging(args.verbose)

    subjects = ["math", "chinese", "english"] if args.all else ([args.subject] if args.subject else ["math"])
    all_papers = []

    for subject in subjects:
        logger.info(f"{'='*40}")
        logger.info(f"开始爬取: 科目={SUBJECT_MAP[subject]['name']}, 分类={CATEGORY_MAP[args.category]}, 页数={args.pages}")

        papers = crawl_papers(
            subject=subject,
            category=args.category,
            pages=args.pages,
            grade=args.grade,
            max_papers=args.max_papers,
        )

        # 添加科目信息
        for paper in papers:
            paper["subject"] = subject
            paper["subject_name"] = SUBJECT_MAP[subject]["name"]

        all_papers.extend(papers)
        logger.info(f"科目 {SUBJECT_MAP[subject]['name']} 爬取完成: {len(papers)} 张试卷")

    if not all_papers:
        logger.error("未爬取到任何试卷")
        sys.exit(1)

    logger.info(f"\n总计爬取 {len(all_papers)} 张试卷")

    data = save_papers(all_papers, args.output)

    if args.do_import:
        logger.info("=" * 40)
        logger.info("开始导入到数据库...")
        import_to_api(all_papers)

    logger.info("爬取完成!")


if __name__ == "__main__":
    main()
