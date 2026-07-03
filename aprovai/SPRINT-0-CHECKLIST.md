# Sprint 0 — Checklist para destravar produção

Bloqueadores de receita do funil Aprovaí. Ordem importa: cada passo destrava o próximo.
Marque `[x]` conforme concluir.

**Divisão de responsabilidade:**

| Você (CEO) faz | Engenheiro faz |
|---|---|
| Criar/colar `ANTHROPIC_API_KEY` na Vercel | Redeploy e validar output |
| Criar o endpoint webhook na Stripe | Implementar validação HMAC |
| Gerar a senha de app + credencial SMTP | Montar node de e-mail e Data Table |
| Clicar **Active** no fim | Testar a compra ponta a ponta |

---

## 🔴 Passo 1 — `ANTHROPIC_API_KEY` na Vercel
_Sem isso a ferramenta não gera nada. Comece por aqui._

- [ ] Pegar a chave: https://platform.claude.com → **API Keys** → **Create Key** → copiar (`sk-ant-api03-...`). Só aparece uma vez.
- [ ] https://vercel.com → projeto **aprovai-lp** → **Settings** → **Environment Variables**.
- [ ] Adicionar:
  - **Key:** `ANTHROPIC_API_KEY`
  - **Value:** a chave copiada
  - **Environments:** Production, Preview e Development
- [ ] **Save**.
- [ ] Aba **Deployments** → último deploy → **⋯** → **Redeploy** (a env var só entra em vigor num novo deploy).
- [ ] ✅ Teste: abrir a LP em produção e usar a ferramenta com vaga + currículo reais. Se gerar resultado, funcionou.

---

## 🟠 Passo 2 — Webhook no dashboard da Stripe
_Isso gera o "signing secret" que o Passo 4 (validação de segurança) precisa._

- [ ] https://dashboard.stripe.com → **Desenvolvedores** → **Webhooks** → **Adicionar endpoint**.
- [ ] **URL do endpoint:** `https://n8n.mentoriaaprovai.com.br/webhook/stripe-aprovai`
  _(URL de produção, não a `/webhook-test/`)_
- [ ] **Selecionar eventos:** marcar apenas `checkout.session.completed`.
- [ ] **Adicionar endpoint**.
- [ ] Revelar o **Signing secret** (`whsec_...`) e copiar — usar no Passo 4.

---

## 🟡 Passo 3 — SMTP no n8n (e-mail de acesso)
_Recomendado: criar uma "Senha de app" no Gmail em vez de usar a senha real._

- [ ] Gmail: https://myaccount.google.com/apppasswords → gerar senha de app → copiar os 16 caracteres.
- [ ] Entrar no n8n: https://n8n.mentoriaaprovai.com.br (login `bruno-bsn@hotmail.com`).
- [ ] **Credentials** → **Add credential** → buscar **SMTP**.
- [ ] Preencher:
  - **Host:** `smtp.gmail.com`
  - **Port:** `465` · **SSL/TLS:** ligado
  - **User:** seu e-mail Gmail
  - **Password:** a senha de app de 16 caracteres
- [ ] **Save**.

---

## 🟡 Passo 4 — Amarrar tudo no workflow n8n e publicar
_Nodes de engenharia ficam com o Engenheiro Fundador. Você entrega o signing secret + credencial SMTP e clica Active no fim._

- [ ] Abrir o workflow **Aprovai - Entrega Pos-Pagamento** (`.../workflow/lf5tQEsgZD8AJ0Q8`).
- [ ] Guardar o **signing secret** (`whsec_...`) em **Settings → Variables** ou numa Credential — **nunca** em texto puro num node.
- [ ] Confirmar a cadeia: **Webhook → validação HMAC → If → Gerar Token → Insert row (`tokens_aprovai`) → Send Email → Respond to Webhook**.
- [ ] Clicar no toggle **Active** (canto superior direito) para publicar.

---

## ✅ Teste final (ponta a ponta)
- [ ] Rodar uma compra de teste (Stripe test mode) e confirmar que o acesso chega por e-mail automaticamente.
- [ ] Validar o output do Motor Anti-ATS em produção com vaga + currículo reais.
- [ ] Configurar a chave real do PostHog (hoje `phc_REPLACE_WITH_YOUR_KEY`) para medir o funil.

---

## Regras inegociáveis (valem para qualquer passo)
- Nunca commitar chaves (Stripe secret, signing secret, senha SMTP) em texto puro no repositório — usar env vars / Credentials.
- Validar sempre a assinatura HMAC do webhook Stripe antes de confiar no payload.
- Sem promessa de renda/emprego garantido, sem depoimento fabricado, sem timer de escassez falso. Conformidade LGPD/CDC.
