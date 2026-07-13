"""
学科网试卷 API 捕获脚本

流程：
1. 打开浏览器，访问登录页
2. 你手动登录（手机短信验证码）
3. 登录成功后，脚本自动访问试卷页面，拦截所有 API 请求
4. 将捕获的请求保存到 captured_apis.json

Usage:
    python capture_paper_api.py
"""

import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# 试卷页面 URL 列表
PAPER_URLS = [
    "https://zujuan.xkw.com/xxsx/shijuan/jdcs/",      # 小学数学-基础达标
    "https://zujuan.xkw.com/xxsx/shijuan/zqjm/",      # 小学数学-期中期末
    "https://zujuan.xkw.com/xxwx/shijuan/jdcs/",      # 小学语文-基础达标
    "https://zujuan.xkw.com/xxyx/shijuan/jdcs/",      # 小学英语-基础达标
]

OUTPUT_FILE = Path(__file__).parent / "captured_apis.json"
COOKIES_FILE = Path(__file__).parent / "cookies.json"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        )
        page = context.new_page()

        # 存储捕获的请求
        captured_requests = []

        # 拦截请求 - 只关注 API 请求
        def on_response(response):
            url = response.url
            # 只捕获 zujuan.xkw.com 的 API 请求
            if "zujuan.xkw.com" not in url:
                return
            if "zujuan-api" not in url and "shijuan" not in url and "paper" not in url and "list" not in url and "search" not in url and "calendar" not in url:
                return

            try:
                status = response.status
                content_type = response.headers.get("content-type", "")
                body_size = len(response.body()) if status == 200 else 0

                req = {
                    "url": url,
                    "method": response.request.method,
                    "status": status,
                    "content_type": content_type,
                    "body_size": body_size,
                    "post_data": response.request.post_data or "",
                    "headers": dict(response.request.headers),
                }

                # 尝试获取响应体
                if status == 200 and body_size < 50000:
                    try:
                        text = response.text()
                        req["response_body"] = text[:2000]
                    except Exception:
                        pass

                captured_requests.append(req)
                print(f"  [CAPTURE] {response.request.method} {status} {url[:120]}")
            except Exception as e:
                print(f"  [ERROR] {e}")

        page.on("response", on_response)

        # Step 1: 打开登录页
        print("=" * 60)
        print("Step 1: 正在打开登录页面...")
        print("=" * 60)
        page.goto("https://zujuan.xkw.com/", wait_until="domcontentloaded")

        print("\n请手动登录学科网（手机短信验证码）")
        print("登录完成后，脚本将自动开始捕获 API 请求...")
        print("按 Enter 键继续（登录完成后按）...")
        input()

        # 保存登录后的 cookies
        cookies = context.cookies()
        with open(COOKIES_FILE, "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)
        print(f"\nCookie 已保存到 {COOKIES_FILE}")

        # Step 2: 访问试卷页面，捕获 API
        print("\n" + "=" * 60)
        print("Step 2: 开始访问试卷页面，捕获 API 请求...")
        print("=" * 60)

        for i, url in enumerate(PAPER_URLS):
            print(f"\n[{i+1}/{len(PAPER_URLS)}] 访问: {url}")
            try:
                page.goto(url, wait_until="networkidle", timeout=30000)
                # 等待页面稳定
                page.wait_for_timeout(3000)
                print(f"  页面加载完成，继续下一个...")
            except Exception as e:
                print(f"  [WARN] {e}")

        # Step 3: 尝试访问第2页，捕获分页 API
        print("\n" + "=" * 60)
        print("Step 3: 尝试访问分页...")
        print("=" * 60)
        for i, url in enumerate(PAPER_URLS):
            page2_url = url.rstrip("/") + "2/"
            print(f"\n[{i+1}/{len(PAPER_URLS)}] 访问第2页: {page2_url}")
            try:
                page.goto(page2_url, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(3000)
            except Exception as e:
                print(f"  [WARN] {e}")

        # Step 4: 尝试点击试卷链接，捕获试卷详情 API
        print("\n" + "=" * 60)
        print("Step 4: 尝试点击第一张试卷，捕获详情 API...")
        print("=" * 60)
        try:
            # 回到第一个页面
            page.goto(PAPER_URLS[0], wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)

            # 尝试点击第一个试卷链接
            links = page.query_selector_all("a[href*='shijuan']")
            if links:
                print(f"  找到 {len(links)} 个试卷链接，点击第一个...")
                links[0].click()
                page.wait_for_timeout(5000)
            else:
                print("  未找到试卷链接，尝试其他选择器...")
                # 尝试其他可能的选择器
                for selector in [
                    ".paper-list a",
                    ".list-item a",
                    "[class*='paper'] a",
                    "a[href*='p/']",
                    "a[href*='zujuan']",
                ]:
                    link = page.query_selector(selector)
                    if link:
                        print(f"  使用选择器 '{selector}' 找到链接，点击...")
                        link.click()
                        page.wait_for_timeout(5000)
                        break
        except Exception as e:
            print(f"  [WARN] {e}")

        # 保存结果
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "total": len(captured_requests),
                "captured_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "requests": captured_requests,
            }, f, indent=2, ensure_ascii=False)

        print(f"\n{'=' * 60}")
        print(f"捕获完成！共捕获 {len(captured_requests)} 个 API 请求")
        print(f"结果保存到: {OUTPUT_FILE}")
        print(f"Cookie 保存到: {COOKIES_FILE}")
        print(f"{'=' * 60}")

        # 去重统计
        unique_urls = set()
        for req in captured_requests:
            # 去掉 query string 中的时间戳等动态参数
            base_url = req["url"].split("?")[0]
            unique_urls.add(base_url)

        print(f"\n去重后的 API 端点 ({len(unique_urls)} 个):")
        for url in sorted(unique_urls):
            print(f"  - {url}")

        browser.close()


if __name__ == "__main__":
    main()
