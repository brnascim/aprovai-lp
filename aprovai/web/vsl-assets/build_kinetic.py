#!/usr/bin/env python3
"""
Kinetic text VSL — 011.video style
Animates large white text over dark background, synced to narration.
Output: vsl-kinetic.mp4 at 1280x720 24fps
"""
import os, sys, math, subprocess
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
ASSETS = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1280, 720, 24
BG     = (10, 13, 18)
ORANGE = (255, 122, 26)
WHITE  = (238, 241, 246)
MUTED  = (120, 128, 140)

def get_font(size, bold=False):
    candidates = [
        ("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        ("C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf"),
    ]
    for p in candidates:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def lerp(a, b, t): return a + (b - a) * t
def ease_out(t): return 1 - (1-t)**3

def render_frame(text_lines, progress, accent_color=WHITE):
    """Render one frame. progress 0-1: fade-in phase 0-0.3, hold 0.3-0.8, fade-out 0.8-1.0"""
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Subtle grid
    for x in range(0, W, 64): draw.line([(x,0),(x,H)], fill=(18,22,30), width=1)
    for y in range(0, H, 64): draw.line([(0,y),(W,y)], fill=(18,22,30), width=1)

    # Opacity based on phase
    if progress < 0.25:
        alpha = ease_out(progress / 0.25)
    elif progress > 0.80:
        alpha = 1.0 - ease_out((progress - 0.80) / 0.20)
    else:
        alpha = 1.0

    # Scale: start at 88%, reach 100% by progress=0.25
    scale = lerp(0.88, 1.0, min(1.0, progress / 0.25))

    for i, (text, size, color) in enumerate(text_lines):
        fnt = get_font(int(size * scale), bold=(color == ORANGE or color == WHITE and size >= 60))
        tw = draw.textlength(text, font=fnt)
        # Vertical offset: slight upward drift during fade-in
        drift = int(lerp(12, 0, min(1.0, progress / 0.25)))
        total_h = len(text_lines) * (size + 12)
        y_base = (H - total_h) // 2 + i * (size + 12) - drift
        x = (W - tw) // 2

        # Apply alpha by blending with background
        r, g, b = color
        br, bg_, bb = BG
        cr = int(lerp(br, r, alpha))
        cg = int(lerp(bg_, g, alpha))
        cb = int(lerp(bb, b, alpha))
        draw.text((x, y_base), text, fill=(cr, cg, cb), font=fnt)

    return img

# Scene definitions: (duration_sec, [(text, font_size, color), ...])
SCENES = [
    (6.5,  [("VOCÊ MANDOU", 88, WHITE),
            ("DEZENAS DE CURRÍCULOS.", 42, MUTED),
            ("", 20, MUTED),
            ("0 respostas.", 52, ORANGE)]),

    (8.0,  [("UM ROBÔ DECIDE", 72, WHITE),
            ("EM 6 SEGUNDOS", 96, ORANGE),
            ("se você passa ou é descartado.", 32, MUTED)]),

    (10.0, [("ELE LÊ POR PALAVRAS-CHAVE.", 52, WHITE),
            ("Tabela e coluna viram texto quebrado.", 30, MUTED),
            ("", 10, MUTED),
            ("Mesmo qualificado = eliminado.", 38, ORANGE)]),

    (13.0, [("MOTOR ANTI-ATS", 76, ORANGE),
            ("reescreve na língua do robô.", 36, WHITE),
            ("", 10, MUTED),
            ("Cola a vaga. 2 minutos. Versão que passa.", 28, MUTED)]),

    (12.0, [("R$47", 120, ORANGE),
            ("Acesso perpétuo. Uma única vez.", 34, WHITE),
            ("", 10, MUTED),
            ("7 dias de garantia incondicional.", 30, MUTED)]),

    (7.5,  [("PARE DE SER", 74, WHITE),
            ("DESCARTADO PELO ROBÔ.", 56, ORANGE),
            ("", 10, MUTED),
            ("mentoriaaprovai.com.br", 28, MUTED)]),
]

def build_kinetic():
    frames_dir = os.path.join(ASSETS, "kinetic_frames")
    os.makedirs(frames_dir, exist_ok=True)

    frame_idx = 0
    total_frames = sum(int(d * FPS) for d, _ in SCENES)
    print(f"Generating {total_frames} frames at {FPS}fps...")

    for scene_i, (duration, lines) in enumerate(SCENES):
        n_frames = int(duration * FPS)
        for f in range(n_frames):
            progress = f / max(n_frames - 1, 1)
            img = render_frame(lines, progress)
            img.save(os.path.join(frames_dir, f"frame_{frame_idx:05d}.png"))
            frame_idx += 1
        print(f"  Scene {scene_i+1}/6 done ({n_frames} frames)")

    print(f"All {frame_idx} frames written. Running ffmpeg...")

    voice  = sys.argv[1] if len(sys.argv) > 1 else "leticia"
    audio  = os.path.join(ASSETS, "narration-leticia.mp3" if voice == "leticia" else "narration.mp3")
    output = os.path.join(ASSETS, f"vsl-kinetic-{voice}.mp4")

    cmd = [
        FFMPEG, "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(frames_dir, "frame_%05d.png"),
        "-i", audio,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        output
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("STDERR:", result.stderr[-1500:])
        return
    size = os.path.getsize(output) // 1024
    print(f"Done: {size} KB -> {output}")

    # Cleanup frames
    import shutil
    shutil.rmtree(frames_dir)
    print("Frames cleaned up.")

if __name__ == "__main__":
    build_kinetic()
