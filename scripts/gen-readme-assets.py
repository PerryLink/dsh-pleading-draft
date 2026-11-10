#!/usr/bin/env python3
"""Generate the README visuals for dsh-pleading-draft, from the shipped code.

What the figures are derived from (nothing is invented below):

  src/model.ts            the material contract: 10 canonical row fields and 6
                          header fields, with the authored column aliases that
                          are normalised onto them; `requireAnyOf` refuses
                          material that carries none of the row columns.
  rules/pleading-draft.yaml
                          the pack: 7 rules, version 2026.1, all `warn`;
                          PL-001/002/003 are `presence` on fact / evidence /
                          law, PL-004 is `conditionalPresence` from amount to
                          deadline, PL-005 is `headerPresence` on
                          plaintiff + defendant, PL-006 is `unique` on
                          elementNo, PL-007 is `containsAny` on claim with the
                          11 placeholder terms; four rules are `direct`, three
                          `derived-from-principle`.
  src/shared/rows.ts      the engine: one `check.kind` per rule, findings that
                          carry `locator {row, column}` plus found / expected /
                          fix, and `skip(reason)` for a check that cannot run.
                          A rule that ran and found nothing is NOT skipped.
  src/shared/ruleset.ts   load-time guards: verbatim excerpt, and the kind ->
                          severity cap (derived <= warn, institutional <= info).
  src/view.ts             the report the model reads: issues + skipped +
                          summary counts, markdown + reportJson, disclaimer.
  samples/quickstart/     the real run used for every number and string:
    input/PL-001-unsafe.json
                          caseNo （2026）某民初 1234 号, court 某某人民法院,
                          plaintiff 原告某某公司, defendant 被告某某公司,
                          cause 买卖合同纠纷, one claim row (序号 1, 请求要素
                          本金给付请求, 事实依据 empty, 证据 证1、证2、证3,
                          法律依据《中华人民共和国民法典》第五百七十七条,
                          金额 1250000, 期限 本判决生效之日起十日内,
                          撰写人 王律师).
    expected/result.json  issueCount 1, summary error 0 / warn 1 / info 0,
                          skippedCount 0.

Outputs (idempotent overwrite):

  docs/assets/dsh-pleading-draft-hero-{zh,en}-{light,dark}.webp  1440x576, Pillow
  docs/assets/dsh-pleading-draft-flow-v5-{light,dark}.svg        1100x660, hand-written SVG

Hero  - the four elements of claim 1, drawn as four column tiles. Three are
        filled; 事实依据 is a hollow slot, and the PL-001 slip below quotes the
        engine's own found / fix wording for it. The conditional pair
        金额 -> 期限 is the thin line under the tiles (PL-004, no diff), and the
        summary pills are the quickstart result. The left column is the family
        banner column: kicker / wordmark / two value lines / two subtitle lines
        / meta / footer.

Flow  - grammar: a COLUMN-MOUNTED CHECK REGISTER, not a row of nodes. One
        read-only element register is set as seven vertical columns
        (序号 / 诉讼请求 / 事实依据 / 证据 / 法律依据 / 金额 / 期限), each column
        name standing vertically in the Chinese ledger manner. The rule that
        reads a column is mounted in a chip at the foot of that column with its
        `check.kind` and this run's outcome; PL-004 owns the amount+deadline
        pair and gets one chip spanning both columns; PL-005 owns the header
        band (plaintiff + defendant) and is stamped there. The empty
        事实依据 cell is hollow, which is exactly the one finding. The bar at
        the foot is the report the tool returns: issues[] 1, skipped[] 0,
        summary error 0 / warn 1 / info 0, then markdown + reportJson. The
        footer states the pack's citation discipline and the 4 direct /
        3 derived split. Labels are command-surface tokens and short English
        annotations, so all five README languages share the same pair.

Design parameters: GitHub renders the 1440px hero at ~880px, so the title is
79px, subtitles 25px and meta 21px; the 1100px SVG is checked at native size,
with node text >= 13px and annotations >= 11px. Palette: light #f9f6fd ->
#e4eaf8, dark #131a2a -> #0c1016, family accent #4B67B4 (dark #8496f5),
radius 18-22, soft shadows; fonts msyh.ttc / msyhbd.ttc / consola.ttf.

Every string is measured before it is drawn; a string that would overflow its
box aborts the run instead of shipping clipped text.

The older single-skin assets (dsh-pleading-draft-flow.svg,
-flow-{light,dark}.svg, -hero.png, -demo.*, quickstart.*) are left untouched
for external deep links; the READMEs reference only the new pair.

Run:  python scripts/gen-readme-assets.py
Needs: Python 3, Pillow, and the Windows fonts named above.
"""
from __future__ import annotations

import math
import os
import re
import sys
from html import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")
NAME = "dsh-pleading-draft"

FONT_FILES = {
    "cjk": r"C:\Windows\Fonts\msyh.ttc",
    "cjk_b": r"C:\Windows\Fonts\msyhbd.ttc",
    "mono": r"C:\Windows\Fonts\consola.ttf",
    "mono_b": r"C:\Windows\Fonts\consolab.ttf",
}
for _kind, _path in FONT_FILES.items():
    if not os.path.exists(_path):
        sys.exit(f"FATAL: font missing ({_kind}): {_path}")

