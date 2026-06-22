#!/bin/bash
# setup-evolution-api.sh
# Instala Evolution API v2 no VPS Hostinger (187.77.231.13)
# Proxy reverso via Nginx + SSL Certbot
# Subdomínio: evo.mentoriaaprovai.com.br

set -e

EVO_DOMAIN="evo.mentoriaaprovai.com.br"
EVO_PORT="8080"
EVO_API_KEY="aprovai-evo-$(openssl rand -hex 12)"
COMPOSE_DIR="/opt/evolution-api"

echo "================================================"
echo " Evolution API Setup — Aprovaí"
echo " Domínio: $EVO_DOMAIN"
echo "================================================"

# ── 1. Pré-requisitos ────────────────────────────────────────────────────────
apt-get update -qq
apt-get install -y -qq docker.io docker-compose nginx certbot python3-certbot-nginx

systemctl enable --now docker

# ── 2. Criar diretório e docker-compose ──────────────────────────────────────
mkdir -p "$COMPOSE_DIR"
cat > "$COMPOSE_DIR/docker-compose.yml" <<COMPOSE
version: '3.8'

services:
  evolution-api:
    image: atendai/evolution-api:v2.2.3
    container_name: evolution-api
    restart: unless-stopped
    ports:
      - "${EVO_PORT}:8080"
    environment:
      SERVER_URL: "https://${EVO_DOMAIN}"
      AUTHENTICATION_TYPE: apikey
      AUTHENTICATION_API_KEY: "${EVO_API_KEY}"
      AUTHENTICATION_EXPOSE_IN_FETCH_INSTANCES: true
      QRCODE_LIMIT: 30
      QRCODE_COLOR: "#FF7A1A"
      DEL_INSTANCE: false
      LANGUAGE: pt-BR
      LOG_LEVEL: ERROR
      LOG_BAILEYS: error
      CONFIG_SESSION_PHONE_CLIENT: "Aprovaí"
      CONFIG_SESSION_PHONE_NAME: "Chrome"
      # Banco de dados local (SQLite)
      DATABASE_PROVIDER: sqlite
      DATABASE_CONNECTION_URI: "file:./db/evolution.db"
      # Webhooks globais
      WEBHOOK_GLOBAL_ENABLED: false
      WEBHOOK_GLOBAL_URL: ""
      WEBHOOK_GLOBAL_WEBHOOK_BY_EVENTS: false
      # Redis (desabilitado para MVP)
      CACHE_REDIS_ENABLED: false
    volumes:
      - "${COMPOSE_DIR}/data:/evolution/store"
      - "${COMPOSE_DIR}/db:/evolution/db"

COMPOSE

echo "→ docker-compose.yml criado em $COMPOSE_DIR"

# ── 3. Nginx reverse proxy ───────────────────────────────────────────────────
cat > /etc/nginx/sites-available/evolution-api <<NGINX
server {
    listen 80;
    server_name ${EVO_DOMAIN};

    location / {
        proxy_pass         http://127.0.0.1:${EVO_PORT};
        proxy_http_version 1.1;
        proxy_set_header   Upgrade \$http_upgrade;
        proxy_set_header   Connection 'upgrade';
        proxy_set_header   Host \$host;
        proxy_set_header   X-Real-IP \$remote_addr;
        proxy_set_header   X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 86400s;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/evolution-api /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# ── 4. SSL com Certbot ───────────────────────────────────────────────────────
certbot --nginx -d "$EVO_DOMAIN" --non-interactive --agree-tos --email brnascim@gmail.com --redirect

# ── 5. Iniciar Evolution API ─────────────────────────────────────────────────
cd "$COMPOSE_DIR"
docker-compose up -d

echo ""
echo "================================================"
echo " ✓ Evolution API iniciada!"
echo ""
echo " URL:     https://${EVO_DOMAIN}"
echo " API Key: ${EVO_API_KEY}"
echo ""
echo " IMPORTANTE: salve essa API key no n8n:"
echo "   n8n > Settings > Variables > EVO_API_KEY = ${EVO_API_KEY}"
echo "   EVO_URL  = https://${EVO_DOMAIN}"
echo "   EVO_INSTANCE = aprovai-bot"
echo "================================================"
echo ""
echo "Próximos passos:"
echo "1. Criar instância WhatsApp:"
echo "   curl -X POST https://${EVO_DOMAIN}/instance/create \\"
echo "     -H 'apikey: ${EVO_API_KEY}' \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"instanceName\":\"aprovai-bot\",\"number\":\"5511932282317\",\"qrcode\":true,\"mobile\":false}'"
echo ""
echo "2. Obter QR code para conexão:"
echo "   curl https://${EVO_DOMAIN}/instance/connect/aprovai-bot \\"
echo "     -H 'apikey: ${EVO_API_KEY}'"
echo ""
echo "3. Criar grupos por área (repetir para cada área):"
echo "   curl -X POST https://${EVO_DOMAIN}/group/create/aprovai-bot \\"
echo "     -H 'apikey: ${EVO_API_KEY}' \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"subject\":\"Aprovaí | Administrativo\",\"description\":\"Vagas diárias de Administrativo — Comunidade Aprovaí\",\"participants\":[\"5511932282317@s.whatsapp.net\"]}'"
