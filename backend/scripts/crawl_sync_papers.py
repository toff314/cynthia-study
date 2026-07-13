"""
学科网同步教学试卷爬虫

爬取同步教学章节下的试卷（如一年级上册、二年级上册等）

Usage:
    python crawl_sync_papers.py --subject chinese --grade 1 --semester 1
    python crawl_sync_papers.py --subject math --grade 3 --semester 2
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

logger = logging.getLogger("crawl_sync_papers")

BASE_URL = "https://zujuan.xkw.com"

SUBJECT_MAP = {
    "math": {"name": "数学", "prefix": "xxsx", "bank_id": "23"},
    "chinese": {"name": "语文", "prefix": "xxyw", "bank_id": "24"},
    "english": {"name": "英语", "prefix": "xxyy", "bank_id": "25"},
}

GRADE_MAP = {
    1: "一年级",
    2: "二年级",
    3: "三年级",
    4: "四年级",
    5: "五年级",
    6: "六年级",
}

SEMESTER_MAP = {
    1: "上册",
    2: "下册",
}

DEFAULT_OUTPUT = Path(__file__).parent.parent / "data" / "sync_papers.json"


def setup_logging(verbose: bool = False):
    """设置日志"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def build_sync_url(subject: str, grade: int, semester: int) -> str:
    """构建同步教学章节页URL"""
    prefix = SUBJECT_MAP[subject]["prefix"]
    grade_name = GRADE_MAP[grade]
    semester_name = SEMESTER_MAP[semester]
    
    # 已知的章节ID映射
    CHAPTER_IDS = {
        # 语文
        ("chinese", 1, 1): "197557",  ("chinese", 1, 2): "214054",
        ("chinese", 2, 1): "226506",  ("chinese", 2, 2): "236070",
        ("chinese", 3, 1): "226507",  ("chinese", 3, 2): "236071",
        ("chinese", 4, 1): "260604",  ("chinese", 5, 1): "260605",
        ("chinese", 6, 1): "260606",
        # 数学
        ("math", 1, 1): "197558",     ("math", 1, 2): "213449",
        ("math", 2, 1): "224762",     ("math", 2, 2): "235359",
        ("math", 3, 1): "224763",     ("math", 3, 2): "235360",
        ("math", 4, 1): "262329",     ("math", 5, 1): "262330",
        ("math", 6, 1): "262331",
        # 英语
        ("english", 3, 1): "198559",  ("english", 3, 2): "212948",
        ("english", 4, 1): "223846",  ("english", 4, 2): "235365",
        ("english", 5, 1): "230344",  ("english", 5, 2): "248171",
        ("english", 6, 1): "260607",
    }
    
    key = (subject, grade, semester)
    chapter_id = CHAPTER_IDS.get(key)
    
    if chapter_id:
        return f"{BASE_URL}/{prefix}/shijuan/tbjx/zj{chapter_id}/"
    else:
        # 如果没有预定义的章节ID，使用通用URL
        return f"{BASE_URL}/{prefix}/shijuan/tbjx/"


def find_chapter_id(page, subject: str, grade: int, semester: int) -> str:
    """从同步教学页面找到对应的章节ID"""
    grade_name = GRADE_MAP[grade]
    semester_name = SEMESTER_MAP[semester]
    
    # 查找年级和学期对应的章节链接
    chapter_links = page.query_selector_all('a[href*="zj"]')
    
    for link in chapter_links:
        href = link.get_attribute("href")
        text = link.inner_text().strip()
        
        # 查找匹配的年级和学期
        if grade_name in text and semester_name in text:
            # 提取章节ID
            match = re.search(r'/zj(\d+)', href)
            if match:
                return match.group(1)
    
    return None


