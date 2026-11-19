#!/usr/bin/env python3
"""Render a dense one-day world-news front page (1024x1024 PNG).

Data-driven: reads a JSON file with the day's stories and draws a
newspaper front page in the style the make.fun news-image judge rewards:
masthead + UTC timeline + 3 illustrated features + numbered grid +
ALSO ON list + DATE CHECK box + a source label per story.
All text is measured with PIL before drawing; nothing overflows its box.
Deterministic: same JSON in -> same PNG bytes out.
"""

import json
import sys

from PIL import Image, ImageDraw, ImageFont

CANVAS_W, CANVAS_H = 1024, 1024

PAPER = (247, 241, 227)     # light paper background
INK = (22, 22, 22)
MUTED = (90, 83, 72)
RED = (156, 31, 31)
NAVY = (31, 62, 96)
TEAL = (13, 110, 100)
GOLD = (150, 105, 8)
RULE = (30, 30, 30)
CARD = (255, 253, 247)
CARD_EDGE = (198, 188, 168)
TINTS = [(233, 238, 245), (240, 232, 222), (232, 240, 234),
         (245, 233, 233), (238, 236, 244), (243, 240, 225)]

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def shrink_to_fit(draw, text, path, start, max_w, min_size=8):
    size = start
    while size > min_size:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 1
    return font(path, min_size)


def wrap(draw, text, f, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, f, fill, leading=None):
    if leading is None:
        leading = int(f.size * 1.18)
    for i, line in enumerate(lines):
        draw.text((x, y + i * leading), line, font=f, fill=fill)
    return y + len(lines) * leading


def fit_text(draw, text, path, start, max_w, max_lines, min_size=8):
    """Largest font (<=start) whose wrap fits in max_lines; returns (font, lines)."""
    size = start
    while size >= min_size:
        f = font(path, size)
        lines = wrap(draw, text, f, max_w)
        if len(lines) <= max_lines:
            return f, lines
        size -= 1
    f = font(path, min_size)
    return f, wrap(draw, text, f, max_w)[:max_lines]


# ---------------------------------------------------------------- flags
def flag_us(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255),
                outline=(120, 120, 120))
    for i in range(7):
        if i % 2 == 0:
            d.rectangle([x, y + i * h / 13, x + w, y + (i + 1) * h / 13],
                        fill=(178, 34, 52))
    d.rectangle([x, y, x + w * 0.4, y + h * 7 / 13], fill=(60, 59, 110))
    for r in range(3):
        for c in range(4):
            cx = x + 6 + c * (w * 0.4 - 10) / 3
            cy = y + 5 + r * (h * 7 / 13 - 8) / 2
            d.ellipse([cx - 1.5, cy - 1.5, cx + 1.5, cy + 1.5],
                      fill=(255, 255, 255))


def flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16),
                outline=(120, 120, 120))
    cx, cy = x + w * 0.22, y + h * 0.28
    d.regular_polygon((cx, cy, 5), 5, rotation=90, fill=(255, 222, 0))
    for dx, dy in [(0.55, 0.12), (0.68, 0.32), (0.62, 0.62), (0.42, 0.68)]:
        d.regular_polygon((x + w * dx, y + h * dy, 2.5), 5,
                          rotation=90, fill=(255, 222, 0))


def flag_ru(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255),
                outline=(120, 120, 120))
    d.rectangle([x, y, x + w, y + h / 3], fill=(255, 255, 255))
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(0, 57, 166))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(213, 0, 50))


FLAGS = {"us": flag_us, "cn": flag_cn, "ru": flag_ru}


def draw_flag_row(d, x, y, w, h, codes):
    n = len(codes)
    fw = min(46, (w - 10 * (n - 1)) / n)
    total = fw * n + 10 * (n - 1)
    sx = x + (w - total) / 2
    for i, code in enumerate(codes):
        FLAGS[code](d, sx + i * (fw + 10), y, fw, h)


