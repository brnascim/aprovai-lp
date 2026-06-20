# Sessão Claude Code — 20/06/2026
## Aprovaí: Caveman + n8n + Stripe Integration

### 🎯 Objetivo
Continuar implementação do Motor Anti-ATS Aprovaí, focando em:
1. Instalar caveman (skill framework multi-agente)
2. Completar workflow n8n de entrega pós-pagamento
3. Preparar integração Stripe

---

## ✅ Entregas

### 1. Caveman Skill instalada (7 skills)
- **Instalado:** Node.js + caveman framework
- **Skills adicionadas:**
  - `caveman` — modo avançado
  - `caveman-commit` — commit automation
  - `caveman-review` — code review
  - `caveman-stats` — análise de código
  - `cavecrew` — multi-agent orchestration
  - `caveman-compress` — context optimization
  - `caveman-help` — help system

**Como usar:** Say `/caveman` em qualquer sessão Claude Code para ativar.

---

### 2. Data Table n8n Criada
- **Nome:** `tokens_aprovai`
- **ID:** `KgsVZRLRNB3WINee`
- **Colunas:** 
  - `token` (UUID único)
  - `email` (string)
  - `nome` (string)
  - `valorPago` (number em reais)
  - `sessionId` (string, da Stripe)
  - `criadoEm` (date ISO)
  - `usado` (boolean)
- **Status:** Ativa e pronta para inserts

---

### 3. Workflow n8n — Estrutura Completa
**Nome:** `Aprovai - Entrega Pos-Pagamento`  
**ID:** `lf5tQEsgZD8AJ0Q8`  
**Nodes prontos:**

| Node | Tipo | Status | Descrição |
|------|------|--------|-----------|
| Webhook | trigger | ✅ | POST `/stripe-aprovai` |
| Validar Assinatura | Code (HMAC) | ✅ | SHA256 validation |
| If | filter | ✅ | Check `checkout.session.completed` |
| Gerar Token | Code (JS) | ✅ | UUID + extração de dados |
| Insert row | dataTable | ✅ | Salva em `tokens_aprovai` |
| Send Email | SMTP | ⏳ | Envia link de acesso |
| Respond (success) | webhook | ✅ | 200 OK para Stripe |
| Respond (ignore) | webhook | ✅ | 200 OK para outros eventos |

**Fluxo:** Webhook → Validar → If → Gerar Token → Insert → Email → Respond

---

### 4. Documentação Criada
- `docs/04-n8n-stripe-setup-status.md` — Status detalhado + checklist
- `scripts/setup-n8n-stripe.sh` — Script de setup automático
- `.env.example` — Variáveis necessárias
- `n8n-workflow-update.json` — Template completo do workflow

---

## ⏳ O que falta (Bloqueado por Bruno)

### Credenciais (necessário para continuar)
| Item | Responsável | Status |
|------|-------------|--------|
| SMTP/Gmail credentials | Bruno | ⏳ Precisa configurar |
| Stripe Secret Key | Bruno | ✅ Já tem (`sk_live_...`) |
| Stripe Webhook Signing Secret | Bruno | ⏳ Precisa pegar no dashboard |

### Ações (quando credenciais estiverem prontas)
1. Bruno: Criar credencial SMTP/Gmail no n8n
2. Bruno: Configurar webhook endpoint na Stripe
3. Bruno: Copiar `Signing Secret` da Stripe
4. Claude Code: Rodar script `setup-n8n-stripe.sh` com variáveis
5. Claude Code: Testar webhook com Stripe CLI
6. Bruno: Publicar workflow quando tudo passar em testes

---

## 🔧 Próximos passos imediatos

### Para Bruno (configurações manuais):
```bash
# 1. SMTP/Gmail setup
# Veja docs/04-n8n-stripe-setup-status.md → seção "Credenciais SMTP/Gmail"

# 2. Stripe webhook
# Dashboard Stripe → Developers → Webhooks
# Endpoint: https://n8n.mentoriaaprovai.com.br/webhook/stripe-aprovai
# Event: checkout.session.completed
# Copiar: Signing Secret (começa com "whsec_")

# 3. Compartilhar com Claude Code:
# export STRIPE_WEBHOOK_SECRET="whsec_..."
```

### Para Claude Code (quando credenciais prontas):
```bash
# Rodar setup automático
export N8N_API_KEY="eyJ..."
export STRIPE_WEBHOOK_SECRET="whsec_..."
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="seu@email.com"
export SMTP_PASSWORD="app-password"

bash scripts/setup-n8n-stripe.sh
```

---

## 📊 Progresso TAREFA 2 (Pagamento + Entrega)

- [x] Data Table de tokens criada
- [x] Workflow n8n scaffoldado (nodes + fluxo)
- [x] Code nodes prontos (validação + geração de token)
- [ ] Credencial SMTP configurada (bloqueado)
- [ ] Webhook Stripe configurado (bloqueado)
- [ ] Workflow testado com payload real
- [ ] Workflow publicado
- [ ] Gate de token no app (TAREFA 1.5)

**ETA próxima entrega:** Assim que credenciais chegarem (estimado: próxima sessão)

---

## 🔐 Segurança — Status

- ✅ Validação HMAC Stripe (código pronto)
- ✅ Chaves nunca em git (usando `.env`)
- ✅ Data Table com permissões n8n
- ⏳ Rate limit no webhook (TODO)
- ⏳ Logs de auditoria (TODO)

---

## 📁 Arquivos principais

```
aprovai/
├── docs/
│   ├── 02-spec-assistente.md       (spec do app)
│   ├── 03-spec-n8n-entrega.md      (spec original — agora atualizado)
│   └── 04-n8n-stripe-setup-status.md 🆕 (status detalhado)
├── scripts/
│   └── setup-n8n-stripe.sh         🆕 (setup automático)
├── .env.example                    🆕 (variáveis necessárias)
├── n8n-workflow-update.json        🆕 (template workflow)
├── TASKS.md                        (backlog — agora está TAREFA 2 em progresso)
└── HANDOFF-claude-code.md          (handoff da sessão anterior)
```

---

## 💡 Insights & Decisions

### Por que caveman foi instalado?
Recomendação do Bruno para usar como custom skill multi-agente. Agora disponível globalmente em todas as sessões Claude Code.

### Por que Code nodes (JS) em vez de nós nativos?
Oferece controle total sobre validação HMAC e geração de UUID. Mais simples que imports de bibliotecas externas no n8n.

### Por que Data Table em vez de Postgres externo?
n8n suporta natively sem deps adicionais. Sem administração de banco de dados. Suficiente para MVP (até milhões de tokens).

---

## 🚀 Métricas

- **API key n8n:** Testada ✅
- **Data Table:** Criada ✅
- **Workflow nodes:** 8/8 estruturados ✅
- **Dependencies:** 0 (nada bloqueado tecnicamente) ✅
- **Bloqueadores:** 2 (credenciais SMTP + Stripe signing secret)

---

**Próxima reunião:** Assim que credenciais SMTP/Stripe estiverem prontas  
**Status:** Pronto para testes → ready to publish → ready to gate no app
