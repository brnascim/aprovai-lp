import asyncio
import edge_tts


async def _synthesize(text, voice, out_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(out_path)


def synthesize(text, voice, out_path):
    asyncio.run(_synthesize(text, voice, out_path))
    return out_path
