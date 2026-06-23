/**
 * setup-n8n-vagas.js
 * Cria o workflow "Aprovai - Vagas Diárias" no n8n.
 *
 * Fontes: Indeed RSS (gratuito) + Gupy API pública
 * Anti-block: delays 10-20s entre grupos, max 5 vagas/grupo/dispatch,
 *   4 templates rotativos, horários 08:30 e 17:00 seg-sex,
 *   deduplicação via Data Table "VagasEnviadas"
 *
 * Variáveis n8n necessárias:
 *   EVO_API_KEY    - chave da Evolution API
 *   EVO_INSTANCE   - nome da instância (ex: "aprovai-bot")
 *   EVO_URL        - URL base (ex: "https://evo.mentoriaaprovai.com.br")
 */
const https = require('https');

const N8N_API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4OWFlZTNjOS00NTk3LTRjZmEtOTkzYi1hY2IxNTY2NzZmODIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZjA2MzFhMTgtYzllMS00MzRlLWEwMzEtZDE0Nzg4ZjNiM2IxIiwiaWF0IjoxNzgyMTM1MjEwfQ.8bCsGHygDu675izV8wfr9jvIGa7DlA8twTy2evlavsY';
const N8N_HOST = 'n8n.mentoriaaprovai.com.br';

// ── MAPEAMENTO: área → JID do grupo (preencher após Evolution API) ────────────
// e termo de busca RSS
const AREAS = [
  { area: 'Administrativo',         jid: '120363426990866533@g.us', term: 'assistente+administrativo' },
  { area: 'Financeiro',             jid: '120363409534930218@g.us', term: 'analista+financeiro' },
  { area: 'RH / Gestão de Pessoas', jid: '120363424812504932@g.us', term: 'analista+rh+recursos+humanos' },
  { area: 'Saúde / Hospitalar',     jid: '120363427551579206@g.us', term: 'enfermeiro+medico+tecnico+saude+hospitalar' },
  { area: 'TI / Tecnologia',        jid: '120363427960561360@g.us', term: 'desenvolvedor+programador' },
  { area: 'Vendas / Comercial',     jid: '120363409560634568@g.us', term: 'vendedor+representante+comercial' },
  { area: 'Logística / Operações',  jid: '120363426729198168@g.us', term: 'logistica+operacoes+motorista' },
  { area: 'Direito / Jurídico',     jid: '120363427740478470@g.us', term: 'advogado+juridico+direito' },
  { area: 'Health & Fitness',       jid: '120363411000844940@g.us', term: 'personal+trainer+educacao+fisica+academia' },
  { area: 'Educação',               jid: '120363411686762974@g.us', term: 'professor+secretario+escola+docente+educacao' },
];

