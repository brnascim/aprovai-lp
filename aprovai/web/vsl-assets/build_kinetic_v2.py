#!/usr/bin/env python3
"""
VSL Kinetic v2 — Production Grade
Word-by-word reveals, orange glow accents, professional composition
"""
import os, sys, math, subprocess
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

FFMPEG  = imageio_ffmpeg.get_ffmpeg_exe()
ASSETS  = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1280, 720, 24

BG      = (10,  13,  18)
ORANGE  = (255, 122, 26)
ORANGE2 = (255, 176, 46)
WHITE   = (238, 241, 246)
MUTED   = (95,  108, 128)
DIM     = (45,  55,  70)
RED     = (215, 65,  65)

# ─── helpers ────────────────────────────────────────────────────────────────

def get_font(size, bold=True):
    tries = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/segoeuiz.ttf",
        "C:/Windows/Fonts/arialbd.ttf"  if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
    ]
    for p in tries:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def eoc(t): return 1 - (1-min(1.0,max(0.0,t)))**3      # ease out cubic
def eoq(t): return 1 - (1-min(1.0,max(0.0,t)))**4      # ease out quart

def blend(fg, bg, a):
    a = max(0.0, min(1.0, a))
    return tuple(int(bg[i] + (fg[i]-bg[i])*a) for i in range(3))

def tw(draw, text, font):
    return draw.textlength(text, font=font)

# ─── background ─────────────────────────────────────────────────────────────

