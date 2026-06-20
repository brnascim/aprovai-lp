# Handoff — Projeto Aprovaí → Claude Code

Documento de transição. Tudo abaixo foi construído clicando manualmente no painel da Hostinger e na interface do n8n (via Claude in Chrome). A partir daqui, o trabalho deve continuar via terminal/SSH/API no Claude Code — muito mais confiável do que automação de UI no navegador (tivemos vários travamentos de canvas, timeouts de screenshot e quedas de sessão intermitentes durante a construção).

## 1. Contexto do negócio (resumo)

**Aprovaí** é um infoproduto "Motor Anti-ATS" (R$47 entrada + bump + upsell + recorrência R$19,90/mês) que funciona como **máquina de caixa** para financiar tráfego pago dos dois SaaS core do Bruno: **MargemOS** e **LicitaTrack**. Lucro líquido: 30% reinveste no próprio funil, 70% vai para anúncios dos core products — mas só depois que o funil atingir **LTV:CAC ≥ 3:1**.

Regras inegociáveis: sem promessa de renda/emprego garantido, sem depoimento fabricado, sem timer de escassez falso, conformidade LGPD/CDC. **Lovable está proibido** neste projeto.

## 2. Infraestrutura já provisionada

| Recurso | Valor |
|---|---|
| Domínio | `mentoriaaprovai.com.br` (registrado, ativo, vence 2027-06-19) |
| VPS | Hostinger KVM 1 · `srv1767887.hstgr.cloud` · IP `187.77.231.13` · datacenter Campinas · vence 2026-07-18 |
| n8n | Rodando via Docker (template oficial do catálogo Hostinger), projeto Docker `n8n-otjh`, container `n8n-otjh-n8n-1` na porta interna 5678 |
| Proxy/SSL | Traefik (projeto Docker `traefik`) — certificado Let's Encrypt válido e funcionando em `https://n8n.mentoriaaprovai.com.br` |
| DNS | Registro `A` em `n8n.mentoriaaprovai.com.br` → `187.77.231.13` (TTL 300), já propagado |
| n8n owner | Conta criada por Bruno (e-mail `bruno-bsn@hotmail.com`) — login manual necessário, sessão do navegador é instável (cai sozinha às vezes) |
| Landing page | Continua na Vercel (free tier) — não tocamos nisso nesta etapa |

**Configuração do container n8n** (editada via Docker Compose no painel Hostinger, aba "Editor .yaml" do projeto `n8n-otjh`):
- Label Traefik do router: `Host(\`n8n.mentoriaaprovai.com.br\`)` (hardcoded — **não** usa mais a variável padrão `${COMPOSE_PROJECT_NAME}.${TRAEFIK_HOST}` que a Hostinger gera por padrão)
- `WEBHOOK_URL=https://n8n.mentoriaaprovai.com.br/`
- Variáveis de ambiente do projeto: `TZ=America/Sao_Paulo`, `TRAEFIK_HOST=srv1767887.hstgr.cloud` (deixada como estava, não é mais usada pelas labels após a edição)

**Recomendação imediata para o Claude Code**: gerar uma API key do n8n (Settings → n8n API → Create API key, dentro da própria UI, ação que só o Bruno pode fazer pois requer estar autenticado) e usar a REST API (`https://n8n.mentoriaaprovai.com.br/api/v1/...` com header `X-N8N-API-KEY`) para criar/editar workflows programaticamente, em vez de clicar na interface. Isso evita todos os problemas de renderização de canvas que tivemos.

## 3. Workflow n8n já construído

**Nome**: `Aprovai - Entrega Pos-Pagamento`
**ID**: `lf5tQEsgZD8AJ0Q8`
**URL**: `https://n8n.mentoriaaprovai.com.br/workflow/lf5tQEsgZD8AJ0Q8`
**Status**: não publicado ainda (inativo)

Nodes construídos, nessa ordem e já conectados:

### 3.1 `Webhook` (trigger)
- Method: `POST`
- Path: `stripe-aprovai`
- Authentication: `None` (a validação de autenticidade precisa ser feita manualmente verificando a assinatura da Stripe — **ainda não implementada**, ver pendências)
- Respond: `Immediately`
- URL de produção: `https://n8n.mentoriaaprovai.com.br/webhook/stripe-aprovai`
- URL de teste: `https://n8n.mentoriaaprovai.com.br/webhook-test/stripe-aprovai`

### 3.2 `If`
- Condição: `{{ $json.body.type }}` **is equal to** `checkout.session.completed`
- Saída `true` → vai para o node `Gerar Token`
- Saída `false` → **sem nada conectado ainda** (deveria ao menos responder 200 vazio pra Stripe, ou ignorar)

### 3.3 `Gerar Token` (Code node, JavaScript)
Código exato já inserido:
```javascript
const crypto = require('crypto');
const session = $json.body.data.object;

const token = crypto.randomUUID();
const email = (session.customer_details && session.customer_details.email) || session.customer_email || '';
const nome = (session.customer_details && session.customer_details.name) || '';
const valorPago = session.amount_total ? session.amount_total / 100 : null;
const sessionId = session.id;

return [{
  json: {
    token,
    email,
    nome,
    valorPago,
    sessionId,
    criadoEm: new Date().toISOString(),
    usado: false
  }
}];
```
**Não testado ainda** (não foi possível confirmar se `require('crypto')` é permitido no sandbox do Code node desta instância — testar isso é o primeiro passo técnico a fazer).

