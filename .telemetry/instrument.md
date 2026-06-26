# Instrumentation Guide — Aprovaí

## Targets: PostHog (product analytics) + Meta CAPI (ad attribution)

Generated from tracking-plan.yaml v1 on 2026-06-26.

**Stack overview:**

| Layer | Tecnologia | Como rastrear |
|-------|-----------|--------------|
| HTML estático (`index.html`, `motor.html`) | Vanilla JS | PostHog JS snippet via `<script>` |
| API Next.js (`/api/generate/route.ts`) | TypeScript (Node.js) | posthog-node SDK |
| Webhooks Stripe | n8n | HTTP Request node → PostHog Ingest API + Meta CAPI |

Não há grupo hierárquico (B2C single-player). Seção `group()` não se aplica.

---

## 1. SDK Setup

### 1a. PostHog JS (HTML estático)

Adicione ao `<head>` de `index.html` e `motor.html`:

```html
<!-- PostHog JS — cole antes de fechar </head> -->
<script>
  !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]);t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="init me ws ".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
  posthog.init('__POSTHOG_API_KEY__', {
    api_host: 'https://us.i.posthog.com',
    defaults: '2026-01-30',
    autocapture: false,        // desativado — só eventos explícitos
    capture_pageview: false,   // página rastreada manualmente via lp.viewed
    persistence: 'localStorage+cookie'
  });
</script>
```

### 1b. PostHog Node SDK (Next.js)

```bash
npm install posthog-node
```

Crie `aprovai/assistant/lib/analytics.ts`:

```typescript
import { PostHog } from 'posthog-node';

// Singleton — reutiliza a conexão entre requests Next.js
let _ph: PostHog | null = null;

export function getPostHog(): PostHog {
  if (!_ph) {
    _ph = new PostHog(process.env.POSTHOG_API_KEY!, {
      host: 'https://us.i.posthog.com',
      flushAt: 1,          // flush imediato em serverless (Vercel)
      flushInterval: 0,    // sem buffer — cada evento vai na hora
    });
  }
  return _ph;
}

export async function shutdownPostHog() {
  if (_ph) {
    await _ph.shutdown();
    _ph = null;
  }
}
```

> **Importante para Vercel (serverless):** `flushAt: 1` e `flushInterval: 0` garantem que o evento é enviado antes da função encerrar. Com buffer padrão em serverless, eventos são perdidos.

### 1c. Variáveis de Ambiente

| Variável | Onde usar | Obrigatório |
|----------|-----------|-------------|
| `POSTHOG_API_KEY` | Next.js API + n8n | Sim |
| `META_PIXEL_ID` | n8n | Sim |
| `META_ACCESS_TOKEN` | n8n | Sim |

Adicione ao `.env` (já gitignored):

```env
POSTHOG_API_KEY=phc_xxxxxxxxxxxxxxxxxxxxxx
META_PIXEL_ID=0000000000000000
META_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxx
```

Para o PostHog JS no HTML, substitua `__POSTHOG_API_KEY__` pelo valor real diretamente no HTML (é uma chave pública — pode ficar no frontend).

---

## 2. Identity

### identify() — quando e como

`identify()` é chamado uma vez: quando o usuário compra (via Stripe webhook → n8n). Antes da compra, o usuário é anônimo (PostHog gera um `distinct_id` automático no cookie).

**Trigger:** n8n webhook `checkout.session.completed` do Stripe.

**Node.js (n8n via PostHog Ingest API direta):**

```javascript
// n8n — HTTP Request node
// POST https://us.i.posthog.com/batch/
// Body (JSON):
{
  "api_key": "{{ $env.POSTHOG_API_KEY }}",
  "batch": [
    {
      "type": "identify",
      "distinct_id": "{{ $json.customer }}",  // stripe_customer_id como user ID
      "properties": {
        "$set": {
          "email": "{{ $json.customer_details.email }}",
          "plan": "entry",
          "purchased_at": "{{ $now.toISO() }}",
          "utm_source": "{{ $json.metadata.utm_source }}"
        },
        "$set_once": {
          "purchased_at": "{{ $now.toISO() }}"
        }
      }
    }
  ]
}
```

