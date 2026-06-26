"""
LIMIAR LATENTE — Refined Canvas (Pass 2)
Refinements: tighter geometry, more precise amber, richer density gradients,
cleaner typography placement, breath between elements.
"""
from PIL import Image, ImageDraw, ImageFont
import math, os

FONTS = "C:/Users/ednas/AppData/Roaming/Claude/local-agent-mode-sessions/skills-plugin/83bdf9b6-1194-411d-bbc2-7e8a40472731/b00f4908-137d-494b-9ad4-744ef48bcf46/skills/canvas-design/canvas-fonts"

W, H = 1240, 1754

# Refined palette — colder, more precise
BG          = (9, 10, 13)
LINE_GHOST  = (20, 22, 29)
LINE_DIM    = (34, 38, 50)
LINE_MID    = (58, 65, 82)
LINE_BRIGHT = (98, 108, 134)
AMBER       = (208, 134, 38)
AMBER_DIM   = (120, 76, 18)
AMBER_GHOST = (60, 38, 10)
WHITE       = (235, 239, 246)
MUTED       = (82, 90, 112)
GHOST       = (38, 42, 56)

img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

def font(name, size):
    try:
        return ImageFont.truetype(os.path.join(FONTS, name), size)
    except:
        return ImageFont.load_default()

f_mono_xs   = font("IBMPlexMono-Regular.ttf", 10)
f_mono_sm   = font("IBMPlexMono-Regular.ttf", 13)
f_jura_sm   = font("Jura-Light.ttf", 15)
f_jura_md   = font("Jura-Medium.ttf", 19)
f_gloock_xl = font("Gloock-Regular.ttf", 80)
f_gloock_sm = font("Gloock-Regular.ttf", 22)
f_instrument= font("InstrumentSans-Regular.ttf", 11)
f_jura_lg   = font("Jura-Light.ttf", 36)

# ── Grid — invisible foundation ──────────────────────────
GRID = 62
for x in range(0, W, GRID):
    draw.line([(x, 0), (x, H)], fill=LINE_GHOST, width=1)
for y in range(0, H, GRID):
    draw.line([(0, y), (W, y)], fill=LINE_GHOST, width=1)

# ── Structural constants ──────────────────────────────────
MARGIN_TOP = 195
MARGIN_BOT = H - 250
APEX_X = W // 2
APEX_Y = MARGIN_BOT
FUNNEL_HEIGHT = MARGIN_BOT - MARGIN_TOP

# Golden ratio threshold
PHI = 0.618
THRESHOLD_Y = int(MARGIN_TOP + PHI * FUNNEL_HEIGHT)
THRESHOLD_HW = int((W / 2 - 60) * (1.0 - PHI))  # half-width at threshold

# ── Converging line fan ───────────────────────────────────
N = 56
SPREAD_TOP = W * 0.48  # half-spread at top

for i in range(N):
    t = i / (N - 1)
    # Offset from center at top — non-linear (root) spacing for density feel
    offset = SPREAD_TOP * math.pow(t * 2 - 1 if t > 0.5 else -(1 - t * 2), 1)

    # left half
    for side in [-1, 1]:
        sx = APEX_X + side * SPREAD_TOP * t
        sy = MARGIN_TOP - 20
        ex = APEX_X
        ey = APEX_Y

        # Brightness = lines near center edges are brightest
        dist_from_center = abs(t - 0.5)  # 0 at center, 0.5 at edges
        # Penultimate lines are brightest
        brightness = 1.0 - abs(dist_from_center - 0.18) / 0.32
        brightness = max(0.05, min(1.0, brightness))

        r = int(LINE_DIM[0] + brightness * (LINE_BRIGHT[0] - LINE_DIM[0]))
        g = int(LINE_DIM[1] + brightness * (LINE_BRIGHT[1] - LINE_DIM[1]))
        b = int(LINE_DIM[2] + brightness * (LINE_BRIGHT[2] - LINE_DIM[2]))

        draw.line([(int(sx), int(sy)), (ex, ey)], fill=(r, g, b), width=1)
        break  # both sides handled via side parameter
    # Re-do properly:
