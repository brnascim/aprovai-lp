# AGENTS.md — Aprovaí

> Arquivo de instruções para agentes de código (Codex e afins). Leia por completo antes de editar qualquer coisa.

## 1. O que é este projeto
**Aprovaí** é um produto digital de entrada (assistente de IA) no nicho de **empregabilidade**.
Promessa: reescrever currículo, carta de apresentação e LinkedIn para **passar pela triagem automática (ATS)** e chegar ao recrutador — adaptado a cada vaga, em ~2 minutos.

Mecanismo único: **Motor Anti-ATS**.

> Contexto de negócio: o lucro do Aprovaí financia campanhas de OUTROS produtos da holding (MargemOS e LicitaTrack). **Este repositório NÃO contém e NÃO deve referenciar esses produtos.** Aprovaí é uma entidade independente: marca, domínio, pixel e funil próprios. Sem funil compartilhado, sem cross-sell com eles.

## 2. Regras inegociáveis (valem para copy, UI e features)
1. **Nunca prometer emprego ou renda garantida.** Vender resultado verificável: passar no ATS / mais entrevistas.
2. **Nunca inventar depoimentos, prints ou números.** Provas sociais só quando reais. Onde não há, deixar slot vazio rotulado.
3. **Nada de "Potencial R$ X mil/mês"** nem claims de renda — risco legal (CDC) e de reprovação no Meta.
4. **Anúncios de emprego = Categoria Especial no Meta** ("Emprego"): segmentação restrita. Documentar isso em qualquer material de tráfego.
5. **LGPD/CDC:** páginas de Privacidade, Termos e Reembolso obrigatórias antes de rodar tráfego.
6. **Honestidade da escassez:** "preço de lançamento" é real (sobe após coletar resultados). Proibido cronômetro falso.
7. Idioma de toda saída ao usuário final: **pt-BR**.

## 3. Stack e decisões (NÃO usar Lovable)
- **Landing page:** `web/index.html` — HTML estático único, Tailwind via CDN. Hospedar na **Vercel**. (Para produção, compilar o Tailwind.)
- **Assistente (Motor Anti-ATS):** **Next.js (App Router) na Vercel**, chamando a **API da Anthropic** server-side. Ver `docs/02-spec-assistente.md`.
- **Pagamento:** Mercado Pago e/ou Stripe (PIX + cartão). Order bump R$27 e upsell R$97 no checkout.
- **Automação/entrega:** **n8n** (VPS Hostinger). Webhook de pagamento → e-mail/WhatsApp com acesso. Ver `docs/03-spec-n8n-entrega.md`.
- **Domínio:** aprovai.com.br (confirmar). Domínio na Hostinger, LP/app na Vercel via DNS.
- **Modelo padrão:** `claude-sonnet-4-6` (qualidade/custo). Alto volume: `claude-haiku-4-5-20251001`.

## 4. Mapa do repositório
- `web/index.html` — landing page pronta (versão de frame estático, sem animação).
- `assistant/` — **app Next.js do assistente (Motor Anti-ATS)** — scaffold pronto e rodável (ver `assistant/README.md`).
- `docs/00-estrategia-caixa.md` — plano de negócio (nicho, oferta Hormozi, unit economics, 90 dias).
- `docs/01-copy-e-premortem.md` — copy seção a seção + pré-mortem (14 riscos + solução).
- `docs/02-spec-assistente.md` — especificação do app assistente (o que construir).
- `docs/03-spec-n8n-entrega.md` — especificação da automação de entrega.
- `config/content-engine.yaml` — config do motor de conteúdo orgânico (Instagram).
- `examples/generate.ts` — referência de chamada à API Anthropic (server-side).
- `TASKS.md` — backlog ordenado. **Comece por aqui.**

## 5. Como rodar (hoje)
- LP: abrir `web/index.html` no navegador, ou `npx serve web`. Deploy: subir `web/` na Vercel (static).
- Assistente: ainda não scaffoldado — é a TAREFA 1 do `TASKS.md`.

## 6. Definition of Done
- LP: 4 placeholders resolvidos (link de checkout, foto/nome do fundador, páginas legais, og:image); Lighthouse mobile > 90.
- Assistente: recebe vaga + experiência → devolve CV/carta/LinkedIn otimizados; chave de API só no servidor; sem claim proibido na UI.
- Entrega: pagamento aprovado dispara acesso automático em < 1 min, com retry.

## 7. Estilo de código
- TypeScript no app. Componentes pequenos. Sem segredo no client. `.env` nunca commitado (ver `.env.example`).
- Acessibilidade (AA), mobile-first, respeitar `prefers-reduced-motion`.