### 3.4 Próximo node (não finalizado): `Insert row` em Data Table
- Estávamos criando uma **n8n Data Table** chamada `tokens_aprovai` (feature nativa do n8n, evita precisar de Postgres externo) para guardar: `token`, `email`, `nome`, `valorPago`, `sessionId`, `criadoEm`, `usado`.
- A criação da tabela ficou pendente — o fluxo de "Create new data table" abriu uma aba separada (`/projects/{projectId}/datatables/new`) que não chegamos a preencher.
- Project ID visto na URL: `jxASuvOX1g42b5Ow`

## 4. Pendências (ordem recomendada)

1. **Criar a Data Table `tokens_aprovai`** com as colunas acima (tipo string para token/email/nome/sessionId, number para valorPago, string/date para criadoEm, boolean para usado).
2. **Testar o node `Gerar Token`** com dados mock de um payload real de `checkout.session.completed` da Stripe (a Stripe tem exemplos de payload na documentação, ou usar o Stripe CLI `stripe trigger checkout.session.completed`).
3. **Conectar o `Insert row`** depois do `Gerar Token`.
4. **Adicionar validação de assinatura da Stripe** (HMAC com o webhook signing secret) — idealmente um Code node logo após o `Webhook`, antes do `If`, que rejeita a requisição se a assinatura não bater. Isso é importante por segurança: sem isso, qualquer um pode forjar um POST pra esse endpoint e gerar tokens de acesso de graça.
5. **Adicionar node de e-mail** (Send Email / SMTP / Gmail — credencial pendente) que envia o link de acesso com o token pro cliente.
6. **Adicionar `Respond to Webhook`** no final pra confirmar 200 pra Stripe rapidamente (Stripe exige resposta em poucos segundos).
7. **Configurar o endpoint de webhook no dashboard da Stripe** apontando para `https://n8n.mentoriaaprovai.com.br/webhook/stripe-aprovai` (URL de produção, não a de teste), selecionando o evento `checkout.session.completed`. Isso gera o **signing secret** necessário para o passo 4.
8. **Publicar (Publish/Active) o workflow** no n8n só depois de tudo testado.
9. No app Next.js do assistente (`assistant/app/api/generate/route.ts`, já existente no `aprovai-codex.zip`), adicionar a verificação do token: chamar a Data Table (ou expor um endpoint n8n próprio) pra confirmar que o token existe e `usado=false` antes de gerar o currículo, e marcar `usado=true` depois.

## 5. Status da Stripe

Bruno **já criou a conta Stripe** durante esta sessão (eu não participei disso — criação de conta é ação que não posso executar). Na última verificação, ele estava na tela `Desenvolvedores → Chaves de API` do dashboard Stripe (`https://dashboard.stripe.com/acct_1T8uxwD77xpAMwpo/apikeys`).

**Pendente**: pegar a Secret Key e o Publishable Key, e depois de configurar o endpoint de webhook (passo 7 acima), pegar o Signing Secret também. **Nenhuma dessas chaves deve ser compartilhada comigo nem digitada por mim** — o Bruno insere direto onde for preciso (variável de ambiente do n8n, ou n8n Credentials se usarmos um node nativo da Stripe).

## 6. Regras de segurança que se aplicam também ao Claude Code

- Nunca commitar chaves (Stripe secret key, signing secret, senha de e-mail) em texto puro no repositório. Usar `.env` (já existe `.env.example` no projeto) e `.gitignore`.
- Validar sempre a assinatura do webhook da Stripe antes de confiar no payload.
- Manter as 7 regras inegociáveis do `AGENTS.md` (sem promessa de renda, sem depoimento falso, etc.) em qualquer geração de copy/conteúdo.

## 7. Acesso técnico que o Claude Code vai precisar (o Bruno configura, não eu)

- **SSH para o VPS**: IP `187.77.231.13`. Bruno tem a senha root (definida no painel Hostinger, nunca compartilhada comigo).
- **n8n API key**: gerar em Settings → n8n API dentro da UI logada.
- **Stripe Secret Key + Webhook Signing Secret**: do dashboard Stripe.
- **Credencial SMTP/Gmail**: ainda não decidido qual usar para o envio do e-mail de entrega.

## 8. Arquivos relevantes já existentes do projeto (do `aprovai-codex.zip` anterior)

- `AGENTS.md` — contexto e regras para agente de código
- `TASKS.md` — backlog (esta etapa corresponde à "Tarefa 2: pagamento + entrega")
- `docs/03-spec-n8n-entrega.md` — spec original do fluxo de entrega (vale comparar com o que foi efetivamente construído acima e atualizar)
- `assistant/app/api/generate/route.ts` — endpoint que vai precisar da verificação de token (passo 9 da seção 4)
