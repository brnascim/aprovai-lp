# Canal Dark — Produção Automatizada de Vídeos (n8n)

Workflow do **n8n** que produz vídeos de canal dark (faceless) de ponta a ponta:
gera roteiro, imagens, narração com legendas, monta o vídeo e publica no YouTube —
tudo a partir de uma fila de ideias em uma planilha.

> ⚠️ **Nota de origem:** não consegui acessar o vídeo do YouTube
> (`f-4s0-pGnn4`) neste ambiente — o YouTube bloqueia acesso automatizado (HTTP 403).
> Por isso, este fluxo **não é uma cópia byte-a-byte** do vídeo, e sim uma
> reconstrução fiel da arquitetura mais comum usada nesses tutoriais de canal dark.
> Se você colar aqui a **transcrição**, a **descrição** ou um **print dos nós** do
> vídeo, eu ajusto para bater exatamente com o original.

---

## Arquitetura do fluxo

```
Agendador (diário)
   → Buscar próxima ideia (Google Sheets)
   → Gerar roteiro (GPT-4o)
   → Gerar cenas + prompts de imagem (GPT-4o, JSON)
   → Separar cenas (Code, 1 item por cena)
   → Gerar imagem por cena (DALL·E 3)  ── roda por item
   → Montar cena / Juntar cenas (Aggregate)
   → Montar payload JSON2Video (Code)
   → Renderizar (JSON2Video)
   → Aguardar / Checar status ⇄ (loop até "done")
   → Gerar metadados SEO (GPT-4o)
   → Baixar MP4
   → Publicar no YouTube (privado por padrão)
   → Atualizar planilha (status = publicado)
```

## Ferramentas escolhidas (e por quê)

| Etapa | Ferramenta padrão | Alternativas fáceis |
|-------|-------------------|---------------------|
| Fila de ideias | Google Sheets | Airtable, Notion, ou um nó *Set* fixo |
| Roteiro/cenas/SEO | OpenAI GPT-4o | Anthropic Claude, Google Gemini |
| Imagens | OpenAI DALL·E 3 | Replicate (Flux), Leonardo, Midjourney |
| Voz + legendas + montagem | **JSON2Video** | Creatomate, Shotstack, FFmpeg self-hosted |
| Voz (TTS) | Azure (`pt-BR-AntonioNeural`) via JSON2Video | ElevenLabs (troque `model` e `voice`) |
| Publicação | YouTube (nó nativo) | Só salvar no Drive para aprovação manual |

> **Por que JSON2Video?** Ele faz TTS, sincroniza imagens com a narração e gera as
> legendas em um único render — é o padrão nos tutoriais de canal dark. Se preferir
> **ElevenLabs**, no nó *Montar Payload JSON2Video* troque o elemento de voz por:
> ```js
> { type: 'voice', text: c.texto, voice: 'SEU_VOICE_ID', model: 'elevenlabs' }
> ```

---

## Como importar

1. No n8n: **Workflows → ⋯ → Import from File** e selecione
   `dark-channel-video-automation.json`.
2. Preencha os `PLACEHOLDER_*` (veja abaixo).
3. Rode uma vez manualmente (**Execute Workflow**) antes de ativar o agendador.

## Credenciais necessárias

Crie estas credenciais no n8n e ligue nos respectivos nós:

| Credencial (n8n) | Onde obter | Placeholder no JSON |
|------------------|-----------|---------------------|
| **OpenAI (Header Auth)** — Header `Authorization` = `Bearer sk-...` | platform.openai.com | `PLACEHOLDER_OPENAI_CRED` |
| **Google Sheets OAuth2** | Google Cloud Console | `PLACEHOLDER_GSHEETS_CRED` |
| **YouTube OAuth2** | Google Cloud Console (YouTube Data API v3) | `PLACEHOLDER_YOUTUBE_CRED` |
| **JSON2Video API key** — header `x-api-key` | json2video.com | `PLACEHOLDER_JSON2VIDEO_API_KEY` (colada direto nos nós HTTP) |
| **Google Sheet ID** | URL da sua planilha | `PLACEHOLDER_SHEET_ID` |

> 💡 Para a chave do JSON2Video, o ideal é criar uma credencial **Header Auth** no n8n
> em vez de colar a chave em texto puro nos nós HTTP. Deixei em texto só para o fluxo
> ficar legível na importação.

## Planilha de ideias (aba `Ideias`)

O fluxo espera uma planilha com pelo menos estas colunas:

| id | topic | status | youtube_id |
|----|-------|--------|-----------|
| 1  | A casa que aparecia só à meia-noite | pendente | |
| 2  | O elevador que descia para o 13º andar | pendente | |

- O nó **Buscar Próxima Ideia** pega a primeira linha com `status = pendente`.
- Ao final, **Atualizar Planilha** marca `status = publicado` e grava o `youtube_id`.

---

## Ajustes recomendados

- **Aprovação manual antes de postar:** desconecte *Publicar no YouTube* e deixe o
  vídeo só ser baixado / salvo, ou coloque um nó de notificação (Telegram/E-mail)
  com o link do MP4 antes do upload. O `privacyStatus` já vem como `private`.
- **Frequência:** ajuste o nó *Agendador* (hoje: todo dia às 9h).
- **Duração/nº de cenas:** no prompt do nó *Gerar Cenas + Prompts* (hoje: 6–12 cenas).
- **Idioma/voz:** troque `pt-BR-AntonioNeural` por outra voz suportada.
- **Custo por vídeo (aprox.):** GPT-4o (roteiro+cenas+SEO) + N imagens DALL·E 3 +
  1 render JSON2Video. Comece com poucas cenas para calibrar.

## Limitações conhecidas

- Os `typeVersion` dos nós seguem versões recentes do n8n; se o seu n8n for mais
  antigo, alguns nós podem pedir reconfiguração leve ao importar.
- O nó *Baixar MP4* espera que a URL do render esteja em `movie.url` (formato atual
  da API do JSON2Video v2). Confirme no retorno de *Checar Status*.
- O loop de polling usa espera fixa de 45s por rodada. Aumente se seus vídeos forem
  longos.
