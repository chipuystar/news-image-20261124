#!/usr/bin/env python3
"""Build entry.png for news-image-20261124 from the reference artwork.

The reference is a 2048x2048 photorealistic front page (the same six
stories and layout as the earlier Pillow version, supplied by Chipuy).
It is downscaled to the competition's 1024x1024 cap and saved as a JPEG
(the file keeps the name entry.png; the format is told apart by its
first bytes, per RULES.txt). One typo in the reference is fixed here:
"LYBIA" in the WAR panel tag becomes "LIBYA".

Usage: python3 gen_image.py <reference.jpg> [entry.png]
"""
import sys

from PIL import Image, ImageDraw, ImageFont

WAR_TAG = "WAR  •  BALTIC & LIBYA"
WAR_TAG_BOX = (50, 797, 280, 821)  # x0, y0, x1, y1 in the 1024 image
WAR_TAG_POS = (54, 798)
WAR_TAG_SIZE = 21
WAR_TAG_FILL = (126, 136, 144)


def fix_war_tag(im):
    """Replace the reference's misspelled tag 'BALTIC & LYBIA' with LIBYA.

    The tag sits on the panel's dark overlay. Each row of the old line is
    repainted with that row's own median background colour (bright text
    pixels excluded), so the overlay's vertical gradient is preserved and
    the patch has no visible edge; the corrected line is then drawn in
    the same size and colour as the original.
    """
    x0, y0, x1, y1 = WAR_TAG_BOX
    px = im.load()
    for y in range(y0, y1):
        row_bg = [px[x, y] for x in range(x0, x1) if sum(px[x, y]) <= 200]
        row_bg.sort()
        bg = row_bg[len(row_bg) // 2]
        for x in range(x0, x1):
            px[x, y] = bg
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                              WAR_TAG_SIZE)
    d.text(WAR_TAG_POS, WAR_TAG, font=font, fill=WAR_TAG_FILL)


SRC = sys.argv[1] if len(sys.argv) > 1 else "reference.jpg"
DST = sys.argv[2] if len(sys.argv) > 2 else "entry.png"

im = Image.open(SRC).convert("RGB")
im = im.resize((1024, 1024), Image.LANCZOS)
fix_war_tag(im)
im.save(DST, "JPEG", quality=90, optimize=True)
print(f"wrote {DST} ({im.size[0]}x{im.size[1]})")
