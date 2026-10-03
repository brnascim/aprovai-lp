from PIL import Image, ImageDraw, ImageFont

from pipeline import assemble

_FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]


def _load_font(size):
    for path in _FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap_text(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def generate(video_path, text, out_path, timestamp=1.0):
    frame_path = out_path + ".frame.jpg"
    assemble.extract_frame(video_path, frame_path, timestamp)

    img = Image.open(frame_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    font_size = int(img.width * 0.09)
    font = _load_font(font_size)
    max_width = img.width * 0.88
    lines = _wrap_text(draw, text.upper(), font, max_width)

    line_height = font_size * 1.15
    total_height = line_height * len(lines)
    y = img.height * 0.6 - total_height / 2

    outline = max(2, font_size // 18)
    for line in lines:
        w = draw.textlength(line, font=font)
        x = (img.width - w) / 2
        for dx in range(-outline, outline + 1):
            for dy in range(-outline, outline + 1):
                if dx or dy:
                    draw.text((x + dx, y + dy), line, font=font, fill="black")
        draw.text((x, y), line, font=font, fill="white")
        y += line_height

    img.save(out_path, "JPEG", quality=90)
    return out_path
