# DY Lab 小红书图文排版规范（v2）

本规范是「DY的AI实验室」账号所有小红书图文的**唯一排版依据**。每次做图先读本文件，禁止凭感觉临时调整。所有数值基于 1080×1440 画布。

> **v1 → v2 变更摘要**
> - §1 猫角标：88px 独立角标 → **42px 并入底部签名条**（含账号 handle + 页码）
> - §4 页面垂直结构：删除 `issue-row` / `issue-strip` / 独立 `cat-badge`
> - §5 新增小字纪律（每页最多两个小字区块）
> - §6 页数：修正上限表述
> - §8 验收清单同步更新
>
> ⚠️ **v1 失效的直接原因（务必记住）**：v1 写进了 `~/.agents/skills/dy-xhs-brand/`，而实际出图用的是 `~/.workbuddy/skills/dy-xhs-brand/`（不含本文件）→ **规范写了但没生效**，角标一直按模板旧值 120px 渲染。副本分叉造成过一次用户可见的失败。见文末 §9。

---

## 1. 签名条 sig-strip（取代猫角标，固定禁止改）

每页底部一条签名，同时承载**账号 handle** 与**页码**。构建时把 `{{PAGE}}` 顺序替换为 `NN / TT`。

```html
<div class="sig-strip">
  <span class="sig-brand"><img src="assets/cat-badge.png" alt=""/>DY的AI实验室</span>
  <span class="sig-page">{{PAGE}}</span>
</div>
```

| 项 | 值 | 说明 |
|---|---|---|
| 猫标尺寸 | **42×42px** | `object-fit: contain`，`flex: none` |
| 猫标透明度 | **`opacity: .55`** | 压印感；不要调到 .8 以上，会变「贴纸」 |
| handle 字号 | 21px mono，`letter-spacing: .11em` | 色 `rgba(ink, .70)` |
| 页码字号 | 20px mono | 色 `rgba(ink, .42)`，要更弱于 handle |
| 位置 | `left/right: 88px`；`bottom: 46px` | 上方一条 `1px rgba(244,235,208,.13)` hairline |
| 内容底部 padding | **≥176px** | 保证正文不压签名条 |

**为什么不用独立角标**：早期是 120px 独立圆（占卡宽 11%，与标题同量级），`opacity .92` 使它成为全卡最亮物体，且孤立飘在右下角、不与任何元素对齐——读起来是「贴纸」而不是「签名」；同时另有一条独立页脚小字条，导致一页底部出现两处小字。合并成一个单元后：角标变小、底部小字从两处收敛为一处、账号 ID 有了落点（**帖被单张截图转发时不丢来源**）。

**禁止**：页面内联覆盖签名条尺寸；把猫标单独拿出来放别处（如右上角、右下角浮动）。

---

## 2. 配图策略（先判断，不硬配）

不是每页都要配图。按页面任务决定：

| 页面任务 | 是否配图 | 图类型 |
|---|---|---|
| 封面（P1） | 可选，推荐配 | 项目实证截图 / 真实素材主视觉 |
| 方法 / 清单页 | 不配 | — |
| 复盘 / 案例页 | **必须配** | 真实截图（`frame-shot`） |
| 数据 / 证据页 | **必须配** | 真实截图 / 官方原文 |
| **纯观点页** | **不配** | — |
| 收尾 / 引导页 | 不配 | — |

规则：
- **没图就不配**，用文字排版填满，绝不为了有图而塞装饰图。
- **纯观点页配图 = 填充物**，读者能感觉到，反而掉可信度。留白跟前后的图页形成呼吸。
- 真实截图 > 生成插画。复盘/证据类必须用真实截图，可信度优先。
- 图片选择属**作者性判断，归 DY**。AI 写「配图需求单」（导航级粒度：打开哪个页面 → 滚到哪 → 截哪块），DY 供图，AI 排版。详见 `image-planning-and-capture.md`。

