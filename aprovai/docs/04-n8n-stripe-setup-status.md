# n8n + Stripe — Setup Status & Próximos Passos

**Data:** 2026-06-20  
**Status:** Infra pronta, Data Table criada, workflow estruturado. Pendente: credenciais e publicação.

---

## ✅ Completado

### Infraestrutura
- **n8n rodando** em `https://n8n.mentoriaaprovai.com.br` (SSL via Traefik)
- **DNS propagado:** `n8n.mentoriaaprovai.com.br` → `187.77.231.13`
- **Acesso API validado** — n8n API key ativa

### Data Table
- **Nome:** `tokens_aprovai`
- **ID:** `KgsVZRLRNB3WINee`
- **Colunas:** token, email, nome, valorPago, sessionId, criadoEm, usado
- **Status:** Criada e pronta para receber inserts

### Workflow (parcialmente pronto)
- **Nome:** `Aprovai - Entrega Pos-Pagamento`
- **ID:** `lf5tQEsgZD8AJ0Q8`
- **Nodes prontos:**
  - ✅ Webhook (POST `/stripe-aprovai`)
  - ✅ If (filtro `checkout.session.completed`)
  - ✅ Gerar Token (Code node — gera UUID + extrai dados)
  - ✅ Insert row (conectado à Data Table)
  - ⏳ Send Email (template pronto, falta credencial SMTP/Gmail)
  - ⏳ Respond to Webhook (200 OK para Stripe)
  - ⏳ Validar Assinatura Stripe (Code node — HMAC SHA256)

---

## ⏳ Pendências (ordem recomendada)

### 1️⃣ Credenciais SMTP/Gmail (Bruno configura)
**O que fazer:**
- [ ] Escolher SMTP: Gmail, SendGrid, AWS SES, etc.
- [ ] Criar credenciais (e-mail de saída + senha/token)
- [ ] Testar envio de e-mail fora do n8n primeiro
- [ ] Adicionar credencial no n8n: Settings → Credentials → New

**Código de teste (terminal SSH na VPS):**
```bash
# Para Gmail (SMTP)
host: smtp.gmail.com
port: 587
user: seu-email@gmail.com
password: seu-app-password (não a senha da conta)

# Testar com OpenSSL
openssl s_client -connect smtp.gmail.com:587 -starttls smtp
```

### 2️⃣ Configurar webhook na Stripe (Bruno no dashboard)
**O que fazer:**
- [ ] Dashboard Stripe → Developers → Webhooks
- [ ] Adicionar endpoint: `https://n8n.mentoriaaprovai.com.br/webhook/stripe-aprovai`
- [ ] Eventos a escutar: `checkout.session.completed`
- [ ] **Copiar Signing Secret** (vai precisar disso)

**Onde guardar a Secret:**
```bash
# SSH na VPS, editar /root/.env ou variável de ambiente do n8n
SSH → Hostinger painel → VPS → Terminal
export STRIPE_WEBHOOK_SECRET="whsec_..."
```

### 3️⃣ Atualizar workflow com credencial SMTP e webhook secret
**Script (Claude Code via API):**
```bash
# 1. Criar credencial SMTP no n8n
curl -X POST "https://n8n.mentoriaaprovai.com.br/api/v1/credentials" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gmail SMTP",
    "type": "smtp",
    "data": {
      "host": "smtp.gmail.com",
      "port": 587,
      "user": "seu-email@gmail.com",
      "password": "app-password"
    }
  }'

# 2. Pegar ID da credencial do response
# 3. Atualizar node "Send Email" com credentialsId
```

### 4️⃣ Testar webhook localmente
**Com Stripe CLI (do seu laptop):**
```bash
# Instalar stripe-cli
curl https://raw.githubusercontent.com/stripe/stripe-cli/master/install.sh | sh

# Fazer login e criar tunnel
stripe login
stripe listen --forward-to https://n8n.mentoriaaprovai.com.br/webhook/stripe-aprovai

# Em outro terminal, disparar evento mock
stripe trigger checkout.session.completed

# Verificar no n8n se webhook foi recebido
# Logs: Workflow → Executions → último run
```

### 5️⃣ Validar assinatura Stripe no Code node
**Já preparado, só falta:** inserir STRIPE_WEBHOOK_SECRET como variável de ambiente do n8n.

**No painel Hostinger → VPS → Docker Compose:**
```yaml
services:
  n8n:
    environment:
      STRIPE_WEBHOOK_SECRET: "whsec_..."
```

### 6️⃣ Publicar workflow
**Depois que tudo for testado:**
```bash
curl -X POST "https://n8n.mentoriaaprovai.com.br/api/v1/workflows/lf5tQEsgZD8AJ0Q8/activate" \
  -H "X-N8N-API-KEY: $N8N_API_KEY"
```

---

## 📋 Arquivo de referência

**Template completo do workflow:** [`n8n-workflow-update.json`](../../n8n-workflow-update.json)

Contém estrutura pronta dos nodes. Para usar via API:
```bash
# Atualizar workflow com template
curl -X PUT "https://n8n.mentoriaaprovai.com.br/api/v1/workflows/lf5tQEsgZD8AJ0Q8" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d @n8n-workflow-update.json
```

---

## 🔐 Segurança — Checklist

- [ ] STRIPE_WEBHOOK_SECRET em variável de ambiente (nunca hardcoded)
- [ ] SMTP password em credencial n8n (encrypted), nunca no código
- [ ] Validação HMAC ativa no Code node (rejeita requests forjados)
- [ ] Rate limit no webhook (não implementado ainda — TODO)
- [ ] Logs do webhook guardados (para auditoria)

---

## 📞 Contatos próximas ações

| Quem | O quê | Status |
|------|-------|--------|
| Bruno (usuário) | Criar credencial SMTP/Gmail | ⏳ Pendente |
| Bruno | Configurar webhook Stripe + copiar secret | ⏳ Pendente |
| Claude Code | Atualizar workflow com nodes + credenciais | ⏳ Aguardando credenciais |
| Claude Code | Testar webhook com Stripe CLI | ⏳ Aguardando credentials |
| Bruno + Claude Code | Publicar workflow | ⏳ Após testes |

---

## 🚀 Próximas fases

### Fase 2: Gate de token no app (TAREFA 1.5)
Depois que workflow for publicado e gerando tokens:
- [ ] Atualizar `assistant/app/api/generate/route.ts` para validar token
- [ ] Chamar Data Table do n8n ou expor endpoint `/api/tokens/verify`
- [ ] Marcar `usado: true` após primeira geração

### Fase 3: Integração de pagamento
- [ ] Criar rota Stripe checkout no app Next.js
- [ ] Redirecionar para checkout após form
- [ ] Receber `session_id` no frontend
- [ ] Usar `session_id` para validar acesso

---

**Última atualização:** 2026-06-20 15:53 UTC  
**Próximo milestone:** Credenciais SMTP + webhook Stripe configurados
