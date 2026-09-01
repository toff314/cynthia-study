#!/usr/bin/env python3
"""
题库内容格式化清洗脚本

处理问题：
1. 题目末尾的元数据 footer（次组卷、卷引用、相似题、纠错、详情、收藏、加入试题篮等）
2. 选项 A/B/C/D 与题干挤在同一行，需要换行
3. 小题号 1. / 18. 等需要换行
4. 英语听力题开头的 00:00/00:00 占位符
5. 选项在 question_text 和 options JSON 中重复出现
6. 部分选择题被错误标记为 short_answer/fill_blank，且 options 为空
7. 选项 JSON 被题干内容污染

Usage:
    python clean_question_bank.py --dry-run          # 预览，不修改
    python clean_question_bank.py --apply            # 执行清洗并写入数据库
    python clean_question_bank.py --sample 20        # 预览 20 条随机样本
"""

import argparse
import json
import re
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).parent.parent / "data" / "cynthia.db"

# 元数据 footer：从 "|\nXX次组卷" 开始到末尾的所有内容
METADATA_FOOTER_RE = re.compile(r"\n\|\n\d+次组卷.*$", re.DOTALL)

# 需要删除的整行/段落（按顺序匹配）
REMOVE_LINE_PATTERNS = [
    r"^相似题$",
    r"^纠错$",
    r"^详情$",
    r"^收藏$",
    r"^加入试题篮$",
    r"^加入试卷篮$",
    r"^整体分析：.*",
    r"^类文阅读[：].*",
    r"^\d{4}/\d{2}/\d{2}$",
    r"^00:00/00:00$",
]

OPTION_LABEL_CHARS = "ABCDEFGHIJ"


def normalize_text(text: str) -> str:
    """基础清理：删除 footer、清理空行、合并空格等。"""
    # 1. 删除 metadata footer
    text = METADATA_FOOTER_RE.sub("", text)

    # 2. 按行删除无用行
    lines = text.split("\n")
    clean_lines = []
    for line in lines:
        stripped = line.strip()
        if any(re.match(p, stripped) for p in REMOVE_LINE_PATTERNS):
            continue
        clean_lines.append(line)
    text = "\n".join(clean_lines)

    # 3. 删除开头残留的 00:00/00:00
    text = re.sub(r"^(?:00:00/00:00\s*)+", "", text)

    # 4. 合并多个空白字符为单个空格，但保留换行
    text = re.sub(r"[ \t\u00a0]+", " ", text)

    # 5. 删除多余空行
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def find_option_groups(text: str) -> list[list[re.Match]]:
    """
    找出文本中所有连续的 A/B/C/D/E/F 选项组。
    只识别连续递增的字母序列（如 A->B->C），且至少包含 2 个选项。
    """
    # 匹配选项标签：前面不能是字母/数字（允许空白、开头、标点），后面跟着分隔符或字符串结尾
    label_set = OPTION_LABEL_CHARS
    pattern = re.compile(r"(?<![A-Za-z0-9])([" + label_set + r"])(?:[\s.．、]+|$)")
    matches = list(pattern.finditer(text))

    groups: list[list[re.Match]] = []
    i = 0
    while i < len(matches):
        m = matches[i]
        start_label = m.group(1)
        group = [m]
        # 在当前字符集内找下一个连续字母
        label_index = label_set.index(start_label)
        j = i + 1
        while j < len(matches):
            expected_label = label_set[label_index + 1] if label_index + 1 < len(label_set) else None
            if expected_label and matches[j].group(1) == expected_label:
                group.append(matches[j])
                label_index += 1
                j += 1
            else:
                break
        if len(group) >= 2:
            groups.append(group)
            i = j
        else:
            i += 1
    return groups


def extract_options_from_group(text: str, group: list[re.Match]) -> list[dict[str, str]]:
    """从选项组 match 中提取 label 和 text。"""
    options: list[dict[str, str]] = []
    for idx, m in enumerate(group):
        start = m.end()
        if idx + 1 < len(group):
            end = group[idx + 1].start()
        else:
            end = len(text)
        opt_text = text[start:end].strip()
        # 去除开头可能残留的分隔符
        opt_text = re.sub(r"^[\s.．、]+", "", opt_text)
        options.append({"label": m.group(1), "text": opt_text})
    return options


