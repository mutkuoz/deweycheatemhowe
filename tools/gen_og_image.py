"""Build the 1200x630 social share image and the PNG/ICO icon set.

usage: python3 tools/gen_og_image.py <dir with LibreCaslonDisplay-Regular.ttf and LibreCaslonText-Italic[wght].ttf>
Run from the project root. Needs Pillow, rsvg-convert and ImageMagick.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONTS = Path(sys.argv[1])
ROOT = Path.cwd()
IMG = ROOT / "assets" / "img"

W, H = 1200, 630
GREEN = (14, 29, 23)
PAPER = (246, 243, 234)
MUTED = (238, 235, 226, 190)
BRASS = (205, 178, 124)


def render_svg(svg: Path, width: int) -> Image.Image:
    with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
        subprocess.run(["rsvg-convert", "-w", str(width), str(svg), "-o", tmp.name], check=True)
        return Image.open(tmp.name).convert("RGBA").copy()


def og_image():
    src = Image.open(IMG / "hero-reading-room-2560.jpg").convert("RGB")
    scale = W / src.width * 1.18  # slight zoom so the vault fills the frame
    im = src.resize((round(src.width * scale), round(src.height * scale)), Image.LANCZOS)
    left = (im.width - W) // 2 + 120
    top = int((im.height - H) * 0.42)
    im = im.crop((left, top, left + W, top + H)).convert("RGBA")

    # Green tint, then a left-to-right and bottom shade for the type.
    tint = Image.new("RGBA", (W, H), (28, 58, 48, 70))
    im = Image.alpha_composite(im, tint)
    shade = Image.new("RGBA", (W, H))
    px = shade.load()
    for x in range(W):
        a_x = max(0.0, 0.9 - 0.75 * (x / W) ** 1.2)
        for y in range(H):
            a_y = max(0.0, (y / H - 0.45) / 0.55) * 0.55
            a = min(0.94, a_x + a_y * (1 - a_x))
            px[x, y] = (*GREEN, int(a * 255))
    im = Image.alpha_composite(im, shade)

    logo = render_svg(IMG / "brand" / "logo-reverse.svg", 470)
    im.alpha_composite(logo, (72, 64))

    draw = ImageDraw.Draw(im)
    display = ImageFont.truetype(str(FONTS / "LibreCaslonDisplay-Regular.ttf"), 66)
    italic = ImageFont.truetype(str(FONTS / "LibreCaslonText-Italic[wght].ttf"), 24)
    lines = ["Ninety-five years of getting", "our clients exactly what", "they deserve."]
    y = 300
    for line in lines:
        draw.text((72, y), line, font=display, fill=PAPER)
        y += 74
    draw.line([(72, H - 64), (110, H - 64)], fill=BRASS, width=1)
    draw.text((124, H - 79), "deweycheatemhowe.net", font=italic, fill=MUTED)

    im.convert("RGB").save(IMG / "og-image.jpg", quality=86, progressive=True, optimize=True)


def icons():
    fav = IMG / "brand" / "favicon.svg"
    for size, name in [(180, "apple-touch-icon.png"), (192, "icon-192.png"), (512, "icon-512.png"), (32, "favicon-32.png")]:
        render_svg(fav, size).save(IMG / "brand" / name, optimize=True)
    # Maskable icon: full-bleed green with the mark inside the safe zone.
    mark = render_svg(IMG / "brand" / "mark.svg", 300)
    r, g, b, a = mark.split()
    gold = Image.new("RGBA", mark.size, (233, 221, 191, 255))
    gold.putalpha(a)
    m = Image.new("RGBA", (512, 512), (28, 58, 48, 255))
    m.alpha_composite(gold, (106, 106))
    m.save(IMG / "brand" / "icon-maskable-512.png", optimize=True)
    with tempfile.TemporaryDirectory() as d:
        sizes = []
        for s in (16, 32, 48):
            p = Path(d) / f"{s}.png"
            render_svg(fav, s).save(p)
            sizes.append(str(p))
        subprocess.run(["magick", *sizes, str(ROOT / "favicon.ico")], check=True)


if __name__ == "__main__":
    og_image()
    icons()
    print("ok")