---

## 3. 图片框尺寸控制

- 图片框**必须定高**，禁止 `flex:1` 撑满（会溢出）。
- 截图用 `.frame-shot.r-{ratio}`，`r-*` 按**实测**原图比例选，不是凭习惯。差 >3% 就把原图裁到该比例，别留着黑边（`object-fit: contain` 会把内容缩到数字看不清）。
- 单页图井高度档位：**320px**（辅助图）/ **400px**（图文各半）/ **480–540px**（封面主视觉）。

## 3b. ⚠️ SVG 示意图不要当 flex item 压缩

`.stack` 里的 SVG 默认 `flex-shrink: 1`。加内容后 SVG 会被自动缩高，`preserveAspectRatio` 居中缩放，**标签小到看不清**，且不报错。

- 写法：SVG 加 `flex: none`，再按页面预算反推 `viewBox` 高度。
- 判断标准：`gapToStrip` 变负 = 撑爆（砍图高或砍内容行数）；`fill%` 低于 75% = 图太小或内容太薄。

---

## 4. 页面垂直结构

标准内容页从上到下：

```
kicker（唯一顶栏小字）    21px mono
标题区（h-xl / h-display） ~200px
正文 / 图片 / 台账         主体
hr
签名条 sig-strip          固定贴底 bottom:46px
```

- 内容容器：`padding: 92px 88px 176px`，`display:flex; flex-direction:column`。
- **不要在中间留大段孤立空白**；底部内容用 `margin-top:auto` 贴向签名条。
- 空白超过 ~180px 且无法用内容填时，补内容或把图井加高，**不要干留**。
- `issue-row` / `issue-strip` / 独立 `.cat-badge` 在 `data-theme="dy-navy"` 下已 `display: none`，不要再引用它们。

---

## 5. 字体、颜色与小字纪律

- 标题：黑体（sans-zh），weight 700。**禁用宋体**。
- 色板：藏青 `#12243A` / 米白 `#F4EBD0` / 做旧金 `#C9A663` / 蓝灰 `#5B7C99`。
- 标题字号档：封面 `h-display` 104px，内页 `h-xl` 按标题长度带调，台账标题 42px。
- 正文最小 **20px**（手机端可读）。

**小字纪律（v2 新增）**：
- 全组小字（≤21px mono）下限 **20px**，不要出现 18px 及以下。
- **每页最多两个小字区块**：顶部一个 `kicker` + 底部一个 `sig-strip`。不要再引入第三个各自为政的小字条。
- `label`（来源标注）只在引用外部资料的页出现，算第三个区块时需删掉其他小字。

## 5b. ⚠️ CSS 特异性陷阱

同特异性的 `:root` 在源码中位置更靠后，会**赢过** `[data-theme="dy-navy"]`。品牌级覆盖一律写成 `html[data-theme="dy-navy"]`（特异性 0,1,1）并置于 `:root` 之后。

（历史事故：`[data-theme="dy-navy"]` 里覆盖 `--serif-zh` 被后面的 `:root` 干掉 → **所有藏青金卡片标题都回落成宋体**，违反品牌红线。）

---

## 6. 每篇页数

- 按内容定页数，**不凑页**。短内容 4–6 页；内容厚的（如产品全图）8–12 页完全合理。
- 小红书单帖上限 **18 张**，在此范围内以内容完整度优先。
- 加配图时**优先拆页**（文案零损失），不要压字换图位。

---

## 7. 图从哪来

1. **DY 提供**：项目截图 / 控制台 / 部署输出（复盘、证据类**必须**用它）。
2. **DY 自行截取的官方公开页**：定价页、文档原文（作者性统一，AI 不代劳）。
3. **AI 画的 SVG 示意图**：层级、阶梯、流程这类抽象结构——现实里没有对应画面。
4. **AI 抓的公开页截图**：仅当 DY 明确同意时才做，**不是默认动作**。

---

