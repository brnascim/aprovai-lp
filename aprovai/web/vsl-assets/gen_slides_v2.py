#!/usr/bin/env python3
"""
Slides VSL v2 — Production Grade Redesign
Clean hierarchy, large type, orange accents, breathing room
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

ASSETS = os.path.dirname(os.path.abspath(__file__))
W, H   = 1280, 720

BG      = (10,  13,  18)
SURFACE = (17,  22,  30)
ORANGE  = (255, 122, 26)
WHITE   = (238, 241, 246)
MUTED   = (95,  108, 128)
DIM     = (42,  52,  66)
RED     = (215, 65,  65)

def font(size, bold=True):
    tries = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf"  if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
    ]
    for p in tries:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def tw(draw, text, fnt):
    return draw.textlength(text, font=fnt)

def centered_x(draw, text, fnt):
    return int((W - tw(draw, text, fnt)) / 2)

def put(draw, x, y, text, fnt, color):
    draw.text((x, y), text, fill=color, font=fnt)

def put_c(draw, y, text, fnt, color):
    draw.text((centered_x(draw, text, fnt), y), text, fill=color, font=fnt)

def put_spaced(draw, y, text, fnt, color, spacing=5):
    """Letter-spaced centered text"""
    chars  = list(text)
    widths = [tw(draw, c, fnt) for c in chars]
    total  = sum(widths) + spacing*(len(chars)-1)
    x = int((W - total)/2)
    for c, cw in zip(chars, widths):
        draw.text((x, y), c, fill=color, font=fnt)
        x += cw + spacing

def glow(draw, cx, cy, color, radius=260, strength=0.18):
    for r in range(radius, 0, -14):
        a = ((radius-r)/radius)**2 * strength
        c = tuple(int(BG[i] + (color[i]-BG[i])*a) for i in range(3))
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=c)

def divider(draw, y, width=200, color=ORANGE, alpha=0.5):
    x = (W - width)//2
    c = tuple(int(BG[i] + (color[i]-BG[i])*alpha) for i in range(3))
    draw.rectangle([x, y, x+width, y+1], fill=c)

def base():
    img  = Image.new("RGB", (W,H), BG)
    draw = ImageDraw.Draw(img)
    # Subtle center radial warmth
    for r in range(620, 0, -16):
        a = ((620-r)/620)**2 * 0.07
        c = tuple(int(BG[i] + ((22,28,40)[i]-BG[i])*a) for i in range(3))
        draw.ellipse([W//2-r, H//2-r*H//W, W//2+r, H//2+r*H//W], fill=c)
    return img, draw

# ─── slides ──────────────────────────────────────────────────────────────────

def slide1():
    """O Problema — 0 respostas"""
    img, draw = base()

    lbl = font(15, bold=False)
    h1  = font(76, bold=True)
    h2  = font(76, bold=True)
    pch = font(100, bold=True)

    glow(draw, W//2, 530, ORANGE, radius=280, strength=0.14)

    put_spaced(draw, 175, "O PROBLEMA", lbl, ORANGE, spacing=5)
    divider(draw, 200)

    put_c(draw, 250, "Voce mandou dezenas", h1, WHITE)
    put_c(draw, 346, "de curriculos.", h1, WHITE)
    put_c(draw, 460, "0 respostas.", pch, ORANGE)

    img.save(os.path.join(ASSETS, "slide_01.png"))
    print("slide_01 OK")

def slide2():
    """O Vilao — Robo em 6 segundos"""
    img, draw = base()

    lbl = font(15, bold=False)
    h1  = font(58, bold=True)
    big = font(200, bold=True)
    sub = font(38, bold=False)

    glow(draw, W//2, 360, ORANGE, radius=340, strength=0.18)

    put_spaced(draw, 130, "QUEM DECIDE", lbl, ORANGE, spacing=5)
    divider(draw, 155)

    put_c(draw, 195, "Um robo decide.", h1, WHITE)

    # Giant "6"
    n_fnt = big
    n_x   = centered_x(draw, "6", n_fnt)
    draw.text((n_x, 228), "6", fill=ORANGE, font=n_fnt)

    # "segundos" below
    draw.text((centered_x(draw,"segundos",sub), 498), "segundos", fill=MUTED, font=sub)

    img.save(os.path.join(ASSETS, "slide_02.png"))
    print("slide_02 OK")

def slide3():
    """ATS — O que o robo analisa"""
    img, draw = base()

    lbl  = font(15, bold=False)
    num  = font(22, bold=False)
    item = font(50, bold=True)
    sub  = font(26, bold=False)

    # Glows FIRST — always before text to avoid overwrite
    glow(draw, W//2, 560, RED, radius=220, strength=0.10)

    put_spaced(draw, 130, "O QUE O ROBO ANALISA", lbl, ORANGE, spacing=5)
    divider(draw, 155)

    items_data = [
        (232, "01", "Palavras-chave"),
        (318, "02", "Formatacao do arquivo"),
        (404, "03", "Ranking por relevancia"),
    ]
    for row_y, n, txt in items_data:
        n_fnt   = font(20, bold=False)
        itm_fnt = font(46, bold=True)
        gap     = 22
        n_w     = int(tw(draw, n, n_fnt))
        t_w     = int(tw(draw, txt, itm_fnt))
        row_w   = n_w + gap + t_w
        x0      = (W - row_w) // 2
        draw.text((x0, row_y + 14), n, fill=ORANGE, font=n_fnt)
        draw.rectangle([x0 + n_w + 7, row_y + 24, x0 + n_w + 14, row_y + 25], fill=DIM)
        draw.text((x0 + n_w + gap, row_y), txt, fill=WHITE, font=itm_fnt)

    # Alert footer text (glow already drawn above)
    put_c(draw, 528, "Qualificado nao e suficiente.", sub, RED)

    img.save(os.path.join(ASSETS, "slide_03.png"))
    print("slide_03 OK")

def slide4():
    """A Solucao — Motor Anti-ATS"""
    img, draw = base()

    lbl  = font(15, bold=False)
    pre  = font(36, bold=False)
    hero = font(108, bold=True)
    sub  = font(30, bold=False)
    det  = font(22, bold=False)

    glow(draw, W//2, 350, ORANGE, radius=340, strength=0.15)

    put_spaced(draw, 120, "A SOLUCAO", lbl, ORANGE, spacing=5)
    divider(draw, 145)

    put_c(draw, 192, "MOTOR", pre, MUTED)
    put_c(draw, 228, "Anti-ATS", hero, WHITE)

    put_c(draw, 412, "Reescreve o curriculo na lingua do robo.", sub, MUTED)
    put_c(draw, 456, "Cole a vaga  —  2 minutos  —  curriculo aprovado.", det, DIM)

    # Pill
    pill_txt = "Por vaga. Ilimitado."
    pfnt = font(20, bold=False)
    ptw  = int(tw(draw, pill_txt, pfnt))
    px   = (W - ptw - 44)//2
    draw.rounded_rectangle([px, 520, px+ptw+44, 558], radius=20,
                            fill=tuple(int(BG[i]+(ORANGE[i]-BG[i])*0.10) for i in range(3)),
                            outline=tuple(int(BG[i]+(ORANGE[i]-BG[i])*0.45) for i in range(3)), width=1)
    put(draw, px+22, 528, pill_txt, pfnt, ORANGE)

    img.save(os.path.join(ASSETS, "slide_04.png"))
    print("slide_04 OK")

def slide5():
    """Preco — R$47"""
    img, draw = base()

    lbl  = font(15, bold=False)
    old  = font(48, bold=False)
    hero = font(158, bold=True)
    sub  = font(26, bold=False)
    det  = font(20, bold=False)

    glow(draw, W//2, 388, ORANGE, radius=340, strength=0.22)

    put_spaced(draw, 120, "INVESTIMENTO", lbl, ORANGE, spacing=5)
    divider(draw, 145)

    # Old price + strikethrough
    old_txt = "R$480"
    ox = centered_x(draw, old_txt, old)
    draw.text((ox, 195), old_txt, fill=MUTED, font=old)
    mid = 195 + old.size//2 - 1
    draw.rectangle([ox, mid, ox+int(tw(draw,old_txt,old)), mid+2], fill=MUTED)

    # Hero price
    put_c(draw, 240, "R$47", hero, ORANGE)

    # Benefits
    put_c(draw, 474, "Acesso perpetuo · Uma unica vez.", sub, MUTED)
    put_c(draw, 512, "7 dias de garantia incondicional.", det, DIM)

    img.save(os.path.join(ASSETS, "slide_05.png"))
    print("slide_05 OK")

def slide6():
    """CTA — Pare de ser descartado"""
    img, draw = base()

    lbl  = font(15, bold=False)
    hero = font(90, bold=True)
    sub  = font(90, bold=True)
    url  = font(30, bold=False)

    # All glows FIRST
    glow(draw, W//2, 360, ORANGE, radius=300, strength=0.12)
    glow(draw, W//2, 510, ORANGE, radius=160, strength=0.12)

    put_spaced(draw, 148, "PROXIMO PASSO", lbl, ORANGE, spacing=5)
    divider(draw, 173)

    put_c(draw, 222, "Pare de ser", hero, WHITE)
    put_c(draw, 324, "descartado.", sub, ORANGE)
    put_c(draw, 490, "mentoriaaprovai.com.br", url, ORANGE)

    img.save(os.path.join(ASSETS, "slide_06.png"))
    print("slide_06 OK")

if __name__ == "__main__":
    slide1(); slide2(); slide3(); slide4(); slide5(); slide6()
    print("All slides generated.")
