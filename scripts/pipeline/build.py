#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 posters.html 拼进 dy-xhs-brand 的 editorial 种子模板，输出 dy-navy 版 HTML

用法:
    python build.py                          # 默认 posters.html -> index.html
    python build.py posters.html index.html

自动处理:
    - data-theme -> dy-navy
    - 注入任务级 CSS（TASK_CSS）
    - 把 {{PAGE}} 顺序替换成 "NN / TT"，TT 按实际页数计算

⚠️ 改这个文件时不要并行发多个 Edit 到同一文件 —— 实测会互相覆盖，
   表现为「工具报成功、改动其实没落盘」。逐个改，改完 Read 回来确认。
"""
import pathlib, re, sys

# ⚠️ 位置无关：本篇工作目录运行时解析（--note / $XHS_NOTE / 当前目录）。
#    原来这里硬编码绝对路径，搬一次目录就静默读旧目录 —— 别再改回硬编码。
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _resolve import config, note_dir, positional_args  # noqa: E402

T = note_dir()
CFG = config(T)

# ⚠️ 模板单一真源 = 本仓库 assets/（相对脚本位置解析，可整仓搬动）。
# 踩坑记录：① 读任务目录里的模板快照副本 → 改模板不生效；
# ② skill 存在两份实体副本 → 改动只落一份，静默失效（详见 references/dy-layout-rules.md §9）。
_REPO = pathlib.Path(__file__).resolve().parent.parent.parent  # scripts/pipeline/ → 仓库根
_TPL_CANDIDATES = [
    _REPO / "assets/template-editorial-card.html",
]
for _c in _TPL_CANDIDATES:
    if _c.exists():
        TPL = _c
        break
else:
    raise SystemExit("厂牌模板找不到，检查 dy-xhs-brand 是否已安装")

TASK_CSS = """
    /* =========================================================
       XK · 任务级覆盖示例（仅本组卡片生效）
       ========================================================= */
    .poster.xhs .content      { padding: 92px 88px 176px; }
    .poster.xhs .ledger-row   { grid-template-columns: 84px 1fr; gap: 26px; padding: 11px 0; }
    .poster.xhs .ledger-title { font-size: 40px; }
    .poster.xhs .ledger-note  { font-size: 25px; line-height: 1.5; color: rgba(var(--ink-rgb), .74); }
    .poster.xhs .callout      { font-style: normal; font-size: 30px; line-height: 1.46; padding: 22px 26px; }
    .poster.xhs .callout .callout-src { font-size: 19px; }
    .poster.xhs .pipeline-v   { gap: 22px; }
    .poster.xhs .pipeline-v .step { padding-bottom: 20px; }
    .poster.xhs .pipeline-v .step-title { font-size: 38px; }
    .poster.xhs .pipeline-v .step-desc  { font-size: 25px; }
    [data-theme="dy-navy"] .h-sub { font-style: normal; letter-spacing: .02em; color: var(--muted); }

    /* 截图证据窗：厂牌下禁投影，只留一条藏青描边环 */
    [data-theme="dy-navy"] .poster.xhs .frame-shot {
      box-shadow: none;
      outline: 1px solid rgba(244,235,208,.14);
      outline-offset: -1px;
    }
    .poster.xhs .frame-shot { margin-left: 0; margin-right: 0; background: #0E1D2E; }

    /* 小字收敛：下限 20px */
    .poster.xhs .label {
      font-family: var(--mono); font-size: 20px; letter-spacing: .09em;
      color: rgba(var(--ink-rgb), .50); text-transform: none;
    }

    /* --- 封面数据条 --- */
    .xk-stats { display: grid; grid-template-columns: repeat(4, 1fr); }
    .xk-stats .cell { padding: 0 22px; border-left: 1px solid var(--line); }
    .xk-stats .cell:first-child { padding-left: 0; border-left: 0; }
    .xk-stats .big { font-family: var(--mono); font-size: 80px; line-height: 1; color: var(--accent); letter-spacing: -.02em; }
    .xk-stats .lbl { font-family: var(--mono); font-size: 20px; letter-spacing: .06em; color: var(--muted); margin-top: 14px; }

    /* --- 目次 --- */
    .xk-toc { display: flex; flex-direction: column; }
    .xk-toc .toc-row { display: grid; grid-template-columns: 52px 1fr; gap: 20px; align-items: baseline; padding: 9px 0; }
    .xk-toc .toc-nb { font-family: var(--mono); font-size: 22px; color: var(--accent); letter-spacing: .06em; }
    .xk-toc .toc-tx { font-family: var(--serif-zh); font-size: 25px; line-height: 1.4; color: rgba(var(--ink-rgb), .84); }

    /* --- 规格表（左键右值） --- */
    .xk-kv { display: flex; flex-direction: column; }
    .xk-kv .r { display: grid; grid-template-columns: 1fr auto; gap: 28px; align-items: baseline; padding: 17px 0; border-bottom: 1px solid var(--line); }
    .xk-kv .k { font-family: var(--serif-zh); font-size: 28px; color: rgba(var(--ink-rgb), .86); }
    .xk-kv .v { font-family: var(--mono); font-size: 30px; color: var(--accent); white-space: nowrap; }

    /* --- 双栏对照（名字的两个来源） --- */
    .xk-duo { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; }
    .xk-duo .col { padding-top: 22px; border-top: 2px solid var(--accent); }
    .xk-duo .tag { font-family: var(--mono); font-size: 20px; letter-spacing: .12em; color: var(--muted); margin-bottom: 12px; }
    .xk-duo .ttl { font-family: var(--serif-zh); font-weight: 700; font-size: 40px; line-height: 1.2; color: var(--ink); margin-bottom: 6px; }
    .xk-duo .en  { font-family: var(--mono); font-size: 21px; letter-spacing: .04em; color: var(--accent); margin-bottom: 20px; }
    .xk-duo .tx  { font-family: var(--serif-zh); font-size: 25px; line-height: 1.54; color: rgba(var(--ink-rgb), .80); margin: 0 0 22px; }
    .xk-duo .leaf{ font-family: var(--serif-zh); font-weight: 700; font-size: 23px; color: var(--accent); margin-bottom: 8px; }

    /* --- 证据区（GitHub 截图） --- */
    .xk-shot-name { width: 100%; }
    .xk-shot-name img { display: block; width: 100%; height: auto; }
    .xk-evi { display: grid; grid-template-columns: 1fr 420px; gap: 34px; align-items: start; }
    .xk-evi .notes p { font-family: var(--serif-zh); font-size: 25px; line-height: 1.5; color: rgba(var(--ink-rgb), .80); margin: 0 0 18px; }
    .xk-shot-about { width: 420px; }
    .xk-shot-about img { display: block; width: 100%; height: auto; }

    /* --- 架构图 --- */
    .xk-arch { margin: 10px 0 46px; }
    .xk-arch svg { display: block; width: 100%; height: auto; }
    .xk-bullets p { font-family: var(--serif-zh); font-size: 26px; line-height: 1.55; color: rgba(var(--ink-rgb), .80); margin: 0 0 22px; }
    .xk-bullets b { color: var(--accent); font-weight: 700; }

    /* --- 补充说明（承接结论，不是装饰） --- */
    .xk-note { font-family: var(--serif-zh); font-size: 25px; line-height: 1.52; color: rgba(var(--ink-rgb), .80); margin: 34px 0 0; }
    .xk-note b { color: var(--accent); font-weight: 700; }

    /* --- 本机核验清单 --- */
    .xk-check .r { display: grid; grid-template-columns: 32px 112px 1fr; gap: 14px; align-items: baseline; padding: 14px 0; border-bottom: 1px solid var(--line); }
    .xk-check .m { font-family: var(--mono); font-size: 24px; color: rgba(var(--ink-rgb), .58); }
    .xk-check .warn .m { color: var(--accent); }
    .xk-check .k { font-family: var(--mono); font-size: 21px; letter-spacing: .06em; color: var(--muted); }
    .xk-check .v { font-family: var(--serif-zh); font-size: 25px; line-height: 1.42; color: rgba(var(--ink-rgb), .86); }
    .xk-verdict { display: grid; grid-template-columns: 92px 1fr; gap: 22px; align-items: baseline; margin-top: 26px; padding: 22px 26px; background: var(--paper-2); border-left: 3px solid var(--accent); }
    .xk-verdict .lb { font-family: var(--mono); font-size: 20px; letter-spacing: .12em; color: var(--muted); }
    .xk-verdict .tx { font-family: var(--serif-zh); font-weight: 700; font-size: 31px; line-height: 1.36; color: var(--ink); }

    /* --- 新旧代速度对照表 / 三条路对照表 --- */
    .xk-speed, .xk-paths { display: flex; flex-direction: column; }
    .xk-speed .r, .xk-speed .hd,
    .xk-paths .r, .xk-paths .hd { display: grid; grid-template-columns: 1fr 190px 190px; gap: 18px; align-items: baseline; padding: 17px 0; border-bottom: 1px solid var(--line); }
    .xk-speed .hd, .xk-paths .hd { border-bottom: 1px solid var(--accent); padding-bottom: 12px; }
    .xk-speed .hd span, .xk-paths .hd span { font-family: var(--mono); font-size: 20px; letter-spacing: .10em; color: var(--muted); }
    .xk-speed .hd .c1, .xk-paths .hd .c1 { color: rgba(var(--ink-rgb), .60); }
    .xk-speed .c1, .xk-paths .c1 { font-family: var(--serif-zh); font-size: 28px; color: var(--ink); }
    .xk-speed .c2, .xk-paths .c2 { font-family: var(--mono); font-size: 30px; color: var(--accent); text-align: right; }
    .xk-speed .c3, .xk-paths .c3 { font-family: var(--mono); font-size: 26px; color: rgba(var(--ink-rgb), .58); text-align: right; }

    /* --- 大标题封面（纯钩子页，与「导读」页拆开） ---
       ⚠️ 必须带 .poster.xhs 前缀。模板里 .h-display / .h-sub / .lead 都有
       [data-theme="dy-navy"] 前缀规则（特异度 0,2,0），裸类（0,1,0）覆盖不动，
       表现是「改了字号没反应」。 */
    .poster.xhs .content.xk-cover  { padding: 128px 88px 200px; justify-content: space-between; }
    .poster.xhs .xk-cover-mid      { flex: 1; display: flex; flex-direction: column; justify-content: center; padding-top: 104px; }
    .poster.xhs .xk-cover-title    { font-size: 300px; line-height: 1; letter-spacing: .01em; margin: 0 0 24px; color: var(--ink); }
    .poster.xhs .xk-cover-zh       { font-family: var(--serif-zh); font-weight: 700; font-size: 82px; line-height: 1.16;
                                     letter-spacing: .04em; color: var(--ink); margin: 0; }
    .poster.xhs .xk-cover-bot .rule-accent { width: 132px; margin: 0 0 30px; }
    .poster.xhs .xk-cover-lead     { font-size: 30px; line-height: 1.52; margin: 0 0 30px; max-width: 860px; }
    .poster.xhs .xk-cover-foot     { display: flex; justify-content: space-between; align-items: baseline; gap: 24px;
                                     padding-top: 26px; border-top: 1px solid var(--line); }
    .poster.xhs .xk-cover-foot span { font-family: var(--mono); font-size: 22px; letter-spacing: .08em;
                                      color: rgba(var(--ink-rgb), .62); }
    .poster.xhs .xk-cover-foot span:first-child { color: var(--accent); }
  </style>"""


def build(posters_file=None, out_file=None, title=None):
    posters_file = posters_file or CFG.get("posters", "posters.html")
    out_file = out_file or CFG.get("index", "index.html")
    tpl = TPL.read_text(encoding="utf-8")
    posters = (T / posters_file).read_text(encoding="utf-8")

    # 1. theme + title
    tpl = tpl.replace('data-theme="ink-classic"', 'data-theme="dy-navy"', 1)
    if title is None:
        title = CFG.get("htmlTitle", "小红书图文组")
    tpl = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", tpl, count=1, flags=re.S)

    # 2. inject task css
    assert tpl.count("</style>") == 1, "expected exactly one </style>"
    tpl = tpl.replace("  </style>", TASK_CSS, 1)

    # 3. splice posters
    start = tpl.index('<main class="sheet">') + len('<main class="sheet">')
    end = tpl.index("</main>")
    assert "POSTERS_HERE" in tpl[start:end], "poster region not found"
    tpl = tpl[:start] + "\n" + posters + "\n  " + tpl[end:]

    # 4. 页码注入：{{PAGE}} -> "NN / TT"，TT 按实际 poster 数
    total = tpl.count('<section class="poster xhs"')
    counter = {"i": 0}

    def _page(m):
        counter["i"] += 1
        return f'<span class="sig-page">{counter["i"]:02d} / {total:02d}</span>'

    tpl = re.sub(r'<span class="sig-page">\{\{PAGE\}\}</span>', _page, tpl)

    (T / out_file).write_text(tpl, encoding="utf-8")
    print(f"built: {out_file}  {len(tpl)} chars | pages: {total} | sig-strip: {tpl.count('sig-strip')} | "
          f"leftover PAGE placeholders: {tpl.count('{{PAGE}}')}")

    # 自检：任务级 CSS 是否真的注入进去（并行改写过这里，静默丢过规则）
    must_have = [".xk-arch", ".xk-bullets b", ".xk-note", ".xk-verdict", ".xk-speed", ".xk-duo",
                 ".xk-check", ".xk-kv", ".xk-stats", ".xk-toc", ".xk-evi", ".xk-paths",
                 ".xk-cover-title", ".xk-cover-foot"]
    missing = [m for m in must_have if m not in tpl]
    if missing:
        raise SystemExit(f"❌ TASK_CSS 注入不完整，缺: {missing}")
    print(f"css self-check: {len(must_have)}/{len(must_have)} 条规则就位")
    return out_file


if __name__ == "__main__":
    args = positional_args()          # 摘掉 --note，剩下的才是位置参数
    print(f"工作目录: {T}")
    if len(args) >= 2:
        build(args[0], args[1])
    elif len(args) == 1:
        build(args[0])
    else:
        build()