**Traits de usuário — referência completa:**

| Trait | Tipo | PII | Quando atualizar |
|-------|------|-----|-----------------|
| `email` | string | ✓ | set_on_purchase (Stripe) |
| `plan` | string | — | on_change (cada compra/upgrade) |
| `purchased_at` | datetime | — | set_once |
| `first_generate_at` | datetime | — | set_once (primeiro cv.generated) |
| `generate_count` | integer | — | incremento a cada cv.generated |
| `utm_source` | string | — | set_on_first_visit |
| `utm_medium` | string | — | set_on_first_visit |
| `utm_campaign` | string | — | set_on_first_visit |

**Alias anonymous → identified (opcional mas recomendado):**

Para ligar os eventos pré-compra (lp.viewed, checkout.started) ao comprador, passe o PostHog `distinct_id` como metadata no link de checkout do Stripe:

```javascript
// index.html — ao construir o link de checkout
const phId = posthog.get_distinct_id();
const stripeUrl = `https://checkout.stripe.com/...?client_reference_id=${phId}`;
```

No n8n, após o `identify`, chame o endpoint de alias:

```javascript
// n8n — HTTP Request adicional após identify
// POST https://us.i.posthog.com/batch/
{
  "api_key": "{{ $env.POSTHOG_API_KEY }}",
  "batch": [{
    "type": "alias",
    "distinct_id": "{{ $json.customer }}",    // stripe_customer_id (novo)
    "alias": "{{ $json.client_reference_id }}" // posthog anonymous_id (antigo)
  }]
}
```

---

## 3. Events

### 3a. Cliente — PostHog JS (HTML estático)

#### lp.viewed

```javascript
// index.html — DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
  const params = new URLSearchParams(window.location.search);
  posthog.capture('lp.viewed', {
    utm_source:   params.get('utm_source')   || null,
    utm_medium:   params.get('utm_medium')   || null,
    utm_campaign: params.get('utm_campaign') || null,
    utm_content:  params.get('utm_content')  || null,
    referrer:     document.referrer          || null,
    // Salva UTMs nas traits para segmentação futura
    $set_once: {
      utm_source:   params.get('utm_source')   || undefined,
      utm_medium:   params.get('utm_medium')   || undefined,
      utm_campaign: params.get('utm_campaign') || undefined,
    }
  });
});
```

#### checkout.started

```javascript
// index.html — adicione data-cta-location a cada botão de CTA
// Exemplo: <a href="..." class="cta-btn" data-cta-location="hero">Quero agora</a>

document.querySelectorAll('.cta-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    posthog.capture('checkout.started', {
      cta_location: btn.dataset.ctaLocation || 'unknown'
    });
  });
});
```

#### motor.accessed

```javascript
// motor.html — DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
  const generateCount = parseInt(localStorage.getItem('ph_generate_count') || '0');
  posthog.capture('motor.accessed', {
    is_first_access: generateCount === 0
  });
});
```

### 3b. Servidor — PostHog Node SDK (Next.js)

#### cv.generated — em `/api/generate/route.ts`

```typescript
import { getPostHog } from '@/lib/analytics';

