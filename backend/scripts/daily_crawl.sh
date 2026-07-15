#!/bin/bash
# 每日增量爬取试卷 - 使用增量爬虫，记录进度，循环抓取
# crontab: 0 2 * * * /home/yuanwu/cynthia-study/backend/scripts/daily_crawl.sh >> /var/log/crawl.log 2>&1

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
cd "$BACKEND_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 开始每日增量爬取 ==="

# 使用 python3.11 (playwright 需要) 执行增量爬虫，每次抓30张
python3.11 scripts/daily_crawl.py --batch 30 2>&1

# 查看进度
echo ""
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 当前进度:"
python3.11 scripts/daily_crawl.py --status 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 每日爬取完成 ==="
