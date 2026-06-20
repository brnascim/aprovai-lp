# Spec — Assistente "Motor Anti-ATS"

## Objetivo
App web onde o usuário cola (1) a descrição da vaga e (2) sua experiência, e recebe:
- Currículo otimizado para ATS
- Carta de apresentação
- Texto de LinkedIn (headline + "sobre")
Tudo adaptado às palavras-chave daquela vaga, em ~2 minutos.

## Stack
- Next.js (App Router) + TypeScript, deploy na Vercel.
- Chamada à API Anthropic **server-side** (rota `/api/generate`). Chave só no servidor.
- Modelo: `claude-sonnet-4-6` (padrão) ou `claude-haiku-4-5-20251001` (volume).
- Doc oficial da API (fonte de verdade, verificar versão/headers atuais): https://docs.claude.com/en/api/overview

## Fluxo
1. Form: textarea "vaga" + textarea "sua experiência" + select "área".
2. POST `/api/generate` → monta prompt → chama Anthropic → devolve 3 blocos.
3. UI mostra os 3 resultados com botão copiar/baixar. Mostrar um "score ATS" estimado **rotulado como estimativa** (não garantia).

## Regras de produto (ver AGENTS.md)
- Sem prometer emprego/renda. Sem inventar dados.
- O "score" é estimativa ilustrativa, sempre rotulado.
- Acesso liberado por token enviado após o pagamento (ver spec n8n).

## Prompt (rascunho — refinar)
- System: "Você é um especialista em otimização de currículos para sistemas ATS no Brasil. Reescreva para maximizar correspondência de palavras-chave e legibilidade por máquina, mantendo tudo verdadeiro. NÃO invente experiências, números ou certificações que o usuário não forneceu."
- User: vaga + experiência + área → pedir saída em 3 seções marcadas.

## Controles de custo
- Limitar tokens de saída; cachear nada sensível; rate-limit por usuário; degradar para haiku se volume alto.

Ver `examples/generate.ts` para o esqueleto da rota.