export async function POST(req: Request) {
  const start = Date.now();
  const { vaga, experiencia, area } = await req.json();

  // ... validação e chamada Claude existente ...

  const ph = getPostHog();
  // user_id: ideal vir no header via cookie/token; fallback para 'anonymous'
  const userId = req.headers.get('x-posthog-id') || 'anonymous';

  try {
    const resp = await fetch('https://api.anthropic.com/v1/messages', { /* ... */ });
    const success = resp.ok;

    ph.capture({
      distinctId: userId,
      event: 'cv.generated',
      properties: {
        job_area:                  area || null,
        vaga_length_chars:         String(vaga).length,
        experiencia_length_chars:  String(experiencia).length,
        duration_ms:               Date.now() - start,
        success,
        error_type: success ? null : 'api_error',
      }
    });

    // Atualiza first_generate_at e generate_count
    if (success) {
      ph.capture({
        distinctId: userId,
        event: 'cv.generated',  // propriedades de trait via $set_once/$set
        properties: {
          $set_once: { first_generate_at: new Date().toISOString() },
          $set:      { generate_count: { $incr: 1 } }
        }
      });
    }

    await ph.shutdown(); // flush antes da função Vercel encerrar
    // ... retorna resposta ...
  } catch (e) {
    ph.capture({
      distinctId: userId,
      event: 'cv.generated',
      properties: {
        job_area: area || null,
        vaga_length_chars: String(vaga).length,
        experiencia_length_chars: String(experiencia).length,
        duration_ms: Date.now() - start,
        success: false,
        error_type: 'unexpected',
      }
    });
    await ph.shutdown();
    throw e;
  }
}
```

> **Nota:** Para passar o PostHog `distinct_id` do browser para o servidor, o `motor.html` pode incluir o ID num header ou query param ao chamar `/api/generate`. Alternativa simpler: o `distinct_id` não é crítico no server-side — os eventos de `cv.generated` podem ficar sob o `stripe_customer_id` se o link de acesso entregue pelo n8n incluir o customer ID.

### 3c. n8n — Webhooks Stripe → PostHog + Meta CAPI

Configure um workflow n8n que recebe o webhook do Stripe. Cada tipo de evento Stripe dispara os eventos PostHog e Meta CAPI correspondentes.

#### purchase.completed

```javascript
// n8n — Function node para montar o payload PostHog
const session = $json; // checkout.session.completed
const productType = {
  'price_entry_47':   'entry',
  'price_bump_27':    'bump',
  'price_upsell_97':  'upsell',
  'price_downsell_27':'downsell',
}[session.line_items?.[0]?.price?.id] || 'entry';

return [{
  json: {
    posthog_batch: [
      {
        type: 'capture',
        distinct_id: session.customer,
        event: 'purchase.completed',
        properties: {
          product_type:      productType,
          amount_brl:        session.amount_total / 100,
          payment_method:    session.payment_method_types?.[0] || null,
          stripe_session_id: session.id,
        },
        timestamp: new Date().toISOString()
      }
    ],
    meta_event: {
      event_name:   'Purchase',
      event_time:   Math.floor(Date.now() / 1000),
      event_id:     session.id,  // deduplicação com pixel client-side
      value:        session.amount_total / 100,
      currency:     'BRL',
      email_hashed: $crypto.createHash('sha256')
                     .update(session.customer_details?.email?.toLowerCase().trim() || '')
                     .digest('hex')
    }
  }
}];
```

**HTTP Request 1 — PostHog Ingest:**
```
POST https://us.i.posthog.com/batch/
Body: { "api_key": "{{ $env.POSTHOG_API_KEY }}", "batch": {{ $json.posthog_batch }} }
```

**HTTP Request 2 — Meta CAPI:**
```
POST https://graph.facebook.com/v19.0/{{ $env.META_PIXEL_ID }}/events
  ?access_token={{ $env.META_ACCESS_TOKEN }}
