def _fmt(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(timeline, out_path):
    with open(out_path, "w", encoding="utf-8") as f:
        for i, (start, end, text) in enumerate(timeline, 1):
            f.write(f"{i}\n{_fmt(start)} --> {_fmt(end)}\n{text}\n\n")
    return out_path
