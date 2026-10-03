import subprocess
import re

_DURATION_RE = re.compile(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)")


def probe_duration(path):
    out = subprocess.run(
        ["ffmpeg", "-i", path],
        capture_output=True, text=True,
    )
    m = _DURATION_RE.search(out.stderr)
    if not m:
        raise RuntimeError(f"could not read duration from: {path}")
    h, mnt, s = m.groups()
    return int(h) * 3600 + int(mnt) * 60 + float(s)


def generate_placeholder(duration, out_path):
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=0x1a1a2e:s=1080x1920:d={duration}",
        "-r", "30", out_path,
    ], check=True, capture_output=True)
    return out_path


def prepare_scene_clip(src_video, duration, out_path):
    subprocess.run([
        "ffmpeg", "-y", "-stream_loop", "-1", "-i", src_video,
        "-t", str(duration),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
        "-an", out_path,
    ], check=True, capture_output=True)
    return out_path


def mux_scene(video_path, audio_path, out_path):
    subprocess.run([
        "ffmpeg", "-y", "-i", video_path, "-i", audio_path,
        "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-shortest", out_path,
    ], check=True, capture_output=True)
    return out_path


def concat_scenes(scene_paths, out_path):
    list_file = out_path + ".txt"
    with open(list_file, "w") as f:
        for p in scene_paths:
            f.write(f"file '{p}'\n")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file,
        "-c", "copy", out_path,
    ], check=True, capture_output=True)
    return out_path


def burn_subtitles_ass(video_path, ass_path, out_path):
    subprocess.run([
        "ffmpeg", "-y", "-i", video_path,
        "-vf", f"ass={ass_path}",
        "-c:a", "copy", out_path,
    ], check=True, capture_output=True)
    return out_path


def extract_frame(video_path, out_path, timestamp=1.0):
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(timestamp), "-i", video_path,
        "-frames:v", "1", out_path,
    ], check=True, capture_output=True)
    return out_path
