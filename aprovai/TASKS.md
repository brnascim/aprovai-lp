# TASKS — backlog ordenado (Codex começa por aqui)

> Regras inegociáveis em `AGENTS.md`. Não pular a leitura.

## TAREFA 0 — Setup
- [ ] `git init`, criar repo, copiar `.env.example` → `.env`.
- [ ] Deploy da `web/index.html` na Vercel; apontar aprovai.com.br (DNS).
- [ ] Resolver os 4 placeholders da LP (procurar `TROCAR` no HTML): link de checkout, foto/nome do fundador, páginas legais, og:image.

## TAREFA 1 — Assistente Motor Anti-ATS  ✅ scaffold incluído em `assistant/`
- [x] Scaffold Next.js (App Router) + Tailwind, identidade Aprovaí.
- [x] Form (área, vaga, experiência) + tela de resultado (copiar/baixar).
- [x] Rota `/api/generate` com prompt honesto (sem inventar dados/promessa de emprego). Chave só no servidor.
- [x] Estimativa de aderência às palavras-chave da vaga (rotulada como estimativa).
- [ ] `npm install && npm run dev` para validar; preencher `ANTHROPIC_API_KEY`.
- [x] Rate-limit por IP/sessão. (endpoint `web/api/otimizar.js` — Upstash se configurado, senão best-effort; ver `docs/07`.)
- [x] Gate de acesso por token pós-pagamento (HMAC server-side em `web/api/otimizar.js` e `assistant/.../generate/route.ts`; falta emitir o token no n8n — Tarefa 2). Ver `docs/07-token-acesso-e-endpoint.md`.
- [ ] Telemetria de custo (tokens) + limite por usuário.
- [ ] Setar `ACCESS_TOKEN_SECRET` (Vercel + n8n) e, recomendado, provisionar Upstash Redis.

## TAREFA 2 — Pagamento + entrega automática
- [ ] Checkout Mercado Pago/Stripe (entrada R$47, bump R$27, upsell R$97).
- [ ] Fluxo n8n: webhook de pagamento → token de acesso → e-mail/WhatsApp. Ver `docs/03-spec-n8n-entrega.md`.
- [ ] Páginas legais (Privacidade, Termos, Reembolso) — LGPD/CDC.

## TAREFA 3 — Continuidade (LTV)
- [ ] Assinatura opcional R$19,90/mês (Stripe) + dunning.

## TAREFA 4 — Conteúdo orgânico (depois do caixa)
- [ ] Pipeline a partir de `config/content-engine.yaml`.

## Não fazer
- [ ] Não usar Lovable. Não inventar depoimentos/números. Não prometer emprego/renda.
