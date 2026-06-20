# Aprovaí

Assistente de IA que reescreve currículo, carta e LinkedIn para **passar pela triagem automática (ATS)** e chegar ao recrutador — em ~2 minutos, para cada vaga.

Produto de entrada, independente. Para o contexto completo e as regras do projeto, leia **`AGENTS.md`** e depois **`TASKS.md`**.

## Conteúdo
- `web/` — landing page (HTML estático, pronta para Vercel).
- `docs/` — estratégia, copy + pré-mortem, e specs do assistente e da automação.
- `config/` — config do motor de conteúdo orgânico.
- `examples/` — referência de chamada à API Anthropic.

## Começar
1. Leia `AGENTS.md` (regras inegociáveis — destaque para honestidade e compliance).
2. Siga `TASKS.md` na ordem.
3. Copie `.env.example` para `.env` e preencha as chaves.

## Stack
LP estática (Vercel) · Assistente em Next.js + API Anthropic · Pagamento Mercado Pago/Stripe · Automação n8n. **Não usar Lovable.**
