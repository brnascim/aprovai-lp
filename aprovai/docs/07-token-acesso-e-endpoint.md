# Token de acesso + proteção do endpoint (P0 do Conselho)

Fecha 2 dos P0 técnicos apontados pela auditoria: **endpoint sem verificação de
pagamento** e **gate de acesso apenas client-side**. O gate real passa a ser
server-side, com token assinado emitido só após o pagamento.

## Como funciona

1. Pagamento aprovado → webhook Stripe cai no n8n (`Aprovai - Entrega Pos-Pagamento`).
2. O n8n **emite um token assinado (HMAC-SHA256)** com o mesmo `ACCESS_TOKEN_SECRET`
   usado no endpoint e envia por e-mail o link:
   `https://mentoriaaprovai.com.br/acesso.html?tk=<TOKEN>`
3. `acesso.html` guarda o token em `localStorage` e o repassa ao `motor.html`.
4. `motor.html` envia o token em toda chamada a `/api/otimizar`
   (`Authorization: Bearer <TOKEN>` + no corpo).
5. O endpoint **verifica a assinatura e a expiração** antes de chamar a IA.
   Sem token válido → `401`.

O token **não** é segredo de servidor: é uma credencial de portador (bearer).
O segredo é o `ACCESS_TOKEN_SECRET`, que nunca sai do servidor/n8n.

## Formato do token

```
<payloadB64url>.<sigB64url>
```

- `payload` = base64url(JSON), contendo ao menos `{ "exp": <unix seconds> }`.
  Campos opcionais: `sid` (id da sessão/compra), `email`.
- `sig` = base64url(HMAC-SHA256(payloadB64url, ACCESS_TOKEN_SECRET)).

## Variáveis de ambiente

Configurar na Vercel (projeto da LP e do assistant) e no n8n:

| Variável | Onde | Descrição |
|---|---|---|
| `ACCESS_TOKEN_SECRET` | Vercel + n8n | Segredo forte compartilhado (gera e valida o token). |
| `ALLOWED_ORIGINS` | Vercel | CSV de origens liberadas no CORS. Default: domínios `mentoriaaprovai.com.br`. |
| `RATE_LIMIT_MAX` | Vercel (opcional) | Máx. de requisições por janela. Default `12`. |
| `RATE_LIMIT_WINDOW_SEC` | Vercel (opcional) | Janela do rate-limit em segundos. Default `60`. |
| `UPSTASH_REDIS_REST_URL` / `UPSTASH_REDIS_REST_TOKEN` | Vercel (opcional) | Rate-limit distribuído. Sem eles, cai para best-effort em memória. |
| `ALLOW_UNVERIFIED_ACCESS` | Vercel (dev) | `true` libera sem token. **Nunca em produção.** |
| `ANTHROPIC_MODEL` | Vercel (opcional) | Default `claude-haiku-4-5-20251001`. |

> **Fail-closed:** se `ACCESS_TOKEN_SECRET` não estiver setado e
> `ALLOW_UNVERIFIED_ACCESS` não for `true`, o endpoint **nega** todas as chamadas.
> Isso é proposital — melhor bloqueado do que aberto.

## Emitir um token (teste / manual)

```bash
ACCESS_TOKEN_SECRET="seu-segredo-forte" \
  node scripts/generate-access-token.js aluno@exemplo.com 365
```

## Emitir no n8n (Code node, após o pagamento)

```js
const crypto = require('crypto');
const secret = $env.ACCESS_TOKEN_SECRET;
const exp = Math.floor(Date.now() / 1000) + 365 * 24 * 60 * 60;
const payload = { exp, sid: $json.sessionId, email: $json.email };
const payloadB64 = Buffer.from(JSON.stringify(payload)).toString('base64url');
const sig = crypto.createHmac('sha256', secret).update(payloadB64).digest('base64url');
const token = `${payloadB64}.${sig}`;
return [{ json: {
  ...$json,
  token,
  link: `https://mentoriaaprovai.com.br/acesso.html?tk=${token}` } }];
```

## Rate-limit

- Com Upstash configurado: janela fixa por IP via `INCR`+`EXPIRE`.
- Sem Upstash: best-effort por isolate (defesa em profundidade). Para rate-limit
  forte em produção, **configure o Upstash** — edge functions são stateless.

## Ainda pendente (depende de credenciais do Bruno)

- Publicar o workflow n8n de entrega (bloqueado por SMTP + `STRIPE_WEBHOOK_SECRET`).
- Setar `ACCESS_TOKEN_SECRET` igual na Vercel e no n8n.
- (Recomendado) Provisionar Upstash Redis e setar as duas vars REST.
