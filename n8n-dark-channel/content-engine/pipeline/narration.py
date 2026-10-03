import asyncio
import os

import edge_tts
import requests

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
ELEVENLABS_MODEL = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")


async def _synthesize_edge(text, voice, out_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(out_path)


def _synthesize_elevenlabs(text, voice_id, out_path):
    resp = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
        json={"text": text, "model_id": ELEVENLABS_MODEL},
        timeout=60,
    )
    resp.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(resp.content)
    return out_path


def synthesize(text, voice, out_path, provider=None):
    provider = provider or ("elevenlabs" if ELEVENLABS_API_KEY else "edge")
    if provider == "elevenlabs":
        return _synthesize_elevenlabs(text, voice, out_path)
    asyncio.run(_synthesize_edge(text, voice, out_path))
    return out_path