Body:
{
  "data": [{
    "event_name":  "{{ $json.meta_event.event_name }}",
    "event_time":  {{ $json.meta_event.event_time }},
    "event_id":    "{{ $json.meta_event.event_id }}",
    "action_source": "website",
    "custom_data": {
      "currency": "{{ $json.meta_event.currency }}",
      "value":    {{ $json.meta_event.value }}
    },
    "user_data": {
      "em": ["{{ $json.meta_event.email_hashed }}"]
    }
  }],
  "test_event_code": "TEST12345"
}
```

> Remova `test_event_code` em produção. Use-o durante a validação com o Events Manager do Meta.

#### subscription.started

```javascript
// n8n — customer.subscription.created
{
  "api_key": "{{ $env.POSTHOG_API_KEY }}",
  "batch": [{
    "type": "capture",
    "distinct_id": "{{ $json.customer }}",
    "event": "subscription.started",
    "properties": {
      "amount_brl": {{ $json.items.data[0].price.unit_amount / 100 }},
      "stripe_subscription_id": "{{ $json.id }}"
    }
  }, {
    "type": "identify",
    "distinct_id": "{{ $json.customer }}",
    "properties": { "$set": { "plan": "subscription" } }
  }]
}
```

#### subscription.cancelled

```javascript
// n8n — customer.subscription.deleted
{
  "api_key": "{{ $env.POSTHOG_API_KEY }}",
  "batch": [{
    "type": "capture",
    "distinct_id": "{{ $json.customer }}",
    "event": "subscription.cancelled",
    "properties": {
      "reason": "{{ $json.cancellation_details?.reason || 'user_cancelled' }}",
      "stripe_subscription_id": "{{ $json.id }}"
    }
  }, {
    "type": "identify",
    "distinct_id": "{{ $json.customer }}",
    "properties": { "$set": { "plan": "entry" } }
  }]
}
```

---

## 4. Módulo Completo — PostHog Node (Next.js)

Arquivo: `aprovai/assistant/lib/analytics.ts` — copy-paste completo:

```typescript
import { PostHog } from 'posthog-node';

// ─── Singleton ───────────────────────────────────────────────────────────────

let _ph: PostHog | null = null;

export function getPostHog(): PostHog {
  if (!_ph) {
    if (!process.env.POSTHOG_API_KEY) {
      throw new Error('POSTHOG_API_KEY não configurada');
    }
    _ph = new PostHog(process.env.POSTHOG_API_KEY, {
      host: 'https://us.i.posthog.com',
      flushAt: 1,
      flushInterval: 0,
    });
  }
  return _ph;
}

// ─── Tipos ───────────────────────────────────────────────────────────────────

type CvGeneratedProps = {
  job_area?: string | null;
  vaga_length_chars: number;
  experiencia_length_chars: number;
  duration_ms: number;
  success: boolean;
  error_type?: 'validation' | 'api_error' | 'timeout' | 'unexpected' | null;
};

// ─── Helpers ─────────────────────────────────────────────────────────────────

export function trackCvGenerated(userId: string, props: CvGeneratedProps) {
  const ph = getPostHog();
  ph.capture({
    distinctId: userId,
    event: 'cv.generated',
    properties: {
      job_area:                props.job_area ?? null,
      vaga_length_chars:       props.vaga_length_chars,
      experiencia_length_chars:props.experiencia_length_chars,
      duration_ms:             props.duration_ms,
      success:                 props.success,
      error_type:              props.error_type ?? null,
      ...(props.success ? {
        $set_once: { first_generate_at: new Date().toISOString() }
      } : {})
    }
  });
}

