#!/usr/bin/env node
/*
 * Emite um token de acesso assinado (HMAC-SHA256) para o Motor Anti-ATS.
 *
 * O mesmo ACCESS_TOKEN_SECRET precisa estar configurado:
 *   - na Vercel (endpoint web/api/otimizar.js e assistant/app/api/generate/route.ts)
 *   - no n8n (Code node que emite o token após o pagamento — ver docs/07)
 *
 * Uso:
 *   ACCESS_TOKEN_SECRET="..." node scripts/generate-access-token.js [email] [dias]
 *
 * Ex.:
 *   ACCESS_TOKEN_SECRET="segredo-forte" node scripts/generate-access-token.js aluno@ex.com 365
 *
 * O token resultante entra no link de acesso enviado por e-mail:
 *   https://mentoriaaprovai.com.br/acesso.html?tk=<TOKEN>
 */
const crypto = require('node:crypto');

const secret = process.env.ACCESS_TOKEN_SECRET;
if (!secret) {
  console.error('ERRO: defina ACCESS_TOKEN_SECRET no ambiente.');
  process.exit(1);
}

const email = process.argv[2] || null;
const dias = Number(process.argv[3] || 365);
const exp = Math.floor(Date.now() / 1000) + dias * 24 * 60 * 60;

const payload = { exp, sid: crypto.randomUUID(), ...(email ? { email } : {}) };
const payloadB64 = Buffer.from(JSON.stringify(payload)).toString('base64url');
const sig = crypto.createHmac('sha256', secret).update(payloadB64).digest('base64url');
const token = `${payloadB64}.${sig}`;

console.log(token);
