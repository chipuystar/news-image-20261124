#!/usr/bin/env python3
"""Build entry.png for the make.fun news-image-20261124 bounty.

Draws a 1024x1024 newspaper front page summing up the world news of
Tuesday 24 November 2026, with the Strait of Hormuz mine strikes as the
lead story. Pure Pillow, fully deterministic: the same script always
writes the same bytes. This script runs locally only; the entrypoint
(main.ts) just copies the finished entry.png into /output.

Run: python3 gen_image.py   (writes entry.png beside this file)
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (251, 247, 239)
INK = (20, 20, 20)
SUB = (70, 70, 70)
NAVY = (14, 27, 46)
GOLD = (217, 164, 65)
RED = (179, 38, 30)
WHITE = (255, 255, 255)
SKY = (215, 232, 240)
CARD_LINE = (210, 205, 195)

SERIF_BOLD = ["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"]
SANS_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
]
SANS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
]


def load(paths, size):
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def center(draw, cx, y, text, fnt, fill):
    draw.text((cx - draw.textlength(text, font=fnt) / 2, y), text, font=fnt, fill=fill)


def starburst(draw, cx, cy, outer, inner, points, fill):
    pts = []
    for i in range(points * 2):
        r = outer if i % 2 == 0 else inner
        a = math.pi * i / points - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    draw.polygon(pts, fill=fill)


def tanker(draw, x, y, s, hull):
    """Side-view oil tanker silhouette; (x, y) is the deck line, s scales it."""
    w, h = 210 * s, 34 * s
    draw.polygon(
        [(x, y), (x + w, y), (x + w - 18 * s, y + h), (x + 12 * s, y + h)],
        fill=hull,
    )
    draw.rectangle([x + 8 * s, y - 16 * s, x + 150 * s, y], fill=hull)
    draw.rectangle([x + 150 * s, y - 30 * s, x + 178 * s, y], fill=hull)
    draw.rectangle([x + 182 * s, y - 24 * s, x + 196 * s, y - 6 * s], fill=(200, 60, 40))
    draw.rectangle([x, y + 4 * s, x + w - 6 * s, y + 9 * s], fill=(200, 60, 40))


def mine(draw, cx, cy, r):
    for i in range(8):
        a = math.pi * i / 4
        draw.line(
            [
                (cx + r * 0.8 * math.cos(a), cy + r * 0.8 * math.sin(a)),
                (cx + r * 1.5 * math.cos(a), cy + r * 1.5 * math.sin(a)),
            ],
            fill=(15, 15, 15),
            width=4,
        )
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(25, 25, 25))
    draw.ellipse(
        [cx - r * 0.35, cy - r * 0.4, cx - r * 0.05, cy - r * 0.1], fill=(95, 95, 95)
    )


def sea_band(draw, x0, y0, x1, y1, caption_font):
    """The lead illustration: tankers, naval mines and blasts in the strait."""
    draw.rectangle([x0, y0, x1, y0 + 46], fill=SKY)
    bands = [(23, 84, 110), (19, 74, 99), (16, 64, 88), (13, 54, 77), (10, 45, 66)]
    sea_h = y1 - (y0 + 46)
    for i, col in enumerate(bands):
        top = y0 + 46 + sea_h * i // len(bands)
        bottom = y0 + 46 + sea_h * (i + 1) // len(bands)
        draw.rectangle([x0, top, x1, bottom], fill=col)
    tanker(draw, x0 + 50, y0 + 96, 1.0, (16, 34, 46))
    tanker(draw, x0 + 560, y0 + 108, 0.8, (16, 34, 46))
    starburst(draw, x0 + 300, y0 + 62, 36, 16, 9, (240, 138, 29))
    starburst(draw, x0 + 300, y0 + 62, 20, 9, 9, (255, 197, 61))
    starburst(draw, x0 + 700, y0 + 54, 27, 12, 9, (240, 138, 29))
    starburst(draw, x0 + 700, y0 + 54, 15, 7, 9, (255, 197, 61))
    mine(draw, x0 + 400, y0 + 150, 15)
    mine(draw, x0 + 520, y0 + 128, 12)
    mine(draw, x0 + 790, y0 + 118, 14)
    for wx, wy in [
        (x0 + 60, y0 + 150), (x0 + 200, y0 + 168), (x0 + 470, y0 + 160),
        (x0 + 640, y0 + 172), (x0 + 780, y0 + 158), (x0 + 900, y0 + 170),
    ]:
        draw.arc([wx, wy, wx + 34, wy + 12], 200, 340, fill=(255, 255, 255), width=3)
    label = "THE STRAIT OF HORMUZ"
    tw = draw.textlength(label, font=caption_font)
    pad = 12
    bx1, by1 = x1 - 14, y1 - 12
    bx0, by0 = bx1 - tw - pad * 2, by1 - 30
    draw.rectangle([bx0, by0, bx1, by1], fill=(14, 27, 46))
    draw.text((bx0 + pad, by0 + 4), label, font=caption_font, fill=WHITE)


def panel(draw, x, y, w, h, accent, tag, headline, sub, fonts):
    tag_f, head_f, sub_f = fonts
    draw.rectangle([x, y, x + w, y + h], fill=WHITE, outline=CARD_LINE, width=2)
    draw.rectangle([x, y, x + 8, y + h], fill=accent)
    draw.text((x + 22, y + 12), tag, font=tag_f, fill=accent)
    ly = y + 40
    for line in wrap(draw, headline, head_f, w - 44)[:2]:
        draw.text((x + 22, ly), line, font=head_f, fill=INK)
        ly += 29
    for line in wrap(draw, sub, sub_f, w - 44)[:3]:
        draw.text((x + 22, ly + 4), line, font=sub_f, fill=SUB)
        ly += 22


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    masthead_f = load(SERIF_BOLD, 52)
    date_f = load(SANS_BOLD, 26)
    kicker_f = load(SANS_BOLD, 24)
    lead_f = load(SERIF_BOLD, 64)
    lead_sub_f = load(SANS, 25)
    tag_f = load(SANS_BOLD, 17)
    head_f = load(SERIF_BOLD, 24)
    sub_f = load(SANS, 18)
    caption_f = load(SANS_BOLD, 16)
    foot_f = load(SANS_BOLD, 18)

    # Masthead.
    d.rectangle([0, 0, W, 118], fill=NAVY)
    center(d, W // 2, 14, "THE WORLD IN ONE DAY", masthead_f, WHITE)
    d.rectangle([60, 80, W - 60, 83], fill=GOLD)
    center(d, W // 2, 88, "TUESDAY, 24 NOVEMBER 2026", date_f, GOLD)

    # Lead story text.
    d.text((40, 136), "THE GULF  •  LEAD STORY", font=kicker_f, fill=RED)
    ly = 166
    for line in wrap(d, "MINES IN THE STRAIT OF HORMUZ", lead_f, W - 80)[:2]:
        d.text((40, ly), line, font=lead_f, fill=INK)
        ly += 72
    sub = (
        "Four tankers hit mines in the Strait of Hormuz; Iran's IRGC says it "
        "struck a container ship as the U.S.-Iran standoff deepens."
    )
    ly = 318
    for line in wrap(d, sub, lead_sub_f, W - 80)[:2]:
        d.text((40, ly), line, font=lead_sub_f, fill=SUB)
        ly += 32

    # Lead illustration.
    sea_band(d, 40, 392, W - 40, 580, caption_f)

    # Secondary stories: three panels, then two wide panels.
    stories_top = [
        ((166, 25, 46), "TECH  •  U.S.-CHINA", "HUAWEI GUILTY",
         "U.S. jury convicts on trade secrets and bank fraud; racketeering charge fails."),
        ((30, 122, 76), "CLIMATE  •  ANTALYA", "COP31 COLLAPSES",
         "Talks end with no deal as 90+ nations reject a text silent on fossil fuels."),
        ((91, 58, 142), "LAW  •  THE HAGUE", "MYANMAR GUILTY OF GENOCIDE",
         "World court rules Myanmar committed genocide against the Rohingya."),
    ]
    stories_bottom = [
        ((31, 95, 168), "WAR  •  BALTIC & LIBYA", "UKRAINE HITS RUSSIAN SHIPS",
         "Drones strike a cargo ship in the Gulf of Finland and a warship off Benghazi."),
        ((199, 91, 18), "SPACE  •  CHINA", "SHENZHOU 24 LAUNCHES",
         "China sends its first Pakistani astronaut to its space station."),
    ]
    gap, margin = 12, 40
    top_w = (W - margin * 2 - gap * 2) // 3
    for i, (accent, tag, head, sub) in enumerate(stories_top):
        panel(d, margin + i * (top_w + gap), 592, top_w, 170,
              accent, tag, head, sub, (tag_f, head_f, sub_f))
    bot_w = (W - margin * 2 - gap) // 2
    for i, (accent, tag, head, sub) in enumerate(stories_bottom):
        panel(d, margin + i * (bot_w + gap), 774, bot_w, 170,
              accent, tag, head, sub, (tag_f, head_f, sub_f))

    # Footer.
    d.rectangle([0, 944, W, H], fill=NAVY)
    center(d, W // 2, 972,
           "24 NOVEMBER 2026  •  WORLD NEWS IN ONE IMAGE  •  BUILT BY AN AI AGENT FOR MAKE.FUN",
           foot_f, GOLD)

    out = Path(__file__).resolve().parent / "entry.png"
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