def deduplicate_options(options: list[dict[str, str]]) -> list[dict[str, str]]:
    seen = set()
    result = []
    for opt in options:
        key = (opt.get("label", ""), opt.get("text", ""))
        if key not in seen:
            seen.add(key)
            result.append(opt)
    return result


def insert_newlines_at_positions(text: str, positions: list[tuple[int, int]]) -> str:
    """从右到左在指定位置前插入换行（若前面不是换行）。"""
    positions = sorted(positions, key=lambda x: x[0], reverse=True)
    for pos, _ in positions:
        if pos > 0 and text[pos - 1] != "\n":
            before = text[:pos].rstrip()
            text = before + "\n" + text[pos:]
    return text


def format_question_text(text: str, groups: list[list[re.Match]]) -> str:
    """在选项标签和小题号前插入换行。"""
    positions: list[tuple[int, int]] = []

    # 选项标签位置
    for group in groups:
        for m in group:
            positions.append((m.start(), m.end()))

    # 小题号位置：1. 18. 等，支持中英文点号
    num_pattern = re.compile(r"(?<!\S)\d{1,2}[\.．]\s*")
    for m in num_pattern.finditer(text):
        positions.append((m.start(), m.end()))

    # 括号小题号 (1) （1）
    paren_pattern = re.compile(r"(?<!\S)(?:\(|（)\d{1,2}(?:\)|）)\s*")
    for m in paren_pattern.finditer(text):
        positions.append((m.start(), m.end()))

    return insert_newlines_at_positions(text, positions)


def contains_subquestion_marker(text: str) -> bool:
    """检查文本中是否包含小题号标记（1. / 18. / 18． / (1) / （1） 等）。"""
    patterns = [
        r"\d{1,2}[\.．](?!\d)",  # 1. 18. 18． 但不匹配 11.5
        r"(?:\(|（)\d{1,2}(?:\)|）)",
    ]
    return any(re.search(p, text) for p in patterns)


def parse_options(options_json: Any) -> list[dict[str, str]] | None:
    """解析并去重 options JSON，非法则返回 None。"""
    if not options_json:
        return None
    opts = options_json
    if isinstance(opts, str):
        try:
            opts = json.loads(opts)
        except (json.JSONDecodeError, TypeError):
            return None
    if not isinstance(opts, list):
        return None
    valid = []
    for item in opts:
        if isinstance(item, dict) and "label" in item and "text" in item:
            valid.append({"label": str(item["label"]), "text": str(item["text"])})
    return deduplicate_options(valid) if valid else None


def clean_question(text: str, options_json: Any, q_type: str) -> tuple[str, Any, str]:
    """
    清洗单道题目。
    返回：(cleaned_question_text, cleaned_options, cleaned_question_type)
    """
    original_text = text
    text = normalize_text(text)

    # 解析原始 options JSON（用于没有 inline 选项时保留合法选项）
    original_options = parse_options(options_json)

    groups = find_option_groups(text)

    # 默认：清理 options JSON 中的污染，避免重复显示
    cleaned_options = None

    # 判断是否可以从题干末尾提取单一选项组
    extracted_options = None
    if len(groups) == 1:
        group = groups[0]
        last_label_end = group[-1].end()
        remaining_after_last_label = text[last_label_end:].strip()
        # 只有当末尾剩余内容不含小题号标记时才提取，避免把阅读理解等多小题题干的选项误拆
        if remaining_after_last_label and not contains_subquestion_marker(remaining_after_last_label):
            extracted_options = extract_options_from_group(text, group)

    if extracted_options:
        # 删除题干末尾的选项文本，保留选项 JSON
        start_pos = groups[0][0].start()
        stem_text = text[:start_pos].rstrip()
        # 去除选项前可能残留的标点/分隔符
        stem_text = re.sub(r"[\s.．]+$", "", stem_text)
        text = stem_text
        cleaned_options = deduplicate_options(extracted_options)
        q_type = "choice"
        # 提取后题干已变短，重新查找剩余 option group 位置用于格式化
        groups = find_option_groups(text)
    elif not groups:
        # 题干中没有 inline 选项，保留原始合法 options JSON
        cleaned_options = original_options
    else:
        # 多个 inline 选项组，无法提取为单一 JSON，清空 options 避免重复显示
        cleaned_options = None

    # 最后格式化：给选项标签和小题号前加换行
    text = format_question_text(text, groups)

    # 处理提取后题干为空的情况（极少见）
    if not text.strip():
        text = original_text.strip()

    return text, cleaned_options, q_type


