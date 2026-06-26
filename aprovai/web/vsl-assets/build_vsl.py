#!/usr/bin/env python3
"""Build VSL MP4 from slides + narration using bundled ffmpeg."""
import subprocess, os, sys, imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
ASSETS = os.path.dirname(os.path.abspath(__file__))

# Slide durations per voice (seconds) — total must cover audio length
TIMING = {
    "george":  [6.5,  7.5, 10.0, 12.0, 11.0,  6.5],   # ~53.5s George
    "leticia": [7.5,  9.0, 12.0, 14.0, 12.0,  8.0],    # ~62.5s LeticIA
}

def build(voice: str):
    durs = TIMING[voice]
    audio = os.path.join(ASSETS, f"narration-{voice}.mp3" if voice != "george" else "narration.mp3")
    output = os.path.join(ASSETS, f"vsl-{voice}.mp4")
    concat = os.path.join(ASSETS, "concat_list.txt")

    # Write ffmpeg concat file
    with open(concat, "w", encoding="utf-8") as f:
        for i, d in enumerate(durs, 1):
            slide = os.path.join(ASSETS, f"slide_0{i}.png").replace("\\", "/")
            f.write(f"file '{slide}'\nduration {d}\n")
        # ffmpeg concat needs last entry repeated to avoid 1-frame drop
        last = os.path.join(ASSETS, f"slide_06.png").replace("\\", "/")
        f.write(f"file '{last}'\n")

    cmd = [
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0", "-i", concat,
        "-i", audio,
        "-vf", "scale=1280:720,fps=24",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        output
    ]

    print(f"\n[{voice.upper()}] Building {output}")
    print("CMD:", " ".join(cmd[:8]) + " ...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("STDERR:", result.stderr[-2000:])
        return False
    size = os.path.getsize(output) // 1024
    print(f"[{voice.upper()}] Done: {size} KB -> {output}")
    return True

if __name__ == "__main__":
    voices = sys.argv[1:] if len(sys.argv) > 1 else ["george", "leticia"]
    for v in voices:
        build(v)
