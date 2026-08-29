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
apt update && apt install -y python3 python3-pip python3-venv ffmpeg git

# 2. Código (clona o repo direto do GitHub)
cd /opt
git clone -b claude/n8n-video-production-nk56hl https://github.com/brnascim/aprovai-lp.git
cd aprovai-lp/n8n-dark-channel/content-engine

# 3. Ambiente virtual + dependências Python
#    (obrigatório em Debian/Ubuntu recentes — "pip install" direto no sistema
#    falha com "externally-managed-environment")
python3 -m venv venv
venv/bin/pip install -r requirements.txt

# 4. Variáveis de ambiente
cp .env.example .env
# edite .env e cole PEXELS_API_KEY (PIXABAY_API_KEY pode ficar em branco — é opcional,
# o sistema cai automaticamente pra Pexels-only ou fundo sólido se faltar)
nano .env

# 5. Suba o serviço (teste manual)
set -a; source .env; set +a
venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port 8787
```

Teste rápido (em outro terminal SSH, com o comando acima ainda rodando):
```bash
curl http://localhost:8787/health
# {"status":"ok"}
```
Encerre o teste manual com `Ctrl+C` antes de seguir pro systemd.

### Rodando permanentemente (systemd)

Crie `/etc/systemd/system/content-engine.service`:

```ini
[Unit]
Description=Content Engine
After=network.target

[Service]
WorkingDirectory=/opt/aprovai-lp/n8n-dark-channel/content-engine
EnvironmentFile=/opt/aprovai-lp/n8n-dark-channel/content-engine/.env
ExecStart=/opt/aprovai-lp/n8n-dark-channel/content-engine/venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port 8787
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable --now content-engine
systemctl status content-engine   # confirme "active (running)"
curl http://localhost:8787/health
```

### ⚠️ Se o n8n rodar em Docker (gotcha comum)

`localhost` dentro de um container Docker **não é** o host da VPS — é o próprio
container. Se o n8n estiver containerizado e o content-engine rodando direto na VPS
(fora do Docker, como acima), descubra o IP do gateway Docker e use-o no lugar de
`localhost` no nó **Escolher Tema** do workflow:

```bash
# dentro do container do n8n (ou via docker exec):
ip route | grep default   # ex: "default via 172.17.0.1" → esse é o gateway
```
Use `http://172.17.0.1:8787` (ou o IP que aparecer) no campo `content_engine_url`.
Se o n8n rodar fora de Docker (instalação nativa/PM2), `http://localhost:8787`
funciona normalmente e nada precisa mudar.

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
