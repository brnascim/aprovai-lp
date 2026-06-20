# Aprovaí — Assistente (Motor Anti-ATS)

App Next.js (App Router) que recebe a vaga + experiência e devolve currículo, carta e LinkedIn otimizados para ATS, via API da Anthropic (server-side).

## Rodar local
1. `cp .env.example .env` e preencha `ANTHROPIC_API_KEY`.
2. `npm install`
3. `npm run dev` → http://localhost:3000

## Deploy
- Vercel: importar o repo, definir `ANTHROPIC_API_KEY` (e `ANTHROPIC_MODEL`) nas Environment Variables. A chave fica só no servidor.

## Status (Tarefa 1)
- [x] Scaffold Next.js + Tailwind (identidade Aprovaí)
- [x] Form (área, vaga, experiência) + tela de resultado (copiar/baixar)
- [x] Rota `/api/generate` com prompt honesto (sem inventar dados, sem promessa de emprego)
- [x] Estimativa de aderência (rotulada como estimativa)
- [ ] Rate-limit por IP/sessão (TODO)
- [ ] Gate de acesso por token pós-pagamento (integra com Tarefa 2 / n8n)
- [ ] Telemetria de custo (tokens)

## Regras (ver ../AGENTS.md)
Sem promessa de emprego/renda. Sem inventar experiências/números. pt-BR. Chave nunca no client.