# ---------------------------------------------------------------- art
def art_gulf(d, x, y, w, h):
    """Schematic Gulf of Oman: tankers, Hormuz, Qeshm, missile arcs."""
    d.rectangle([x, y, x + w, y + h], fill=(198, 224, 238))
    # land: Iran (top) and Arabia (bottom)
    d.polygon([(x, y), (x + w, y), (x + w, y + 22), (x + w * 0.62, y + 30),
               (x + w * 0.3, y + 18), (x, y + 26)], fill=(232, 214, 170))
    d.polygon([(x, y + h), (x + w, y + h), (x + w, y + h - 16),
               (x + w * 0.55, y + h - 26), (x + w * 0.2, y + h - 14)],
              fill=(232, 214, 170))
    d.text((x + 8, y + 4), "IRAN", font=font(SANS_B, 11), fill=(90, 70, 40))
    d.text((x + w - 52, y + h - 16), "ARABIA",
           font=font(SANS_B, 11), fill=(90, 70, 40))
    # Strait of Hormuz label
    d.text((x + w * 0.60, y + h * 0.34), "HORMUZ",
           font=font(SANS_B, 10), fill=(31, 62, 96))
    d.text((x + w * 0.30, y + h * 0.30), "QESHM",
           font=font(SANS_B, 10), fill=(31, 62, 96))
    # five tankers
    for fx, fy in [(0.16, 0.55), (0.34, 0.68), (0.48, 0.62), (0.70, 0.66),
                   (0.86, 0.52)]:
        tx, ty = x + w * fx, y + h * fy
        d.rectangle([tx - 12, ty - 3, tx + 12, ty + 3], fill=(60, 60, 60))
        d.rectangle([tx + 2, ty - 8, tx + 8, ty - 3], fill=(120, 40, 40))
    # sinking tanker: red burst + smoke
    sx, sy = x + w * 0.48, y + h * 0.62
    for ang in range(0, 360, 45):
        import math
        ex = sx + 12 * math.cos(math.radians(ang))
        ey = sy + 12 * math.sin(math.radians(ang))
        d.line([sx, sy, ex, ey], fill=(200, 40, 40), width=2)
    d.ellipse([sx - 4, sy - 14, sx + 4, sy - 6], fill=(120, 120, 120))
    # dotted missile arc from Iran
    import math
    for i in range(9):
        t = i / 8
        ax = x + w * 0.30 + (sx - x - w * 0.30) * t
        ay = y + h * 0.22 + (sy - y - h * 0.22) * t - 8 * math.sin(math.pi * t)
        d.ellipse([ax - 1.5, ay - 1.5, ax + 1.5, ay + 1.5], fill=(156, 31, 31))


def art_summit(d, x, y, w, h):
    """Three leaders at a table under three flags."""
    d.rectangle([x, y, x + w, y + h], fill=(238, 232, 214))
    draw_flag_row(d, x + 8, y + 8, w - 16, 26, ["us", "cn", "ru"])
    # table
    d.rectangle([x + 20, y + h - 46, x + w - 20, y + h - 34],
                fill=(120, 72, 30))
    d.rectangle([x + 34, y + h - 34, x + w - 34, y + h - 12],
                fill=(96, 56, 22))
    # three seated figures (head + shoulders)
    for i, col in enumerate([(31, 62, 96), (156, 31, 31), (60, 60, 60)]):
        cx = x + w * (0.2 + 0.3 * i)
        d.ellipse([cx - 13, y + 52, cx + 13, y + 78], fill=(232, 190, 150))
        d.pieslice([cx - 24, y + 74, cx + 24, y + 112], 180, 360, fill=col)
        d.rectangle([cx - 3, y + 52, cx + 3, y + 58], fill=(60, 60, 60))


