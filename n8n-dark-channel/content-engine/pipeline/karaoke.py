ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Word,DejaVu Sans,90,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,6,0,2,60,60,220,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def _fmt_time(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def build_ass(word_timeline, out_path, width=1080, height=1920):
    lines = [ASS_HEADER.format(width=width, height=height)]
    for word in word_timeline:
        if word["end"] <= word["start"]:
            continue
        text = word["text"].upper().replace("\n", " ").strip()
        if not text:
            continue
        lines.append(
            f"Dialogue: 0,{_fmt_time(word['start'])},{_fmt_time(word['end'])},Word,,0,0,0,,{text}\n"
        )
    with open(out_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    return out_path
