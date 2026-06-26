"""
LIMIAR LATENTE — Canvas Generator
Design: converging lines / invisible filter / threshold aesthetics
Conceptual soul: the ATS gate — systems that decide before humans see
"""
from PIL import Image, ImageDraw, ImageFont
import math
import os

FONTS = "C:/Users/ednas/AppData/Roaming/Claude/local-agent-mode-sessions/skills-plugin/83bdf9b6-1194-411d-bbc2-7e8a40472731/b00f4908-137d-494b-9ad4-744ef48bcf46/skills/canvas-design/canvas-fonts"

# Canvas: A3 portrait at 150dpi → 1240 × 1754 px (premium print quality)
W, H = 1240, 1754

# Palette — Limiar Latente
BG        = (10, 11, 14)        # near-black, deep charcoal
SURFACE   = (16, 18, 24)        # slightly lifted
LINE_DIM  = (38, 42, 52)        # dimmed structural lines
LINE_MID  = (62, 68, 84)        # mid-toned lines
LINE_BRIGHT = (110, 118, 142)   # bright structural lines
AMBER     = (210, 138, 42)      # the threshold amber — the gate color
AMBER_DIM = (140, 88, 24)       # dimmed amber
WHITE     = (238, 241, 246)     # clinical white highlight
MUTED     = (88, 96, 118)       # muted text

img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

# ─────────────────────────────────────────────
# LOAD FONTS
# ─────────────────────────────────────────────
def font(name, size):
    try:
        return ImageFont.truetype(os.path.join(FONTS, name), size)
    except:
        return ImageFont.load_default()

f_mono_sm   = font("IBMPlexMono-Regular.ttf", 13)
f_mono_xs   = font("IBMPlexMono-Regular.ttf", 10)
f_jura_sm   = font("Jura-Light.ttf", 14)
f_jura_md   = font("Jura-Medium.ttf", 22)
f_jura_lg   = font("Jura-Medium.ttf", 38)
f_gloock_xl = font("Gloock-Regular.ttf", 72)
f_gloock_md = font("Gloock-Regular.ttf", 28)
f_instrument= font("InstrumentSans-Regular.ttf", 11)

# ─────────────────────────────────────────────
# BACKGROUND: subtle grid texture
# ─────────────────────────────────────────────
GRID_STEP = 62
for x in range(0, W, GRID_STEP):
    draw.line([(x, 0), (x, H)], fill=(18, 20, 26), width=1)
for y in range(0, H, GRID_STEP):
    draw.line([(0, y), (W, y)], fill=(18, 20, 26), width=1)

# ─────────────────────────────────────────────
# FUNNEL STRUCTURE — converging lines
# The visual soul: many become few, few become one
# ─────────────────────────────────────────────
MARGIN_TOP = 160
MARGIN_BOT = H - 220
APEX_X = W // 2
APEX_Y = MARGIN_BOT

# Left fan: lines from left edge → apex
LEFT_ORIGIN_Y_START = MARGIN_TOP - 40
LEFT_ORIGIN_Y_END   = MARGIN_BOT + 40
N_LINES = 48

for i in range(N_LINES):
    t = i / (N_LINES - 1)
    # left fan
    lx = 0
    ly = LEFT_ORIGIN_Y_START + t * (LEFT_ORIGIN_Y_END - LEFT_ORIGIN_Y_START)
    # right fan (mirrored)
    rx = W
    ry = LEFT_ORIGIN_Y_START + t * (LEFT_ORIGIN_Y_END - LEFT_ORIGIN_Y_START)

    # Color: lines near center of fan are brighter
    proximity = 1.0 - abs(t - 0.5) * 2
    r = int(LINE_DIM[0] + proximity * (LINE_BRIGHT[0] - LINE_DIM[0]))
    g = int(LINE_DIM[1] + proximity * (LINE_BRIGHT[1] - LINE_DIM[1]))
    b = int(LINE_DIM[2] + proximity * (LINE_BRIGHT[2] - LINE_DIM[2]))
    col = (r, g, b)
    w = 1 if proximity < 0.5 else 1

    draw.line([(lx, int(ly)), (APEX_X, APEX_Y)], fill=col, width=w)
    draw.line([(rx, int(ry)), (APEX_X, APEX_Y)], fill=col, width=w)

