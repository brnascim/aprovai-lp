#!/bin/bash
# Setup n8n Stripe webhook + credenciais SMTP
# Requer variáveis de ambiente antes de rodar:
#   N8N_API_KEY
#   STRIPE_WEBHOOK_SECRET
#   SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

set -e

API_KEY="${N8N_API_KEY}"
N8N_URL="https://n8n.mentoriaaprovai.com.br"
WORKFLOW_ID="lf5tQEsgZD8AJ0Q8"
DATA_TABLE_ID="KgsVZRLRNB3WINee"

if [ -z "$API_KEY" ]; then
  echo "❌ N8N_API_KEY não definida. Defina com:"
  echo "   export N8N_API_KEY='sua-chave-aqui'"
  exit 1
fi

echo "🔧 Setup n8n Stripe Webhook + SMTP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Step 1: Testar API
echo "1️⃣  Testando conexão com n8n API..."
API_TEST=$(curl -s "$N8N_URL/api/v1/workflows" \
  -H "X-N8N-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" | grep -c "Aprovai")

if [ "$API_TEST" -eq 0 ]; then
  echo "❌ Falha ao conectar na n8n API. Verifique N8N_API_KEY"
  exit 1
fi

echo "✅ Conexão com n8n validada"

# Step 2: Verificar Data Table
echo ""
echo "2️⃣  Verificando Data Table 'tokens_aprovai'..."
DT_CHECK=$(curl -s "$N8N_URL/api/v1/data-tables" \
  -H "X-N8N-API-KEY: $API_KEY" | grep -c "tokens_aprovai")

if [ "$DT_CHECK" -eq 0 ]; then
  echo "⚠️  Data Table não encontrada. Criando..."
  curl -s -X POST "$N8N_URL/api/v1/data-tables" \
    -H "X-N8N-API-KEY: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "tokens_aprovai",
      "columns": [
        {"id": "token", "name": "token", "type": "string"},
        {"id": "email", "name": "email", "type": "string"},
        {"id": "nome", "name": "nome", "type": "string"},
        {"id": "valorPago", "name": "valorPago", "type": "number"},
        {"id": "sessionId", "name": "sessionId", "type": "string"},
        {"id": "criadoEm", "name": "criadoEm", "type": "date"},
        {"id": "usado", "name": "usado", "type": "boolean"}
      ]
    }' > /dev/null
  echo "✅ Data Table criada"
else
  echo "✅ Data Table já existe"
fi

# Step 3: Criar credencial SMTP (se configurada)
if [ -n "$SMTP_HOST" ]; then
  echo ""
  echo "3️⃣  Configurando credencial SMTP..."

  CRED_RESPONSE=$(curl -s -X POST "$N8N_URL/api/v1/credentials" \
    -H "X-N8N-API-KEY: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "SMTP Email",
      "type": "smtp",
      "data": {
        "host": "'$SMTP_HOST'",
        "port": '${SMTP_PORT:-587}',
        "user": "'$SMTP_USER'",
        "password": "'$SMTP_PASSWORD'",
        "secure": true
      }
    }')

  CRED_ID=$(echo "$CRED_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

  if [ -n "$CRED_ID" ]; then
    echo "✅ Credencial SMTP criada: $CRED_ID"
    echo "   Salve esse ID para referência: $CRED_ID"
  else
    echo "⚠️  Erro ao criar credencial SMTP. Resposta:"
    echo "$CRED_RESPONSE"
  fi
else
  echo ""
  echo "⚠️  SMTP não configurado. Defina variáveis de ambiente:"
  echo "   export SMTP_HOST='smtp.gmail.com'"
  echo "   export SMTP_PORT='587'"
  echo "   export SMTP_USER='seu-email@gmail.com'"
  echo "   export SMTP_PASSWORD='seu-app-password'"
fi

# Step 4: Resumo
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup parcial concluído!"
echo ""
echo "Próximos passos:"
echo "1. Configurar webhook no dashboard Stripe"
echo "2. Copiar STRIPE_WEBHOOK_SECRET"
echo "3. Reexecute esse script com:"
echo "   export STRIPE_WEBHOOK_SECRET='whsec_...'"
echo "   bash scripts/setup-n8n-stripe.sh"
echo ""
echo "Mais info: docs/04-n8n-stripe-setup-status.md"