def make_bg():
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    # Very subtle vignette (darken corners)
    for r in range(720, 0, -20):
        a = max(0, (720-r)/720 * 0.45)
        c = blend((4, 6, 10), BG, a)
        cx, cy = W//2, H//2
        draw.ellipse([cx-r, cy-r*H//W, cx+r, cy+r*H//W], fill=c)
    return img

# ─── drawing primitives ──────────────────────────────────────────────────────

def put_text(draw, x, y, text, font, color, alpha=1.0, bg_color=None):
    c = blend(color, bg_color or BG, alpha)
    draw.text((x, y), text, fill=c, font=font)

def put_centered(draw, y, text, font, color, alpha=1.0):
    x = int((W - tw(draw, text, font)) / 2)
    put_text(draw, x, y, text, font, color, alpha)

def put_words(draw, y, words, font, color, frame, start_f,
              stagger=4, anim=9, slide=28, accents=None, gap=11):
    """Word-by-word slide-up reveal, centered line"""
    wws   = [tw(draw, w, font) for w in words]
    total = sum(wws) + (len(words)-1)*gap
    x     = int((W - total) / 2)
    for i, (word, ww) in enumerate(zip(words, wws)):
        sf = start_f + i * stagger
        if frame < sf:
            x += ww + gap
            continue
        p  = min(1.0, (frame - sf) / anim)
        a  = eoc(p)
        dy = int((1-eoc(p)) * slide)
        c  = ORANGE if (accents and i in accents) else color
        put_text(draw, x, y - dy, word, font, c, a)
        x += ww + gap

def put_slide(draw, y, text, font, color, frame, start_f, anim=12, slide=35):
    if frame < start_f: return
    p  = min(1.0, (frame - start_f) / anim)
    a  = eoq(p)
    dy = int((1-eoq(p)) * slide)
    put_centered(draw, y - dy, text, font, color, a)

def put_fade(draw, y, text, font, color, frame, start_f, anim=9):
    if frame < start_f: return
    a = eoc(min(1.0, (frame-start_f)/anim))
    put_centered(draw, y, text, font, color, a)

def put_label(draw, y, text, font, color, frame, start_f, anim=8):
    """Fades in + draws a thin underline"""
    if frame < start_f: return
    p = eoc(min(1.0, (frame-start_f)/anim))
    put_centered(draw, y, text, font, color, p)
    # Underline draws from center outward
    line_w = int(tw(draw, text, font) * p)
    if line_w > 0:
        cx = W//2
        y_line = y + font.size + 6
        c = blend(color, BG, p * 0.7)
        draw.rectangle([cx-line_w//2, y_line, cx+line_w//2, y_line+1], fill=c)

def put_glow(img, cx, cy, color=ORANGE, radius=280, strength=0.18):
    """Soft radial glow behind hero element"""
    draw = ImageDraw.Draw(img)
    for r in range(radius, 0, -12):
        a = ((radius-r)/radius)**2 * strength
        c = blend(color, BG, a)
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=c)

def outro_alpha(frame, total):
    """1.0 → 0.0 in last 12 frames"""
    rem = total - frame
    return min(1.0, rem / 12)

# ─── letter-spaced text helper ───────────────────────────────────────────────

def put_spaced(draw, y, text, font, color, spacing=6, alpha=1.0):
    """Render text with extra letter spacing (for labels)"""
    chars  = list(text)
    widths = [tw(draw, c, font) for c in chars]
    total  = sum(widths) + spacing * (len(chars)-1)
    x      = int((W - total) / 2)
    for c, cw in zip(chars, widths):
        put_text(draw, x, y, c, font, color, alpha)
        x += cw + spacing

def put_spaced_animated(draw, y, text, font, color, spacing, frame, start_f, anim=8):
    if frame < start_f: return
    a = eoc(min(1.0, (frame-start_f)/anim))
    put_spaced(draw, y, text, font, color, spacing, a)

# ─── scene definitions ───────────────────────────────────────────────────────

def fs(n): return int(n * FPS)   # seconds → frames

def render_scene(scene_id, frame, total_frames, img):
    draw = ImageDraw.Draw(img)
    oa   = outro_alpha(frame, total_frames)   # global fade-out multiplier
    if oa < 0.01: return

    # ── scene 0: O Problema ──────────────────────────────────────────
    if scene_id == 0:
        f_label = 0
        f_hero1 = fs(0.30)
        f_hero2 = fs(0.90)
        f_punch = fs(2.10)

        lbl_fnt  = get_font(15, bold=False)
        hero_fnt = get_font(78, bold=True)
        pch_fnt  = get_font(96, bold=True)

        # Glow behind counter (appears with punch)
        if frame >= f_punch:
            p = min(1.0, (frame-f_punch)/12)
            put_glow(img, W//2, 505, ORANGE, radius=260, strength=0.16*eoq(p)*oa)

        put_spaced_animated(draw, 178, "O PROBLEMA", lbl_fnt, ORANGE, 6, frame, f_label*oa)
        put_words(draw, 268, ["Voce", "mandou", "dezenas"], hero_fnt, WHITE,
                  frame, f_hero1, accents=[])
        put_words(draw, 358, ["de", "curriculos."], hero_fnt, WHITE,
                  frame, f_hero2)
        put_slide(draw, 462, "0 respostas.", pch_fnt, ORANGE, frame, f_punch)

        # Apply global fade
        if oa < 1.0:
            fade = Image.new("RGB", (W,H), BG)
            img.paste(Image.blend(img, fade, 1-oa))

    # ── scene 1: O Vilao ─────────────────────────────────────────────
    elif scene_id == 1:
        f_label = 0
        f_hero  = fs(0.28)
        f_num   = fs(1.20)
        f_sub   = fs(2.20)

        lbl_fnt = get_font(15, bold=False)
        hro_fnt = get_font(68, bold=True)
        num_fnt = get_font(180, bold=True)
        sub_fnt = get_font(32, bold=False)

        # Giant "6" glow
        if frame >= f_num:
            p = min(1.0, (frame-f_num)/15)
            put_glow(img, W//2, 350, ORANGE, radius=300, strength=0.22*eoq(p)*oa)

        put_spaced_animated(draw, 148, "QUEM DECIDE SEU FUTURO", lbl_fnt, ORANGE, 6, frame, f_label)
        put_words(draw, 222, ["Um", "robo", "decide."], hro_fnt, WHITE,
                  frame, f_hero, accents=[1])

        # Giant "6"
        if frame >= f_num:
            p  = min(1.0,(frame-f_num)/12)
            a  = eoq(p) * oa
            dy = int((1-eoq(p))*40)
            fnt6 = num_fnt
            x6 = int((W - tw(draw,"6",fnt6))/2)
            put_text(draw, x6, 282-dy, "6", fnt6, ORANGE, a)

        put_fade(draw, 492, "segundos para te descartar.", sub_fnt, MUTED, frame, f_sub)

    # ── scene 2: ATS ─────────────────────────────────────────────────
    elif scene_id == 2:
        f_label = 0
        f_i1    = fs(0.35)
        f_i2    = fs(1.10)
        f_i3    = fs(1.85)
        f_alert = fs(2.80)

        lbl_fnt = get_font(15, bold=False)
        itm_fnt = get_font(52, bold=True)
        sub_fnt = get_font(24, bold=False)
        alt_fnt = get_font(30, bold=False)

        put_spaced_animated(draw, 152, "O QUE O ROBO VERIFICA", lbl_fnt, ORANGE, 6, frame, f_label)

        items = [
            (f_i1, 248, "Palavras-chave"),
            (f_i2, 328, "Formatacao do arquivo"),
            (f_i3, 408, "Ranking por relevancia"),
        ]
        for sf, y, txt in items:
            if frame < sf: continue
            p  = min(1.0,(frame-sf)/10)
            a  = eoc(p) * oa
            dy = int((1-eoc(p))*28)
            # Left-aligned with indent for rhythm
            x  = 220
            put_text(draw, x, y-dy, txt, itm_fnt, WHITE, a)
            # Orange bullet
            bx = x - 28
            put_text(draw, bx, y-dy+14, "—", sub_fnt, ORANGE, a)

        # Alert
        if frame >= f_alert:
            p  = min(1.0,(frame-f_alert)/10)
            a  = eoc(p) * oa
            put_centered(draw, 510, "Qualificado nao e suficiente.", alt_fnt, RED, a)

    # ── scene 3: A Solucao ───────────────────────────────────────────
    elif scene_id == 3:
        f_label = 0
        f_hero  = fs(0.30)
        f_name  = fs(0.65)
        f_sub   = fs(1.60)
        f_flow  = fs(2.50)
        f_pill  = fs(3.50)

        lbl_fnt = get_font(15, bold=False)
        pre_fnt = get_font(38, bold=False)
        nme_fnt = get_font(100, bold=True)
        sub_fnt = get_font(30, bold=False)
        pil_fnt = get_font(22, bold=False)

        # Glow behind name
        if frame >= f_name:
            p = min(1.0,(frame-f_name)/14)
            put_glow(img, W//2, 360, ORANGE, radius=320, strength=0.14*eoc(p)*oa)

        put_spaced_animated(draw, 138, "A SOLUCAO", lbl_fnt, ORANGE, 6, frame, f_label)

        put_words(draw, 210, ["MOTOR"], pre_fnt, MUTED, frame, f_hero)
        put_slide(draw, 258, "Anti-ATS", nme_fnt, WHITE, frame, f_name)

        put_fade(draw, 430, "Reescreve o curriculo na lingua do robo.", sub_fnt, MUTED, frame, f_sub)
        put_fade(draw, 480, "Cole a vaga  —  2 minutos  —  curriculo aprovado.", pil_fnt, DIM, frame, f_flow)

        if frame >= f_pill:
            p  = min(1.0,(frame-f_pill)/10)
            a  = eoc(p) * oa
            pill_txt = "Por vaga. Ilimitado."
            pfnt = get_font(20, bold=False)
            ptw = int(tw(draw, pill_txt, pfnt))
            px  = (W - ptw - 40)//2
            py  = 552
            draw.rounded_rectangle([px, py, px+ptw+40, py+36], radius=18,
                                    fill=blend(ORANGE, BG, 0.12*a),
                                    outline=blend(ORANGE, BG, 0.5*a), width=1)
            put_text(draw, px+20, py+8, pill_txt, pfnt, ORANGE, a)

    # ── scene 4: Preco ───────────────────────────────────────────────
    elif scene_id == 4:
        f_label = 0
        f_old   = fs(0.30)
        f_price = fs(0.95)
        f_sub   = fs(1.70)
        f_guar  = fs(2.30)

        lbl_fnt = get_font(15, bold=False)
        old_fnt = get_font(48, bold=False)
        prc_fnt = get_font(148, bold=True)
        sub_fnt = get_font(26, bold=False)
        gur_fnt = get_font(22, bold=False)

        if frame >= f_price:
            p = min(1.0,(frame-f_price)/14)
            put_glow(img, W//2, 388, ORANGE, radius=310, strength=0.2*eoq(p)*oa)

        put_spaced_animated(draw, 138, "INVESTIMENTO", lbl_fnt, ORANGE, 6, frame, f_label)

        # Old price with strikethrough
        if frame >= f_old:
            p  = min(1.0,(frame-f_old)/9)
            a  = eoc(p) * oa
            old_txt = "R$480"
            otw = int(tw(draw, old_txt, old_fnt))
            ox  = (W - otw)//2
            oy  = 212
            put_text(draw, ox, oy, old_txt, old_fnt, MUTED, a)
            # Strikethrough line
            mid_y = oy + old_fnt.size//2 - 2
            sw = int(otw * min(1.0, (frame-f_old)/(5)))
            if sw > 0:
                lc = blend(MUTED, BG, a * 0.8)
                draw.rectangle([ox, mid_y, ox+sw, mid_y+2], fill=lc)

        # New price
        put_slide(draw, 252, "R$47", prc_fnt, ORANGE, frame, f_price)
        put_fade(draw, 468, "Acesso perpetuo · Uma unica vez.", sub_fnt, MUTED, frame, f_sub)
        put_fade(draw, 510, "7 dias de garantia incondicional.", gur_fnt, DIM, frame, f_guar)

    # ── scene 5: CTA ─────────────────────────────────────────────────
    elif scene_id == 5:
        f_label = 0
        f_hero1 = fs(0.28)
        f_hero2 = fs(1.05)
        f_url   = fs(1.80)

        lbl_fnt = get_font(15, bold=False)
        hro_fnt = get_font(84, bold=True)
        url_fnt = get_font(30, bold=False)

        put_spaced_animated(draw, 168, "PROXIMO PASSO", lbl_fnt, ORANGE, 6, frame, f_label)
        put_words(draw, 268, ["Pare", "de", "ser"], hro_fnt, WHITE,
                  frame, f_hero1, accents=[])
        put_words(draw, 368, ["descartado", "pelo", "robo."], hro_fnt, WHITE,
                  frame, f_hero2, accents=[0])

        if frame >= f_url:
            p = min(1.0,(frame-f_url)/12)
            a = eoq(p)*oa
            put_glow(img, W//2, 510, ORANGE, radius=180, strength=0.12*a)
            put_centered(draw, 495, "mentoriaaprovai.com.br", url_fnt, ORANGE, a)

# ─── render pipeline ─────────────────────────────────────────────────────────

DURATIONS = [7.5, 9.0, 12.0, 14.0, 12.0, 8.0]     # seconds each scene

def build(voice="leticia"):
    audio  = os.path.join(ASSETS, "narration-leticia.mp3" if voice=="leticia" else "narration.mp3")
    output = os.path.join(ASSETS, f"vsl-kinetic-{voice}-v2.mp4")
    frames_dir = os.path.join(ASSETS, "frames_v2")
    os.makedirs(frames_dir, exist_ok=True)

    total_frames = sum(int(d*FPS) for d in DURATIONS)
    print(f"Rendering {total_frames} frames ({sum(DURATIONS):.0f}s)...")

    frame_idx = 0
    for scene_id, dur in enumerate(DURATIONS):
        n = int(dur * FPS)
        for f in range(n):
            img  = make_bg()
            render_scene(scene_id, f, n, img)
            img.save(os.path.join(frames_dir, f"f{frame_idx:05d}.png"))
            frame_idx += 1
        print(f"  Scene {scene_id+1}/6 OK ({n}fr)")

    print("Running ffmpeg...")
    cmd = [
        FFMPEG, "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(frames_dir, "f%05d.png"),
        "-i", audio,
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest", output
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ERROR:", r.stderr[-1500:])
        return
    import shutil; shutil.rmtree(frames_dir)
    sz = os.path.getsize(output)//1024
    print(f"Done: {sz} KB -> {output}")

if __name__ == "__main__":
    v = sys.argv[1] if len(sys.argv)>1 else "leticia"
    build(v)