_LRU: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}
CHECKS: list[tuple[str, float, float]] = []


def font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    key = (kind, size)
    if key not in _LRU:
        _LRU[key] = ImageFont.truetype(FONT_FILES[kind], size)
    return _LRU[key]


def tw(text: str, kind: str, size: int) -> float:
    """Measured width of a string in the Windows font it will be drawn with."""
    return font(kind, size).getlength(text)


def check(name: str, text: str, kind: str, size: int, limit: float) -> None:
    CHECKS.append((name, tw(text, kind, size), limit))


def mixed_w(text: str, size: int, mono: bool = True, bold: bool = False) -> float:
    """SVG text width: CJK advances one em, Latin advances the font's own width."""
    kind = ("mono_b" if bold else "mono") if mono else ("cjk_b" if bold else "cjk")
    f = font(kind, size)
    total = 0.0
    for ch in text:
        total += size if ord(ch) >= 0x2E80 else f.getlength(ch)
    return total


def mix(a, b, t: float):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


# ---------------------------------------------------------------------------
# Hero (Pillow): 1440 x 576
# ---------------------------------------------------------------------------
W, H = 1440, 576

HERO = {
    "light": dict(
        bg_top=(249, 246, 253), bg_bot=(228, 234, 248),
        ink=(21, 20, 32), sub=(74, 79, 100), faint=(126, 130, 150),
        accent=(75, 103, 180), accent_soft=(236, 235, 249),
        card=(255, 255, 255), border=(226, 223, 240), divider=(219, 216, 235),
        tile=(248, 246, 253), tile_edge=(232, 229, 243),
        hollow=(244, 241, 254),
        warn=(176, 83, 9), warn_soft=(253, 241, 227),
        warn_border=(228, 178, 116), warn_text=(138, 84, 26),
        ok=(31, 122, 74), ok_soft=(234, 247, 239),
        mute_bg=(243, 241, 248), mute_ink=(116, 120, 138),
        pill=(255, 255, 255), pill_border=(226, 222, 240),
        shadow=(24, 18, 48),
    ),
    "dark": dict(
        bg_top=(19, 26, 42), bg_bot=(12, 16, 22),
        ink=(237, 241, 252), sub=(160, 170, 198), faint=(128, 138, 168),
        accent=(132, 150, 245), accent_soft=(35, 44, 74),
        card=(26, 34, 51), border=(44, 54, 80), divider=(40, 50, 74),
        tile=(31, 40, 59), tile_edge=(47, 58, 86),
        hollow=(35, 44, 74),
        warn=(240, 180, 95), warn_soft=(52, 40, 25),
        warn_border=(122, 91, 45), warn_text=(233, 190, 120),
        ok=(111, 211, 154), ok_soft=(28, 47, 38),
        mute_bg=(30, 39, 59), mute_ink=(146, 156, 184),
        pill=(36, 46, 70), pill_border=(52, 64, 92),
        shadow=(0, 0, 0),
    ),
}

# Field tokens and the Chinese column names are the register's own; the sample
# values are the quickstart row verbatim. `fact` ships empty in that row.
TILES = [
    ("PL-007", "no diff", "claim", "诉讼请求", "判令被告支付货款本金人民币 1,250,000 元", "mute"),
    ("PL-001", "1 issue", "fact", "事实依据", None, "warn"),
    ("PL-002", "no diff", "evidence", "证据", "证1、证2、证3", "mute"),
    ("PL-003", "no diff", "law", "法律依据", "《中华人民共和国民法典》第五百七十七条", "mute"),
]

HERO_TEXT = {
    "zh": dict(
        kicker="DeepSeek Harness 插件 · 起诉状要素核对",
        title="dsh-pleading-draft",
        value=["每项诉请，四要素逐栏核对", "差什么、怎么补，指到行与栏"],
        sub=["读一份要素核对表：表头 + 每项诉请一行，", "七条规则逐栏核对，只列差异、不下结论。"],
        meta="pleading_draft · PL-001..PL-007 · rules/pleading-draft.yaml",
        footer="Apache-2.0 · 只读材料 · 不联网 · 不调用模型",
        card_title="MATERIAL · 第 1 项诉请",
        card_pill="序号 1",
        card_sub="本金给付请求 · 撰写人 王律师",
        empty="（空）",
        cond="PL-004 · 金额 1,250,000 → 期限 本判决生效之日起十日内 · no diff",
        slip1="PL-001 · warn · row 1 · fact",
        slip2="found 第 1 行「fact」为空",
        slip3="fix 补填事实依据；本条只核对是否写明，不判断事实是否属实",
        summary=[("error 0", "mute"), ("warn 1", "warn"),
                 ("info 0", "mute"), ("skipped 0", "accent")],
        source="样例：samples/quickstart/input/PL-001-unsafe.json",
    ),
    "en": dict(
        kicker="DeepSeek Harness plugin · pleading elements",
        title="dsh-pleading-draft",
        value=["Four elements, column by column.", "Name the row, the gap, the fix."],
        sub=["Reads one pleading element register — header + claim rows.",
             "Seven checks list differences only; never a verdict."],
        meta="pleading_draft · PL-001..PL-007 · rules/pleading-draft.yaml",
        footer="Apache-2.0 · read-only · no network · no model calls",
        card_title="MATERIAL · claim 1",
        card_pill="序号 1",
        card_sub="本金给付请求 · drafted by 王律师",
        empty="(empty)",
        cond="PL-004 · amount 1,250,000 → deadline 本判决生效之日起十日内 · no diff",
        slip1="PL-001 · warn · row 1 · fact",
        slip2="found 第 1 行「fact」为空",
        slip3="fix fill in the factual basis; presence only, not truth",
        summary=[("error 0", "mute"), ("warn 1", "warn"),
                 ("info 0", "mute"), ("skipped 0", "accent")],
        source="Sample: samples/quickstart/input/PL-001-unsafe.json",
    ),
}


