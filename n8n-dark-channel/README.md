# YT - Veo3 — Canal Dark de Shorts (n8n + MoviAPI)

Reconstrução do workflow **"YT - Veo3"** do vídeo tutorial. Produz **YouTube Shorts**
de canal dark (faceless) de forma automática usando a **MoviAPI** (geração de vídeo
com **Google Veo3**), refina o título com um agente **OpenAI** e publica direto no
YouTube via **API de upload resumível**.

> Este JSON foi reconstruído a partir dos frames do vídeo enviado. Onde a URL/parâmetro
> exato da MoviAPI não aparecia na tela, usei o formato mais provável — **confirme os
> endpoints na documentação atual da MoviAPI** antes de rodar em produção.

---

## Arquitetura real (do vídeo)

```
[Manual Trigger]  ┐
                  ├─→ Credenciais (Set: moviapi_key, email)
[Schedule Trigger]┘
        → MOVIAPI        (POST  — inicia a geração do Short com template "veo3short")
        → Wait1          (aguarda a renderização do Veo3)
        → MOVIAPI1       (GET   — status "done" + url do MP4 + title + script)
        → Titulo         (Agente OpenAI — reescreve o título no estilo "Zack D. Films")
        ── grupo "Sobe Youtube" ──
        → CriaURL        (POST googleapis /upload/youtube/v3/videos?uploadType=resumable)
        → Download Video1(GET  — baixa o MP4 da MoviAPI como binário)
        → FinalizaUpload (PUT  — envia o binário para a URL resumível do YouTube)
```

**Insight central:** a MoviAPI com o template `veo3short` já devolve o **vídeo pronto +
roteiro + título**. O n8n só orquestra: dispara, espera, melhora o título e sobe no
YouTube. É por isso que o fluxo é curto.

## Ferramentas usadas

| Papel | Ferramenta |
|-------|-----------|
| Geração do vídeo (Veo3) + roteiro + título | **MoviAPI** (`v1.moviapi.com`, template `veo3short`) |
| Refino do título (estilo viral) | **OpenAI** (Agent + `gpt-4o-mini`) |
| Publicação | **YouTube Data API v3** (upload resumível via HTTP) |
| Pesquisa de nicho / espionar receita de canais | **NexLev Analytics** (mostrado no vídeo, fora do fluxo) |

## Como importar e configurar

1. n8n → **Import from File** → `dark-channel-video-automation.json`.
2. No nó **Credenciais**, cole sua `moviapi_key` e seu e-mail.
3. Crie/ligue a credencial **OpenAI** no nó `OpenAI Chat Model5`.
4. Crie/ligue a credencial **YouTube OAuth2** (Google Cloud → YouTube Data API v3) no nó `CriaURL`.
5. Rode 1x pelo **Manual Trigger** para testar; depois ative o **Schedule Trigger**.

### Placeholders a substituir
- `PLACEHOLDER_MOVIAPI_KEY` — sua chave da MoviAPI (nó Credenciais)
- `PLACEHOLDER_OPENAI_CRED` — credencial OpenAI
- `PLACEHOLDER_YOUTUBE_CRED` — credencial YouTube OAuth2

### Detalhes que valem conferir
- **Endpoint MoviAPI:** usei `POST /api/v1/video` e `GET /api/v1/video/{id}`. Ajuste ao
  path real da sua conta MoviAPI (no vídeo aparecia `v1.moviapi.com/...` e body
  `template=veo3short`, `language=en`).
- **`CriaURL`** precisa retornar o header `location` (por isso `fullResponse: true`).
  Esse header é a URL usada pelo `FinalizaUpload`.
- **`FinalizaUpload`** envia `Content-Type: video/mp4` e o binário no campo `data`.
- **Privacidade:** o vídeo publica como `public`. Troque para `private` enquanto testa.

---

## ⚠️ Observações honestas (leia antes de escalar)

- **Políticas do YouTube:** conteúdo 100% gerado por IA, repetitivo e em massa pode
  cair em *"conteúdo inautêntico/spam"* (regra reforçada em 2025). Varie ângulo,
  roteiro e ritmo; não suba 20 vídeos idênticos por dia.
- **Custo:** cada Short = 1 render Veo3 (MoviAPI) + 1 chamada OpenAI. Veo3 não é barato;
  calcule o custo por vídeo antes de programar dezenas por dia.
- **Monetização de Shorts:** o RPM de Shorts é baixo. O jogo real é volume + usar os
  Shorts como funil para vídeos longos, produtos ou outra oferta (veja a mentoria).
