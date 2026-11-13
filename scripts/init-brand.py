#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一键把 dy-xhs-brand 换成你自己的品牌（开源版初始化）

开源后每个人拿到的都是同一套模板——这个脚本负责把它变成「你自己的」：
把签名条里的账号名、assets/ 里的角标图，一次换成你的。

用法:
    # 1) 换成你自己的（账号名 + 头像/logo 图片）
    python3 scripts/init-brand.py --handle "你的账号名" --avatar ~/Pictures/my-logo.png

    # 2) 只改账号名（不想换图）
    python3 scripts/init-brand.py --handle "你的账号名"

    # 3) 看当前配置
    python3 scripts/init-brand.py --show

    # 4) 先看会发生什么（不落盘）
    python3 scripts/init-brand.py --handle "测试名" --dry-run

做了什么:
    ① 写 brand.config.json —— 你的品牌配置（唯一配置源）
    ② 把你的头像复制成 assets/cat-badge.png（建图时签名条引用的就是它）
    ③ 把 SKILL.md / README.md / references 里原作者的账号名换成你的
       —— 这样 AI 照着示例生成新卡片时，写的自动是你的名字

之后做图时，签名条文字必须来自 brand.config.json 的 handle（见 SKILL.md §换成你自己的品牌）。
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "brand.config.json"
AVATAR_TARGET = ROOT / "assets" / "cat-badge.png"

# 会被替换账号名的文本文件（相对 skill 根目录）
TEXT_TARGETS = [
    "SKILL.md",
    "README.md",
    "references/dy-layout-rules.md",
    "references/theme-presets.md",
    "assets/template-editorial-card.html",
]

# 原作者的账号名 —— 只在首次初始化时作为「旧值」使用
ORIGINAL_HANDLE = "DY的AI实验室"


def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"⚠️ {CONFIG_PATH.name} 不是合法 JSON，将按新配置重写")
    return {}


def save_config(cfg: dict) -> None:
    CONFIG_PATH.write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def replace_handle(old: str, new: str, dry_run: bool) -> list[tuple[str, int]]:
    """把文本文件里的旧账号名替换成新的，返回 [(文件, 替换次数)]。"""
    report: list[tuple[str, int]] = []
    if old == new:
        return report
    for rel in TEXT_TARGETS:
        p = ROOT / rel
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        n = text.count(old)
        if not n:
            continue
        report.append((rel, n))
        if not dry_run:
            p.write_text(text.replace(old, new), encoding="utf-8")
    return report


def main() -> int:
    ap = argparse.ArgumentParser(
        description="把 dy-xhs-brand 换成你自己的品牌（账号名 + 头像）"
    )
    ap.add_argument("--handle", help="你的账号名（会出现在每页签名条）")
    ap.add_argument("--avatar", help="你的头像/logo 图片路径（png/jpg）")
    ap.add_argument("--show", action="store_true", help="只看当前配置")
    ap.add_argument("--dry-run", action="store_true", help="只打印将发生的改动，不落盘")
    args = ap.parse_args()

    cfg = load_config()

    if args.show or (not args.handle and not args.avatar):
        print("当前配置（brand.config.json）:")
        print(json.dumps(cfg or {"handle": ORIGINAL_HANDLE, "avatar": "assets/cat-badge.png"},
                         ensure_ascii=False, indent=2))
        if not args.show:
            print("\n用法: python3 scripts/init-brand.py --handle \"你的账号名\" [--avatar 图片路径]")
        return 0

    if not args.handle:
        print("❌ 先给 --handle：你的账号名会印在每一页的签名条上")
        return 1

    handle = args.handle.strip()
    if not handle:
        print("❌ 账号名不能是空白")
        return 1

    # 1) 账号名替换
    old_handle = cfg.get("handle", ORIGINAL_HANDLE)
    changes = replace_handle(old_handle, handle, args.dry_run)
    if changes:
        print("账号名替换:")
        for rel, n in changes:
            print(f"  {rel}  ×{n}")
        if args.dry_run:
            print("  （--dry-run：未写入）")
    else:
        print(f"账号名已是「{handle}」或模板里找不到旧账号名，跳过")

    # 2) 头像
    avatar_rel = cfg.get("avatar", "assets/cat-badge.png")
    if args.avatar:
        src = Path(args.avatar).expanduser().resolve()
        if not src.exists():
            print(f"❌ 头像文件不存在: {src}")
            return 1
        if src.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            print(f"❌ 头像需要 png/jpg/webp，收到 {src.suffix}")
            return 1
        if not args.dry_run:
            AVATAR_TARGET.parent.mkdir(parents=True, exist_ok=True)
            if src == AVATAR_TARGET.resolve():
                print("头像已经是这个文件，跳过")
            else:
                shutil.copy2(src, AVATAR_TARGET)
                print(f"头像已复制 → {AVATAR_TARGET.relative_to(ROOT)}")
        else:
            print(f"（--dry-run）将把 {src.name} 复制为 assets/cat-badge.png")
        avatar_rel = "assets/cat-badge.png"

    # 3) 写配置
    if not args.dry_run:
        cfg.update({
            "handle": handle,
            "avatar": avatar_rel,
            "note": "这是你的品牌配置。签名条文字必须来自这里的 handle；头像文件 = assets/cat-badge.png",
        })
        save_config(cfg)
        print(f"\n✅ 已写入 {CONFIG_PATH.name}：handle = 「{handle}」")
        print("下一步：让 AI 读 SKILL.md 的「换成你自己的品牌」一节，开始做你自己的图文。")
    else:
        print("\n（--dry-run：配置未写入）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