for i in range(N):
    t = i / (N - 1)
    sx_left  = int(APEX_X - SPREAD_TOP * t)
    sx_right = int(APEX_X + SPREAD_TOP * t)
    sy = MARGIN_TOP - 20

    dist_from_extreme = 1.0 - abs(t - 0.5) * 2
    brightness = 0.1 + 0.8 * (1.0 - (1.0 - dist_from_extreme) ** 2)

    r = int(LINE_DIM[0] + brightness * (LINE_BRIGHT[0] - LINE_DIM[0]))
    g = int(LINE_DIM[1] + brightness * (LINE_BRIGHT[1] - LINE_DIM[1]))
    b_ch = int(LINE_DIM[2] + brightness * (LINE_BRIGHT[2] - LINE_DIM[2]))
    col = (r, g, b_ch)

    draw.line([(sx_left, sy), (APEX_X, APEX_Y)], fill=col, width=1)
    draw.line([(sx_right, sy), (APEX_X, APEX_Y)], fill=col, width=1)

# ── Top spread rule ───────────────────────────────────────
spread_y = MARGIN_TOP - 20
draw.line(
    [(int(APEX_X - SPREAD_TOP), spread_y),
     (int(APEX_X + SPREAD_TOP), spread_y)],
    fill=LINE_MID, width=1
)
# End tick marks
for sign in [-1, 1]:
    tx = int(APEX_X + sign * SPREAD_TOP)
    draw.line([(tx, spread_y - 8), (tx, spread_y + 8)], fill=LINE_MID, width=1)

# ── Threshold amber band ──────────────────────────────────
# Three-line amber passage: ghost / main / ghost
for dy, col, w in [(-2, AMBER_GHOST, 1), (-1, AMBER_DIM, 1),
                    (0, AMBER, 2),
                    (1, AMBER_DIM, 1), (2, AMBER_GHOST, 1)]:
    draw.line(
        [(APEX_X - THRESHOLD_HW, THRESHOLD_Y + dy),
         (APEX_X + THRESHOLD_HW, THRESHOLD_Y + dy)],
        fill=col, width=w
    )

# Threshold bracket ticks
for sign in [-1, 1]:
    tx = APEX_X + sign * THRESHOLD_HW
    draw.line([(tx, THRESHOLD_Y - 14), (tx, THRESHOLD_Y + 14)], fill=AMBER, width=2)
    # Outer ghost
    draw.line([(tx + sign * 6, THRESHOLD_Y - 10), (tx + sign * 6, THRESHOLD_Y + 10)],
              fill=AMBER_DIM, width=1)

# ── Apex — decision point ─────────────────────────────────
r1, r2, r3 = 4, 12, 28
draw.ellipse([(APEX_X-r3, APEX_Y-r3), (APEX_X+r3, APEX_Y+r3)],
             outline=AMBER_GHOST, width=1)
draw.ellipse([(APEX_X-r2, APEX_Y-r2), (APEX_X+r2, APEX_Y+r2)],
             outline=AMBER_DIM, width=1)
draw.ellipse([(APEX_X-r1, APEX_Y-r1), (APEX_X+r1, APEX_Y+r1)],
             fill=AMBER, outline=AMBER)

# Cross-hair extending from apex
ch = 40
for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
    start = (APEX_X + dx * (r1 + 4), APEX_Y + dy * (r1 + 4))
    end   = (APEX_X + dx * ch, APEX_Y + dy * ch)
    draw.line([start, end], fill=AMBER_DIM, width=1)

