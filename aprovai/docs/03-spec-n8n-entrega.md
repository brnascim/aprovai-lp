# Spec — Automação de entrega (n8n)

## Objetivo
Pagamento aprovado → acesso liberado automaticamente, sem intervenção humana.

## Fluxo
1. **Webhook** recebe evento de pagamento (Mercado Pago / Stripe).
2. **Filtro** por `external_reference` (ex.: `aprovai-entrada`, `aprovai-bump`, `aprovai-upsell`).
3. **Gera/recupera token de acesso** ao assistente (ou licença).
4. **Envia e-mail + WhatsApp** com o link de acesso (template pt-BR).
5. **Registra** a venda em planilha (mesma lógica do relatório diário de tráfego já existente).
6. **Retry/erro:** fila com reprocessamento; alerta se entrega falhar.

## Continuidade
- Assinatura opcional R$19,90/mês (Stripe) → webhook de renovação/cancelamento mantém o acesso.

## Observações
- Idempotência: tratar webhooks duplicados.
- Nunca logar dados sensíveis em claro (LGPD).
