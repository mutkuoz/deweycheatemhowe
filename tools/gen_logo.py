"""Generate outlined SVG logo assets for Dewey, Cheatem & Howe from Libre Caslon glyphs."""
import math
import sys
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

FONTS = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)


def load(name, wght=None):
    f = TTFont(FONTS / name)
    if wght is not None and "fvar" in f:
        f = instantiateVariableFont(f, {"wght": wght})
    return f


DISPLAY = load("LibreCaslonDisplay-Regular.ttf")
TEXT = load("LibreCaslonText[wght].ttf", 500)
ITALIC = load("LibreCaslonText-Italic[wght].ttf", 400)


class Face:
    def __init__(self, font):
        self.font = font
        self.gs = font.getGlyphSet()
        self.cmap = font.getBestCmap()
        self.upm = font["head"].unitsPerEm
        self.hmtx = font["hmtx"]
        self.kern = self._kern_pairs()

    def _kern_pairs(self):
        """Read simple pair kerning (format 1 PairPos) from GPOS, enough for a wordmark."""
        pairs = {}
        if "GPOS" not in self.font:
            return pairs
        gpos = self.font["GPOS"].table
        for lookup in gpos.LookupList.Lookup:
            for st in lookup.SubTable:
                if lookup.LookupType == 9:
                    st = st.ExtSubTable
                if getattr(st, "LookupType", None) != 2 and lookup.LookupType not in (2, 9):
                    continue
                if not hasattr(st, "Format"):
                    continue
                cov = st.Coverage.glyphs
                if st.Format == 1:
                    for i, first in enumerate(cov):
                        for pvr in st.PairSet[i].PairValueRecord:
                            v = pvr.Value1
                            if v is not None and getattr(v, "XAdvance", None):
                                pairs.setdefault((first, pvr.SecondGlyph), v.XAdvance)
                elif st.Format == 2:
                    cd1 = st.ClassDef1.classDefs
                    cd2 = st.ClassDef2.classDefs
                    for first in cov:
                        c1 = cd1.get(first, 0)
                        rec = st.Class1Record[c1]
                        for second, c2 in list(cd2.items()):
                            v = rec.Class2Record[c2].Value1
                            if v is not None and getattr(v, "XAdvance", None):
                                pairs.setdefault((first, second), v.XAdvance)
        return pairs

    def gname(self, ch):
        if len(ch) > 1:  # explicit glyph name
            return ch
        return self.cmap[ord(ch)]

    def adv(self, g):
        return self.hmtx[g][0]

    def path(self, g, transform):
        pen = SVGPathPen(self.gs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
        self.gs[g].draw(TransformPen(pen, transform))
        return pen.getCommands()

    def bounds(self, g):
        bp = BoundsPen(self.gs)
        self.gs[g].draw(bp)
        return bp.bounds


D, T, I = Face(DISPLAY), Face(TEXT), Face(ITALIC)


def glyphs_of(face, text):
    return [face.gname(c) for c in text]


def line(face, text, size, x, y, tracking=0.0, kern=True):
    """Lay out a line; returns (path_d, width). x,y is baseline-left in SVG units. tracking in em."""
    k = size / face.upm
    gl = glyphs_of(face, text) if isinstance(text, str) else text
    cx = 0.0
    parts = []
    for i, g in enumerate(gl):
        parts.append(face.path(g, (k, 0, 0, -k, x + cx * k, y)))
        cx += face.adv(g)
        if i < len(gl) - 1:
            if kern:
                cx += face.kern.get((g, gl[i + 1]), 0)
            cx += tracking * face.upm
    width = cx * k
    return " ".join(parts), width


def measure(face, text, size, tracking=0.0, kern=True):
    return line(face, text, size, 0, 0, tracking, kern)[1]


def arc_text(face, text, size, cx, cy, r, center_deg, tracking=0.0, bottom=False, span=None):
    """Place text on a circle. Top: baseline at radius r reading clockwise.
    Bottom: baseline at radius r reading left->right with glyph tops toward centre."""
    k = size / face.upm
    gl = glyphs_of(face, text)
    advs = [face.adv(g) * k for g in gl]
    # punctuation hugs the preceding letter: it gets a fraction of the normal tracking before it
    weights = [0.15 if (i + 1 < len(gl) and gl[i + 1] in ("comma", "period")) else 1.0 for i in range(len(gl) - 1)] + [0.0]
    track = tracking * size
    if span is not None:
        track = (math.radians(span) * r - sum(advs)) / sum(weights)
    total = sum(advs) + track * sum(weights)
    out = []
    pos = 0.0
    for g, a, w in zip(gl, advs, weights):
        mid = pos + a / 2
        pos += a + track * w
        dtheta = math.degrees((mid - total / 2) / r)
        if not bottom:
            phi = center_deg + dtheta
            th = math.radians(phi)
            # rotation matrix for clockwise rotation by phi, then translate so baseline sits at radius r
            c, s = math.cos(th), math.sin(th)
            # local glyph coords: x' = (gx*k - a/2), y' = -gy*k - r  (then rotate, then translate to centre)
            def tf(c=c, s=s, a=a):
                # combined affine: [k*c, k*s, k*s, -k*c ...] derived below
                return (k * c, k * s, k * s, -k * c,
                        cx + c * (-a / 2) - s * (-r),
                        cy + s * (-a / 2) + c * (-r))
            out.append(face.path(g, tf()))
        else:
            phi = center_deg - dtheta
            th = math.radians(phi - 180)
            c, s = math.cos(th), math.sin(th)
            def tf(c=c, s=s, a=a):
                return (k * c, k * s, k * s, -k * c,
                        cx + c * (-a / 2) - s * r,
                        cy + s * (-a / 2) + c * r)
            out.append(face.path(g, tf()))
    return " ".join(out)


def centered_glyph(face, g, height, cx, cy):
    """Scale glyph so its ink bbox height == height, centred on (cx, cy)."""
    xMin, yMin, xMax, yMax = face.bounds(g)
    k = height / (yMax - yMin)
    w = (xMax - xMin) * k
    x0 = cx - w / 2 - xMin * k
    y0 = cy + height / 2 + yMin * k
    return face.path(g, (k, 0, 0, -k, x0, y0)), w


def diamond(cx, cy, s):
    return f"M{cx:.2f} {cy - s:.2f}L{cx + s * 0.62:.2f} {cy:.2f}L{cx:.2f} {cy + s:.2f}L{cx - s * 0.62:.2f} {cy:.2f}Z"


def ring(cx, cy, r, w):
    """Annulus as a single even-odd path."""
    ro, ri = r + w / 2, r - w / 2
    return (f"M{cx - ro:.2f} {cy:.2f}a{ro:.2f} {ro:.2f} 0 1 0 {2 * ro:.2f} 0a{ro:.2f} {ro:.2f} 0 1 0 {-2 * ro:.2f} 0Z"
            f"M{cx - ri:.2f} {cy:.2f}a{ri:.2f} {ri:.2f} 0 1 0 {2 * ri:.2f} 0a{ri:.2f} {ri:.2f} 0 1 0 {-2 * ri:.2f} 0Z")


AMP = "ampersand"  # chosen after comparing with ampersand.ss01


def seal(fill="currentColor"):
    cx = cy = 120
    p = []
    p.append(ring(cx, cy, 116, 2.2))
    p.append(ring(cx, cy, 111, 0.8))
    p.append(ring(cx, cy, 76, 0.8))
    p.append(ring(cx, cy, 71, 2.2))
    cap = 14
    # text band between r=76 and r=111 -> centre ~93.5; cap height ratio for Text 1523/2000
    ch = cap * 1523 / 2000
    top_r = 93.5 - ch / 2
    bot_r = 93.5 + ch / 2
    glyphs = []
    glyphs.append(arc_text(T, "DEWEY, CHEATEM & HOWE", cap, cx, cy, top_r, 0, span=146))
    glyphs.append(arc_text(T, "CAVEAT CLIENS", cap, cx, cy, bot_r, 180, span=96, bottom=True))
    for ang in (90, 270):
        th = math.radians(ang)
        p.append(diamond(cx + 93.5 * math.sin(th), cy - 93.5 * math.cos(th), 3.4))
    amp, _ = centered_glyph(I, AMP, 74, cx, cy - 6)
    glyphs.append(amp)
    yr, w = line(T, "MCMXXXI", 9, 0, 0, tracking=0.22)
    yr, _ = line(T, "MCMXXXI", 9, cx - w / 2, cy + 50, tracking=0.22)
    glyphs.append(yr)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" role="img" aria-label="Seal of Dewey, Cheatem &amp; Howe">'
            f'<path fill="{fill}" fill-rule="evenodd" d="{" ".join(p)}"/><path fill="{fill}" d="{" ".join(glyphs)}"/></svg>')