# ─────────────────────────────────────────────
# AMBER ACCENT LINES — the threshold
# A narrow band of amber at the critical narrowing zone
# ─────────────────────────────────────────────
# Zone: ~65% down the funnel
THRESHOLD_Y = int(MARGIN_TOP + 0.62 * (MARGIN_BOT - MARGIN_TOP))
THRESHOLD_HALF_W = int((W / 2) * (1.0 - 0.62))  # narrowed width at threshold

# Horizontal amber line across the threshold
for dy in range(-1, 2):
    alpha = 255 if dy == 0 else 140
    col_a = (AMBER[0], AMBER[1], AMBER[2]) if dy == 0 else AMBER_DIM
    draw.line(
        [(APEX_X - THRESHOLD_HALF_W, THRESHOLD_Y + dy),
         (APEX_X + THRESHOLD_HALF_W, THRESHOLD_Y + dy)],
        fill=col_a, width=1
    )

# Small amber tick marks on left and right edges of threshold
tick_len = 12
for sign in [-1, 1]:
    tx = APEX_X + sign * THRESHOLD_HALF_W
    draw.line([(tx, THRESHOLD_Y - tick_len), (tx, THRESHOLD_Y + tick_len)],
              fill=AMBER, width=2)

# ─────────────────────────────────────────────
# APEX CIRCLE — the singular point of decision
# ─────────────────────────────────────────────
apex_r = 5
draw.ellipse(
    [(APEX_X - apex_r, APEX_Y - apex_r),
     (APEX_X + apex_r, APEX_Y + apex_r)],
    outline=AMBER, width=2
)
draw.ellipse(
    [(APEX_X - 2, APEX_Y - 2),
     (APEX_X + 2, APEX_Y + 2)],
    fill=AMBER
)

# Outer ring — faint
outer_r = 18
draw.ellipse(
    [(APEX_X - outer_r, APEX_Y - outer_r),
     (APEX_X + outer_r, APEX_Y + outer_r)],
    outline=AMBER_DIM, width=1
)

# ─────────────────────────────────────────────
# TOP HORIZONTAL RULE
# ─────────────────────────────────────────────
rule_y = MARGIN_TOP - 24
draw.line([(60, rule_y), (W - 60, rule_y)], fill=LINE_MID, width=1)

