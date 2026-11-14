"""Cut-paper silhouette portraits for the testimonials. Profiles face right."""
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

PAPER = "#ECE8DE"
INK = "#15231D"
BRASS = "#B4955A"

# Shared lower body: jacket shoulders from the front of the neck round to the back of the neck.
SUIT_FRONT = "C 150 206, 182 218, 198 300 L 2 300 C 8 236, 32 204, 70 196"

DEVIL = """
M 72 160
C 62 140, 55 120, 56 98
C 57 66, 78 44, 108 41
C 134 40, 149 56, 151 76
C 152 84, 151 88, 154 93
C 155 96, 153 99, 151 101
C 155 110, 161 118, 165 125
C 166 129, 162 131, 157 130
C 155 131, 155 133, 156 135
C 157 138, 155 140, 153 141
C 155 143, 154 146, 152 147
C 150 149, 150 151, 151 154
C 154 166, 159 176, 162 190
C 150 184, 136 174, 126 170
C 123 178, 123 188, 125 196
L 137 210
L 132 196
""" + """
C 150 206, 182 218, 198 300 L 2 300 C 8 236, 32 204, 70 196
C 74 186, 74 172, 72 160 Z
M 118 45 C 123 32, 131 20, 142 6 C 140 22, 136 36, 134 50 Z
M 86 50 C 83 36, 86 24, 95 13 C 94 27, 96 38, 101 45 Z
"""

VADER = """
M 2 300
C 6 252, 16 214, 38 196
L 48 189
L 16 182
C 34 160, 46 128, 50 104
C 52 60, 84 32, 118 32
C 146 33, 160 52, 162 76
L 167 86
L 150 90
L 152 104
L 163 112
L 158 118
L 172 132
L 170 150
L 160 164
L 136 166
L 132 176
C 150 180, 178 196, 190 224
L 198 300 Z
"""

RIDDLE = """
M 74 162
C 64 144, 57 124, 57 102
C 56 70, 70 44, 98 35
C 118 28, 140 32, 151 44
C 156 50, 155 57, 148 60
C 152 66, 152 76, 152 86
C 152 91, 152 95, 154 99
C 153 101, 152 102, 151 104
C 155 112, 159 119, 162 124
C 163 127, 160 129, 156 129
C 154 130, 154 132, 155 134
C 156 137, 154 139, 152 140
C 154 142, 153 145, 151 146
C 149 148, 149 150, 150 153
C 152 158, 149 162, 143 164
C 136 166, 129 166, 125 168
C 123 175, 123 182, 124 188
L 133 196
L 130 184
""" + """
C 150 202, 182 218, 198 300 L 2 300 C 8 236, 32 204, 70 196
C 75 186, 76 174, 74 162 Z
"""

WHITE = """
M 82 172
L 72 190
L 70 176
L 56 186
L 58 170
L 44 172
L 52 158
C 47 140, 48 118, 52 100
C 50 70, 62 46, 84 38
C 96 24, 120 16, 142 22
C 156 26, 165 38, 160 50
C 158 56, 153 60, 148 62
C 151 72, 152 82, 153 90
C 154 95, 155 98, 158 101
C 157 104, 155 106, 153 108
C 158 117, 165 126, 172 134
C 173 137, 168 139, 162 138
C 159 139, 159 141, 160 143
C 163 146, 163 148, 158 149
L 151 150
L 158 152
C 160 153, 159 156, 156 157
C 153 159, 153 161, 155 165
C 160 172, 157 181, 147 182
C 139 183, 132 180, 127 182
C 125 186, 125 190, 125 196
L 136 206
L 132 194
""" + """
C 150 206, 182 218, 198 300 L 2 300 C 8 236, 32 204, 74 198
C 78 190, 80 182, 82 172 Z
"""

# Paper-coloured detail strokes, the way silhouette artists added highlights in white or gilt.
DETAILS = {
    "riddle": """
      <path d="M 133 196 L 150 250" />
      <path d="M 126 190 L 128 200 C 130 214, 132 232, 134 260" />
    """,
    "devil": """
      <path d="M 137 210 L 150 244" />
    """,
    "white": """
      <path d="M 136 206 L 152 246" />
      <g transform="translate(144 222)" stroke="none" fill="{paper}">
        <circle r="2.6"/>
        <ellipse cx="0" cy="-6" rx="2.4" ry="4.2"/>
        <ellipse cx="0" cy="6" rx="2.4" ry="4.2"/>
        <ellipse cx="-6" cy="0" rx="4.2" ry="2.4"/>
        <ellipse cx="6" cy="0" rx="4.2" ry="2.4"/>
        <ellipse cx="4.3" cy="-4.3" rx="2.2" ry="4" transform="rotate(45 4.3 -4.3)"/>
        <ellipse cx="-4.3" cy="4.3" rx="2.2" ry="4" transform="rotate(45 -4.3 4.3)"/>
        <ellipse cx="-4.3" cy="-4.3" rx="2.2" ry="4" transform="rotate(-45 -4.3 -4.3)"/>
        <ellipse cx="4.3" cy="4.3" rx="2.2" ry="4" transform="rotate(-45 4.3 4.3)"/>
      </g>
      <circle cx="144" cy="222" r="2" fill="{ink}" stroke="none"/>
    """,
    "vader": """
      <path d="M 16 182 C 52 176, 100 170, 136 166" />
      <path d="M 165 85 C 140 87, 116 95, 100 112 C 88 126, 78 150, 72 178" opacity=".55"/>
      <path d="M 152 104 L 140 120 L 150 150 L 160 164" opacity=".45"/>
    """,
}


def portrait(key, d, label):
    details = DETAILS.get(key, "").replace("{paper}", PAPER).replace("{ink}", INK)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 250" role="img" aria-label="{label}">
  <defs><clipPath id="o-{key}"><ellipse cx="100" cy="125" rx="92" ry="117"/></clipPath></defs>
  <ellipse cx="100" cy="125" rx="98" ry="123" fill="none" stroke="{BRASS}" stroke-width="1.4"/>
  <ellipse cx="100" cy="125" rx="92" ry="117" fill="{PAPER}"/>
  <g clip-path="url(#o-{key})">
    <g transform="translate(17 32) scale(.84)">
    <path fill="{INK}" d="{" ".join(d.split())}"/>
    <g fill="none" stroke="{PAPER}" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round" opacity=".7">{details}</g>
    </g>
  </g>
  <ellipse cx="100" cy="125" rx="92" ry="117" fill="none" stroke="{BRASS}" stroke-width=".6"/>
</svg>
'''


for key, d, label in [
    ("devil", DEVIL, "Silhouette portrait of The Devil, in profile, horns and goatee"),
    ("vader", VADER, "Silhouette portrait of Darth Vader's helmet in profile"),
    ("riddle", RIDDLE, "Silhouette portrait of Tom Marvolo Riddle as a young man, in profile"),
    ("white", WHITE, "Silhouette portrait of J. Oswald White in profile, with a flower in his lapel"),
]:
    (OUT / f"{key}.svg").write_text(portrait(key, d, label))
print("ok")