def mark(fill="currentColor"):
    cx = cy = 32
    p = [ring(cx, cy, 30.5, 1.6), ring(cx, cy, 26.6, 0.7)]
    amp, _ = centered_glyph(I, AMP, 31, cx, cy)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Dewey, Cheatem &amp; Howe">'
            f'<path fill="{fill}" fill-rule="evenodd" d="{" ".join(p)}"/><path fill="{fill}" d="{amp}"/></svg>')


def wordmark_paths(x, baseline, size):
    """'Dewey, Cheatem & Howe' with the italic ampersand. Returns (d, width)."""
    parts = []
    d1, w1 = line(D, "Dewey, Cheatem", size, x, baseline)
    parts.append(d1)
    gap = size * 0.24
    amp_size = size * 1.06
    xa = x + w1 + gap
    da, wa = line(I, [AMP], amp_size, xa, baseline + size * 0.02, kern=False)
    parts.append(da)
    xh = xa + wa + gap * 0.9
    dh, wh = line(D, "Howe", size, xh, baseline)
    parts.append(dh)
    return " ".join(parts), (xh + wh) - x


def lockup(fill="currentColor", accent=None):
    accent = accent or fill
    size = 44
    pad = 2
    mk_size = 72
    gap = 22
    # mark
    cx = cy = pad + mk_size / 2
    s = mk_size / 64
    mk = [ring(cx, cy, 30.5 * s, 1.6 * s), ring(cx, cy, 26.6 * s, 0.7 * s)]
    amp, _ = centered_glyph(I, AMP, 31 * s, cx, cy)
    x0 = pad + mk_size + gap
    base = pad + 44
    wd, ww = wordmark_paths(x0, base, size)
    sub = "ATTORNEYS AT LAW"
    sw = measure(T, sub, 10.5, tracking=0.32)
    sd, _ = line(T, sub, 10.5, x0 + 1, base + 26, tracking=0.32)
    rule_y = base + 22.4
    rule_x = x0 + sw + 16
    rule = f"M{rule_x:.2f} {rule_y - 0.45:.2f}H{x0 + ww:.2f}V{rule_y + 0.45:.2f}H{rule_x:.2f}Z"
    W = x0 + ww + pad
    H = pad * 2 + mk_size
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="Dewey, Cheatem &amp; Howe, Attorneys at Law">'
            f'<path fill="{accent}" fill-rule="evenodd" d="{" ".join(mk)}"/><path fill="{accent}" d="{amp}"/>'
            f'<path fill="{fill}" d="{wd}"/>'
            f'<path fill="{fill}" d="{sd} {rule}"/></svg>'), W, H