def add_shadow(img, box, radius, dy=10, blur=18, alpha=38, color=(24, 18, 48)):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((box[0], box[1] + dy, box[2], box[3] + dy),
                        radius=radius, fill=color + (alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(layer)


def hero_bg(theme: str) -> Image.Image:
    p = HERO[theme]
    small = Image.new("RGB", (72, 72))
    px = small.load()
    top, bot = p["bg_top"], p["bg_bot"]
    for y in range(72):
        for x in range(72):
            t = (0.66 * y + 0.34 * x) / 71.0
            px[x, y] = mix(top, bot, t)
    img = small.resize((W, H), Image.BICUBIC).convert("RGBA")

    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(deco)
    # Rule-fibre motif: faint vertical rules behind the wordmark, like the
    # column ledger the checker reads. No other repo in the family uses it.
    for x in range(46, 470, 24):
        dd.line((x, 40, x, H - 40), fill=p["accent"] + (16,), width=1)
    glow = p["bg_top"] if theme == "light" else mix(p["bg_top"], p["accent"], 0.14)
    dd.ellipse((980, -220, 1620, 420), fill=glow + (118,))
    for off in (0, 34, 68):
        r = 210 + off
        dd.arc((60 - r, 620 - r, 60 + r, 620 + r), 250, 360,
               fill=p["accent"] + (18,), width=2)
    deco = deco.filter(ImageFilter.GaussianBlur(22))
    img.alpha_composite(deco)
    return img


def _arc(cx, cy, r, a0, a1, steps=10):
    pts = []
    for k in range(1, steps + 1):
        a = math.radians(a0 + (a1 - a0) * k / steps)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def _stroke_dashed(d, pts, color, width, dash=7.0, gap=4.5):
    width = max(1, int(round(width)))
    on, remain = True, dash
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        seg = math.hypot(x1 - x0, y1 - y0)
        if seg <= 0.01:
            continue
        t = 0.0
        while t < seg - 0.01:
            step = min(remain, seg - t)
            if on:
                a = (x0 + (x1 - x0) * t / seg, y0 + (y1 - y0) * t / seg)
                b = (x0 + (x1 - x0) * (t + step) / seg,
                     y0 + (y1 - y0) * (t + step) / seg)
                d.line([a, b], fill=color, width=width)
            t += step
            remain -= step
            if remain <= 0.01:
                on = not on
                remain = dash if on else gap


def dashed_round_rect(d, box, radius, color, width=2, dash=6.0, gap=4.0):
    x0, y0, x1, y1 = box
    r = min(radius, (x1 - x0) / 2 - 0.5, (y1 - y0) / 2 - 0.5)
    pts = [(x0 + r, y0), (x1 - r, y0)]
    pts += _arc(x1 - r, y0 + r, r, -90, 0)
    pts.append((x1, y1 - r))
    pts += _arc(x1 - r, y1 - r, r, 0, 90)
    pts.append((x0 + r, y1))
    pts += _arc(x0 + r, y1 - r, r, 90, 180)
    pts.append((x0, y0 + r))
    pts += _arc(x0 + r, y0 + r, r, 180, 270)
    pts.append((x0 + r, y0))
    _stroke_dashed(d, pts, color, width, dash, gap)


def rr(d, box, radius, **kw):
    b = tuple(int(round(v)) for v in box)
    r = int(round(min(radius, (b[2] - b[0]) / 2, (b[3] - b[1]) / 2)))
    if kw.get("width") is not None:
        kw["width"] = max(1, int(round(kw["width"])))
    d.rounded_rectangle(b, radius=r, **kw)
    return b


def pill(d, x, y, h, text, kind, size, fg, bg, padx=12, border=None):
    w = tw(text, kind, size) + padx * 2
    rr(d, (x, y, x + w, y + h), h / 2, fill=bg, outline=border, width=1)
    d.text((x + padx, y + h / 2 + 0.5), text, font=font(kind, size), fill=fg,
           anchor="lm")
    return w


_ASCII = re.compile(r"[A-Za-z0-9][A-Za-z0-9.,:;/%+\-]*")


def wrap_text(text: str, kind: str, size: int, max_w: float) -> list[str]:
    """Greedy wrap: CJK breaks anywhere, Latin stays on word boundaries."""
    units: list[str] = []
    i = 0
    while i < len(text):
        m = _ASCII.match(text, i)
        if m:
            units.append(m.group(0))
            i = m.end()
            continue
        if text[i] == " ":
            units.append(" ")
            i += 1
            continue
        units.append(text[i])
        i += 1
    lines: list[str] = []
    cur = ""
    for unit in units:
        candidate = cur + unit
        if cur and tw(candidate, kind, size) > max_w:
            lines.append(cur.rstrip())
            cur = "" if unit == " " else unit
        else:
            cur = candidate
    if cur.strip():
        lines.append(cur.rstrip())
    return lines


def draw_hero(lang: str, theme: str) -> Image.Image:
    t = HERO_TEXT[lang]
    p = HERO[theme]
    img = hero_bg(theme)

    # ---- banner card + left column ---------------------------------------
    card = (884, 56, 1392, 520)
    add_shadow(img, card, 22, dy=16, blur=28,
               alpha=44 if theme == "light" else 96, color=p["shadow"])
    d = ImageDraw.Draw(img)
    rr(d, card, 22, fill=p["card"], outline=p["border"], width=2)

    kicker = t["kicker"]
    kw = tw(kicker, "cjk", 19)
    check(f"hero/{lang}/{theme}/kicker", kicker, "cjk", 19, 700)
    rr(d, (64, 58, 64 + kw + 62, 96), 19, fill=p["pill"],
       outline=p["pill_border"], width=2)
    d.ellipse((79, 73, 86, 80), fill=p["accent"])
    d.text((96, 77), kicker, font=font("cjk", 19), fill=p["accent"],
           anchor="lm")

    title = t["title"]
    title_size = 79
    check(f"hero/{lang}/{theme}/title", title, "cjk_b", title_size, 812)
    while tw(title, "cjk_b", title_size) > 812 and title_size > 64:
        title_size -= 1
    check(f"hero/{lang}/{theme}/title-final", title, "cjk_b", title_size, 812)
    d.text((64, 202), title, font=font("cjk_b", title_size), fill=p["ink"],
           anchor="ls")

    for i, line in enumerate(t["value"]):
        check(f"hero/{lang}/{theme}/value{i}", line, "cjk_b", 40, 800)
        d.text((64, 276 + i * 50), line, font=font("cjk_b", 40), fill=p["ink"],
               anchor="ls")

    for i, line in enumerate(t["sub"]):
        check(f"hero/{lang}/{theme}/sub{i}", line, "cjk", 25, 800)
        d.text((64, 386 + i * 32), line, font=font("cjk", 25), fill=p["sub"],
               anchor="ls")

    check(f"hero/{lang}/{theme}/meta", t["meta"], "mono", 21, 800)
    d.text((64, 470), t["meta"], font=font("mono", 21), fill=p["faint"],
           anchor="ls")

    d.line((64, 496, 820, 496), fill=p["divider"], width=1)
    check(f"hero/{lang}/{theme}/footer", t["footer"], "cjk", 20, 780)
    d.text((64, 532), t["footer"], font=font("cjk", 20), fill=p["faint"],
           anchor="ls")

    # ---- right card: claim 1 as four element tiles ------------------------
    lx = 908
    check(f"hero/{lang}/{theme}/card-title", t["card_title"], "cjk_b", 20, 360)
    d.text((lx, 100), t["card_title"], font=font("cjk_b", 20), fill=p["ink"],
           anchor="ls")
    pf = font("cjk", 13)
    pw = tw(t["card_pill"], "cjk", 13) + 26
    rr(d, (1368 - pw, 82, 1368, 108), 13, fill=p["accent_soft"])
    d.text((1368 - pw / 2, 95.5), t["card_pill"], font=pf, fill=p["accent"],
           anchor="mm")
    check(f"hero/{lang}/{theme}/card-sub", t["card_sub"], "cjk", 15.5, 460)
    d.text((lx, 128), t["card_sub"], font=font("cjk", 15.5), fill=p["sub"],
           anchor="ls")
    d.line((lx, 144, 1368, 144), fill=p["divider"], width=1)

    tile_w, gap = 108, 9
    tile_top, tile_h = 160, 168
    for i, (rule, outcome, token, label, value, cls) in enumerate(TILES):
        x = lx + i * (tile_w + gap)
        accent = p["warn"] if cls == "warn" else p["accent"]
        rr(d, (x, tile_top, x + tile_w, tile_top + tile_h), 14,
           fill=p["tile"], outline=p["tile_edge"], width=1.4)
        check(f"hero/{lang}/{theme}/tile-token{i}", token, "mono", 11.5, 88)
        d.text((x + 10, tile_top + 18), token, font=font("mono", 11.5),
               fill=accent, anchor="ls")
        check(f"hero/{lang}/{theme}/tile-label{i}", label, "cjk_b", 13, 88)
        d.text((x + 10, tile_top + 38), label, font=font("cjk_b", 13),
               fill=p["ink"], anchor="ls")
        d.line((x + 10, tile_top + 46, x + tile_w - 10, tile_top + 46),
               fill=p["divider"], width=1)
        if value is None:
            box = (x + 10, tile_top + 56, x + tile_w - 10, tile_top + 118)
            dashed_round_rect(d, box, 9, p["warn"], width=1.6, dash=5, gap=4)
            d.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2 + 1),
                   t["empty"], font=font("cjk", 13), fill=p["warn"],
                   anchor="mm")
        else:
            lines = wrap_text(value, "cjk", 12, tile_w - 20)
            for j, line in enumerate(lines[:4]):
                check(f"hero/{lang}/{theme}/tile-value{i}-{j}", line, "cjk", 12,
                      tile_w - 18)
                d.text((x + 10, tile_top + 70 + j * 15), line,
                       font=font("cjk", 12), fill=p["ink"], anchor="ls")
        if cls == "warn":
            fg, bg = p["warn"], p["warn_soft"]
        else:
            fg, bg = p["ok"], p["ok_soft"]
        # Two lines, mirroring the chips mounted at the column feet in the
        # flow diagram: rule id on top, this run's outcome below.
        check(f"hero/{lang}/{theme}/tile-chip-rule{i}", rule, "mono", 12, 88)
        check(f"hero/{lang}/{theme}/tile-chip-out{i}", outcome, "cjk", 12, 88)
        rr(d, (x + 8, tile_top + tile_h - 38, x + tile_w - 8,
               tile_top + tile_h - 8), 10, fill=bg)
        d.text((x + tile_w / 2, tile_top + tile_h - 26), rule,
               font=font("mono", 12), fill=fg, anchor="mm")
        d.text((x + tile_w / 2, tile_top + tile_h - 14), outcome,
               font=font("cjk", 12), fill=fg, anchor="mm")

    check(f"hero/{lang}/{theme}/cond", t["cond"], "cjk", 12, 460)
    d.text((lx, 350), t["cond"], font=font("cjk", 12), fill=p["faint"],
           anchor="ls")

    slip = (lx, 372, 1368, 452)
    rr(d, slip, 14, fill=p["warn_soft"], outline=p["warn_border"], width=1.6)
    rr(d, (lx + 5, 380, lx + 10, 444), 2.5, fill=p["warn"])
    check(f"hero/{lang}/{theme}/slip1", t["slip1"], "mono", 13, 426)
    d.text((lx + 20, 392), t["slip1"], font=font("mono", 13), fill=p["warn"],
           anchor="ls")
    check(f"hero/{lang}/{theme}/slip2", t["slip2"], "cjk", 13.5, 426)
    d.text((lx + 20, 413), t["slip2"], font=font("cjk", 13.5),
           fill=p["warn_text"], anchor="ls")
    check(f"hero/{lang}/{theme}/slip3", t["slip3"], "cjk", 13, 426)
    d.text((lx + 20, 435), t["slip3"], font=font("cjk", 13),
           fill=p["warn_text"], anchor="ls")

    sx = lx
    for text, kind in t["summary"]:
        if kind == "warn":
            fg, bg = p["warn"], p["warn_soft"]
        elif kind == "accent":
            fg, bg = p["accent"], p["accent_soft"]
        else:
            fg, bg = p["mute_ink"], p["mute_bg"]
        w = pill(d, sx, 466, 24, text, "mono", 13.5, fg, bg, padx=11)
        sx += w + 7

    check(f"hero/{lang}/{theme}/source", t["source"], "cjk", 13, 500)
    d.text((884, 544), t["source"], font=font("cjk", 13), fill=p["faint"],
           anchor="ls")
    return img


