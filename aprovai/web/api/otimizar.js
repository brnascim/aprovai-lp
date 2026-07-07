export const config = { runtime: 'edge' };

/*
 * Endpoint do Motor Anti-ATS — protegido.
 *
 * Camadas de defesa (P0 da auditoria do Conselho):
 *  1. CORS restrito a origens conhecidas (ALLOWED_ORIGINS), não mais "*".
 *  2. Token de acesso assinado (HMAC-SHA256) emitido após pagamento.
 *     - Verificação server-side com ACCESS_TOKEN_SECRET (mesmo segredo no n8n).
 *     - Fail-closed: sem segredo configurado, o acesso é negado, a menos que
 *       ALLOW_UNVERIFIED_ACCESS === 'true' seja setado explicitamente (dev).
 *  3. Rate-limit por IP (Upstash Redis REST se configurado; senão, best-effort
 *     em memória por isolate) para conter abuso/estouro de custo da API.
 *
 * Formato do token: `<payloadB64url>.<sigB64url>`
 *   payload = base64url(JSON) contendo pelo menos { exp: <unix seconds> }.
 *   sig     = base64url(HMAC-SHA256(payloadB64url, ACCESS_TOKEN_SECRET)).
 * Ver scripts/generate-access-token.js e docs/07-token-acesso-e-endpoint.md
 * para emitir tokens (Node ou Code node do n8n).
 */

const SYSTEM = `Você é um especialista sênior em recrutamento e otimização de currículos para o mercado brasileiro, com profundo conhecimento de sistemas ATS (Applicant Tracking System) como Gupy, Kenoby, TOTVS, Workday e similares.

OBJETIVO: Analisar a vaga e o currículo fornecidos e produzir materiais completamente otimizados para maximizar a aderência às palavras-chave da vaga e a legibilidade por máquina na triagem automática.

ANÁLISE:
1. Extraia todas as palavras-chave críticas da vaga: hard skills, soft skills, ferramentas, tecnologias, certificações, jargão do setor, cargos relacionados, nível de senioridade
2. Estime a aderência do currículo original às palavras-chave da vaga (0-100): proporção das palavras-chave críticas que aparecem naturalmente no currículo atual
3. Estime a aderência pós-otimização

REGRAS DE REESCRITA:
- CURRÍCULO: Preserve TODAS as experiências e informações verdadeiras — nunca invente dados. Reescreva as descrições de cargo incorporando palavras-chave de forma natural e contextualizada. Use verbos de ação no pretérito (Liderou, Desenvolveu, Implementou, Reduziu, Aumentou). Inclua métricas quantitativas sempre que possível. Formato reverso cronológico. Remova dados irrelevantes (foto, objetivo genérico, CPF).
- CARTA DE APRESENTAÇÃO: Tom profissional e direto, 3 parágrafos: (1) por que esta empresa e esta vaga, (2) 2-3 conquistas específicas relevantes para os requisitos, (3) chamada para ação. Máximo 250 palavras.
- LINKEDIN (seção Sobre): Em primeira pessoa, 3-4 parágrafos fluidos, rico em palavras-chave mas sem parecer spam. 1500-2500 caracteres.
- DICAS: 3 orientações específicas e acionáveis baseadas no gap identificado — nunca dicas genéricas.

Os campos score_antes/score_depois são ESTIMATIVAS de aderência às palavras-chave da vaga, não um score oficial de nenhum ATS. Nunca prometa emprego, contratação ou aprovação.

RETORNE APENAS JSON VÁLIDO sem markdown, delimitadores de código, comentários ou qualquer texto fora do objeto JSON:
{"score_antes":<inteiro 0-100>,"score_depois":<inteiro 0-100>,"palavras_chave":[<máximo 12 strings>],"curriculo_otimizado":"<texto completo>","carta_apresentacao":"<texto completo>","resumo_linkedin":"<texto completo>","dicas":["<dica acionável 1>","<dica acionável 2>","<dica acionável 3>"]}`;

const DEFAULT_ORIGINS = [
  'https://mentoriaaprovai.com.br',
  'https://www.mentoriaaprovai.com.br',
];

function allowedOrigins() {
  const raw = (process.env.ALLOWED_ORIGINS || '').trim();
  if (!raw) return DEFAULT_ORIGINS;
  return raw.split(',').map((s) => s.trim()).filter(Boolean);
}

function corsHeaders(req) {
  const origin = req.headers.get('origin') || '';
  const list = allowedOrigins();
  const allow = list.includes(origin) ? origin : list[0];
  return {
    'content-type': 'application/json',
    'access-control-allow-origin': allow,
    'access-control-allow-methods': 'POST, OPTIONS',
    'access-control-allow-headers': 'content-type, authorization',
    'access-control-max-age': '86400',
    'vary': 'Origin',
  };
}

/* ── base64url helpers (edge-safe) ───────────────────────────────── */
function b64urlToBytes(b64url) {
  const b64 = b64url.replace(/-/g, '+').replace(/_/g, '/').padEnd(Math.ceil(b64url.length / 4) * 4, '=');
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}
function bytesToB64url(bytes) {
  let bin = '';
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
  return btoa(bin).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}
