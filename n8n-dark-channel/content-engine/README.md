# Content Engine — motor de vídeo 100% gratuito

Serviço próprio que substitui a MoviAPI/Veo3 (paga) por um pipeline gratuito:
**roteiro → voz (Edge-TTS) → visual (Pexels/Pixabay) → montagem + legenda (FFmpeg)**.

Inspirado na lógica do [VUZA](https://github.com/AliRash3ed/VUZA-Free-AI-Video-Creator-and-Pinterest-Video-Scraper)
(stock gratuito + Edge-TTS, sem GPU), mas reescrito do zero como API própria (MIT, sem
restrição de licença comercial) pra poder ser chamado direto pelo n8n.

> Testado nesta sessão: geração de vídeo vertical 1080x1920 com legenda queimada e
> sincronizada, ponta a ponta, usando FFmpeg puro — sem depender de licença de terceiros.
> A parte de rede (Pexels/Pixabay/Edge-TTS) usa APIs públicas estáveis e bem documentadas;
> teste com suas chaves reais na sua VPS antes de rodar em produção.

## Requisitos

- VPS com acesso root/SSH (você já tem — a mesma onde roda o n8n)
- Python 3.10+
- FFmpeg (`apt install ffmpeg` — traz `ffmpeg` e `ffprobe` juntos)
- **Nenhuma GPU necessária**

## Chaves gratuitas necessárias

| Serviço | Onde pegar | Custo |
|---|---|---|
| Pexels API | https://www.pexels.com/api/ (cadastro grátis) | R$0 |
| Pixabay API | https://pixabay.com/api/docs/ (cadastro grátis) | R$0 |
| Edge-TTS | Nenhuma chave — usa a voz do Microsoft Edge de graça | R$0 |

O único custo real do sistema continua sendo os **poucos centavos** das chamadas de
roteiro no OpenAI (gpt-4o-mini) já configuradas no workflow n8n — pode trocar por um
modelo local via Ollama se quiser custo zero absoluto, mas o ganho de qualidade do
roteiro geralmente compensa o centavo.

## Instalação na VPS

```bash
# 1. Dependências do sistema
apt update && apt install -y python3 python3-pip ffmpeg

# 2. Código
cd /opt
git clone <seu-fork-ou-copie-esta-pasta> content-engine
cd content-engine

# 3. Dependências Python
pip install -r requirements.txt

# 4. Variáveis de ambiente
cp .env.example .env
# edite .env e cole PEXELS_API_KEY e PIXABAY_API_KEY

# 5. Suba o serviço (teste manual)
export $(cat .env | xargs)
python3 -m uvicorn app:app --host 0.0.0.0 --port 8787
```

Teste rápido:
```bash
curl http://localhost:8787/health
# {"status":"ok"}
```

### Rodando permanentemente (systemd)

Crie `/etc/systemd/system/content-engine.service`:

```ini
[Unit]
Description=Content Engine
After=network.target

[Service]
WorkingDirectory=/opt/content-engine
EnvironmentFile=/opt/content-engine/.env
ExecStart=/usr/bin/python3 -m uvicorn app:app --host 127.0.0.1 --port 8787
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable --now content-engine
```

Mantenha `--host 127.0.0.1` (não exponha pra internet) — o n8n roda na mesma VPS e
acessa via `localhost:8787`. Se n8n estiver em outro container/Docker, use a rede
interna do Docker em vez de `127.0.0.1`.

## API

### `POST /generate`
```json
{
  "voz": "pt-BR-AntonioNeural",
  "cenas": [
    { "texto": "Você está afogado em dívidas...", "busca": "worried person bills" }
  ]
}
```
Retorna `{"job_id": "...", "status": "done", "duration": 45.2}` (processamento é
síncrono — a chamada só responde quando o vídeo termina).

### `GET /videos/{job_id}`
Retorna o binário do MP4 final (1080x1920, legenda queimada).

## Vozes Edge-TTS em português

`pt-BR-AntonioNeural` (masculina) e `pt-BR-FranciscaNeural` (feminina) — mesma
qualidade de voz que a Azure Neural usada por ferramentas pagas, só que grátis.
Liste todas com `edge-tts --list-voices | grep pt-BR`.

## Limitações honestas

- CPU-only: cada Short leva ~30–90s pra renderizar (aceitável pra 3–5 vídeos/dia).
- Sem avatar/rosto de IA — é o formato "narração sobre imagens/vídeos reais", que foi
  o formato escolhido para o teste inicial.
- Se quiser testar o formato de avatar depois (SamurAIGPT/AI-Influencer-Generator),
  isso exige GPU — trate como uma fase separada, não bloqueie o lançamento por isso.
