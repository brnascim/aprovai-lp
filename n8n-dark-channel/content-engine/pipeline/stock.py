import os
import requests

PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
PIXABAY_KEY = os.environ.get("PIXABAY_API_KEY", "")


def _pexels_video(query):
    if not PEXELS_KEY:
        return None
    r = requests.get(
        "https://api.pexels.com/videos/search",
        headers={"Authorization": PEXELS_KEY},
        params={"query": query, "per_page": 5, "orientation": "portrait"},
        timeout=20,
    )
    r.raise_for_status()
    videos = r.json().get("videos", [])
    if not videos:
        return None
    files = sorted(videos[0]["video_files"], key=lambda f: f.get("width", 0))
    for f in files:
        if f.get("width", 0) >= 720:
            return f["link"]
    return files[-1]["link"] if files else None


def _pixabay_video(query):
    if not PIXABAY_KEY:
        return None
    r = requests.get(
        "https://pixabay.com/api/videos/",
        params={"key": PIXABAY_KEY, "q": query, "per_page": 5},
        timeout=20,
    )
    r.raise_for_status()
    hits = r.json().get("hits", [])
    if not hits:
        return None
    videos = hits[0]["videos"]
    best = videos.get("large") or videos.get("medium") or videos.get("small")
    return best["url"] if best else None


def find_clip_url(query):
    return _pexels_video(query) or _pixabay_video(query)


def download(url, dest_path):
    r = requests.get(url, stream=True, timeout=60)
    r.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1 << 16):
            f.write(chunk)
    return dest_path