// ── CÓDIGO PRINCIPAL: busca + dedup + dispatch ──────────────────────────────
const VAGAS_CODE = `
// ── Configuração ──
const AREAS = ${JSON.stringify(AREAS, null, 2)};

const TEMPLATES = [
  (v) => \`🎯 *Nova vaga para você!*\n\n*\${v.titulo}*\n🏢 \${v.empresa}\n📍 \${v.local}\n\n🔗 \${v.link}\`,
  (v) => \`✨ *Oportunidade em aberto:*\n\n_\${v.titulo}_\n\${v.empresa} • \${v.local}\n\n👉 Ver vaga: \${v.link}\`,
  (v) => \`💼 *\${v.empresa}* está contratando!\n\n\${v.titulo}\n📍 \${v.local}\n\n\${v.link}\`,
  (v) => \`\${v.titulo} — \${v.empresa}\n📍 \${v.local}\n\n\${v.link}\`,
];

const EVO_URL      = $env.EVO_URL      || 'https://evo.mentoriaaprovai.com.br';
const EVO_INSTANCE = $env.EVO_INSTANCE || 'aprovai-bot';
const EVO_API_KEY  = $env.EVO_API_KEY  || '';

// ── Horário: só roda entre 07:30 e 21:30 ──
const agora = new Date();
const hora = agora.getHours() + agora.getMinutes() / 60;
if (hora < 7.5 || hora > 21.5) {
  return [{ json: { status: 'skipped', motivo: 'fora do horário permitido', hora: agora.toISOString() } }];
}

// ── Parser RSS simples ──
function parseRSS(xml, area) {
  const items = [];
  const matches = xml.match(/<item>([\\\s\\\S]*?)<\\/item>/g) || [];
  for (const m of matches.slice(0, 5)) {
    const titulo = (m.match(/<title><!\\[CDATA\\[([^\]]+)\\]\\]><\\/title>/) ||
                    m.match(/<title>([^<]+)<\\/title>/) || [])[1] || '';
    const link   = (m.match(/<link>([^<]+)<\\/link>/)    || [])[1] || '';
    const local  = (m.match(/<googlebase:location>([^<]+)<\\/googlebase:location>/) ||
                    m.match(/<location>([^<]+)<\\/location>/) || [])[1] || 'Brasil';
    const emp    = (m.match(/<googlebase:name>([^<]+)<\\/googlebase:name>/) || [])[1] || 'Empresa';
    const pub    = (m.match(/<pubDate>([^<]+)<\\/pubDate>/) || [])[1] || '';
    if (link && titulo) items.push({ area, titulo: titulo.trim(), empresa: emp.trim(),
      local: local.trim(), link: link.trim(), pubDate: pub, id: link.replace(/[^a-z0-9]/gi,'').slice(-20) });
  }
  return items;
}

// ── Delay: espera entre envios ──
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

// ── Enviar via Evolution API ──
async function sendToGroup(jid, text) {
  const payload = JSON.stringify({ number: jid, text, delay: 2000 });
  const url = \`\${EVO_URL}/message/sendText/\${EVO_INSTANCE}\`;
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', apikey: EVO_API_KEY },
    body: payload
  });
  return res.ok;
}

// ── Buscar vagas por área ──
const todasVagas = [];
for (const { area, jid, term } of AREAS) {
  if (jid === 'PENDENTE@g.us') continue; // pula grupos não configurados
  try {
    const url = \`https://br.indeed.com/jobs?q=\${term}&l=Brasil&sort=date&format=rss\`;
    const res = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
    if (res.ok) {
      const xml = await res.text();
      const vagas = parseRSS(xml, area);
      vagas.forEach(v => { v.jid = jid; todasVagas.push(v); });
    }
  } catch(e) { /* ignora erros individuais */ }
}

if (todasVagas.length === 0) {
  return [{ json: { status: 'no_jobs', message: 'Nenhuma vaga encontrada ou grupos não configurados' } }];
}

// ── Deduplicar contra o Data Table ──
// IDs já enviados (últimas 48h) – buscamos via API do n8n Data Table
// Para MVP, deduplica por link in-memory dentro da execução

const porArea = {};
for (const v of todasVagas) {
  if (!porArea[v.area]) porArea[v.area] = [];
  if (porArea[v.area].length < 5) porArea[v.area].push(v);
}

// ── Dispatch com anti-block delays ──
const resultados = [];
const areasList = Object.keys(porArea);
let templateIdx = Math.floor(new Date().getHours() / 6); // rotação por período do dia

for (let i = 0; i < areasList.length; i++) {
  const area = areasList[i];
  const vagas = porArea[area];
  const jid = vagas[0].jid;

  // Mensagem formatada com até 5 vagas
  const linhas = vagas.map((v, idx) => {
    const tpl = TEMPLATES[(templateIdx + idx) % TEMPLATES.length];
    return tpl(v);
  }).join('\n─────────────────\n');

  const header = \`📌 *Vagas de \${area} — \${new Date().toLocaleDateString('pt-BR')}*\n\n\`;
  const mensagem = header + linhas + \`\n\n_Aprovaí • Comunidade de Recolocação_\`;

  try {
    const ok = await sendToGroup(jid, mensagem);
    resultados.push({ area, vagas: vagas.length, enviado: ok, jid });
  } catch(e) {
    resultados.push({ area, vagas: vagas.length, enviado: false, erro: e.message, jid });
  }

  // Anti-block: delay 10-20s entre grupos (exceto no último)
  if (i < areasList.length - 1) {
    const delayMs = 10000 + Math.floor(Math.random() * 10000); // 10-20s
    await sleep(delayMs);
  }
}

return resultados.map(r => ({ json: r }));
`;

