# DY XHS Brand — 小红书图文卡片生成 Skill

把一篇文章、一组素材，变成一套**风格统一**的小红书 3:4 图文卡片（HTML → PNG，确定性排版，不靠 AI 生图）。

> 默认厂牌「藏青纸感底 + 米白字 + 做旧金」来自小红书 **@DY的AI实验室**。
> 本仓库是 [guizang-social-card-skill](https://github.com/op7418/guizang-social-card-skill)（归藏）的厂牌改造版，遵循 **AGPL-3.0**，详见文末「许可」。

## 它能做什么

- 小红书 3:4 图文组（1080×1440），一套 1–18 页
- 每页底部固定**签名条**（你的账号名 + 页码）——一张图被单独转发也丢不了来源
- 版式库继承归藏：Editorial M01–M16 / Swiss S01–S12
- 真实截图处理（`.frame-shot`）、内容密度自检、压签名条检测
- Live Photo 动卡、公众号封面（21:9）等扩展形态

## 需要什么

- Python 3.9+
- Node 18+，且本机装有 **Google Chrome**（渲染用 `channel: "chrome"`）
- 一个能读 `SKILL.md` 的 AI agent（Claude Code / Codex / Cursor / 其他支持 Skills 的工具）

## 安装

```bash
git clone https://github.com/DY991dy/dy-xhs-brand.git
cd dy-xhs-brand
npm install          # 安装 playwright
```

把仓库放进（或软链到）你 agent 读取 skills 的目录。

## 5 分钟快速开始

**第 1 步 · 换成你自己的品牌**（30 秒）

```bash
python3 scripts/init-brand.py --handle "你的账号名" --avatar ~/Pictures/你的logo.png
```

**第 2 步 · 跑示例**

```bash
cd examples/demo
python3 ../../scripts/pipeline/build.py   # 拼模板 → index.html
node    ../../scripts/pipeline/render.mjs # 截图 → 图/demo-01.png …
```

**第 3 步 · 看结果**

打开 `examples/demo/图/` 里的 PNG。改 `posters.html` 里的文字，重跑第 2 步，就是你的新一套。

## 换成你自己的品牌

| 要换什么 | 怎么换 |
|---|---|
| **账号名** | 跑 `scripts/init-brand.py --handle "你的名字"`；之后签名条文字必须来自 `brand.config.json` |
| **头像/角标** | `scripts/init-brand.py --avatar 你的logo.png`（会复制成 `assets/cat-badge.png`，42px 小标记） |
| **配色** | 改 `assets/template-editorial-card.html` 里 `data-theme="dy-navy"` 的 CSS 变量：`--paper` / `--ink` / `--accent` / `--muted` |
| **主题预设** | 参考 `references/theme-presets.md` 加自己的主题 |

> 开源版每个人拿到的都是同一套模板——`init-brand.py` 就是把它变成「你自己的」那一步。

## 厂牌改造点（相对归藏原版）

1. **dy-navy 主题**：藏青纸感底（#12243A~#1A2F4A）+ 米白字（#F4EBD0）+ 做旧金强调（#C9A663）
2. **签名条（sig-strip）**：取代「独立角标 + 页脚条」双元素，猫标缩到 42px / opacity .55 作压印
3. **黑体标题**：厂牌主题下所有标题走无衬线（Noto Sans SC / 苹方），不用衬线
4. **小字纪律**：小字 ≥20px，每页最多两处（顶部 kicker + 底部签名条）
5. **截图组件适配深色底**，工具实测类内容建议用真截图
6. **密度纪律**：内容 ≥75%、不压签名条（`render.mjs` 自检，不过就改版）
7. **构建读模板本体**，不读任务目录里的快照副本（否则「模板已改、渲染没变」静默失效）
8. **单一真源**：多 agent 用相对软链指向本仓库，不造实体副本

## 目录结构

```
SKILL.md                        ← 给 AI 读的主文件（工作流、规范、红线）
brand.config.json               ← 你的品牌配置（init-brand.py 生成）
assets/
  template-editorial-card.html  ← 主模板（CSS 变量在这改）
  cat-badge.png                 ← 签名条角标（换成你的 logo）
references/                     ← 版式库、截图处理、主题预设等细则
scripts/
  init-brand.py                 ← 一键换品牌
  pipeline/build.py             ← posters.html → index.html
  pipeline/render.mjs           ← index.html → PNG（含密度自检）
examples/demo/                  ← 最小可跑示例（2 页）
```

## 常见问题

- **渲染报错找不到 Chrome**：装 Google Chrome；或把 `render.mjs` 里 `channel: "chrome"` 删掉，改用 Playwright 自带 chromium（`npx playwright install chromium`）
- **提示找不到模板**：确认用仓库内 `assets/`（不要复制模板到任务目录）
- **中文显示异常**：系统缺中文字体，装 Noto Sans SC 或苹方
- **改了模板不生效**：检查是不是读的快照副本（见 SKILL.md 第 7 条）

## 许可

**AGPL-3.0**。可以免费使用、修改、商用；但分发（包括作为网络服务提供）必须开源全部源码、保留版权声明，衍生作品同样使用 AGPL-3.0。

基于 [guizang-social-card-skill](https://github.com/op7418/guizang-social-card-skill)（归藏，AGPL-3.0）改造。默认厂牌来自小红书 **@DY的AI实验室**。