# ---------------------------------------------------------------------------
# Flow (hand-written SVG): 1100 x 660
# ---------------------------------------------------------------------------
FW, FH = 1100, 660

FLOW = {
    "light": dict(
        bg1="#f9f6fd", bg2="#e4eaf8", card="#ffffff", border="#e3e1f0",
        ink="#171821", sub="#565b6b", faint="#8b8fa3",
        accent="#4B67B4", accent_soft="#ecebf9",
        band="#f7f4fc", band_edge="#eae6f4",
        warn="#B0530A", warn_soft="#FDF1E3", warn_border="#E6B87C",
        ok="#1F7A4A", ok_soft="#EAF7EF",
        line="#d8d6e6", spine="#c9c7dd",
        shadow="#1b1533", shadow_op="0.10",
    ),
    "dark": dict(
        bg1="#131a2a", bg2="#0c1016", card="#1a2233", border="#2b3650",
        ink="#e9edf9", sub="#9aa6c4", faint="#7c88a6",
        accent="#8496f5", accent_soft="#232c4a",
        band="#202839", band_edge="#2b3650",
        warn="#F0B45F", warn_soft="#342819", warn_border="#7A5B2D",
        ok="#6FD39A", ok_soft="#1C2F26",
        line="#2b3650", spine="#39456a",
        shadow="#000000", shadow_op="0.45",
    ),
}