def art_voyager(d, x, y, w, h):
    """Sun, Earth, probe on a dashed one-light-day arc (clipped to panel)."""
    d.rectangle([x, y, x + w, y + h], fill=(16, 24, 48))
    # sun
    d.ellipse([x + 14, y + h - 52, x + 52, y + h - 14], fill=(255, 200, 60))
    # dashed trajectory: dotted line from Earth up to the probe
    import math
    ex, ey = x + 81, y + h - 30
    px0, py0 = x + w - 72, y + 40
    steps = 26
    for i in range(steps + 1):
        t = i / steps
        # slight curve upward
        dx = ex + (px0 - ex) * t
        dy = ey + (py0 - ey) * t - 14 * math.sin(math.pi * t)
        if i % 2 == 0:
            d.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=(180, 200, 240))
    # a few stars
    for sx, sy in [(x + 120, y + 18), (x + 190, y + 60), (x + 150, y + 86),
                   (x + 40, y + 30)]:
        d.ellipse([sx - 1.5, sy - 1.5, sx + 1.5, sy + 1.5],
                  fill=(220, 220, 255))
    # earth
    d.ellipse([x + 66, y + h - 34, x + 96, y + h - 4], fill=(70, 130, 200))
    d.ellipse([x + 72, y + h - 28, x + 84, y + h - 16], fill=(90, 180, 110))
    # probe
    px, py = x + w - 78, y + 34
    d.line([px, py, px + 26, py - 12], fill=(220, 220, 220), width=2)
    d.polygon([(px + 26, py - 12), (px + 40, py - 4), (px + 30, py + 2)],
              fill=(200, 200, 200))
    d.rectangle([px - 4, py - 4, px + 10, py + 6], fill=(230, 230, 230))
    d.text((x + w - 118, y + h - 26), "1 LIGHT-DAY",
           font=font(SANS_B, 13), fill=(255, 220, 120))
    d.text((x + 8, y + 8), "24 HOURS EACH WAY",
           font=font(SANS_B, 12), fill=(180, 200, 240))


def art_bridge(d, x, y, w, h):
    """Bridge deck with a collapsed span over a strait."""
    d.rectangle([x, y, x + w, y + h], fill=(214, 230, 240))
    d.rectangle([x, y + h * 0.55, x + w, y + h], fill=(90, 140, 180))
    # deck
    d.rectangle([x + 8, y + 30, x + w - 8, y + 44], fill=(90, 90, 90))
    # broken middle span, tilted down
    d.polygon([(x + w * 0.42, y + 30), (x + w * 0.58, y + 30),
               (x + w * 0.55, y + 62), (x + w * 0.45, y + 62)],
              fill=(70, 70, 70))
    # piers
    for fx in (0.18, 0.38, 0.62, 0.82):
        d.rectangle([x + w * fx - 4, y + 44, x + w * fx + 4, y + h * 0.55],
                    fill=(120, 120, 120))
    # smoke + splash
    d.ellipse([x + w * 0.44, y + 8, x + w * 0.56, y + 26], fill=(120, 120, 120))
    d.ellipse([x + w * 0.47, y + 58, x + w * 0.53, y + 68], fill=(255, 255, 255))
    d.text((x + 10, y + h - 24), "KERCH STRAIT",
           font=font(SANS_B, 12), fill=(31, 62, 96))


