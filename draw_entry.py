#!/usr/bin/env python3
"""Render the 19 November 2026 world-news infographic (1024x1024).

Layout, top to bottom: a navy header with a gold globe and the title,
six story cards (numbered, colour-coded by category), and a one-line
sources footer. All text is measured with PIL before drawing so nothing
overflows its card.
"""

from PIL import Image, ImageDraw, ImageFont

CANVAS_W, CANVAS_H = 1024, 1024

NAVY = (11, 31, 58)          # header background
GOLD = (212, 160, 23)        # globe lines + header kicker
GOLD_LIGHT = (232, 193, 90)  # header kicker text
WHITE = (255, 255, 255)
INK = (17, 24, 39)           # headline colour
BODY = (55, 65, 81)          # summary text colour
MUTED = (107, 114, 128)      # footer colour
CARD_BG = (244, 246, 248)    # card background
CARD_EDGE = (216, 222, 230)  # card border
PANEL_BG = (255, 255, 255)   # left panel inside each card

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# (number, label, accent colour, headline, summary line 1, summary line 2)
STORIES = [
    (1, "DIPLOMACY", (31, 111, 235),
     "Trump, Xi and Putin meet in Shenzhen",
     "The three leaders gather for a first-ever trilateral summit,",
     "with nuclear arms and Iran on the agenda."),
    (2, "JUSTICE", (124, 58, 237),
     "World court rules on Myanmar genocide",
     "The ICJ delivers its final verdict on whether Myanmar",
     "committed genocide against the Rohingya."),
    (3, "MARKETS", (22, 163, 74),
     "Anthropic makes $1.4tn market debut",
     "The Claude-maker begins trading on Nasdaq, valued at up",
     "to $1.4 trillion in its blockbuster debut."),
    (4, "UKRAINE", (220, 38, 38),
     "Crimean Bridge hit for a third time",
     "Traffic halts after a fresh strike on the Kerch bridge,",
     "days after its road deck fell into the strait."),
    (5, "CULTURE", (234, 88, 12),
     "GTA VI launches after 13-year wait",
     "Rockstar's sequel unlocks at midnight around the world,",
     "returning players to Vice City at $79.99."),
    (6, "WEATHER", (13, 148, 136),
     "Cyclone Akvan bears down on India",
     "The severe storm nears Andhra Pradesh and Odisha;",
     "red alerts, schools shut, landfall due Friday."),
]

FOOTER = "Sources: Reuters, AP, BBC, NYT, Motley Fool, IMD \u2014 19 Nov 2026"


def load_font(path, size):
    return ImageFont.truetype(path, size)


def shrink_to_fit(draw, text, path, start_size, max_width, min_size=10):
    """Return the largest font (starting at start_size) that fits max_width."""
    size = start_size
    while size > min_size:
        font = load_font(path, size)
        if draw.textlength(text, font=font) <= max_width:
            return font
        size -= 1
    return load_font(path, min_size)


def draw_globe(draw, cx, cy, radius):
    """Gold wireframe globe: outer ring, one meridian, two latitude arcs."""
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                 outline=GOLD, width=4)
    # Meridian: tall narrow ellipse.
    narrow = radius * 0.42
    draw.ellipse([cx - narrow, cy - radius, cx + narrow, cy + radius],
                 outline=GOLD, width=3)
    # Equator: straight line across the middle.
    draw.line([cx - radius, cy, cx + radius, cy], fill=GOLD, width=3)
    # Latitude arcs above and below the equator.
    for sign in (-1, 1):
        y_off = radius * 0.55
        half = radius * 0.82
        box = [cx - half, cy + sign * y_off - 14,
               cx + half, cy + sign * y_off + 14]
        draw.arc(box, start=180 if sign < 0 else 0,
                 end=360 if sign < 0 else 180, fill=GOLD, width=3)


def draw_header(draw):
    draw.rectangle([0, 0, CANVAS_W, 150], fill=NAVY)
    draw_globe(draw, 78, 75, 46)
    title_font = load_font(FONT_BOLD, 58)
    draw.text((140, 14), "WORLD NEWS", font=title_font, fill=WHITE)
    date_font = load_font(FONT_REG, 26)
    draw.text((142, 82), "Thursday, 19 November 2026",
              font=date_font, fill=WHITE)
    kick_font = load_font(FONT_BOLD, 20)
    draw.text((142, 116), "THE DAY IN SIX STORIES",
              font=kick_font, fill=GOLD_LIGHT)


def draw_card(draw, top, number, label, accent, headline, line1, line2):
    left, right = 24, CANVAS_W - 24
    height = 124
    bottom = top + height
    # Card body: pale fill, thin border, rounded corners.
    draw.rounded_rectangle([left, top, right, bottom], radius=14,
                           fill=CARD_BG, outline=CARD_EDGE, width=1)
    # White left panel holding the number badge and the category label.
    panel_w = 158
    draw.rounded_rectangle([left + 7, top + 7, left + 7 + panel_w, bottom - 7],
                           radius=10, fill=PANEL_BG)
    # Number badge: filled circle with the story number in white.
    badge_cx = left + 7 + panel_w // 2
    badge_cy = top + 44
    badge_r = 27
    draw.ellipse([badge_cx - badge_r, badge_cy - badge_r,
                  badge_cx + badge_r, badge_cy + badge_r], fill=accent)
    num_font = load_font(FONT_BOLD, 34)
    num = str(number)
    nw = draw.textlength(num, font=num_font)
    nh = num_font.getbbox(num)[3]
    draw.text((badge_cx - nw / 2, badge_cy - nh / 2 - 2), num,
              font=num_font, fill=WHITE)
    # Category label under the badge, in the accent colour.
    label_font = shrink_to_fit(draw, label, FONT_BOLD, 17, panel_w - 12)
    lw = draw.textlength(label, font=label_font)
    draw.text((badge_cx - lw / 2, top + 82), label,
              font=label_font, fill=accent)
    # Headline + two summary lines on the right of the panel.
    text_x = left + 7 + panel_w + 18
    text_w = right - 14 - text_x
    head_font = shrink_to_fit(draw, headline, FONT_BOLD, 30, text_w)
    draw.text((text_x, top + 12), headline, font=head_font, fill=INK)
    sum_font = load_font(FONT_REG, 22)
    for i, line in enumerate((line1, line2)):
        fitted = shrink_to_fit(draw, line, FONT_REG, 22, text_w)
        draw.text((text_x, top + 50 + i * 30), line, font=fitted, fill=BODY)


def main():
    image = Image.new("RGB", (CANVAS_W, CANVAS_H), WHITE)
    draw = ImageDraw.Draw(image)
    draw_header(draw)
    card_top = 164
    gap = 10
    for idx, story in enumerate(STORIES):
        draw_card(draw, card_top + idx * (124 + gap), *story)
    footer_font = load_font(FONT_REG, 19)
    fw = draw.textlength(FOOTER, font=footer_font)
    draw.text(((CANVAS_W - fw) / 2, 978), FOOTER,
              font=footer_font, fill=MUTED)
    image.save("entry.png", optimize=True)


if __name__ == "__main__":
    main()
