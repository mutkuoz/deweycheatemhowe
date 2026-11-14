#!/usr/bin/env bash
# Rebuild the self-hosted, Latin-subset WOFF2 fonts in assets/fonts/.
# usage: tools/build_fonts.sh <dir with the Google Fonts TTFs>
#   LibreCaslonDisplay-Regular.ttf, LibreCaslonText[wght].ttf, LibreCaslonText-Italic[wght].ttf, LibreFranklin[wght].ttf
# Needs fontTools with brotli (pip install fonttools brotli).
set -euo pipefail
SRC="$1"
OUT="$(cd "$(dirname "$0")/.." && pwd)/assets/fonts"
mkdir -p "$OUT"

U="U+0020-007E,U+00A0-00FF,U+0131,U+0152-0153,U+02BC,U+02C6,U+02DA,U+02DC,U+2009,U+200A,U+2013-2014,U+2018-201E,U+2020-2022,U+2026,U+2032-2033,U+2039-203A,U+20AC,U+2116,U+2122,U+2190-2193,U+21A9,U+2212"
# Standard features only: no discretionary/historical ligatures or stylistic sets.
FEATS="kern,mark,mkmk,ccmp,locl,liga,lnum,tnum,pnum,onum,case,frac"

python3 - "$SRC" <<'EOF'
import sys
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
src = sys.argv[1]
f = TTFont(f"{src}/LibreFranklin[wght].ttf")
instantiateVariableFont(f, {"wght": (400, 700)}).save(f"{src}/LibreFranklin-400-700.ttf")
EOF

sub() { pyftsubset "$1" --unicodes="$U" --layout-features="$FEATS" --flavor=woff2 --output-file="$2" --no-hinting --desubroutinize; }
sub "$SRC/LibreCaslonDisplay-Regular.ttf" "$OUT/libre-caslon-display.woff2"
sub "$SRC/LibreCaslonText[wght].ttf" "$OUT/libre-caslon-text.woff2"
sub "$SRC/LibreCaslonText-Italic[wght].ttf" "$OUT/libre-caslon-text-italic.woff2"
sub "$SRC/LibreFranklin-400-700.ttf" "$OUT/libre-franklin.woff2"

# The italic puts historical s+t / s+p ligatures in 'liga'; they read as typos ("štandard"), so drop them.
python3 - "$OUT/libre-caslon-text-italic.woff2" <<'EOF'
import sys
from fontTools.ttLib import TTFont
p = sys.argv[1]
f = TTFont(p)
g = f["GSUB"].table
for fr in g.FeatureList.FeatureRecord:
    if fr.FeatureTag != "liga":
        continue
    for li in fr.Feature.LookupListIndex:
        lk = g.LookupList.Lookup[li]
        for st in lk.SubTable:
            if lk.LookupType == 7:
                st = st.ExtSubTable
            ligs = getattr(st, "ligatures", None)
            if ligs and "s" in ligs:
                ligs["s"] = [l for l in ligs["s"] if l.Component not in (["t"], ["p"])]
                if not ligs["s"]:
                    del ligs["s"]
f.flavor = "woff2"
f.save(p)
EOF
ls -la "$OUT"
