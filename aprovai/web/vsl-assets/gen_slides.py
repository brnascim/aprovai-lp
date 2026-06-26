#!/usr/bin/env python3
"""
Generate VSL slide images for Roteiro A — "Não é você, é o robô"
Output: 6 PNG frames at 1280x720, brand colors #0A0D12 / #FF7A1A / #34D399
"""
from PIL import Image, ImageDraw, ImageFont
import os, textwrap, math

OUT = os.path.dirname(os.path.abspath(__file__))
W, H = 1280, 720

# Brand palette
BG       = (10, 13, 18)        # #0A0D12
SURFACE  = (19, 23, 30)        # #13171E
ORANGE   = (255, 122, 26)      # #FF7A1A
ORANGE2  = (255, 176, 46)      # #FFB02E
TRUST    = (52, 211, 153)      # #34D399
WHITE    = (238, 241, 246)     # #EEF1F6
MUTED    = (140, 148, 163)     # muted text
STRIKE   = (180, 50, 50)       # strikethrough red

def get_font(size, bold=False):
    """Try to get a good system font, fall back to default."""
    font_candidates_bold = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]
    font_candidates = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]
    candidates = font_candidates_bold if bold else font_candidates
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()

def make_base(img=None):
    """Create base dark background with subtle grid and glow."""
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Subtle grid
    for x in range(0, W, 48):
        draw.line([(x, 0), (x, H)], fill=(30, 35, 45), width=1)
    for y in range(0, H, 48):
        draw.line([(0, y), (W, y)], fill=(30, 35, 45), width=1)

    # Top-right orange glow (radial simulation with ellipses)
    for r in range(200, 0, -20):
        alpha = int(8 * (1 - r/200))
        cx, cy = W + 100, -80
        draw.ellipse([cx-r*3, cy-r*3, cx+r*3, cy+r*3],
                     outline=None,
                     fill=(255, 122, 26, 0))  # PIL RGB mode, skip alpha

    # Logo top-left
    draw_logo(draw)
    # Badge top-right
    draw_badge(draw)

    return img, draw

def draw_logo(draw):
    fnt = get_font(22, bold=True)
    draw.rounded_rectangle([40, 28, 82, 70], radius=10, fill=ORANGE)
    draw.text((61, 49), "✓", fill=BG, font=get_font(18, bold=True), anchor="mm")
    draw.text((92, 49), "Aprova", fill=WHITE, font=fnt, anchor="lm")
    draw.text((92 + draw.textlength("Aprova", font=fnt), 49), "í", fill=ORANGE, font=fnt, anchor="lm")

def draw_badge(draw):
    fnt = get_font(13, bold=True)
    txt = "MOTOR ANTI-ATS"
    tw = draw.textlength(txt, font=fnt)
    # dot
    draw.ellipse([W - 40 - tw - 20, 44, W - 40 - tw - 11, 53], fill=ORANGE)
    draw.text((W - 40 - tw, 48), txt, fill=ORANGE, font=fnt, anchor="lm")

def centered_text(draw, y, text, font, color=WHITE, max_width=None):
    """Draw centered text, with optional word-wrap."""
    if max_width:
        # Estimate chars per line
        avg_char = draw.textlength("W", font=font)
        chars_per = max(10, int(max_width / avg_char))
        lines = textwrap.wrap(text, width=chars_per)
    else:
        lines = [text]
    line_h = font.size + 8
    for i, line in enumerate(lines):
        tw = draw.textlength(line, font=font)
        draw.text(((W - tw) / 2, y + i * line_h), line, fill=color, font=font)
    return y + len(lines) * line_h

def vline_accent(draw, x, y1, y2, color=ORANGE):
    draw.rectangle([x, y1, x+3, y2], fill=color)


