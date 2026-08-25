import os
import uuid
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from pipeline import stock, narration, assemble, srt

app = FastAPI(title="Content Engine")
WORKDIR = os.environ.get("CONTENT_ENGINE_WORKDIR", "/tmp/content-engine")


class Cena(BaseModel):
    texto: str
    busca: str


class GerarRequest(BaseModel):
    voz: str = "pt-BR-AntonioNeural"
    cenas: List[Cena]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/videos/{job_id}")
def get_video(job_id: str):
    path = os.path.join(WORKDIR, job_id, "final.mp4")
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="video not found")
    return FileResponse(path, media_type="video/mp4", filename="video.mp4")


@app.post("/generate")
def generate(req: GerarRequest):
    job_id = uuid.uuid4().hex
    job_dir = os.path.join(WORKDIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    scene_clips = []
    timeline = []
    t = 0.0

    for i, cena in enumerate(req.cenas):
        audio_path = os.path.join(job_dir, f"scene{i}.mp3")
        narration.synthesize(cena.texto, req.voz, audio_path)
        duration = assemble.probe_duration(audio_path)

        raw_path = os.path.join(job_dir, f"raw{i}.mp4")
        clip_url = stock.find_clip_url(cena.busca)
        if clip_url:
            stock.download(clip_url, raw_path)
        else:
            assemble.generate_placeholder(duration, raw_path)

        visual_path = os.path.join(job_dir, f"visual{i}.mp4")
        assemble.prepare_scene_clip(raw_path, duration, visual_path)

        scene_path = os.path.join(job_dir, f"scene{i}_final.mp4")
        assemble.mux_scene(visual_path, audio_path, scene_path)
        scene_clips.append(scene_path)

        timeline.append((t, t + duration, cena.texto))
        t += duration

    concat_path = os.path.join(job_dir, "concat.mp4")
    assemble.concat_scenes(scene_clips, concat_path)

    srt_path = os.path.join(job_dir, "captions.srt")
    srt.write_srt(timeline, srt_path)

    final_path = os.path.join(job_dir, "final.mp4")
    assemble.burn_subtitles(concat_path, srt_path, final_path)

    return {"job_id": job_id, "status": "done", "duration": t}