def clean_question_dict(q: dict[str, Any]) -> dict[str, Any]:
    """清洗单个题目字典（爬虫/导入链路使用）。"""
    text = q.get("question_text", "")
    opts = q.get("options")
    q_type = q.get("question_type", "short_answer")
    new_text, new_opts, new_type = clean_question(text, opts, q_type)
    q["question_text"] = new_text
    q["options"] = new_opts
    q["question_type"] = new_type
    return q


def clean_papers(papers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """清洗试卷列表中的所有题目。"""
    for paper in papers:
        questions = paper.get("questions", [])
        paper["questions"] = [clean_question_dict(q) for q in questions]
    return papers


def backup_database(db_path: Path) -> Path:
    backup_path = db_path.parent / f"{db_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}{db_path.suffix}"
    shutil.copy2(db_path, backup_path)
    return backup_path


def analyze_sample(db_path: Path, sample_size: int = 20) -> None:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT id, subject, grade, question_type, question_text, options FROM question_bank ORDER BY RANDOM() LIMIT ?",
        (sample_size,),
    )
    rows = cur.fetchall()

    print(f"随机抽取 {len(rows)} 道题目进行清洗预览\n")
    for i, row in enumerate(rows, 1):
        text = row["question_text"]
        opts = row["options"]
        q_type = row["question_type"]
        new_text, new_opts, new_type = clean_question(text, opts, q_type)

        print(f"{'='*80}")
        print(f"[{i}] ID={row['id']} {row['subject']} 年级{row['grade']} 原类型={q_type}")
        print(f"--- 清洗前 ---")
        print(text[:500])
        if len(text) > 500:
            print("...")
        print(f"--- 清洗后 (类型={new_type}) ---")
        print(new_text[:500])
        if len(new_text) > 500:
            print("...")
        if new_opts is not None:
            print(f"--- 提取选项 ---")
            print(json.dumps(new_opts, ensure_ascii=False, indent=2))
        print()

    conn.close()


def apply_cleanup(db_path: Path) -> dict[str, int]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT id, question_type, question_text, options FROM question_bank")
    rows = cur.fetchall()

    stats = {"total": 0, "text_changed": 0, "options_extracted": 0, "type_changed": 0, "options_cleared": 0}

    for row in rows:
        stats["total"] += 1
        qid = row["id"]
        old_text = row["question_text"]
        old_type = row["question_type"]
        old_opts = row["options"]

        new_text, new_opts, new_type = clean_question(old_text, old_opts, old_type)

        text_changed = new_text != old_text
        type_changed = new_type != old_type
        opts_extracted = new_opts is not None and old_opts is None
        opts_cleared = new_opts is None and old_opts is not None

        if text_changed:
            stats["text_changed"] += 1
        if type_changed:
            stats["type_changed"] += 1
        if opts_extracted:
            stats["options_extracted"] += 1
        if opts_cleared:
            stats["options_cleared"] += 1

        cur.execute(
            "UPDATE question_bank SET question_text = ?, options = ?, question_type = ? WHERE id = ?",
            (new_text, json.dumps(new_opts, ensure_ascii=False) if new_opts is not None else None, new_type, qid),
        )

    conn.commit()
    conn.close()
    return stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="题库内容格式化清洗")
    parser.add_argument("--db", type=str, default=str(DB_PATH), help="数据库路径")
    parser.add_argument("--dry-run", action="store_true", help="随机预览清洗效果，不修改数据库")
    parser.add_argument("--sample", type=int, default=20, help="预览样本数（默认 20）")
    parser.add_argument("--apply", action="store_true", help="执行清洗并写入数据库（会自动备份）")
    return parser.parse_args()


def main():
    args = parse_args()
    db_path = Path(args.db)
    if not db_path.exists():
        print(f"数据库不存在: {db_path}")
        return

    if args.dry_run or not args.apply:
        analyze_sample(db_path, sample_size=args.sample)
        print("\n提示：以上仅为预览。如需执行清洗，请追加 --apply 参数。")
        return

    if args.apply:
        backup_path = backup_database(db_path)
        print(f"已备份数据库到: {backup_path}")
        stats = apply_cleanup(db_path)
        print("清洗完成。统计:")
        for k, v in stats.items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
