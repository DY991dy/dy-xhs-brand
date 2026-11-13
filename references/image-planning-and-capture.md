# Image Planning, Shot Lists & Screenshot Capture

Three things the upstream skill left underspecified:

1. **How to decide where an image belongs** — and where it must not go.
2. **How to hand the user a shot list they can execute without thinking.**
3. **How to capture public pages, when the user asks for that** (optional, not the default).

Read this at intake time, before page planning, not after.

---

## Division of labour (get this right first)

```
I plan  →  user shoots  →  I lay out
我给需求单 → 用户截图 → 我排版渲染
```

**Image selection is an authorial decision and belongs to the user.** Do not go capture images on your own initiative — that takes the choice away from the person whose post it is. The agent's job is to make the *choice* easy by writing a precise shot list, not to substitute its own taste for theirs.

Two categories, and they are not interchangeable:

| Category | Examples | Only the user has it? | Why it matters |
| --- | --- | --- | --- |
| **Project evidence** | their console, `wrangler deploy` output, a data page | ✅ yes | "I actually did this" |
| **External corroboration** | a vendor pricing table, docs page | no, publicly checkable | "you can verify this number yourself" |

For project evidence the agent is not just unable, it is **ignorant** — it does not know what the user's project looks like. Guesswork here produces a shot list the user has to reinterpret, which is the same as no help at all.

⚠️ **Do not silently capture public pages to "save the user time."** Offer it as an option and let them decide. If they decline, drop it — do not re-raise. Authorial consistency is a legitimate reason to prefer their own screenshots even for public pages.

---

## Part 1 — Image Planning (before page planning)

The failure mode this prevents: cards get designed as pure typography, then the user asks for images, and the only options left are compressing text or bolting on pages. **Plan images and pages together.**

### Three tests per page

| Test | Question | If yes |
| --- | --- | --- |
| **Evidence** | Does the page make a claim someone could dispute? (a number, a quota, a product existing, an operation having worked) | needs a **real capture** |
| **Spatial** | Is the content about a spatial / hierarchical / sequential relation? (ladder, architecture, pipeline) | draw a **diagram** |
| **Replaceable** | Remove the image — does the page still stand, and is the layout already full? | **no image** |

Tag each page: `M` must-have · `S` optional · `X` none.

### Scarcity ordering

> Cover (decides click-through) → pages with numeric claims → pages with operational proof → diagram pages → **opinion pages (never)**

### Two hard rules

- **Opinion pages get no image.** Pure judgement has no external artifact to show. An image there is filler, readers feel it, and credibility drops. Leave it typographic; the whitespace becomes a breathing beat against the surrounding image pages.
- **Keep the must-have count small.** A content piece naturally suggests 8+ image slots. Opening all of them buries the user in screenshot work and stalls the project. Open **~3 as `M`**, mark the rest `S` ("have it or not, it still ships"), build v1, then decide about the extras. Do the arithmetic for the user and tell them how many screenshots they actually owe.

---

## Part 2 — Writing The Shot List (the primary deliverable)

Emit a `00_配图需求单.md` in the task folder. A table row saying "console screenshot" is **not** a shot list — the user still has to guess. One block per image:

```
### 图 NN · 用于 PX「<page title>」

| 项 | 内容 |
| --- | --- |
| 证明什么 | the specific claim this image backs up |
| 截什么   | which page / which panel / which region |
| 怎么截   | open X → left nav Y → capture the Z column |
| 规格     | landscape, width ≥1200px, dark terminal preferred |
| 文件名   | NN-slug.png |
| 脱敏     | ⚠️ needs masking: email / domain / project name |
| 优先级   | 🔴 M / 🟡 S |
```

Requirements:

- **导航级粒度.** "Open `dash.cloudflare.com` → left nav **Workers & Pages** → capture the project column" — not "a screenshot of your dashboard". If the user has to figure out *where* in the product you mean, the block failed.
- **State what it proves.** This lets the user judge whether they even have such an artifact, and swap in a better one.
- **Tell them what NOT to worry about**: ratio, dimensions, filenames. "Just capture it, I'll crop, scale, and place it." Their only constraint is not cutting off the content.
- **Include the privacy table** (Part 4) and the OS screenshot keybindings.
- **List what the agent will draw itself** (diagrams) separately, so it is visibly not the user's job.
- **Mark pages that get no image** and say why, so the omission reads as a decision rather than an oversight.
- **Give an inbox path** (`assets/inbox/`) and say filenames are free-form and they need not match images to pages.