# Top tick marks at equal intervals
for xi in range(7):
    tx = 60 + xi * ((W - 120) // 6)
    draw.line([(tx, rule_y - 5), (tx, rule_y + 5)], fill=LINE_MID, width=1)

# ─────────────────────────────────────────────
# MAIN TITLE — large Gloock serif
# ─────────────────────────────────────────────
title = "LIMIAR"
tw = draw.textlength(title, font=f_gloock_xl)
draw.text(((W - tw) / 2, 62), title, font=f_gloock_xl, fill=WHITE)

subtitle = "LATENTE"
sw = draw.textlength(subtitle, font=f_jura_lg)
draw.text(((W - sw) / 2, 142), subtitle, font=f_jura_lg, fill=(MUTED[0], MUTED[1], MUTED[2]))

# ─────────────────────────────────────────────
# THRESHOLD LABEL — amber, monospaced, clinical
# ─────────────────────────────────────────────
thresh_label = "threshold · 0.618"
tl_w = draw.textlength(thresh_label, font=f_mono_sm)
draw.text(
    ((W - tl_w) / 2, THRESHOLD_Y + 14),
    thresh_label, font=f_mono_sm, fill=AMBER_DIM
)

# ─────────────────────────────────────────────
# LEFT MARGIN ANNOTATIONS — vertical clinical labels
# ─────────────────────────────────────────────
annotations_left = [
    (80, int(MARGIN_TOP + 0.10 * (MARGIN_BOT - MARGIN_TOP)), "N=∞"),
    (80, int(MARGIN_TOP + 0.35 * (MARGIN_BOT - MARGIN_TOP)), "selection"),
    (80, THRESHOLD_Y,                                           "gate"),
    (80, int(MARGIN_TOP + 0.82 * (MARGIN_BOT - MARGIN_TOP)), "signal"),
    (80, APEX_Y - 10,                                           "N=1"),
]
for ax, ay, label in annotations_left:
    draw.text((ax, ay - 6), label, font=f_mono_xs, fill=MUTED)
    draw.line([(ax + 40, ay), (ax + 80, ay)], fill=LINE_DIM, width=1)

# ─────────────────────────────────────────────
# RIGHT MARGIN — coordinate markers
# ─────────────────────────────────────────────
coords = [
    (W - 120, int(MARGIN_TOP + 0.10 * (MARGIN_BOT - MARGIN_TOP)), "01"),
    (W - 120, int(MARGIN_TOP + 0.35 * (MARGIN_BOT - MARGIN_TOP)), "02"),
    (W - 120, THRESHOLD_Y,                                          "03"),
    (W - 120, int(MARGIN_TOP + 0.82 * (MARGIN_BOT - MARGIN_TOP)), "04"),
    (W - 120, APEX_Y - 10,                                          "05"),
]
for cx, cy, num in coords:
    draw.line([(cx, cy), (cx + 28, cy)], fill=LINE_DIM, width=1)
    draw.text((cx + 32, cy - 6), num, font=f_mono_xs, fill=MUTED)

# ─────────────────────────────────────────────
# BOTTOM RULE + CAPTION
# ─────────────────────────────────────────────
bottom_rule_y = H - 130
draw.line([(60, bottom_rule_y), (W - 60, bottom_rule_y)], fill=LINE_MID, width=1)

caption = "fig. I — structural diagram of an invisible decision"
cw = draw.textlength(caption, font=f_instrument)
draw.text(((W - cw) / 2, bottom_rule_y + 16), caption, font=f_instrument, fill=MUTED)

# Bottom classification line
bottom_note = "series: ARQUITETURA OCULTA · plate 001 · 2026"
bnw = draw.textlength(bottom_note, font=f_mono_xs)
draw.text(((W - bnw) / 2, bottom_rule_y + 42), bottom_note, font=f_mono_xs, fill=LINE_MID)

# ─────────────────────────────────────────────
# CROSS-HAIR at apex — precision detail
# ─────────────────────────────────────────────
ch_len = 30
draw.line([(APEX_X - ch_len, APEX_Y), (APEX_X - apex_r - 4, APEX_Y)],
          fill=AMBER_DIM, width=1)
draw.line([(APEX_X + apex_r + 4, APEX_Y), (APEX_X + ch_len, APEX_Y)],
          fill=AMBER_DIM, width=1)
draw.line([(APEX_X, APEX_Y - ch_len), (APEX_X, APEX_Y - apex_r - 4)],
          fill=AMBER_DIM, width=1)
draw.line([(APEX_X, APEX_Y + apex_r + 4), (APEX_X, APEX_Y + ch_len)],
          fill=AMBER_DIM, width=1)

# ─────────────────────────────────────────────
# FINE REFINEMENT PASS
# Dotted vertical center axis — very subtle
# ─────────────────────────────────────────────
for y in range(MARGIN_TOP, APEX_Y, 8):
    if y % 16 < 8:  # dash
        draw.point((APEX_X, y), fill=LINE_DIM)

# Subtle horizontal banding — density map feel
for band_y in range(MARGIN_TOP, THRESHOLD_Y, 4):
    t = (band_y - MARGIN_TOP) / (THRESHOLD_Y - MARGIN_TOP)
    # Width narrows as we go down
    band_half_w = int(THRESHOLD_HALF_W + (W / 2 - THRESHOLD_HALF_W) * (1 - t))
    # Very faint, barely perceptible fill
    r_fill = int(BG[0] + 4 * (1 - t))
    g_fill = int(BG[1] + 4 * (1 - t))
    b_fill = int(BG[2] + 6 * (1 - t))
    # Just dots every 80px for texture
    for dot_x in range(APEX_X - band_half_w + 10, APEX_X + band_half_w - 10, 80):
        draw.point((dot_x, band_y), fill=(r_fill + 8, g_fill + 8, b_fill + 12))

# ─────────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────────
out_path = "C:/Users/ednas/.claude/Aprovai/aprovai-codex/canvas/limiar-latente.png"
img.save(out_path, "PNG", quality=100, dpi=(150, 150))
print(f"Saved: {out_path}")
print(f"Size: {W}x{H}px")
