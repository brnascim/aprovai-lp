# .telemetry — Rastreamento do Aprovaí

Este diretório contém o plano de telemetria do produto.

| Arquivo | Descrição |
|---------|-----------|
| `product.md` | Modelo do produto — base para todas as decisões de tracking |
| `current-state.yaml` | Auditoria do estado atual (gerado por audit-current-tracking) |
| `tracking-plan.yaml` | Plano alvo — o que deve ser rastreado e como |
| `delta.md` | Diff: estado atual → alvo (backlog de implementação) |
| `audits/` | Histórico de auditorias |

## Lifecycle

```
model → audit → design → guide → implement
```

Rode `/product-tracking-audit-current-tracking` para capturar o estado atual.
Rode `/product-tracking-design-tracking-plan` para desenhar o plano alvo.