export async function flushAndShutdown() {
  if (_ph) {
    await _ph.shutdown();
    _ph = null;
  }
}
```

---

## 5. Arquitetura

### Client vs Server

| Evento | Layer | SDK | Trigger |
|--------|-------|-----|---------|
| `lp.viewed` | client | PostHog JS snippet | DOMContentLoaded em index.html |
| `checkout.started` | client | PostHog JS snippet | Click em CTA |
| `motor.accessed` | client | PostHog JS snippet | DOMContentLoaded em motor.html |
| `cv.generated` | server | posthog-node | Route `/api/generate` |
| `purchase.completed` | server (n8n) | PostHog Ingest API + Meta CAPI | Stripe webhook |
| `subscription.started` | server (n8n) | PostHog Ingest API | Stripe webhook |
| `subscription.cancelled` | server (n8n) | PostHog Ingest API | Stripe webhook |

### Flush/Shutdown

- **PostHog JS (browser):** flush automático, sem ação necessária.
- **posthog-node (Vercel serverless):** `flushAt: 1` + `await ph.shutdown()` ao final de cada handler. Sem isso, eventos são perdidos quando a função encerra.
- **n8n HTTP Requests:** síncronos — confirmação imediata na resposta HTTP.

### Error Handling

```typescript
// Em /api/generate — nunca deixe o tracking quebrar a entrega ao usuário
try {
  trackCvGenerated(userId, { ...props });
  await flushAndShutdown();
} catch (analyticsErr) {
  console.error('[analytics] erro não-bloqueante:', analyticsErr);
  // não relança — usuário recebe a resposta normalmente
}
```

---

## 6. Verificação

### Confirmar entrega

1. **PostHog Live Events:** Dashboard → Activity → Live Events. Filtre por `lp.viewed` e acesse a LP — deve aparecer em <5s.
2. **Meta Events Manager:** Business Manager → Pixels → seu pixel → Test Events. Cole o `test_event_code` no payload n8n e dispare uma compra de teste.
3. **n8n:** cada HTTP Request node mostra o status HTTP da resposta. `200` = entregue.

### Latência esperada

- PostHog JS (browser): real-time (<2s)
- posthog-node (Vercel): síncrono com `flushAt: 1`, <1s após `shutdown()`
- n8n → PostHog Ingest API: <2s após webhook Stripe
- Meta CAPI: aparece no Events Manager em até 1 minuto

### Desenvolvimento sem poluir produção

```javascript
// index.html / motor.html — bloqueia em localhost
posthog.init('__KEY__', {
  loaded: (ph) => {
    if (window.location.hostname === 'localhost') {
      ph.opt_out_capturing();
      console.log('[analytics] PostHog desativado em localhost');
    }
  }
});
```

```typescript
// analytics.ts — bloqueia em desenvolvimento
export function getPostHog(): PostHog {
  if (process.env.NODE_ENV !== 'production') {
    // retorna objeto no-op em dev
    return { capture: () => {}, identify: () => {}, shutdown: async () => {} } as any;
  }
  // ... inicialização real
}
```

Para n8n, use projetos separados: PostHog "Aprovaí Dev" e "Aprovaí Prod" com chaves diferentes.

---

## 7. Rollout Recomendado

**Fase 1 — Receita (máximo impacto, 1-2h):**
1. Configurar `purchase.completed` no n8n → PostHog + Meta CAPI
2. Validar com `test_event_code` no Meta Events Manager
3. Verificar no PostHog Live Events

**Fase 2 — Uso do produto (1h):**
4. Adicionar `cv.generated` em `/api/generate/route.ts`
5. Testar em staging (`next dev`) com `NODE_ENV=development` para ver o no-op

**Fase 3 — Funil completo (1h):**
6. Adicionar snippet PostHog JS no `index.html` (lp.viewed + checkout.started)
7. Adicionar snippet + `motor.accessed` em `motor.html`
8. Verificar funil LP → CTA → compra no PostHog Funnels

**Fase 4 — Retenção (quando houver assinantes):**
9. Adicionar `subscription.started` e `subscription.cancelled` no n8n

---

## 8. Constraints e Observações

- **Meta CAPI sem login:** sem email em eventos pré-compra. O match rate do CAPI depende do hash do email Stripe — espere 40-70% de match rate no Brasil.
- **cv.generated sem user_id:** o Motor não tem autenticação. Opções: (a) passar PostHog `distinct_id` como header no fetch do frontend para a API; (b) usar `stripe_customer_id` via link parametrizado entregue pelo n8n.
- **posthog-node em Vercel:** sempre `flushAt: 1` + `shutdown()` explícito. O comportamento padrão de batching perde eventos em funções serverless de curta duração.
- **Deduplicação Meta CAPI:** use `event_id: stripe_session_id` para deduplicar com o pixel client-side se for adicionado depois. Sem `event_id`, compras são contadas em dobro.
