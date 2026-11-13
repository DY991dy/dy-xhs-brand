// 渲染 + 密度自检
// 用法: cd "<本篇目录>" && node "<引擎目录>/render.mjs" [输入.html] [输出前缀]
//       （也可不 cd，用 XHS_NOTE="<本篇目录>" 指定）
import { chromium } from "playwright";  // 依赖装在仓库根（npm install）
import path from "node:path";
import fs from "node:fs";

// ⚠️ 位置无关：本篇工作目录运行时解析 —— $XHS_NOTE > 当前工作目录。
//    原来这里硬编码绝对路径，搬一次目录就静默读旧目录 —— 别再改回硬编码。
const dir = process.env.XHS_NOTE || process.cwd();
// 认文件走本篇的 pipeline.json（与 python 侧同一份清单），别再硬编码目录名 ——
// 硬编码过一次，目录一改就静默往错的地方写图。
const SRC = "_源";
let cfg = {};
for (const p of [path.join(dir, SRC, "pipeline.json"), path.join(dir, "pipeline.json")]) {
  if (fs.existsSync(p)) { cfg = JSON.parse(fs.readFileSync(p, "utf8")); break; }
}
if (!Object.keys(cfg).length) console.log("⚠️ 没读到 pipeline.json，使用默认值");
const inFile = process.argv[2] || cfg.index || "index.html";
const prefix = process.argv[3] || cfg.outputPrefix || "xhs";
const out = path.join(dir, cfg.outputDir || "output");
fs.mkdirSync(out, { recursive: true });
console.log(`工作目录: ${dir}`);

const browser = await chromium.launch({ channel: "chrome" });
const ctx = await browser.newContext({ viewport: { width: 1200, height: 1600 }, deviceScaleFactor: 1 });
const page = await ctx.newPage();

await page.goto("file://" + path.join(dir, inFile), { waitUntil: "networkidle" });
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(900);

const n = await page.locator("section.poster.xhs").count();
const files = [];
for (let i = 0; i < n; i++) {
  const el = page.locator("section.poster.xhs").nth(i);
  const file = path.join(out, `${prefix}-${String(i + 1).padStart(2, "0")}.png`);
  await el.screenshot({ path: file });
  const box = await el.boundingBox();
  files.push(`${path.basename(file)}  ${Math.round(box.width)}x${Math.round(box.height)}`);
}

// 溢出 / 碰撞 / 图片加载自检
const report = await page.evaluate(() => {
  const rows = [];
  document.querySelectorAll("section.poster.xhs").forEach((p, i) => {
    const c = p.querySelector(".content");
    const box = c.getBoundingClientRect();
    let bottom = box.top;
    c.querySelectorAll("*").forEach((n) => {
      const r = n.getBoundingClientRect();
      if (r.height > 0) bottom = Math.max(bottom, r.bottom);
    });
    const strip = p.querySelector(".sig-strip") || p.querySelector(".issue-strip");
    const sb = strip ? strip.getBoundingClientRect() : null;
    const sTop = sb && sb.height > 0 ? sb.top : Infinity;
    const imgs = [...c.querySelectorAll("img")].map((im) => ({
      src: im.getAttribute("src"),
      ok: im.complete && im.naturalWidth > 0,
      nat: im.naturalWidth + "x" + im.naturalHeight,
    }));
    rows.push({
      page: i + 1,
      h: Math.round(box.height),
      fill: +(((bottom - box.top) / 1440) * 100).toFixed(1),
      gapToStrip: Math.round(sTop - bottom),
      imgs,
    });
  });
  return rows;
});

console.log("\npage  h       fill%   gapToStrip");
report.forEach((r) => {
  const flag = r.gapToStrip < 0 ? "  ❌ 压到签名条" : r.fill < 75 ? "  ⚠️ 密度不足" : "";
  console.log(`  ${r.page}   ${String(r.h).padEnd(5)}   ${String(r.fill + "%").padEnd(6)}   ${r.gapToStrip}px${flag}`);
});

const bad = report.flatMap((r) => r.imgs.filter((i) => !i.ok).map((i) => `  p${r.page}: ✗ ${i.src}`));
const good = report.flatMap((r) => r.imgs.filter((i) => i.ok).map((i) => `  p${r.page}: ✓ ${path.basename(i.src)} (${i.nat})`));
console.log("\n=== 图片加载 ===");
console.log(good.length ? good.join("\n") : "  (本组无图片)");
if (bad.length) { console.log("\n❌ 未加载:"); console.log(bad.join("\n")); }

// ⚠️ 三项都要计入退出码。README 承诺「非 0 = 视觉不过」，但原来只有图片加载失败算失败：
//    压签名条与密度不足只打印 ❌ / ⚠️ 就放行 —— 于是用 && 串起来的发布闸门会
//    「全绿」放过一份明显压版的稿子。踩过一次（2026-09-22，P3/P11 压版却退出 0）。
const overlap = report.filter((r) => r.gapToStrip < 0);
const thin = report.filter((r) => r.fill < 75);

console.log("\n" + files.join("\n"));
await browser.close();

const problems = [
  ...bad,
  ...overlap.map((r) => `  p${r.page}: 压到签名条 ${r.gapToStrip}px`),
  ...thin.map((r) => `  p${r.page}: 密度 ${r.fill}%（低于 75%）`),
];
if (problems.length) {
  console.log("\n❌ 视觉不过，逐项改版后再发：");
  problems.forEach((l) => console.log(l));
}
process.exitCode = problems.length ? 1 : 0;
