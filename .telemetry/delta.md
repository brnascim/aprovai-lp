# Delta: Estado Atual → Plano Alvo
**Produto:** Aprovaí
**Data:** 2026-06-26
**Estado atual:** greenfield — 0 eventos rastreados

## Resumo

| Operação | Quantidade |
|----------|-----------|
| Add (novos) | 7 |
| Remove | 0 |
| Rename | 0 |
| Keep | 0 |
| **Total alvo** | **7** |

Verificação: ADD(7) + RENAME(0) + KEEP(0) = 7 ✓

---

## Add — 7 eventos novos

| Evento | Categoria | Layer | Por que | Prioridade |
|--------|-----------|-------|---------|-----------|
| `lp.viewed` | lifecycle | client | Topo do funil; sem este evento não há taxa de LP→checkout | 🔴 Alta |
| `checkout.started` | lifecycle | client | Intenção de compra; mede abandono entre LP e Stripe | 🔴 Alta |
| `purchase.completed` | billing | server | Receita confirmada; base do Meta CAPI e análise de ROI | 🔴 Alta |
| `cv.generated` | core_value | server | Ação de valor primária — mede uso real do produto pós-compra | 🔴 Alta |
| `motor.accessed` | lifecycle | client | Ativação pós-compra; gap entre compra e primeiro uso | 🟡 Média |
| `subscription.started` | billing | server | Ativação de continuidade; base do LTV recorrente | 🟡 Média |
| `subscription.cancelled` | billing | server | Churn; análise de retenção e coortes | 🟡 Média |

---

## Remove
Nenhum — estado atual é zero.

## Rename
Nenhum.

## Keep
Nenhum.

---

## Sequência de Implementação Recomendada

### Fase 1 — Visibilidade mínima (implementar primeiro)
1. `purchase.completed` via n8n → PostHog + Meta CAPI
   - Maior impacto imediato: elimina o tracking cego das campanhas Meta
   - Unblocks: cálculo de CAC real, otimização de anúncios

2. `cv.generated` via /api/generate route
   - Único indicador de uso real do produto
   - Unblocks: taxa de ativação (comprou → usou) e frequência de uso

### Fase 2 — Funil completo (após fase 1 estável)
3. `lp.viewed` + `checkout.started` via PostHog JS na index.html
   - Fecha o funil end-to-end: LP → CTA → checkout → compra → uso
   - Unblocks: identificação do ponto de maior abandono

4. `motor.accessed` via PostHog JS na motor.html
   - Fecha o gap ativação: comprou → acessou o motor → gerou

### Fase 3 — Retenção (quando houver assinantes)
5. `subscription.started` + `subscription.cancelled` via n8n
   - Só tem sinal quando houver base de assinantes
   - Unblocks: cohort de churn, análise de LTV real

---

## Decisões de Design

| Decisão | Escolha | Razão |
|---------|---------|-------|
| Naming convention | `object.action` snake_case | Greenfield — sem legado pra preservar |
| PII policy | `traits_only` | Email somente em traits via identify(); nunca em propriedades de evento |
| Internal exclusion | Filter por email no PostHog (cohort) | Sem sistema de roles — exclusão pós-ingestão |
| Group hierarchy | Nenhum | B2C single-player |
| Destinations | PostHog + Meta CAPI | PostHog: free tier suficiente; Meta CAPI: crítico para atribuição |
| Identity | anonymous_id → stripe_customer_id | n8n faz alias no webhook de purchase; sem login próprio |