# One register, seven read columns. The rule mounted on a column is the rule
# whose `check.kind` reads that field; PL-004 owns the amount -> deadline pair,
# PL-005 owns the header band. Outcomes are the quickstart run.
COLUMNS = [
    ("elementNo", "序号", "1", ("PL-006", "unique", "no diff · 1 row"), "mute"),
    ("claim", "诉讼请求", "判令被告支付货款本金人民币 1,250,000 元",
     ("PL-007", "containsAny", "no diff"), "mute"),
    ("fact", "事实依据", None, ("PL-001", "presence", "1 issue · row 1"), "warn"),
    ("evidence", "证据", "证1、证2、证3", ("PL-002", "presence", "no diff"), "mute"),
    ("law", "法律依据", "《中华人民共和国民法典》第五百七十七条",
     ("PL-003", "presence", "no diff"), "mute"),
    ("amount", "金额", "1250000", None, "mute"),
    ("deadline", "期限", "本判决生效之日起十日", None, "mute"),
]
PAIR_CHIP = ("PL-004", "conditionalPresence", "amount → deadline · no diff")

SANS_FAM = ("'Microsoft YaHei','PingFang SC','Noto Sans CJK SC',"
            "'Source Han Sans SC',sans-serif")
MONO_FAM = ("Consolas,'Cascadia Mono','SFMono-Regular','Menlo',"
            "ui-monospace,monospace")