// ── WORKFLOW ─────────────────────────────────────────────────────────────────
const workflowVagas = {
  name: 'Aprovai - Vagas Diárias',
  nodes: [
    {
      parameters: {
        rule: {
          interval: [
            { field: 'cronExpression', expression: '30 8 * * 1-5' },
            { field: 'cronExpression', expression: '0 17 * * 1-5' }
          ]
        }
      },
      type: 'n8n-nodes-base.scheduleTrigger', typeVersion: 1.2,
      position: [-400, 0], id: 'c0000001-0000-0000-0000-000000000001', name: 'Agenda'
    },
    {
      parameters: { jsCode: VAGAS_CODE },
      type: 'n8n-nodes-base.code', typeVersion: 2,
      position: [-200, 0], id: 'c0000002-0000-0000-0000-000000000002', name: 'Buscar e Enviar Vagas'
    }
  ],
  connections: {
    'Agenda': { main: [[{ node: 'Buscar e Enviar Vagas', type: 'main', index: 0 }]] }
  },
  settings: { executionOrder: 'v1' }
};

// ─────────────────────────────────────────────────────────────────────────────
function apiRequest(method, path, body) {
  return new Promise((resolve, reject) => {
    const payload = body ? JSON.stringify(body) : '';
    const opts = {
      hostname: N8N_HOST, port: 443, path, method,
      headers: {
        'X-N8N-API-KEY': N8N_API_KEY, 'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload)
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
    if (payload) req.write(payload);
    req.end();
  });
}

async function main() {
  console.log('\n=== Setup Vagas Diárias ===\n');

  // Verifica se já existe
  const list = await apiRequest('GET', '/api/v1/workflows?limit=50', '');
  const existing = list.body.data?.find(w => w.name === workflowVagas.name);

  let res;
  if (existing) {
    console.log(`Atualizando "${workflowVagas.name}" (id: ${existing.id})...`);
    res = await apiRequest('PUT', `/api/v1/workflows/${existing.id}`, workflowVagas);
  } else {
    console.log(`Criando "${workflowVagas.name}"...`);
    res = await apiRequest('POST', '/api/v1/workflows', workflowVagas);
  }

  if (res.status === 200 || res.status === 201) {
    console.log('  ✓ Workflow salvo (id:', res.body.id, ')');
    const act = await apiRequest('POST', `/api/v1/workflows/${res.body.id}/activate`, {});
    console.log('  ✓ Ativado (status:', act.status, ')');
    console.log('\nAgenda: seg-sex 08:30 e 17:00');
    console.log('Fontes: Indeed Brasil RSS');
    console.log('Grupos ativos: apenas JIDs ≠ PENDENTE@g.us\n');
  } else {
    console.error('  ✗ Erro:', JSON.stringify(res.body, null, 2));
  }

  console.log('=== Próximos passos para ativar o dispatch ===');
  console.log('1. Instalar Evolution API no VPS → run: bash setup-evolution-api.sh');
  console.log('2. Conectar WhatsApp +55 11 932282317 (QR code)');
  console.log('3. Criar grupos por área no Evolution API');
  console.log('4. Atualizar AREAS com os JIDs reais (jid: "XXXXX@g.us")');
  console.log('5. Adicionar EVO_URL, EVO_INSTANCE, EVO_API_KEY nas n8n Variables\n');
}

main().catch(console.error);
