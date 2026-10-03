import asyncio
import base64
import os

import edge_tts
import requests

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
ELEVENLABS_MODEL = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")


async def _synthesize_edge(text, voice, out_path):
    communicate = edge_tts.Communicate(text, voice)
    words = []
    with open(out_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append({
                    "text": chunk["text"],
                    "start": chunk["offset"] / 10_000_000,
                    "end": (chunk["offset"] + chunk["duration"]) / 10_000_000,
                })
    return words


def _synthesize_elevenlabs(text, voice_id, out_path):
    resp = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps",
        headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
        json={"text": text, "model_id": ELEVENLABS_MODEL},
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()

    audio_bytes = base64.b64decode(data["audio_base64"])
    with open(out_path, "wb") as f:
        f.write(audio_bytes)

    alignment = data.get("alignment") or {}
    chars = alignment.get("characters", [])
    starts = alignment.get("character_start_times_seconds", [])
    ends = alignment.get("character_end_times_seconds", [])

    words = []
    current_word = ""
    word_start = None
    word_end = None
    for ch, s, e in zip(chars, starts, ends):
        if ch.isspace():
            if current_word:
                words.append({"text": current_word, "start": word_start, "end": word_end})
                current_word = ""
                word_start = None
        else:
            if word_start is None:
                word_start = s
            current_word += ch
            word_end = e
    if current_word:
        words.append({"text": current_word, "start": word_start, "end": word_end})
    return words


def synthesize(text, voice, out_path, provider=None):
    """Synthesizes narration and returns per-word timestamps (seconds, relative to this clip)."""
    provider = provider or ("elevenlabs" if ELEVENLABS_API_KEY else "edge")
    if provider == "elevenlabs":
        return _synthesize_elevenlabs(text, voice, out_path)
    return asyncio.run(_synthesize_edge(text, voice, out_path))