class Svg:
    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self.body: list[str] = []

    def add(self, chunk: str) -> None:
        self.body.append(chunk)

    def text(self, x, y, s, size, fill, mono=True, bold=False,
             anchor="start", ls=None, opacity=None):
        attr = []
        if anchor != "start":
            attr.append(f'text-anchor="{anchor}"')
        if bold:
            attr.append('font-weight="700"')
        if ls is not None:
            attr.append(f'letter-spacing="{ls}"')
        if opacity is not None:
            attr.append(f'opacity="{opacity}"')
        fam = MONO_FAM if mono else SANS_FAM
        self.add(f'<text x="{x:g}" y="{y:g}" fill="{fill}" '
                 f'font-family="{fam}" font-size="{size:g}" '
                 f'{" ".join(attr)}>{escape(s)}</text>')

    def rrect(self, x, y, w, h, r, fill, stroke=None, sw=1.5, dash=None,
              extra=""):
        st = (f' stroke="{stroke}" stroke-width="{sw:g}"'
              if stroke else ' stroke="none"')
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" '
                 f'rx="{r:g}" fill="{fill}"{st}{da}{extra}/>')

    def line(self, x1, y1, x2, y2, stroke, sw=1.5, dash=None, cap="round"):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" '
                 f'stroke="{stroke}" stroke-width="{sw:g}" '
                 f'stroke-linecap="{cap}"{da}/>')

    def path(self, d, stroke, sw=1.5, fill="none", dash=None, cap="round"):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="{d}" stroke="{stroke}" stroke-width="{sw:g}" '
                 f'fill="{fill}" stroke-linecap="{cap}" '
                 f'stroke-linejoin="round"{da}/>')

    def render(self) -> str:
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" '
                f'height="{self.h}" viewBox="0 0 {self.w} {self.h}" '
                f'role="img" aria-label="{NAME} structure">\n'
                + "\n".join(self.body) + "\n</svg>\n")


