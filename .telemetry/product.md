# Product: Aprovaí

**Last updated:** 2026-06-26
**Method:** codebase scan + context from session

## Product Identity
- **One-liner:** Profissionais brasileiros em busca de emprego colam a descrição de uma vaga e seu histórico de experiência, e a ferramenta reescreve currículo, carta de apresentação e seção do LinkedIn em ~2 minutos com linguagem otimizada para passar nos filtros automáticos de triagem (ATS).
- **Category:** B2C AI tool / digital infoproduct
- **Product type:** B2C — usuários individuais, sem conta corporativa ou hierarquia de equipe.
- **Collaboration:** single-player — cada usuário usa a ferramenta de forma independente para suas próprias candidaturas.

## Business Model
- **Monetization:** paid-only (one-time + continuidade)
- **Pricing tiers:**
  - Entrada: R$47 one-time (acesso ao Motor Anti-ATS)
  - Order bump: R$27 (Pacote Entrevista — 50 respostas + scripts de negociação)
  - Upsell 1-clique: R$97 (Operação Vaga Completa — uso ilimitado + plano 30 dias)
  - Downsell: R$27 (só templates, sem o assistente premium)
  - Continuidade: R$19,90/mês (uso ilimitado + atualizações de palavras-chave)
- **Billing integration:** Stripe (primário) + Mercado Pago (alternativo, PIX/cartão)

## Tech Stack
- **Primary language:** HTML estático (LP/funil) + TypeScript (API backend)
- **Framework:** Next.js (assistant/api) + Tailwind CDN (todas as páginas estáticas)
- **Database:** não detectado — sem persistência de usuário no app; entrega por e-mail/WhatsApp via n8n
- **Background jobs:** n8n (webhook Stripe/MP → disparo de e-mail/WhatsApp com link de acesso)
- **HTTP client patterns:** fetch nativo para Anthropic API (`/api/generate` route server-side)
- **Module organization:** `aprovai/web/` (páginas HTML estáticas) + `aprovai/assistant/` (Next.js API)

## Value Mapping

### Primary Value Action
**generate** — usuário cola a descrição da vaga + sua experiência e recebe em ~2 min currículo, carta e LinkedIn otimizados para ATS. Se ninguém clicar em "Gerar", o produto falhou.

### Core Features (directly deliver value)
1. **Motor Anti-ATS** — `/api/generate` chama Claude com `{vaga, experiencia, area}` e devolve `[CURRICULO]`, `[CARTA]`, `[LINKEDIN]`. É o único artefato de valor do produto.
2. **Funil de conversão** — LP (`index.html`) → checkout Stripe → bump → upsell → entrega automática de acesso via n8n.

### Supporting Features (enable core actions)
1. **Automação de entrega** — n8n dispara e-mail/WhatsApp com link para `motor.html` após confirmação de pagamento.
2. **Páginas de pós-compra** — `obrigado.html`, `obrigado-comunidade.html`, `upsell.html`: confirmam compra e direcionam para próxima etapa do funil.
3. **Continuidade (assinatura)** — Stripe recorrente; retém usuário com acesso ilimitado + atualizações de palavras-chave ATS por área.

## Entity Model

### Users
- **ID format:** não há login/UUID próprio — usuário é identificado pelo `email` fornecido no checkout Stripe. Após compra, acesso é entregue por link (sem autenticação persistente no app).
- **Roles:** comprador (acesso one-time) / assinante (continuidade R$19,90)
- **Multi-account:** não — produto individual, sem multi-tenancy.

## Group Hierarchy

Não aplicável — produto B2C, single-player. Não há workspace, equipe ou hierarquia de contas. O nível de tracking é **usuário** (ou sessão anônima pré-compra).

## Current State
- **Existing tracking:** nenhum — nenhum pixel, GA, Segment, Amplitude ou similar detectado nos HTMLs do produto (`index.html`, `motor.html`, `obrigado.html`, `upsell.html`, `acesso.html`).
- **Documentation:** não há plano de tracking documentado.
- **Known issues:**
  - Zero visibilidade sobre funil: não se sabe onde usuários abandonam entre LP → checkout → motor.
  - Sem tracking de geração: não há dado sobre quantas vezes `generate` é chamado por comprador nem taxa de retenção na continuidade.
  - Sem Meta Pixel declarado — campanhas Meta Ads rodando provavelmente sem dados de conversão server-side.

## Integration Targets

*Destinos não configurados ainda. Sugestões baseadas no modelo de negócio:*

| Destination | Purpose | Priority |
|-------------|---------|----------|
| Meta Pixel (CAPI) | Atribuição de conversão para campanhas Meta Ads — sem isso o CAC não é confiável | Alta |
| Google Analytics 4 | Funil de conversão LP → motor, análise de comportamento | Média |
| Stripe webhooks → n8n | Já em uso para entrega; pode alimentar analytics via evento server-side | Alta |
| Accoil (opcional) | Se o foco for retenção da assinatura R$19,90/mês | Baixa (pós-lançamento) |

## Codebase Observations
- **Feature areas inferred:** landing page (vendas) → checkout (Stripe/MP externo) → motor (geração IA) → páginas pós-compra → continuidade (assinatura)
- **Entity model inferred:** sem schema de banco de dados próprio; o único "usuário" é o comprador no Stripe. A `motor.html` não autentica — acesso é por link direto entregue pelo n8n.
- **API surface:** única rota de produto — `POST /api/generate` com body `{vaga, experiencia, area}`, retorna `{curriculo, carta, linkedin}`. Proteção: chave API no servidor, sem rate-limit explícito na leitura do código.
