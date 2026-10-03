# Canal Dívidas — Shorts automáticos com motor próprio (zero-custo)

Workflow **n8n** para produção automatizada de YouTube Shorts no nicho "dívidas e
recuperação financeira", usando um **motor de vídeo próprio e gratuito** em vez de
APIs pagas (MoviAPI/Veo3), pensado pra rodar inteiro na sua VPS Hostinger junto com o
n8n e o Evolution API que você já tem.

## Arquitetura

```
[Manual Trigger] ┐
                 ├─→ Escolher Tema (lista fixa de temas do nicho dívidas)
[Schedule 8/8h]  ┘
        → Gerar Roteiro       (OpenAI gpt-4o-mini, ~150 palavras, PT-BR)
        → Gerar Cenas         (OpenAI — quebra em 5-7 cenas: texto PT-BR + busca EN)
        → Montar Payload      (Code)
        → Gerar Vídeo         (POST no Content Engine local — veja content-engine/README.md)
        → Titulo              (Agente OpenAI — título estilo viral)
        ── grupo "Sobe Youtube" ──
        → CriaURL             (POST googleapis /upload/youtube/v3/videos?uploadType=resumable)
        → Buscar Vídeo Gerado (GET no Content Engine pelo job_id)
        → FinalizaUpload      (PUT do binário na URL resumível do YouTube)
```

## O motor de vídeo (`content-engine/`)

Substitui a MoviAPI por um serviço próprio: **Pexels/Pixabay** (stock de vídeo grátis)
+ **Edge-TTS** (voz neural gratuita) + **FFmpeg** (montagem e legenda queimada). Roda
em qualquer VPS sem GPU. Testado ponta a ponta nesta sessão — veja
[`content-engine/README.md`](content-engine/README.md) pro setup completo.

**Por que não usei os repositórios sugeridos direto:** pesquisei os 4 links indicados
(VUZA, YumCut, AI-Influencer-Generator, Open-Generative-AI) antes de decidir:
- **VUZA** — grátis, sem GPU, mas só tem interface web manual, sem API pra automação.
- **YumCut** — tem API pronta pra automação, mas exige licença comercial paga se for
  usado pra gerar conteúdo vendido/monetizado — risco pra um canal que vai vender
  infoproduto. Confirme direto com o autor se quiser usar mesmo assim.
- **AI-Influencer-Generator** e **Open-Generative-AI** — exigem GPU (Stable Diffusion
  + SadTalker) ou créditos pagos — ficam reservados pra uma fase futura de "avatar IA",
  não pro teste inicial CPU-only que você pediu.

Por isso construí um motor pequeno e próprio (MIT, sem restrição nenhuma), reaproveitando
a mesma lógica gratuita que essas ferramentas usam por baixo.

## Custo real do sistema

| Item | Custo |
|---|---|
| Pexels/Pixabay (stock) | R$0 |
| Edge-TTS (voz) | R$0 |
| FFmpeg (montagem) | R$0 |
| VPS Hostinger | você já paga, sem custo incremental |
| OpenAI (roteiro + cenas + título, ~gpt-4o-mini) | poucos centavos/vídeo |

## Como importar o workflow

1. Suba o `content-engine` na sua VPS primeiro (veja `content-engine/README.md`) e
   confirme `curl http://localhost:8787/health`.
2. No n8n: **Import from File** → `dark-channel-video-automation.json`.
3. Ligue a credencial **OpenAI** (Header Auth) nos 3 nós que chamam a API OpenAI e no
   `OpenAI Chat Model5`.
4. Ligue a credencial **YouTube OAuth2** no nó `CriaURL`.
5. Confira a URL do Content Engine no nó **Escolher Tema** (`content_engine_url`,
   padrão `http://localhost:8787` — ajuste se n8n e o content-engine estiverem em
   containers Docker separados).
6. Rode 1x pelo **Manual Trigger** pra validar antes de ativar o **Schedule Trigger**.
7. O vídeo sobe como `privacyStatus: private` por padrão — revise antes de trocar pra
   `public`.

## Próximas etapas (fora deste workflow)

- **Etapa 3:** replicar a postagem pro Instagram Reels e TikTok (APIs oficiais
  gratuitas, exigem conta Business + aprovação do app — vale começar o cadastro em
  paralelo).
- **Etapa 4:** landing page de captura + checkout Kiwify na sua hospedagem Hostinger.
- **Etapa 5:** automação de nutrição via WhatsApp com o Evolution API que você já tem.
- LinkedIn/X ficam de fora por enquanto — formato de vídeo curto sobre dívida não é o
  ponto forte dessas redes; baixa prioridade até o orgânico em vídeo validar.