def flow_svg(theme: str) -> str:
    p = FLOW[theme]
    s = Svg(FW, FH)
    s.add('<defs>'
          '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
          f'<stop offset="0" stop-color="{p["bg1"]}"/>'
          f'<stop offset="1" stop-color="{p["bg2"]}"/>'
          '</linearGradient>'
          '<filter id="sh" x="-10%" y="-14%" width="120%" height="134%">'
          f'<feDropShadow dx="0" dy="6" stdDeviation="8" '
          f'flood-color="{p["shadow"]}" flood-opacity="{p["shadow_op"]}"/>'
          '</filter>'
          '</defs>')
    s.add(f'<rect width="{FW}" height="{FH}" fill="url(#bg)"/>')

    def chk(name, text, size, mono, limit, bold=False):
        CHECKS.append((f"flow/{theme}/{name}",
                       mixed_w(text, size, mono, bold), limit))

    # ---- page header -----------------------------------------------------
    kicker = "ONE SHEET · SEVEN CHECKS · ROW + COLUMN"
    chk("kicker", kicker, 13, True, 720, True)
    s.text(44, 44, kicker, 13, p["accent"], bold=True, ls=1.1)
    chk("title", NAME, 27, True, 640, True)
    s.text(44, 78, NAME, 27, p["ink"], bold=True)
    sub = ("One element register, read column by column: a finding names the "
           "row, the column and the fix.")
    chk("sub", sub, 14.5, False, 760)
    s.text(44, 102, sub, 14.5, p["sub"], mono=False)
    meta1 = "rules/pleading-draft.yaml · pack 2026.1"
    meta2 = "pleading_draft · JSON | YAML · file | material"
    chk("meta1", meta1, 13, True, 330)
    chk("meta2", meta2, 13, True, 390)
    s.text(1056, 44, meta1, 13, p["faint"], anchor="end")
    s.text(1056, 66, meta2, 13, p["faint"], anchor="end")
    s.line(44, 120, 1056, 120, p["line"], 1.2)

    # ---- card ------------------------------------------------------------
    card = (44, 138, 1012, 466)
    s.add(f'<rect x="{card[0]}" y="{card[1]}" width="{card[2]}" '
          f'height="{card[3]}" rx="20" fill="{p["card"]}" filter="url(#sh)"/>')
    s.rrect(card[0], card[1], card[2], card[3], 20, "none", p["border"], 1.6)

    section = "MATERIAL · pleadings element register · read-only"
    chk("section", section, 13, True, 560, True)
    s.text(68, 166, section, 13, p["accent"], bold=True)
    legend = "chip = rule · check.kind · outcome"
    chk("legend", legend, 11.5, False, 300)
    s.text(1032, 166, legend, 11.5, p["faint"], mono=False, anchor="end")

    # ---- header band (PL-005 reads plaintiff + defendant) ----------------
    chips = [
        ("caseNo", "（2026）某民初 1234 号", 176),
        ("court", "某某人民法院", 128),
        ("plaintiff", "原告某某公司", 150),
        ("defendant", "被告某某公司", 150),
        ("cause", "买卖合同纠纷", 116),
    ]
    x = 68
    chip_pos: dict[str, tuple[float, float]] = {}
    for token, value, cw in chips:
        chk(f"hchk-{token}-token", token, 11, True, cw - 20)
        chk(f"hchk-{token}-value", value, 13, False, cw - 20)
        # The two fields PL-005 reads are tinted, so the clamp and the stamp
        # visibly belong to the same check.
        paired = token in ("plaintiff", "defendant")
        s.rrect(x, 178, cw, 38, 11,
                p["accent_soft"] if paired else p["band"],
                p["accent"] if paired else p["band_edge"],
                1.5 if paired else 1.3)
        s.text(x + 10, 193, token, 11, p["faint"])
        s.text(x + 10, 209, value, 13, p["ink"], mono=False)
        chip_pos[token] = (x, x + cw)
        x += cw + 6

    # dashed clamp under the pair PL-005 checks, tied to the header stamp
    pa, pb = chip_pos["plaintiff"], chip_pos["defendant"]
    cx0, cx1 = (pa[0] + pa[1]) / 2, (pb[0] + pb[1]) / 2
    s.path(f"M{cx0:g} 218 V222 H{cx1:g} V218", p["accent"], 1.6, dash="4 4")

    stamp = (830, 178, 202, 38)
    s.rrect(stamp[0], stamp[1], stamp[2], stamp[3], 11, p["ok_soft"],
            p["ok"], 1.3)
    chk("stamp-1", "PL-005 headerPresence", 11, True, 190)
    chk("stamp-2", "plaintiff + defendant · no diff", 11, False, 190)
    s.text(840, 193, "PL-005 headerPresence", 11, p["ok"])
    s.text(840, 209, "plaintiff + defendant · no diff", 11, p["ok"],
           mono=False)

    # ---- claim banner ----------------------------------------------------
    banner = "第 1 项诉请 · 请求要素 本金给付请求"
    chk("banner", banner, 15, False, 480, True)
    s.text(68, 258, banner, 15, p["ink"], mono=False, bold=True)
    note = "row 1 · rows[] · 1 · 撰写人 王律师"
    chk("banner-note", note, 11.5, False, 300)
    s.text(1032, 256, note, 11.5, p["faint"], mono=False, anchor="end")

    # ---- seven columns, seven mounted checks -----------------------------
    col_x0, col_gap = 68, 9
    col_top, col_h = 278, 230
    # The claim column carries the longest real value, the 序号 column the
    # shortest; widths follow the quickstart row rather than a fixed grid.
    col_widths = [106, 154, 130, 130, 130, 130, 130]
    xs: list[float] = []
    x = col_x0
    for cw in col_widths:
        xs.append(x)
        x += cw + col_gap

    for i, (token, label, value, chip, cls) in enumerate(COLUMNS):
        x, col_w = xs[i], col_widths[i]
        s.rrect(x, col_top, col_w, col_h, 13, p["band"], p["band_edge"], 1.2)
        chk(f"col-{token}-token", token, 11, True, col_w - 16)
        s.text(x + col_w / 2, 298, token, 11, p["accent"], anchor="middle")
        # Chinese column name standing vertically, as a ledger would set it.
        start = 342 - (len(label) - 1) * 8.5 + 5.5
        for j, ch in enumerate(label):
            chk(f"col-{token}-char{j}", ch, 14.5, False, col_w - 16, True)
            s.text(x + col_w / 2, start + j * 17, ch, 14.5, p["ink"],
                   mono=False, bold=True, anchor="middle")
        s.line(x + 14, 392, x + col_w - 14, 392, p["line"], 1.1)
        if value is None:
            s.rrect(x + 12, 402, col_w - 24, 46, 9, p["warn_soft"],
                    p["warn"], 1.4, dash="5 4")
            s.text(x + col_w / 2, 429, "（空）", 13, p["warn"], mono=False,
                   anchor="middle")
        else:
            lines = wrap_text(value, "cjk", 13, col_w - 22)
            for j, line in enumerate(lines[:4]):
                chk(f"col-{token}-line{j}", line, 13, False, col_w - 18)
                s.text(x + 11, 411 + j * 16, line, 13, p["ink"], mono=False)
        if chip is not None:
            rule, kind, outcome = chip
            cw = col_w - 12
            if cls == "warn":
                fg, bg, edge = p["warn"], p["warn_soft"], p["warn_border"]
            else:
                fg, bg, edge = p["ok"], p["ok_soft"], p["ok"]
            s.rrect(x + 6, 466, cw, 34, 9, bg, edge, 1.1)
            chk(f"col-{token}-chip1", f"{rule} {kind}", 11, True, cw - 6)
            chk(f"col-{token}-chip2", outcome, 11, False, cw - 6)
            s.text(x + 6 + cw / 2, 480, f"{rule} {kind}", 11, fg,
                   anchor="middle")
            s.text(x + 6 + cw / 2, 494, outcome, 11, fg, mono=False,
                   anchor="middle")

    # PL-004 spans amount + deadline; its chip is the only two-column mount.
    xa, wa = xs[5], col_widths[5]
    xd, wd = xs[6], col_widths[6]
    rule, kind, outcome = PAIR_CHIP
    pw = xd + wd - 6 - (xa + 6)
    s.rrect(xa + 6, 466, pw, 34, 9, p["ok_soft"], p["ok"], 1.1)
    chk("pair-chip1", f"{rule} {kind}", 11, True, pw - 6)
    chk("pair-chip2", outcome, 11, False, pw - 6)
    s.text(xa + 6 + pw / 2, 480, f"{rule} {kind}", 11, p["ok"],
           anchor="middle")
    s.text(xa + 6 + pw / 2, 494, outcome, 11, p["ok"], mono=False,
           anchor="middle")
    # A thin tie between the two column feet makes the pair explicit.
    s.path(f"M{xa + wa / 2:g} 456 H{xd + wd / 2:g}", p["spine"], 1.2,
           dash="3 4")

    # ---- report bar ------------------------------------------------------
    bar = (68, 520, 964, 66)
    s.rrect(bar[0], bar[1], bar[2], bar[3], 14, p["band"], p["band_edge"], 1.2)
    s.text(84, 541, "REPORT", 12.5, p["accent"], bold=True)
    chk("report-sub", "buildView", 11, True, 70)
    s.text(84, 560, "buildView", 11, p["faint"])

    pa_text, pb_text = "issues[] · 1", "skipped[] · 0"
    w1 = mixed_w(pa_text, 11.5) + 20
    w2 = mixed_w(pb_text, 11.5) + 20
    chk("pill-a", pa_text, 11.5, True, 150)
    chk("pill-b", pb_text, 11.5, True, 150)
    s.rrect(190, 529, w1, 22, 11, p["warn_soft"], p["warn_border"], 1.1)
    s.text(190 + w1 / 2, 544, pa_text, 11.5, p["warn"], anchor="middle")
    s.rrect(190 + w1 + 10, 529, w2, 22, 11, p["accent_soft"], p["accent"], 1.1)
    s.text(190 + w1 + 10 + w2 / 2, 544, pb_text, 11.5, p["accent"],
           anchor="middle")

    ax0 = 190 + w1 + 10 + w2 + 8
    ax1 = ax0 + 22
    s.path(f"M{ax0:g} 540 H{ax1 - 6:g}", p["spine"], 1.3)
    s.add(f'<path d="M{ax1 - 8:g} 534 l8 6 -8 6 z" fill="{p["spine"]}"/>')
    out_text = "markdown · reportJson"
    ow = mixed_w(out_text, 11.5) + 22
    s.rrect(ax1 + 4, 529, ow, 22, 11, p["card"], p["border"], 1.1)
    chk("out-pill", out_text, 11.5, True, 200)
    s.text(ax1 + 4 + ow / 2, 544, out_text, 11.5, p["ink"], anchor="middle")

    finding = ("PL-001 · warn · row 1 · column fact · found 第 1 行「fact」为空"
               " · fix 补填事实依据")
    chk("finding", finding, 11.5, True, 620)
    s.text(190, 570, finding, 11.5, p["sub"])

    summary = "error 0 · warn 1 · info 0"
    chk("summary", summary, 12, True, 240)
    s.text(1016, 541, summary, 12, p["faint"], anchor="end")
    tail = "skipped 0 is not a pass · no verdict"
    chk("tail", tail, 11.5, False, 300)
    s.text(1016, 562, tail, 11.5, p["sub"], mono=False, anchor="end")

    # ---- footer ----------------------------------------------------------
    foot1 = ("excerpt verbatim (≥ 8 chars) · kind caps severity · "
             "skipped is never a pass")
    foot2 = "7 rules · all warn · 4 direct / 3 derived-from-principle"
    chk("foot1", foot1, 12, False, 600)
    chk("foot2", foot2, 12, False, 380)
    s.text(44, 630, foot1, 12, p["faint"], mono=False)
    s.text(1056, 630, foot2, 12, p["faint"], mono=False, anchor="end")

    return s.render()


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    written: list[str] = []

    for theme in ("light", "dark"):
        svg = flow_svg(theme)
        path = os.path.join(OUT, f"{NAME}-flow-v5-{theme}.svg")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(svg)
        written.append(path)

    for lang in ("zh", "en"):
        for theme in ("light", "dark"):
            img = draw_hero(lang, theme)
            path = os.path.join(OUT, f"{NAME}-hero-{lang}-{theme}.webp")
            img.convert("RGB").save(path, "WEBP", quality=92, method=6)
            written.append(path)

    bad = [c for c in CHECKS if c[1] > c[2] + 0.01]
    if bad:
        print("layout overflow (text wider than its box):")
        for name, width, limit in bad:
            print(f"  - {name}: {width:.1f} > {limit:.1f}")
        return 1

    print(f"layout checks: {len(CHECKS)} text boxes fit")
    for path in written:
        print(f"wrote {os.path.relpath(path, ROOT)} "
              f"({os.path.getsize(path)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