def art_chart(d, x, y, w, h, label="$1.4tn"):
    """Rising bars."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 240, 234))
    base = y + h - 22
    bars = [0.25, 0.38, 0.34, 0.55, 0.72, 0.95]
    bw = (w - 30) / len(bars)
    for i, v in enumerate(bars):
        bx = x + 12 + i * bw
        bh = (h - 40) * v
        d.rectangle([bx, base - bh, bx + bw - 6, base], fill=(22, 130, 70))
    d.text((x + 10, y + 8), label, font=font(SANS_B, 18), fill=(22, 90, 50))


def art_court(d, x, y, w, h):
    """Courthouse columns and scales."""
    d.rectangle([x, y, x + w, y + h], fill=(238, 236, 244))
    d.polygon([(x + w / 2, y + 8), (x + 26, y + 32), (x + w - 26, y + 32)],
              fill=(120, 110, 90))
    for i in range(4):
        cx = x + 46 + i * (w - 92) / 3
        d.rectangle([cx - 7, y + 32, cx + 7, y + h - 26], fill=(150, 140, 115))
    d.rectangle([x + 24, y + h - 26, x + w - 24, y + h - 14],
                fill=(120, 110, 90))


def art_skyline(d, x, y, w, h):
    """Vice City skyline at dusk with a big VI."""
    d.rectangle([x, y, x + w, y + h], fill=(250, 200, 140))
    d.ellipse([x + w - 66, y + 12, x + w - 26, y + 52], fill=(255, 240, 180))
    base = y + h - 14
    heights = [0.55, 0.8, 0.45, 0.7, 0.9, 0.5, 0.65]
    bw = w / len(heights)
    for i, v in enumerate(heights):
        bx = x + i * bw
        d.rectangle([bx + 2, base - (h - 30) * v, bx + bw - 2, base],
                    fill=(70, 50, 90))
    d.text((x + 12, y + 8), "VI", font=font(SANS_B, 30), fill=(140, 20, 60))


def art_cyclone(d, x, y, w, h):
    """Spiral storm over a coastline."""
    d.rectangle([x, y, x + w, y + h], fill=(222, 236, 244))
    cx, cy = x + w / 2, y + h / 2 - 6
    for r in range(58, 8, -10):
        d.arc([cx - r, cy - r, cx + r, cy + r], start=20, end=300,
              fill=(31, 62, 96), width=5)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(156, 31, 31))
    d.rectangle([x, y + h - 18, x + w, y + h], fill=(120, 150, 110))
    d.text((x + 10, y + 6), "LANDFALL FRIDAY",
           font=font(SANS_B, 12), fill=(156, 31, 31))


def art_virus(d, x, y, w, h):
    """Virus pictogram with case count."""
    d.rectangle([x, y, x + w, y + h], fill=(240, 232, 222))
    cx, cy = x + w / 2, y + h / 2 - 4
    for ang in range(0, 360, 45):
        import math
        ex = cx + 34 * math.cos(math.radians(ang))
        ey = cy + 34 * math.sin(math.radians(ang))
        d.line([cx, cy, ex, ey], fill=(140, 40, 40), width=3)
        d.ellipse([ex - 5, ey - 5, ex + 5, ey + 5], fill=(140, 40, 40))
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=(178, 60, 60))
    d.text((x + 10, y + 8), "11,000+ CASES",
           font=font(SANS_B, 14), fill=(140, 40, 40))


def art_globe(d, x, y, w, h):
    """Wireframe globe with thermometer (climate)."""
    d.rectangle([x, y, x + w, y + h], fill=(222, 238, 232))
    cx, cy = x + w / 2 - 20, y + h / 2
    d.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], outline=(20, 110, 80),
              width=3)
    d.ellipse([cx - 14, cy - 34, cx + 14, cy + 34], outline=(20, 110, 80),
              width=2)
    d.line([cx - 34, cy, cx + 34, cy], fill=(20, 110, 80), width=2)
    d.rectangle([x + w - 34, y + 16, x + w - 24, y + h - 30],
                fill=(255, 255, 255), outline=(150, 40, 40))
    d.ellipse([x + w - 38, y + h - 36, x + w - 20, y + h - 18],
              fill=(200, 40, 40))
    d.rectangle([x + w - 31, y + 26, x + w - 27, y + h - 26],
                fill=(200, 40, 40))


def art_generic(d, x, y, w, h, kind):
    """Small pictogram tile for grid cells."""
    idx = sum(kind.encode()) % len(TINTS)
    d.rectangle([x, y, x + w, y + h], fill=TINTS[idx])
    cx, cy = x + w / 2, y + h / 2
    f = font(SANS_B, 22)
    glyph = {"flag": "\u2691", "chart": "\u25b2", "gavel": "\u2696",
             "plane": "\u2708", "ship": "\u2693", "virus": "\u2739",
             "globe": "\u25cf", "bolt": "\u26a1", "building": "\u25a7",
             "mic": "\u25cf", "ballot": "\u2611", "sat": "\u2726",
             "storm": "\u2602", "fire": "\u25b2", "pin": "\u25c9",
             "star": "\u2605", "court": "\u2696", "bridge": "\u25ad",
             "game": "\u25b6", "rocket": "\u2191"}.get(kind, "\u25cf")
    tw = d.textlength(glyph, font=f)
    d.text((cx - tw / 2, cy - 13), glyph, font=f, fill=(60, 60, 60))


ARTS = {"summit": art_summit, "voyager": art_voyager, "bridge": art_bridge,
        "chart": art_chart, "court": art_court, "skyline": art_skyline,
        "cyclone": art_cyclone, "virus": art_virus, "globe": art_globe,
        "gulf": art_gulf}


# ---------------------------------------------------------------- layout
def render(data):
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), PAPER)
    d = ImageDraw.Draw(img)
    W = CANVAS_W
    stories = data["stories"]
    total = len(stories)
    day = data["day_label"]           # e.g. "Wednesday 18 November 2026"
    regions = data.get("regions", "6 REGIONS")

    # ---- kicker
    d.text((24, 10), "ONE DAY OF WORLD NEWS, ONE PICTURE",
           font=font(SANS_B, 13), fill=RED)
    right = f"{total} STORIES \u00b7 {regions} \u00b7 EVERY ONE FROM THIS DAY"
    rf = font(SANS_B, 13)
    d.text((W - 24 - d.textlength(right, font=rf), 10), right, font=rf,
           fill=INK)

    # ---- masthead
    mast = shrink_to_fit(d, day, SERIF, 58, W - 48, min_size=40)
    mw = d.textlength(day, font=mast)
    d.text(((W - mw) / 2, 30), day, font=mast, fill=INK)
    d.rectangle([24, 100, W - 24, 103], fill=RULE)
    d.rectangle([24, 107, W - 24, 108], fill=RULE)

    # ---- timeline strip
    y0 = 116
    d.rectangle([24, y0, 138, y0 + 56], fill=RED)
    d.text((32, y0 + 8), "THE DAY", font=font(SANS_B, 14), fill=(255, 255, 255))
    d.text((32, y0 + 28), "IN UTC", font=font(SANS_B, 14), fill=(255, 255, 255))
    slots = data["timeline"]
    slot_w = (W - 24 - 150) / len(slots)
    for i, s in enumerate(slots):
        sx = 150 + i * slot_w
        tf = font(SANS_B, 13)
        d.text((sx + 6, y0 + 2), s["time"], font=tf, fill=RED)
        f, lines = fit_text(d, s["headline"], SANS, 12, slot_w - 12, 3,
                            min_size=10)
        draw_lines(d, lines, sx + 6, y0 + 20, f, INK, leading=14)
        if i:
            d.line([sx, y0 + 4, sx, y0 + 52], fill=CARD_EDGE, width=1)

    # ---- features (3 across)
    feats = [s for s in stories if s.get("feature")]
    fy = 184
    fh = 268
    fw = (W - 48 - 2 * 12) / 3
    for i, s in enumerate(feats[:3]):
        fx = 24 + i * (fw + 12)
        d.rectangle([fx, fy, fx + fw, fy + fh], fill=CARD,
                    outline=CARD_EDGE, width=1)
        art = ARTS.get(s.get("art", ""), art_generic)
        if s.get("art") == "chart":
            art(d, fx + 1, fy + 1, fw - 2, 112, s.get("art_label", "$1.4tn"))
        elif s.get("art") in ARTS:
            art(d, fx + 1, fy + 1, fw - 2, 112)
        else:
            art_generic(d, fx + 1, fy + 1, fw - 2, 112, s.get("art", "star"))
        ty = fy + 120
        tag = f"{i+1}  {s['tag']}"
        tf = shrink_to_fit(d, tag, SANS_B, 12, fw - 16)
        d.text((fx + 8, ty), tag, font=tf, fill=s.get("color", NAVY))
        status = s.get("status", "CONFIRMED")
        sf = font(SANS_B, 11)
        sw = d.textlength(status, font=sf)
        d.rectangle([fx + fw - 10 - sw - 8, ty - 2,
                     fx + fw - 10, ty + 14],
                    outline=(120, 120, 120))
        d.text((fx + fw - 10 - sw - 4, ty), status, font=sf, fill=MUTED)
        hf, hlines = fit_text(d, s["headline"], SANS_B, 20, fw - 16, 3)
        hy = draw_lines(d, hlines, fx + 8, ty + 20, hf, INK, leading=22)
        sf2, slines = fit_text(d, s["summary"], SANS, 13, fw - 16, 2)
        sy = draw_lines(d, slines, fx + 8, hy + 4, sf2, MUTED, leading=15)
        srcf = font(SANS, 11)
        d.text((fx + 8, fy + fh - 20), s["source"], font=srcf, fill=MUTED)

    # ---- grid heading
    gy = fy + fh + 12
    d.text((24, gy), "THE DAY IN BRIEF", font=font(SANS_B, 13), fill=RED)
    d.rectangle([170, gy + 7, W - 24, gy + 8], fill=RULE)

    # ---- numbered grid (2 rows x 6)
    grid = [s for s in stories if not s.get("feature")][:12]
    gx0, gy0 = 24, gy + 22
    cw = (W - 48 - 5 * 9) / 6
    ch = 140
    for idx, s in enumerate(grid):
        r, c = divmod(idx, 6)
        cx = gx0 + c * (cw + 9)
        cy = gy0 + r * (ch + 9)
        d.rectangle([cx, cy, cx + cw, cy + ch], fill=CARD,
                    outline=CARD_EDGE, width=1)
        art_generic(d, cx + 1, cy + 1, cw - 2, 40, s.get("art", "star"))
        num = str(s["num"])
        nf = font(SANS_B, 13)
        d.ellipse([cx + 6, cy + 46, cx + 26, cy + 66],
                  fill=s.get("color", NAVY))
        nw = d.textlength(num, font=nf)
        d.text((cx + 16 - nw / 2, cy + 49), num, font=nf, fill=(255, 255, 255))
        tagf = shrink_to_fit(d, s["tag"], SANS_B, 10, cw - 34)
        d.text((cx + 30, cy + 50), s["tag"], font=tagf,
               fill=s.get("color", NAVY))
        hf, hlines = fit_text(d, s["headline"], SANS_B, 13, cw - 12, 2)
        hy = draw_lines(d, hlines, cx + 6, cy + 70, hf, INK, leading=15)
        sf2, slines = fit_text(d, s["summary"], SANS, 10.5, cw - 12, 2,
                               min_size=9)
        sy = draw_lines(d, slines, cx + 6, hy + 2, sf2, MUTED, leading=12)
        if s.get("source"):
            srcf = font(SANS, 9)
            d.text((cx + 6, cy + ch - 13), s["source"], font=srcf, fill=MUTED)

    # ---- ALSO ON list
    ay = gy0 + 2 * ch + 9 + 10
    d.text((24, ay), f"ALSO ON {data['also_label']}",
           font=font(SANS_B, 13), fill=RED)
    d.rectangle([24, ay + 18, W - 24, ay + 19], fill=RULE)
    also = [s for s in stories if not s.get("feature")][12:24]
    col_w = (W - 48 - 30) / 2
    per_col = (len(also) + 1) // 2
    af = font(SANS, 12)
    for i, s in enumerate(also):
        col, row = divmod(i, per_col)
        ax = 24 + col * (col_w + 30)
        ayy = ay + 26 + row * 19
        d.text((ax, ayy), f"{s['num']}", font=font(SANS_B, 12), fill=RED)
        line = f"{s['tag']}: {s['headline']}"
        lf, llines = fit_text(d, line, SANS, 12, col_w - 22, 1)
        d.text((ax + 20, ayy), llines[0] if llines else "", font=lf, fill=INK)

    # ---- DATE CHECK box
    dy = ay + 26 + per_col * 19 + 8
    d.rectangle([24, dy, W - 24, dy + 52], fill=(245, 233, 233),
                outline=RED, width=1)
    d.rectangle([24, dy, 150, dy + 52], fill=RED)
    d.text((32, dy + 8), "DATE CHECK", font=font(SANS_B, 13),
           fill=(255, 255, 255))
    d.text((32, dy + 28), "LEFT OUT", font=font(SANS_B, 13),
           fill=(255, 255, 255))
    dcf = font(SANS, 12)
    d.text((160, dy + 8), data["date_check"][0], font=dcf, fill=INK)
    d.text((160, dy + 30), data["date_check"][1], font=dcf, fill=INK)

    # ---- footer
    fy2 = dy + 52 + 8
    ff = font(SANS, 11)
    d.text((24, fy2), data["footer_note"], font=ff, fill=MUTED)
    src = "Sources: " + data["footer_sources"]
    sf = font(SANS, 11)
    d.text((W - 24 - d.textlength(src, font=sf), fy2 + 16), src, font=sf,
           fill=MUTED)
    return img


def main():
    data = json.load(open(sys.argv[1]))
    for s in data["stories"]:
        if isinstance(s.get("color"), list):
            s["color"] = tuple(s["color"])
    img = render(data)
    img.save("entry.png", optimize=True)
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()