def amp_compare():
    a, _ = centered_glyph(I, "ampersand", 80, 60, 60)
    b, _ = centered_glyph(I, "ampersand.ss01", 80, 180, 60)
    c, _ = centered_glyph(T, "ampersand", 80, 300, 60)
    d, _ = centered_glyph(D, "ampersand", 80, 420, 60)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 120"><rect width="480" height="120" fill="#fff"/><path d="{a} {b} {c} {d}"/></svg>'


if __name__ == "__main__":
    INK = "#16231E"
    BRASS = "#A2834A"
    PAPER = "#F3F2EE"
    (OUT / "amp-compare.svg").write_text(amp_compare())
    (OUT / "seal.svg").write_text(seal(INK))
    (OUT / "seal-reverse.svg").write_text(seal(PAPER))
    (OUT / "mark.svg").write_text(mark(INK))
    svg, W, H = lockup(INK, BRASS)
    (OUT / "logo.svg").write_text(svg)
    svg, W, H = lockup(PAPER, "#C3A469")
    (OUT / "logo-reverse.svg").write_text(svg)
    # favicon: brass mark on green
    fav = mark("#E9DDBF").replace('role="img"', 'role="img"').replace(
        '<path', '<rect width="64" height="64" rx="12" fill="#1C3A30"/><path', 1)
    (OUT / "favicon.svg").write_text(fav)
    # inline-able path data for the HTML (currentColor)
    (OUT / "seal.inline.svg").write_text(seal())
    (OUT / "mark.inline.svg").write_text(mark())
    print("kern pairs D:", len(D.kern), "lockup size", round(W), round(H))
