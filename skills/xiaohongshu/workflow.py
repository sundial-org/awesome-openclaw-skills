#!/usr/bin/env python3
"""
小红书工作流 - 从内容到发布的完整流程
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 添加路径
SKILL_DIR = Path(__file__).parent
sys.path.insert(0, str(SKILL_DIR / "social-auto-upload"))

from dotenv import load_dotenv
load_dotenv(SKILL_DIR / ".env")


async def setup_cookie():
    """首次登录获取 Cookie（需要有显示器）"""
    from uploader.xiaohongshu_uploader.main import xiaohongshu_cookie_gen
    cookie_file = SKILL_DIR / "social-auto-upload" / "cookies" / "xhs_account.json"
    cookie_file.parent.mkdir(parents=True, exist_ok=True)
    await xiaohongshu_cookie_gen(str(cookie_file))
    print(f"✅ Cookie 已保存到: {cookie_file}")


async def check_cookie():
    """检查 Cookie 是否有效"""
    from uploader.xiaohongshu_uploader.main import cookie_auth
    cookie_file = SKILL_DIR / "social-auto-upload" / "cookies" / "xhs_account.json"
    
    if not cookie_file.exists():
        print("❌ Cookie 文件不存在，请先运行 setup 命令")
        return False
    
    valid = await cookie_auth(str(cookie_file))
    if valid:
        print("✅ Cookie 有效")
    else:
        print("❌ Cookie 已失效，请重新登录")
    return valid


async def publish_images(title: str, desc: str, images: list, schedule_time=None, is_private=False):
    """
    发布图文笔记
    
    Args:
        title: 笔记标题
        desc: 笔记描述/正文
        images: 图片路径列表
        schedule_time: 定时发布时间 (datetime 对象)
        is_private: 是否私密
    """
    from playwright.async_api import async_playwright
    from conf import LOCAL_CHROME_PATH
    
    cookie_file = SKILL_DIR / "social-auto-upload" / "cookies" / "xhs_account.json"
    
    if not cookie_file.exists():
        print("❌ Cookie 文件不存在")
        return False
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=str(cookie_file))
        page = await context.new_page()
        
        print("🌐 打开小红书创作者中心...")
        await page.goto("https://creator.xiaohongshu.com/publish/publish")
        await asyncio.sleep(3)
        
        # 选择"上传图文"
        print("📝 选择图文发布...")
        try:
            await page.click('text=发布图文')
            await asyncio.sleep(2)
        except:
            pass  # 可能已经在图文页面
        
        # 上传图片
        print(f"📷 上传 {len(images)} 张图片...")
        upload_input = await page.query_selector('input[type="file"]')
        if upload_input:
            await upload_input.set_input_files(images)
            await asyncio.sleep(5)  # 等待上传
        
        # 填写标题
        print("✏️ 填写标题...")
        title_input = await page.query_selector('[placeholder*="标题"]')
        if title_input:
            await title_input.fill(title[:20])  # 小红书标题限制
        
        # 填写正文
        print("📄 填写正文...")
        desc_input = await page.query_selector('[placeholder*="正文"]')
        if not desc_input:
            desc_input = await page.query_selector('.ql-editor')
        if desc_input:
            await desc_input.fill(desc)
        
        await asyncio.sleep(2)
        
        # 发布
        print("🚀 发布中...")
        publish_btn = await page.query_selector('button:has-text("发布")')
        if publish_btn:
            await publish_btn.click()
            await asyncio.sleep(5)
            print("✅ 发布成功！")
        
        await browser.close()
        return True


def render_content(markdown_file: str, style: str = "xiaohongshu", output_dir: str = None):
    """渲染 Markdown 为图片"""
    import subprocess
    
    if output_dir is None:
        output_dir = str(SKILL_DIR / "output")
    
    cmd = [
        str(SKILL_DIR / "venv" / "bin" / "python"),
        str(SKILL_DIR / "scripts" / "render_xhs_v2.py"),
        markdown_file,
        "--style", style,
        "-o", output_dir
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        return []
    
    # 返回生成的图片列表
    output_path = Path(output_dir)
    images = sorted(output_path.glob("*.png"))
    return [str(img) for img in images]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="小红书工作流")
    subparsers = parser.add_subparsers(dest="command")
    
    # setup 命令
    subparsers.add_parser("setup", help="首次登录获取 Cookie")
    
    # check 命令
    subparsers.add_parser("check", help="检查 Cookie 状态")
    
    # render 命令
    render_parser = subparsers.add_parser("render", help="渲染内容为图片")
    render_parser.add_argument("markdown_file", help="Markdown 文件路径")
    render_parser.add_argument("--style", default="xiaohongshu", help="样式")
    render_parser.add_argument("-o", "--output", help="输出目录")
    
    # publish 命令
    pub_parser = subparsers.add_parser("publish", help="发布图文笔记")
    pub_parser.add_argument("-t", "--title", required=True, help="标题")
    pub_parser.add_argument("-d", "--desc", required=True, help="描述")
    pub_parser.add_argument("-i", "--images", nargs="+", required=True, help="图片路径")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        asyncio.run(setup_cookie())
    elif args.command == "check":
        asyncio.run(check_cookie())
    elif args.command == "render":
        images = render_content(args.markdown_file, args.style, args.output)
        print(f"生成了 {len(images)} 张图片")
    elif args.command == "publish":
        asyncio.run(publish_images(args.title, args.desc, args.images))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