def extract_paper_links(page, target_grade: int) -> list[dict[str, Any]]:
    grade_name = GRADE_MAP[target_grade]
    seen = set()
    papers = []

    paper_links = page.query_selector_all('a[href^="/"]')

    for link in paper_links:
        href = (link.get_attribute("href") or "").strip()
        if not href or href.startswith("javascript"):
            continue

        href_abs = f"{BASE_URL}{href}" if href.startswith("/") else href

        # 提取试卷 ID: /24p2615919.html
        paper_id_match = re.search(r"/(\d+)p(\d+)\.html", href)
        if not paper_id_match:
            continue

        bank_id = paper_id_match.group(1)
        paper_id = paper_id_match.group(2)

        # 提取试卷标题
        title = link.inner_text().strip()
        
        # 过滤掉类型标签链接（短文本或类型类标签）
        type_tags = {"课前预习", "课后作业", "随堂练习", "单元测试", "课后练习",
                     "删除", "收藏", "加入试卷篮", "下载", "分析"}
        if len(title) < 10 or title in type_tags:
            continue

        # 过滤出目标年级的试卷
        grade_patterns = [
            f"新{grade_name}",          # 新一年级
            grade_name,                  # 一年级
            f"{target_grade}年级",       # 1年级
        ]
        matched = any(p in title for p in grade_patterns)
        if not matched:
            continue

        if href_abs in seen:
            continue
        seen.add(href_abs)

        papers.append({
            "paper_id": paper_id,
            "bank_id": bank_id,
            "title": title,
            "url": href_abs,
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
                    continue
                if re.match(r"^\d+\.", line):
                    clean_lines.append(line)
                elif re.match(r"^[A-Z]\.", line):
                    clean_lines.append(line)
                else:
                    clean_lines.append(line)

            question_text = "\n".join(clean_lines)

            # 检测题目类型
            question_type = "short_answer"
            options = []
            
            # 检查是否有选项（选择题）
            option_pattern = r'^[A-Z]\.'
            has_options = any(re.match(option_pattern, line) for line in clean_lines)
            
            # 检查是否为判断题（需要在检查填空题之前）
            true_false_keywords = ["判断题", "对的打", "错的打", "判一判", "对错"]
            # 检查是否为选择题
            option_pattern = r'^[A-Z][\.\s、]'
            has_options = any(re.match(option_pattern, line) for line in clean_lines)

            if has_options:
                question_type = "choice"
                option_lines = [line for line in clean_lines if re.match(option_pattern, line)]
                for opt_line in option_lines:
                    match = re.match(r'^([A-Z])[\.\s、]\s*(.+)', opt_line)
                    if match:
                        options.append({
                            "label": match.group(1),
                            "text": match.group(2).strip()
                        })
            elif any(kw in question_text for kw in true_false_keywords):
                question_type = "true_false"
            elif "____" in question_text or "（    ）" in question_text or "（  ）" in question_text or "_____" in question_text:
                question_type = "fill_blank"
            else:
                question_type = "short_answer"

            # 提取知识点
            knowledge = []
            knowledge_elements = block.query_selector_all('[class*="knowledge"]')
            for elem in knowledge_elements:
                k_text = elem.inner_text().strip()
                if k_text:
                    knowledge.append(k_text)

            questions.append({
                "question_text": question_text,
                "question_type": question_type,
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
            if grade_match:
                grade = int(grade_match.group(1))

        # 提取日期
        date_match = re.search(r"(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})", body_text)
        date_str = date_match.group(0) if date_match else ""

        # 提取难度
        difficulty = "medium"
        if "容易" in body_text or "简单" in body_text:
            difficulty = "easy"
        elif "困难" in body_text or "较难" in body_text:
            difficulty = "hard"

        # 提取题目
        questions = extract_questions_from_page(page)

        if not questions:
            logger.warning(f"  试卷 {paper_id} 没有找到题目")
            return None

        return {
            "paper_id": paper_id,
            "bank_id": bank_id,
            "title": title,
            "url": url,
            "page_title": page_title,
            "grade": grade,
            "date": date_str,
            "difficulty": difficulty,
            "questions": questions,
            "question_count": len(questions),
        }

    except Exception as e:
        logger.error(f"  爬取试卷 {paper_id} 失败: {e}")
        return None


def crawl_sync_papers(
    subject: str,
    grade: int,
    semester: int,
    max_papers: int = 0,
) -> list[dict[str, Any]]:
    """爬取同步教学试卷"""
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
        # 预设置 bankId cookie
        context.add_cookies([
            {"name": "bankId", "value": SUBJECT_MAP[subject]["bank_id"], "domain": ".xkw.com", "path": "/"}
        ])
        page = context.new_page()

        # 访问同步教学页面
        url = build_sync_url(subject, grade, semester)
        logger.info(f"正在访问同步教学页面: {url}")

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)

            # 从 URL 中提取章节ID
            chapter_match = re.search(r'/zj(\d+)', url)
            if chapter_match:
                chapter_id = chapter_match.group(1)
            else:
                chapter_id = find_chapter_id(page, subject, grade, semester)

            if not chapter_id:
                logger.error(f"未找到 {GRADE_MAP[grade]}{SEMESTER_MAP[semester]} 的章节ID")
                return []

            logger.info(f"使用章节ID: {chapter_id}")

            # 访问课后练习页面
            practice_url = f"{BASE_URL}/{SUBJECT_MAP[subject]['prefix']}/shijuan/tbjx/zj{chapter_id}/t1/"
            logger.info(f"正在访问课后练习页面: {practice_url}")

            page.goto(practice_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)

            # 提取试卷链接
            papers = extract_paper_links(page, grade)
            logger.info(f"找到 {len(papers)} 张试卷")

            if max_papers and len(papers) > max_papers:
                papers = papers[:max_papers]

            # 爬取每张试卷的详细信息
            for i, paper in enumerate(papers):
                if max_papers and i >= max_papers:
                    break

                paper_details = crawl_paper_details(
                    page, paper["paper_id"], paper["bank_id"], paper["title"]
                )

                if paper_details:
                    all_papers.append(paper_details)
                    logger.info(f"  进度: {i + 1}/{len(papers)}, 已爬取 {len(all_papers)} 张")

                # 随机延迟避免被封
                time.sleep(random.uniform(2, 4))

        except Exception as e:
            logger.error(f"爬取失败: {e}")
        finally:
            browser.close()

    # 添加科目信息
    for p in all_papers:
        p["subject"] = subject
        p["grade"] = grade
    return all_papers


def save_papers(papers: list[dict[str, Any]], output: Path) -> dict[str, Any]:
    """保存爬取的试卷到JSON文件"""
    data = {
        "crawled_at": datetime.now().isoformat(),
        "total_papers": len(papers),
        "papers": papers,
    }

    output.parent.mkdir(parents=True, exist_ok=True)

    # 支持追加模式：如果文件已存在，合并数据
    if output.exists():
        try:
            with open(output, "r", encoding="utf-8") as f:
                existing = json.load(f)
            existing_papers = existing.get("papers", [])
            # 去重
            seen_pids = {(p.get("paper_id"), p.get("url")) for p in existing_papers}
            new_papers = [p for p in papers if (p.get("paper_id"), p.get("url")) not in seen_pids]
            existing_papers.extend(new_papers)
            data["papers"] = existing_papers
            data["total_papers"] = len(existing_papers)
        except Exception:
            pass  # 文件损坏则覆盖

    with open(output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"已保存 {len(data['papers'])} 张试卷到 {output}")
    return data


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="学科网同步教学试卷爬虫"
    )
    parser.add_argument(
        "--subject",
        type=str,
        choices=["math", "chinese", "english"],
        required=True,
        help="科目: math/chinese/english",
    )
    parser.add_argument(
        "--grade",
        type=int,
        choices=range(1, 7),
        required=True,
        help="年级: 1-6",
    )
    parser.add_argument(
        "--semester",
        type=int,
        choices=[1, 2],
        default=1,
        help="学期: 1(上册), 2(下册) (默认: 1)",
    )
    parser.add_argument(
        "--max-papers",
        type=int,
        default=0,
        help="最大试卷数量 (0=不限制)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(DEFAULT_OUTPUT),
        help=f"输出 JSON 文件路径 (默认: {DEFAULT_OUTPUT})",
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

    logger.info("=" * 40)
    logger.info(f"开始爬取: 科目={SUBJECT_MAP[args.subject]['name']}, 年级={GRADE_MAP[args.grade]}, 学期={SEMESTER_MAP[args.semester]}")

    papers = crawl_sync_papers(
        subject=args.subject,
        grade=args.grade,
        semester=args.semester,
        max_papers=args.max_papers,
    )

    if not papers:
        logger.error("未爬取到任何试卷")
        sys.exit(1)

    logger.info(f"\n总计爬取 {len(papers)} 张试卷")

    save_papers(papers, Path(args.output))

    logger.info("爬取完成!")


if __name__ == "__main__":
    main()