function timingSafeEqual(a, b) {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

/* ── token de acesso ─────────────────────────────────────────────── */
async function verifyAccessToken(token) {
  const secret = process.env.ACCESS_TOKEN_SECRET;
  if (!secret) {
    // Fail-closed por padrão. Só libera sem token se explicitamente permitido.
    return process.env.ALLOW_UNVERIFIED_ACCESS === 'true';
  }
  if (!token || typeof token !== 'string' || token.indexOf('.') === -1) return false;

  const [payloadB64, sigB64] = token.split('.');
  if (!payloadB64 || !sigB64) return false;

  try {
    const key = await crypto.subtle.importKey(
      'raw',
      new TextEncoder().encode(secret),
      { name: 'HMAC', hash: 'SHA-256' },
      false,
      ['sign'],
    );
    const mac = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(payloadB64));
    const expectedSig = bytesToB64url(new Uint8Array(mac));
    if (!timingSafeEqual(expectedSig, sigB64)) return false;

    const payload = JSON.parse(new TextDecoder().decode(b64urlToBytes(payloadB64)));
    if (payload && typeof payload.exp === 'number') {
      if (Math.floor(Date.now() / 1000) > payload.exp) return false; // expirado
    }
    return true;
  } catch {
    return false;
  }
}

function extractToken(req, body) {
  const auth = req.headers.get('authorization') || '';
  if (auth.toLowerCase().startsWith('bearer ')) return auth.slice(7).trim();
  if (body && typeof body.token === 'string') return body.token.trim();
  return '';
}

/* ── rate-limit ──────────────────────────────────────────────────── */
const MEM_HITS = new Map(); // best-effort por isolate (fallback)
const RL_LIMIT = Number(process.env.RATE_LIMIT_MAX || 12); // req por janela
const RL_WINDOW = Number(process.env.RATE_LIMIT_WINDOW_SEC || 60);

function clientIp(req) {
  const xff = req.headers.get('x-forwarded-for') || '';
  return (xff.split(',')[0] || req.headers.get('x-real-ip') || 'unknown').trim();
}

async function rateLimited(ip) {
  const url = process.env.UPSTASH_REDIS_REST_URL;
  const tok = process.env.UPSTASH_REDIS_REST_TOKEN;
  if (url && tok) {
    // Fixed-window via Upstash REST (INCR + EXPIRE).
    const win = Math.floor(Date.now() / 1000 / RL_WINDOW);
    const key = `rl:otimizar:${ip}:${win}`;
    try {
      const r = await fetch(`${url}/incr/${encodeURIComponent(key)}`, {
        headers: { Authorization: `Bearer ${tok}` },
      });
      const j = await r.json();
      const count = Number(j.result || 0);
      if (count === 1) {
        await fetch(`${url}/expire/${encodeURIComponent(key)}/${RL_WINDOW}`, {
          headers: { Authorization: `Bearer ${tok}` },
        }).catch(() => {});
      }
      return count > RL_LIMIT;
    } catch {
      // Se o Redis falhar, cai no fallback em memória em vez de abrir tudo.
    }
  }
  const now = Date.now();
  const arr = (MEM_HITS.get(ip) || []).filter((t) => now - t < RL_WINDOW * 1000);
  arr.push(now);
  MEM_HITS.set(ip, arr);
  return arr.length > RL_LIMIT;
}

/* ── handler ─────────────────────────────────────────────────────── */
export default async function handler(req) {
  const headers = corsHeaders(req);

  if (req.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers });
  }
  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Método não permitido.' }), { status: 405, headers });
  }

  const ip = clientIp(req);
  if (await rateLimited(ip)) {
    return new Response(
      JSON.stringify({ error: 'Muitas requisições. Aguarde alguns instantes e tente novamente.' }),
      { status: 429, headers: { ...headers, 'retry-after': String(RL_WINDOW) } },
    );
  }

  let body;
  try {
    body = await req.json();
  } catch {
    return new Response(JSON.stringify({ error: 'Payload inválido.' }), { status: 400, headers });
  }

  // Gate de acesso server-side (substitui o gate client-side de motor.html).
  const token = extractToken(req, body);
  if (!(await verifyAccessToken(token))) {
    return new Response(
      JSON.stringify({ error: 'Acesso não autorizado. Verifique o link de acesso enviado por e-mail.' }),
      { status: 401, headers },
    );
  }

  const vaga = (body.vaga || '').trim();
  const curriculo = (body.curriculo || '').trim();

  if (vaga.length < 50) {
    return new Response(JSON.stringify({ error: 'Descrição da vaga muito curta. Cole o texto completo.' }), { status: 400, headers });
  }
  if (curriculo.length < 100) {
    return new Response(JSON.stringify({ error: 'Currículo muito curto. Cole o conteúdo completo.' }), { status: 400, headers });
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return new Response(JSON.stringify({ error: 'Serviço temporariamente indisponível.' }), { status: 503, headers });
  }

  let anthropicRes;
  try {
    anthropicRes = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json',
      },
      body: JSON.stringify({
        model: process.env.ANTHROPIC_MODEL || 'claude-haiku-4-5-20251001',
        max_tokens: 8000,
        system: SYSTEM,
        messages: [{
          role: 'user',
          content: `VAGA:\n${vaga.slice(0, 4000)}\n\nCURRÍCULO ATUAL:\n${curriculo.slice(0, 4000)}`,
        }],
      }),
    });
  } catch {
    return new Response(JSON.stringify({ error: 'Erro de conexão com a IA. Tente novamente.' }), { status: 502, headers });
  }

  if (!anthropicRes.ok) {
    return new Response(JSON.stringify({ error: 'Erro ao processar. Tente novamente em instantes.' }), { status: 500, headers });
  }

  const data = await anthropicRes.json();
  const text = data?.content?.[0]?.text || '';

  let result;
  try {
    result = JSON.parse(text);
  } catch {
    const match = text.match(/\{[\s\S]*\}/);
    if (!match) {
      return new Response(JSON.stringify({ error: 'Resposta inválida da IA. Tente novamente.' }), { status: 500, headers });
    }
    try {
      result = JSON.parse(match[0]);
    } catch {
      return new Response(JSON.stringify({ error: 'Resposta inválida da IA. Tente novamente.' }), { status: 500, headers });
    }
  }

  return new Response(JSON.stringify(result), { status: 200, headers });
}