# ── Center dashed axis ────────────────────────────────────
for y in range(spread_y, APEX_Y - r1 - 1, 6):
    if (y // 6) % 2 == 0:
        draw.point((APEX_X, y), fill=LINE_DIM)

# ── Title block ───────────────────────────────────────────
# "LIMIAR" in Gloock — monumental
title = "LIMIAR"
tw = draw.textlength(title, font=f_gloock_xl)
draw.text(((W - tw) / 2, 48), title, font=f_gloock_xl, fill=WHITE)

# "LATENTE" in Jura Light — thin, contrasting
sub = "L  A  T  E  N  T  E"
sw = draw.textlength(sub, font=f_jura_lg)
draw.text(((W - sw) / 2, 150), sub, font=f_jura_lg, fill=MUTED)

# Thin rule under title block
draw.line([(APEX_X - 180, 188), (APEX_X + 180, 188)], fill=LINE_MID, width=1)

# ── Left margin — level annotations ──────────────────────
LEVELS = [
    (MARGIN_TOP - 20,     "N  →  ∞",   "entrada"),
    (int(MARGIN_TOP + 0.28 * FUNNEL_HEIGHT), "triagem",  "fase I"),
    (THRESHOLD_Y,          "limiar",   "0.618"),
    (int(MARGIN_TOP + 0.82 * FUNNEL_HEIGHT), "seleção",  "fase II"),
    (APEX_Y,               "N  →  1",  "decisão"),
]

LABEL_X = 52
for (ly, label_a, label_b) in LEVELS:
    # Connector line to funnel edge
    # Calculate funnel width at this y
    if ly <= APEX_Y and ly >= MARGIN_TOP:
        frac = (ly - MARGIN_TOP) / FUNNEL_HEIGHT
        hw = int(SPREAD_TOP * (1 - frac))
        edge_x = APEX_X - hw
    else:
        edge_x = APEX_X - int(SPREAD_TOP)

    # Short rule from label to funnel
    rule_start = LABEL_X + 90
    draw.line([(rule_start, ly), (max(rule_start + 10, edge_x - 8), ly)],
              fill=LINE_DIM, width=1)

    # Labels
    draw.text((LABEL_X, ly - 14), label_a, font=f_mono_xs, fill=MUTED)
    draw.text((LABEL_X, ly + 2),  label_b, font=f_jura_sm, fill=GHOST)

# ── Right margin — index numbers ──────────────────────────
IDX_X = W - 110
for idx, (ly, _, _) in enumerate(LEVELS):
    num = f"{idx + 1:02d}"
    draw.text((IDX_X, ly - 6), num, font=f_mono_sm, fill=LINE_MID)
    # Connector
    if ly >= MARGIN_TOP and ly <= APEX_Y:
        frac = (ly - MARGIN_TOP) / FUNNEL_HEIGHT
        hw = int(SPREAD_TOP * (1 - frac))
        edge_x = APEX_X + hw
        draw.line([(min(IDX_X - 4, edge_x + 8), ly),
                   (IDX_X - 12, ly)], fill=LINE_DIM, width=1)

# ── Threshold label — amber, centered below line ──────────
thresh_text = "threshold  ·  φ = 0.618"
tt_w = draw.textlength(thresh_text, font=f_mono_sm)
draw.text(((W - tt_w) / 2, THRESHOLD_Y + 18), thresh_text,
          font=f_mono_sm, fill=AMBER_DIM)

# ── Bottom caption block ──────────────────────────────────
bottom_y = H - 175
draw.line([(60, bottom_y), (W - 60, bottom_y)], fill=LINE_MID, width=1)
# Tick marks along bottom rule
for xi in range(9):
    tx = 60 + xi * ((W - 120) // 8)
    draw.line([(tx, bottom_y - 5), (tx, bottom_y + 5)], fill=LINE_MID, width=1)

caption_1 = "fig. I — diagram of an invisible decision"
c1w = draw.textlength(caption_1, font=f_instrument)
draw.text(((W - c1w) / 2, bottom_y + 18), caption_1, font=f_instrument, fill=MUTED)

caption_2 = "SÉRIE: ARQUITETURA OCULTA  ·  PRANCHA 001  ·  MMXXVI"
c2w = draw.textlength(caption_2, font=f_mono_xs)
draw.text(((W - c2w) / 2, bottom_y + 44), caption_2, font=f_mono_xs, fill=LINE_MID)

# ── Final: top rule with coordinates ─────────────────────
top_rule_y = 44
draw.line([(60, top_rule_y), (W - 60, top_rule_y)], fill=LINE_DIM, width=1)
draw.text((62, top_rule_y + 6), "46°31'N  23°47'W", font=f_mono_xs, fill=GHOST)
draw.text((W - 62 - draw.textlength("MMXXVI", font=f_mono_xs), top_rule_y + 6),
          "MMXXVI", font=f_mono_xs, fill=GHOST)

# ── Save ──────────────────────────────────────────────────
out = "C:/Users/ednas/.claude/Aprovai/aprovai-codex/canvas/limiar-latente.png"
img.save(out, "PNG", dpi=(150, 150))
print(f"Refined canvas saved: {out}")