# ── SCENE 1: Hook — "0 respostas" ──────────────────────────────────────────
def scene1():
    img, draw = make_base()
    f_big  = get_font(84, bold=True)
    f_med  = get_font(36)
    f_sm   = get_font(22)

    # "VOCÊ MANDOU"
    centered_text(draw, 180, "VOCÊ MANDOU", f_big, WHITE)
    centered_text(draw, 280, "DEZENAS DE CURRÍCULOS.", f_med, MUTED)

    # Counter block
    draw.rounded_rectangle([W//2 - 140, 360, W//2 + 140, 460], radius=16, fill=SURFACE)
    centered_text(draw, 380, "0 respostas", get_font(40, bold=True), ORANGE)

    centered_text(draw, 490, 'Nem um "nao". Nem um "talvez".', f_sm, MUTED)
    img.save(os.path.join(OUT, "slide_01.png"))
    print("slide_01.png OK")


# ── SCENE 2: ATS — 6 segundos ──────────────────────────────────────────────
def scene2():
    img, draw = make_base()
    f_big = get_font(72, bold=True)
    f_med = get_font(34)
    f_sm  = get_font(20)

    centered_text(draw, 160, "UM ROBÔ DECIDE", f_big, WHITE)
    centered_text(draw, 255, "EM  6  SEGUNDOS", get_font(64, bold=True), ORANGE)
    centered_text(draw, 355, "se você passa ou é descartado.", f_med, MUTED)

    # ATS pill
    pill_w, pill_h = 260, 64
    px = (W - pill_w) // 2
    py = 435
    draw.rounded_rectangle([px, py, px+pill_w, py+pill_h], radius=32, fill=SURFACE)
    draw.rounded_rectangle([px, py, px+pill_w, py+pill_h], radius=32, outline=ORANGE, width=2)
    centered_text(draw, py+18, "ATS — Applicant Tracking System", get_font(18, bold=True), ORANGE)

    img.save(os.path.join(OUT, "slide_02.png"))
    print("slide_02.png OK")


# ── SCENE 3: Como o ATS elimina ─────────────────────────────────────────────
def scene3():
    img, draw = make_base()
    f_title = get_font(38, bold=True)
    f_card  = get_font(22, bold=True)
    f_desc  = get_font(17)

    centered_text(draw, 130, "Como o robô te elimina:", f_title, WHITE)

    cards = [
        ("🔑", "PALAVRAS-CHAVE", "Seu currículo não usa os termos da vaga"),
        ("⊞",  "FORMATAÇÃO",    "Tabela e coluna viram texto quebrado"),
        ("↓",  "RANKING",       "Abaixo do corte — ninguém te vê"),
    ]
    card_w, card_h = 320, 200
    gap = 40
    total_w = 3*card_w + 2*gap
    start_x = (W - total_w) // 2

    for i, (icon, title, desc) in enumerate(cards):
        cx = start_x + i*(card_w + gap)
        cy = 220
        # Card bg
        draw.rounded_rectangle([cx, cy, cx+card_w, cy+card_h], radius=14, fill=SURFACE)
        # Top accent bar
        draw.rounded_rectangle([cx, cy, cx+card_w, cy+5], radius=0, fill=ORANGE)
        # Icon
        draw.text((cx + card_w//2, cy + 55), icon, fill=ORANGE, font=get_font(34), anchor="mm")
        # Title
        tw = draw.textlength(title, font=f_card)
        draw.text((cx + (card_w - tw)//2, cy + 100), title, fill=WHITE, font=f_card)
        # Desc (wrapped)
        words = desc.split()
        lines = []
        line = ""
        for w in words:
            test = (line + " " + w).strip()
            if draw.textlength(test, font=f_desc) < card_w - 20:
                line = test
            else:
                lines.append(line)
                line = w
        lines.append(line)
        for j, ln in enumerate(lines):
            tw = draw.textlength(ln, font=f_desc)
            draw.text((cx + (card_w-tw)//2, cy + 135 + j*22), ln, fill=MUTED, font=f_desc)

    centered_text(draw, 460, "Mesmo qualificado = eliminado.", get_font(24, bold=True), (240, 80, 80))
    img.save(os.path.join(OUT, "slide_03.png"))
    print("slide_03.png OK")


# ── SCENE 4: Motor Anti-ATS — mecanismo ─────────────────────────────────────
def scene4():
    img, draw = make_base()
    f_big  = get_font(56, bold=True)
    f_med  = get_font(26)

    centered_text(draw, 130, "MOTOR ANTI-ATS", f_big, ORANGE)
    centered_text(draw, 210, "Reescreve na língua que o robô entende.", f_med, WHITE)

    # Flow: Cola vaga → Motor → Versão aprovada
    steps = ["Cola a vaga", "Cola seu currículo", "2 min →", "Versao que passa [OK]"]
    colors = [MUTED, MUTED, ORANGE, TRUST]
    f_step = get_font(22, bold=True)
    total_w = sum(draw.textlength(s, font=f_step) for s in steps) + 3*80
    sx = (W - total_w) // 2
    sy = 330
    for i, (step, col) in enumerate(zip(steps, colors)):
        draw.text((sx, sy), step, fill=col, font=f_step)
        sx += draw.textlength(step, font=f_step)
        if i < len(steps)-1:
            draw.text((sx + 10, sy), " → ", fill=MUTED, font=f_step)
            sx += draw.textlength(" → ", font=f_step) + 10

    # Pill "Por vaga — em 2 minutos"
    draw.rounded_rectangle([W//2-220, 410, W//2+220, 470], radius=30, fill=ORANGE)
    centered_text(draw, 425, "Por vaga. Em 2 minutos.", get_font(24, bold=True), BG)

    img.save(os.path.join(OUT, "slide_04.png"))
    print("slide_04.png OK")


# ── SCENE 5: Oferta + Garantia ───────────────────────────────────────────────
def scene5():
    img, draw = make_base()

    f_price_strike = get_font(42)
    f_price_main   = get_font(110, bold=True)
    f_med          = get_font(26, bold=True)
    f_sm           = get_font(20)

    # Strikethrough R$480
    draw.text((W//2 - 180, 140), "de R$480", fill=MUTED, font=f_price_strike)
    # Strikethrough line
    tw480 = draw.textlength("de R$480", font=f_price_strike)
    sx480 = W//2 - 180
    mid_y = 140 + f_price_strike.size//2
    draw.line([(sx480, mid_y), (sx480 + tw480, mid_y)], fill=STRIKE, width=3)

    # R$47 BIG
    centered_text(draw, 190, "R$47", f_price_main, ORANGE)

    # "Uma única vez. Acesso perpétuo."
    centered_text(draw, 330, "Acesso perpétuo  •  Uma única vez", f_med, WHITE)

    # Guarantee cards
    guar = [
        ("7 DIAS", "DE GARANTIA"),
        ("SEM", "PERGUNTAS"),
        ("BÔNUS", "FICAM"),
    ]
    cw, ch = 270, 100
    gx = (W - 3*cw - 2*30) // 2
    for i, (top, bot) in enumerate(guar):
        cx = gx + i*(cw+30)
        cy = 430
        draw.rounded_rectangle([cx, cy, cx+cw, cy+ch], radius=12, fill=SURFACE)
        draw.rounded_rectangle([cx, cy, cx+cw, cy+5], radius=0, fill=TRUST)
        tw = draw.textlength(top, font=get_font(20, bold=True))
        draw.text((cx + (cw-tw)//2, cy+20), top, fill=TRUST, font=get_font(20, bold=True))
        tw2 = draw.textlength(bot, font=get_font(16))
        draw.text((cx + (cw-tw2)//2, cy+55), bot, fill=MUTED, font=get_font(16))

    img.save(os.path.join(OUT, "slide_05.png"))
    print("slide_05.png OK")


# ── SCENE 6: CTA ─────────────────────────────────────────────────────────────
def scene6():
    img, draw = make_base()
    f_big  = get_font(52, bold=True)
    f_med  = get_font(28)

    centered_text(draw, 160, "PARE DE SER DESCARTADO", f_big, WHITE)
    centered_text(draw, 235, "pelo robô.", f_big, ORANGE)

    # Big CTA button
    btn_w, btn_h = 700, 90
    bx = (W - btn_w) // 2
    by = 360
    draw.rounded_rectangle([bx, by, bx+btn_w, by+btn_h], radius=45, fill=ORANGE)
    centered_text(draw, by+24, "Quero passar pelo robô — R$47", get_font(28, bold=True), BG)

    centered_text(draw, 480, "mentoriaaprovai.com.br", f_med, MUTED)

    img.save(os.path.join(OUT, "slide_06.png"))
    print("slide_06.png OK")


if __name__ == "__main__":
    scene1(); scene2(); scene3()
    scene4(); scene5(); scene6()
    print("All slides generated.")
