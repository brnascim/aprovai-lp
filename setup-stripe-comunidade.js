/**
 * setup-stripe-comunidade.js
 * Cria via API Stripe:
 *  1. Produto "Comunidade Aprovaí - Vagas por WhatsApp" (recorrente R$19,90/mês)
 *  2. Payment Link para o produto
 *  3. Webhook endpoint para stripe-comunidade (checkout.session.completed)
 *
 * Lê a secret key de STRIPE-SETUP-FINAL.md (gitignored — nunca exibe o valor)
 */
const https  = require('https');
const fs     = require('fs');
const path   = require('path');

// ── Ler secret key sem exibir ────────────────────────────────────────────────
const mdPath = path.join(__dirname, 'STRIPE-SETUP-FINAL.md');
const mdText = fs.readFileSync(mdPath, 'utf8');
const keyMatch = mdText.match(/STRIPE_SECRET_KEY=(\S+)/);
if (!keyMatch) { console.error('STRIPE_SECRET_KEY não encontrado em STRIPE-SETUP-FINAL.md'); process.exit(1); }
const STRIPE_SK = keyMatch[1];

// ── Helper: chamada à Stripe API ─────────────────────────────────────────────
function stripe(method, endpoint, params) {
  return new Promise((resolve, reject) => {
    const body = params
      ? Object.entries(params)
          .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
          .join('&')
      : '';
    const opts = {
      hostname: 'api.stripe.com', port: 443,
      path: `/v1/${endpoint}`, method,
      headers: {
        Authorization: `Bearer ${STRIPE_SK}`,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': Buffer.byteLength(body),
      }
    };
    const req = https.request(opts, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, body: JSON.parse(d) }); }
        catch { resolve({ status: res.statusCode, body: d }); }
      });
    });
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
}

// ── Helper para parâmetros aninhados (metadata, price_data etc.) ──────────────
function stripeNested(method, endpoint, params) {
  return new Promise((resolve, reject) => {
    const parts = [];
    function flatten(obj, prefix) {
      for (const [k, v] of Object.entries(obj)) {
        const key = prefix ? `${prefix}[${k}]` : k;
        if (v !== null && typeof v === 'object' && !Array.isArray(v)) flatten(v, key);
        else if (Array.isArray(v)) v.forEach((item, i) => {
          if (typeof item === 'object') flatten(item, `${key}[${i}]`);
          else parts.push(`${encodeURIComponent(`${key}[${i}]`)}=${encodeURIComponent(item)}`);
        });
        else parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(v)}`);
      }
    }
    flatten(params);
    const body = parts.join('&');
    const opts = {
      hostname: 'api.stripe.com', port: 443,
      path: `/v1/${endpoint}`, method,
      headers: {
        Authorization: `Bearer ${STRIPE_SK}`,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': Buffer.byteLength(body),
      }
    };
    const req = https.request(opts, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, body: JSON.parse(d) }); }
        catch { resolve({ status: res.statusCode, body: d }); }
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

async function main() {
  console.log('\n=== Setup Stripe — Comunidade Aprovaí ===\n');

  // ── 1. Produto ──────────────────────────────────────────────────────────────
  console.log('[1/4] Criando produto...');
  const prod = await stripe('POST', 'products', {
    name: 'Comunidade Aprovaí — Vagas por WhatsApp',
    description: 'Acesso à comunidade exclusiva com vagas diárias por área de atuação no WhatsApp.',
    'metadata[funil]': 'aprovai-comunidade',
  });
  if (prod.status !== 200) { console.error('Erro produto:', prod.body?.error?.message); process.exit(1); }
  const prodId = prod.body.id;
  console.log(`  ✓ Produto: ${prodId}`);

  // ── 2. Preço recorrente R$19,90/mês ─────────────────────────────────────────
  console.log('[2/4] Criando preço R$19,90/mês...');
  const price = await stripe('POST', 'prices', {
    product: prodId,
    unit_amount: 1990,
    currency: 'brl',
    'recurring[interval]': 'month',
    'recurring[interval_count]': 1,
    nickname: 'Mensal R$19,90',
  });
  if (price.status !== 200) { console.error('Erro preço:', price.body?.error?.message); process.exit(1); }
  const priceId = price.body.id;
  console.log(`  ✓ Preço: ${priceId}`);

  // ── 3. Payment Link ──────────────────────────────────────────────────────────
  console.log('[3/4] Criando Payment Link...');
  const pl = await stripeNested('POST', 'payment_links', {
    'line_items[0][price]': priceId,
    'line_items[0][quantity]': 1,
    'after_completion[type]': 'redirect',
    'after_completion[redirect][url]': 'https://mentoriaaprovai.com.br/obrigado-comunidade.html',
    'metadata[produto]': 'comunidade-aprovai',
    'subscription_data[metadata][origem]': 'payment-link-comunidade',
  });
  if (pl.status !== 200) { console.error('Erro payment link:', pl.body?.error?.message); process.exit(1); }
  const plUrl = pl.body.url;
  console.log(`  ✓ Payment Link: ${plUrl}`);

  // ── 4. Webhook endpoint para stripe-comunidade ───────────────────────────────
  console.log('[4/4] Registrando webhook stripe-comunidade...');
  const wh = await stripe('POST', 'webhook_endpoints', {
    url: 'https://n8n.mentoriaaprovai.com.br/webhook/stripe-comunidade',
    'enabled_events[0]': 'checkout.session.completed',
    'enabled_events[1]': 'customer.subscription.deleted',
    description: 'Aprovai Comunidade — onboarding e cancelamento',
  });
  if (wh.status !== 200) {
    // Webhook duplicado é aceitável
    if (wh.body?.error?.code === 'resource_already_exists') {
      console.log('  ℹ Webhook já existe (OK)');
    } else {
      console.error('Erro webhook:', wh.body?.error?.message);
    }
  } else {
    const whSecret = wh.body.secret;
    console.log(`  ✓ Webhook ID: ${wh.body.id}`);

    // Gravar segredo no arquivo local (gitignored)
    const secretsFile = path.join(__dirname, 'STRIPE-COMUNIDADE-SECRETS.md');
    fs.writeFileSync(secretsFile, [
      '# Stripe Comunidade — Secrets (GITIGNORED)',
      '',
      `Payment Link: ${plUrl}`,
      `Price ID: ${priceId}`,
      `Product ID: ${prodId}`,
      `Webhook ID: ${wh.body.id}`,
      `STRIPE_COMUNIDADE_WEBHOOK_SECRET=${whSecret}`,
      '',
      '## n8n Variable a adicionar:',
      `STRIPE_COMUNIDADE_WEBHOOK_SECRET=${whSecret}`,
    ].join('\n'));
    console.log(`  ✓ Secrets gravados em STRIPE-COMUNIDADE-SECRETS.md (gitignored)`);
  }

  console.log('\n=== Resumo ===');
  console.log(`Payment Link R$19,90/mês: ${plUrl}`);
  console.log('Webhook: https://n8n.mentoriaaprovai.com.br/webhook/stripe-comunidade');
  console.log('\nPróximos passos:');
  console.log('1. Adicionar link no upsell/landing: var COMUNIDADE_STRIPE_LINK = "' + plUrl + '"');
  console.log('2. Adicionar STRIPE_COMUNIDADE_WEBHOOK_SECRET nas n8n Variables');
  console.log('3. Rodar: bash setup-evolution-api.sh no VPS 187.77.231.13');
}

main().catch(console.error);
