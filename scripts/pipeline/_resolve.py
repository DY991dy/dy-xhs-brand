#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共享路径解析 —— 让流水线脚本与「脚本自己放在哪」解耦。

为什么需要：
    本目录里的脚本原来把「本篇工作目录」硬编码成绝对路径（`T = Path("/abs/path/to/your-note")`）。
    一搬目录就断，而且是静默断（脚本照样跑，读的是旧目录）。

现在改成运行时解析，优先级：
    ① 命令行 --note "<本篇目录>"
    ② 环境变量 XHS_NOTE
    ③ 当前工作目录

推荐用法（cd 进本篇目录再跑，最省事）：
    cd "<本篇目录>"
    python3 "<引擎目录>/build.py"
    python3 "<引擎目录>/check-limits.py"

脚本靠本篇目录里的 pipeline.json 认文件 —— 那是**本篇的路径清单**，
改文件名要同步改它，否则脚本会找不到文件。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

CONFIG_NAME = "pipeline.json"
# 生产件集中在这个子目录；pipeline.json 允许放这里，也允许放本篇根目录
SRC_DIR = "_源"
NOTE_FLAGS = ("--note",)


def note_dir() -> Path:
    """解析「本篇工作目录」"""
    argv = sys.argv[1:]
    for i, a in enumerate(argv):
        if a == "--note" and i + 1 < len(argv):
            return Path(argv[i + 1]).expanduser().resolve()
        if a.startswith("--note="):
            return Path(a.split("=", 1)[1]).expanduser().resolve()
    env = os.environ.get("XHS_NOTE")
    if env:
        return Path(env).expanduser().resolve()
    return Path.cwd().resolve()


def config_file(note: Path) -> Path | None:
    """pipeline.json 在哪：先看本篇根目录，再看 _源/。"""
    for p in (note / CONFIG_NAME, note / SRC_DIR / CONFIG_NAME):
        if p.is_file():
            return p
    return None


def config(note: Path | None = None) -> dict:
    """读本篇的 pipeline.json（路径清单）"""
    note = note or note_dir()
    f = config_file(note)
    if f is None:
        raise SystemExit(
            f"❌ 认不出本篇目录：{note}\n"
            f"   这里没有 {CONFIG_NAME}（也不在 {SRC_DIR}/ 里）。请 cd 进本篇目录再跑，\n"
            f'   或用 --note "<本篇目录>" 指定工作目录。'
        )
    cfg = json.loads(f.read_text(encoding="utf-8"))
    cfg.pop("_说明", None)
    return cfg


def path_of(cfg: dict, key: str, note: Path | None = None) -> Path:
    """取配置里某个键对应的绝对路径"""
    note = note or note_dir()
    return note / cfg[key]


def positional_args() -> list[str]:
    """把 --note / --note=xxx 从参数里摘掉，剩下的位置参数"""
    argv, out, skip = sys.argv[1:], [], False
    for a in argv:
        if skip:
            skip = False
            continue
        if a == "--note":
            skip = True
            continue
        if a.startswith("--note="):
            continue
        out.append(a)
    return out


def publish_body(text: str) -> str:
    """从「库内文档」里剥出「真正要发出去的那段正文」。

    为什么必须剥：文档进库后会加两类东西，**它们都不是发布内容**，
    但都会被朴素 len() 算进字数 —— 实测同一篇因此从 887 变成 1261，直接误判超限。

    要剥掉的两类：
      ① YAML frontmatter（`---` 包起来那段，type/area/定位/tags…）
      ② 开头的导航脚手架（H1 标题 + `> 关联区域` / `> 本篇代码库` 那串引用块）

    剥完才是能贴进小红书输入框的那段字。
    """
    # ① frontmatter
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[2]

    # ② 开头连续的标题行 / 引用块 / 空行
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s or s.startswith("#") or s.startswith(">"):
            i += 1
            continue
        break
    return "\n".join(lines[i:]).strip()