---

## Part 3 — Optional: Capturing Public Pages

Only when the user has opted in. Reference pages are still valuable — a `Free: 100,000 per day` row from the vendor's own pricing page is checkable evidence and beats any stock photo — but it is their call, not yours.

`chromium.launch({ channel: "chrome" })` — system Chrome, no browser download.

```js
await page.goto(url, { waitUntil: "domcontentloaded", timeout: 45000 });
await page.waitForTimeout(2000);

// 1. strip site chrome so the capture reads as content, not as a browser window
await page.addStyleTag({ content: `
  aside, nav[aria-label], .sidebar,
  [class*="toc"], [class*="TableOfContents"] { display:none !important; }
  main { max-width: 1200px !important; }
`});
await page.waitForTimeout(600);

// 2. capture the ELEMENT, not the viewport
const el = page.locator("table").first();
await el.scrollIntoViewIfNeeded();
await page.waitForTimeout(1200);            // let fonts + layout settle
await el.screenshot({ path: out });
```

### Rules learned the hard way

- **Capture the element, not the viewport.** A full-page shot of a docs site carries sidebar + nav + ToC, which reads as "I screenshotted a website" rather than "here is the fact". Element-level is tight, readable, and drops straight into a `.frame-shot`.
- **`deviceScaleFactor: 2`.** A 646 CSS-px table becomes 1292 px, which stays crisp after scaling into a 1080-wide card.
- **Hide site chrome first, then wait ~600 ms, then locate.** Locating before the style injection gives stale boxes.
- **`boundingBox()` is CSS px; the PNG is `boundingBox × deviceScaleFactor`.** Do not compare them when asserting ratio.
- **Verify by reading the PNG back**, not by exit code. A capture can succeed and still be the wrong table — nav tables, cookie tables and footers all match `table:first`.
- **Strip a vendor wordmark baked into the image** before it collides with your own title. Crop it out with PIL; covering it in CSS looks like a patch.

### Matching the frame to the source

Pick `r-*` from the **measured** ratio:

```python
from PIL import Image
w, h = Image.open(p).size
print(round(w / h, 3))     # then pick the nearest r-* token
```

`r-16x9` = 1.778 · `r-16x10` = 1.6 · `r-3x2` = 1.5 · `r-4x3` = 1.333 · `r-21x9` = 2.333

A mismatch shows as letterbox bars; worse, `object-fit: contain` shrinks the content until the numbers are unreadable at card scale. If the nearest token is off by more than ~3%, **crop the source to the token's exact ratio** rather than living with the bars.

Always write `assets/public/SOURCES.md` — `file ← url`, plus capture date. Vendor pricing and quotas change; the date is what makes the card defensible later.

---

## Part 4 — Privacy Red Lines For User-Supplied Screenshots

Console and dashboard captures leak the *account*, not just the product. Before publishing:

| Leaks | Fix |
| --- | --- |
| Email, account ID | demo account, or solid mask |
| Real domain names | mask, or run the flow against a throwaway domain |
| Real project names | mask, or shorten `PS1` before capturing |
| Other windows, chat notifications | clear the screen first |

**Cheapest durable answer:** a throwaway demo account plus a fake domain, run through the flow once. Twenty minutes buys a permanent, zero-risk screenshot library for that product.

**macOS masking steps to hand the user:** `⇧⌘4` → click the floating thumbnail → annotate → rectangle tool + black fill → drag over the target → `⌘S`.

---

## Part 5 — Delivery Order

```
Stage 1  Plan      content in → page plan + shot list (Part 2) → user confirms, especially the M rows
Stage 2  Shoot     I draw diagrams → assets/diagrams/
                   user drops screenshots → assets/inbox/
                   I read each image, QA (legibility / ratio / privacy), place it
Stage 3  Build     generate HTML → render PNG → density self-check
```

**Gating rule:** do not start Stage 3 while `M` images are outstanding — the point is to avoid laying out a page twice. Pages whose image never arrives degrade to their typography-only version and do not block the rest. Diagram work (Stage 2a) is independent and can run in parallel with the user's shooting, which shortens the critical path.