## 8. 渲染后验收清单

先跑 `render.mjs` 自检，再目视核对：

- [ ] 每页 `fill%` **≥75%**，且 `gapToStrip` **为正**（负 = 内容被裁）
- [ ] 签名条就位：猫标 42px、账号 handle、页码 `NN / TT` 正确
- [ ] 小字区块 ≤2 个/页，最小字号 ≥20px
- [ ] 无宋体，标题黑体
- [ ] 色板符合厂牌四色；无投影、无渐变
- [ ] 图片全部加载（`naturalWidth > 0`），无溢出、无裁掉主体
- [ ] 内容在安全区内（上 92 / 下 176 / 左右 88）
- [ ] 截图已脱敏（邮箱、账号 ID、真实域名、项目名）
- [ ] 额度/价格类数字与官方最新公告一致

---

## 9. 单一真源与符号链接（2026-09-18 重构）

**架构**：`~/.agents/skills/dy-xhs-brand/` 是**唯一真源**（实体目录）。其余各 agent 目录都是**指向它的相对符号链接**，不再有实体副本。

| 路径 | 形态 | 备注 |
|---|---|---|
| `~/.agents/skills/dy-xhs-brand/` | **实体目录（源）** | 只有这里改内容 |
| `~/.workbuddy/skills/dy-xhs-brand` | 符号链接 `../../.agents/skills/dy-xhs-brand` | WorkBuddy 读取 |
| `~/.claude/skills/dy-xhs-brand` | 同上 | Claude Code（该目录已有 18 个同类链接，模式已验证） |
| `~/.openclaw/skills/dy-xhs-brand` | 同上 | OpenClaw（该目录全部为链接） |
| `~/.codex/skills/dy-xhs-brand` | 同上 | Codex |
| `~/.cursor/skills/dy-xhs-brand` | 同上 | Cursor |

**改内容只改 `.agents` 那一处**，所有 agent 立刻同步，无需再手工 rsync。

### 为什么会走到这一步（两次静默失效）

1. **副本分叉**：同一 skill 曾有两份实体副本（`.workbuddy` + `.agents`）。v1 规范与「角标 88px」修复只写进了 `.agents`，而出图用的是 `.workbuddy` → **修复没生效**，角标一直按模板旧值 120px 渲染。
2. **模板快照**：构建脚本曾读任务目录里复制的模板副本，改模板本体不会传导 → 「模板已改、渲染没变」。
3. 两次的共同点：**改了一处，别处静默过期，且不报错**。根治办法是消灭副本，不是靠"记得同步"。

### 校验与回归

```bash
# 1. 链接是否都在、是否断链
for p in ~/.workbuddy ~/.claude ~/.codex ~/.openclaw ~/.cursor; do
  ls -l "$p/skills/dy-xhs-brand" 2>/dev/null
done

# 2. 全环境扫描：还有哪些 skill 是多实体副本（应逐步收敛到 0）
python3 ~/.agents/skill-divergence-audit.py
python3 ~/.agents/skill-divergence-audit.py --all      # 含 claude/codex/openclaw/cursor

# 3. 构建链路自检：产物里必须含新样式的选择器，别只看构建成功
grep -c 'html\[data-theme="dy-navy"\] .sig-strip' index.html
```

### 回滚（万一某 agent 不跟随符号链接）

```bash
# 若 WorkBuddy 启动后技能列表里看不到本 skill，恢复成实体目录：
rm ~/.workbuddy/skills/dy-xhs-brand
cp -R ~/.agents/skills/dy-xhs-brand ~/.workbuddy/skills/dy-xhs-brand
```

**遗留待验证**：`~/.workbuddy/` 与 `~/.codex/` 下此前 0 个符号链接，其加载器是否跟随链接尚未实测（`.claude` 18 个、`.openclaw` 全部为链接，已验证可用）。失败表现为「技能列表里消失」，**是显性失败且可秒回滚**。
