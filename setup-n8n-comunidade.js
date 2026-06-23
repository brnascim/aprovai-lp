/**
 * setup-n8n-comunidade.js
 * Cria 2 workflows no n8n para a Comunidade Aprovai:
 *   1. Onboarding pós-Stripe → email com link do formulário
 *   2. Form → Evolution API → adiciona ao grupo WhatsApp correto
 * E cria a Data Table "ComunidadeMembers"
 */
const https = require('https');

const N8N_API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4OWFlZTNjOS00NTk3LTRjZmEtOTkzYi1hY2IxNTY2NzZmODIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZjA2MzFhMTgtYzllMS00MzRlLWEwMzEtZDE0Nzg4ZjNiM2IxIiwiaWF0IjoxNzgyMTM1MjEwfQ.8bCsGHygDu675izV8wfr9jvIGa7DlA8twTy2evlavsY';
const N8N_HOST = 'n8n.mentoriaaprovai.com.br';
const SMTP_CRED_ID = 'XBSdqZXVz8C2kq5Q';
// Evolution API - configurar após instalação no VPS
const EVO_URL = 'https://evo.mentoriaaprovai.com.br';
const EVO_INSTANCE = 'aprovai-bot';

// Mapeamento área → JID do grupo WhatsApp (preencher após criar grupos no Evolution API)
const GROUP_JIDS = {
  'Administrativo':          '120363426990866533@g.us',
  'Financeiro':              '120363409534930218@g.us',
  'RH / Gestão de Pessoas':  '120363424812504932@g.us',
  'Saúde / Hospitalar':      '120363427551579206@g.us',
  'TI / Tecnologia':         '120363427960561360@g.us',
  'Vendas / Comercial':      '120363409560634568@g.us',
  'Logística / Operações':   '120363426729198168@g.us',
  'Direito / Jurídico':      '120363427740478470@g.us',
  'Health & Fitness':        '120363411000844940@g.us',
  'Educação':                '120363411686762974@g.us',
  'Outra área':              '120363426990866533@g.us',
};

// ── EMAIL DE ONBOARDING ──────────────────────────────────────────────────────
const COMMUNITY_EMAIL_HTML = `<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#0A0D12;font-family:Inter,Helvetica,Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#0A0D12">
<tr><td align="center" style="padding:40px 20px">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;background:#13171E;border-radius:16px;overflow:hidden;border:1px solid rgba(255,255,255,0.08)">
<tr><td style="background:linear-gradient(135deg,#FF7A1A,#FFB02E);padding:24px 32px;text-align:center">
<p style="margin:0;font-size:22px;font-weight:700;color:#0A0D12">Aprovai</p>
<p style="margin:6px 0 0;font-size:13px;color:rgba(10,13,18,0.7)">Comunidade de Recolocação</p>
</td></tr>
<tr><td style="padding:32px">
<p style="margin:0 0 8px;font-size:22px;font-weight:700;color:#EEF1F6">Bem-vindo(a) à Comunidade!</p>
<p style="margin:0 0 24px;font-size:15px;color:#98A2B2;line-height:1.6">Sua assinatura foi confirmada. Para acessar o grupo WhatsApp da sua área e receber vagas diariamente, preencha o formulário abaixo em 2 minutos.</p>
<table cellpadding="0" cellspacing="0" style="margin:0 0 28px">
<tr><td style="background:linear-gradient(135deg,#FF7A1A,#FFB02E);border-radius:12px">
<a href="https://n8n.mentoriaaprovai.com.br/form/comunidade-form-webhook" style="display:block;padding:16px 32px;font-size:16px;font-weight:700;color:#0A0D12;text-decoration:none">Preencher formulário de acesso &rarr;</a>
</td></tr></table>
<p style="margin:0 0 12px;font-size:13px;font-weight:600;color:#EEF1F6;text-transform:uppercase;letter-spacing:.06em">O que você vai receber:</p>
<table cellpadding="0" cellspacing="0" width="100%">
<tr><td style="padding:8px 0;border-top:1px solid rgba(255,255,255,0.06);font-size:14px;color:#98A2B2"><b style="color:#FF7A1A">✓</b> Vagas diárias da sua área direto no WhatsApp</td></tr>
<tr><td style="padding:8px 0;border-top:1px solid rgba(255,255,255,0.06);font-size:14px;color:#98A2B2"><b style="color:#FF7A1A">✓</b> Grupo exclusivo com profissionais da mesma área</td></tr>
<tr><td style="padding:8px 0;border-top:1px solid rgba(255,255,255,0.06);font-size:14px;color:#98A2B2"><b style="color:#FF7A1A">✓</b> Vagas filtradas por compatibilidade com seu perfil</td></tr>
</table>
</td></tr>
<tr><td style="padding:20px 32px;border-top:1px solid rgba(255,255,255,0.06)">
<p style="margin:0;font-size:12px;color:#5A6272;text-align:center">Dúvidas? <a href="mailto:contato@mentoriaaprovai.com.br" style="color:#FF7A1A">contato@mentoriaaprovai.com.br</a></p>
</td></tr></table></td></tr></table></body></html>`;

// ── CÓDIGO: MAPEAR ÁREA → JID ────────────────────────────────────────────────
const MAP_AREA_CODE = `const GROUP_JIDS = ${JSON.stringify(GROUP_JIDS, null, 2)};

const nome    = $('Form Trigger').first().json['Seu nome completo'] || '';
const phone   = ($('Form Trigger').first().json['Número de WhatsApp'] || '').replace(/\\D/g, '');
const area    = $('Form Trigger').first().json['Área de atuação'] || 'Outra área';
const email   = $('Form Trigger').first().json['email'] || '';
const groupJid = GROUP_JIDS[area] || GROUP_JIDS['Outra área'];
const phoneJid = '55' + phone + '@s.whatsapp.net';

return [{ json: { nome, phone, phoneJid, area, groupJid, email, ingressoEm: new Date().toISOString() } }];`;

// ── CÓDIGO: MENSAGEM DE BOAS-VINDAS ──────────────────────────────────────────
const WELCOME_MSG_CODE = `const nome  = $json.nome || 'Olá';
const area  = $json.area || 'sua área';

const templates = [
  \`👋 Bem-vindo(a) ao grupo *\${area}* da Comunidade Aprovai!\\n\\nAqui você vai receber vagas diárias filtradas para a sua área, dicas de recolocação e networking com profissionais do mesmo setor.\\n\\nBoas-vindas, \${nome}! 🚀\`,
  \`Seja bem-vindo(a), \${nome}! 🎉\\n\\nVocê agora faz parte do grupo *\${area}* da Comunidade Aprovai.\\n\\n📌 Todo dia às 8h30 e 17h você receberá as melhores vagas filtradas para o seu perfil.\\n\\nConte com a gente na sua recolocação!\`,
];

return [{ json: { ...$json, mensagem: templates[Math.floor(Math.random() * templates.length)] } }];`;

// ── CÓDIGO: ONBOARDING (Stripe → extrair dados) ──────────────────────────────
const ONBOARDING_CODE = `const session = $json.body.data.object;
const email = (session.customer_details && session.customer_details.email) || session.customer_email || '';
const nome  = (session.customer_details && session.customer_details.name) || '';
const sessionId = session.id;
const productId = session.line_items?.data?.[0]?.price?.product || '';
return [{ json: { email, nome, sessionId, productId } }];`;

// ─────────────────────────────────────────────────────────────────────────────
// Workflow 1: Stripe → Email com link do formulário
// ─────────────────────────────────────────────────────────────────────────────
const workflowOnboarding = {
  name: 'Aprovai - Comunidade Onboarding',
  nodes: [
    {
      parameters: { httpMethod: 'POST', path: 'stripe-comunidade', responseMode: 'responseNode', options: {} },
      type: 'n8n-nodes-base.webhook', typeVersion: 2.1, position: [-400, 0],
      id: 'a0000001-0000-0000-0000-000000000001', name: 'Webhook Stripe Comunidade',
      webhookId: 'comunidade-stripe-webhook'
    },
    {
      parameters: {
        conditions: {
          options: { caseSensitive: true, leftValue: '', typeValidation: 'strict', version: 3 },
          conditions: [{ id: 'c1', leftValue: '={{ $json.body.type }}', rightValue: 'checkout.session.completed',
            operator: { type: 'string', operation: 'equals', name: 'filter.operator.equals' } }],
          combinator: 'and'
        }, options: {}
      },
      type: 'n8n-nodes-base.if', typeVersion: 2.3, position: [-200, 0],
      id: 'a0000002-0000-0000-0000-000000000002', name: 'If Checkout Completed'
    },
    {
      parameters: { jsCode: ONBOARDING_CODE },
      type: 'n8n-nodes-base.code', typeVersion: 2, position: [0, 0],
      id: 'a0000003-0000-0000-0000-000000000003', name: 'Extrair Dados'
    },
    {
      parameters: {
        fromEmail: 'br.boulder1@gmail.com',
        toEmail: '={{ $json.email }}',
        subject: 'Acesso à Comunidade Aprovai — preencha o formulário',
        message: COMMUNITY_EMAIL_HTML,
        options: { allowUnauthorizedCerts: false }
      },
      credentials: { smtp: { id: SMTP_CRED_ID, name: 'Gmail SMTP' } },
      type: 'n8n-nodes-base.emailSend', typeVersion: 2.1, position: [200, 0],
      id: 'a0000004-0000-0000-0000-000000000004', name: 'Enviar Email Comunidade'
    },
    {
      parameters: { respondWith: 'json', responseBody: '={{ JSON.stringify({ received: true }) }}', options: {} },
      type: 'n8n-nodes-base.respondToWebhook', typeVersion: 1.1, position: [400, 0],
      id: 'a0000005-0000-0000-0000-000000000005', name: 'Respond 200'
    }
  ],
  connections: {
    'Webhook Stripe Comunidade': { main: [[{ node: 'If Checkout Completed', type: 'main', index: 0 }]] },
    'If Checkout Completed': { main: [[{ node: 'Extrair Dados', type: 'main', index: 0 }]] },
    'Extrair Dados': { main: [[{ node: 'Enviar Email Comunidade', type: 'main', index: 0 }]] },
    'Enviar Email Comunidade': { main: [[{ node: 'Respond 200', type: 'main', index: 0 }]] }
  },
  settings: { executionOrder: 'v1' }
};

// ─────────────────────────────────────────────────────────────────────────────
// Workflow 2: Formulário → Evolution API → Grupo WhatsApp
// ─────────────────────────────────────────────────────────────────────────────
const workflowForm = {
  name: 'Aprovai - Comunidade Form',
  nodes: [
    {
      parameters: {
        formTitle: 'Comunidade Aprovai — Acesso ao Grupo',
        formDescription: 'Preencha para ser adicionado ao grupo da sua área e receber vagas diárias.',
        formFields: {
          values: [
            { fieldLabel: 'Seu nome completo', fieldType: 'text', requiredField: true, placeholder: 'Nome Sobrenome' },
            { fieldLabel: 'Número de WhatsApp', fieldType: 'text', requiredField: true, placeholder: '11999999999 (DDD + número, sem espaços)' },
            { fieldLabel: 'Área de atuação', fieldType: 'dropdown', requiredField: true,
              fieldOptions: { values: [
                { option: 'Administrativo' }, { option: 'Financeiro' },
                { option: 'RH / Gestão de Pessoas' }, { option: 'Saúde / Hospitalar' },
                { option: 'TI / Tecnologia' }, { option: 'Vendas / Comercial' },
                { option: 'Logística / Operações' }, { option: 'Direito / Jurídico' },
                { option: 'Health & Fitness' }, { option: 'Educação' },
                { option: 'Outra área' }
              ]}
            }
          ]
        },
        responseMode: 'onReceived',
        formResponseText: 'Obrigado! Em instantes você receberá uma mensagem no WhatsApp com o link do grupo.',
        path: 'comunidade-form'
      },
      type: 'n8n-nodes-base.formTrigger', typeVersion: 2.2, position: [-600, 0],
      id: 'b0000001-0000-0000-0000-000000000001', name: 'Form Trigger',
      webhookId: 'comunidade-form-webhook'
    },
    {
      parameters: { jsCode: MAP_AREA_CODE },
      type: 'n8n-nodes-base.code', typeVersion: 2, position: [-400, 0],
      id: 'b0000002-0000-0000-0000-000000000002', name: 'Mapear Área'
    },
    {
      // Adicionar participante ao grupo
      parameters: {
        method: 'POST',
        url: `=${EVO_URL}/group/updateParticipant/${EVO_INSTANCE}`,
        sendHeaders: true,
        headerParameters: { parameters: [{ name: 'apikey', value: '={{ $env.EVO_API_KEY }}' }] },
        sendBody: true, contentType: 'json',
        bodyParameters: { parameters: [] },
        jsonBody: `={{ JSON.stringify({ groupJid: $json.groupJid, action: "add", participants: [$json.phoneJid] }) }}`,
        options: { response: { response: { responseFormat: 'json' } } }
      },
      type: 'n8n-nodes-base.httpRequest', typeVersion: 4.2, position: [-200, 0],
      id: 'b0000003-0000-0000-0000-000000000003', name: 'Adicionar ao Grupo'
    },
    {
      parameters: { jsCode: WELCOME_MSG_CODE },
      type: 'n8n-nodes-base.code', typeVersion: 2, position: [0, 0],
      id: 'b0000004-0000-0000-0000-000000000004', name: 'Montar Boas-Vindas'
    },
    {
      // Enviar mensagem de boas-vindas para o membro
      parameters: {
        method: 'POST',
        url: `=${EVO_URL}/message/sendText/${EVO_INSTANCE}`,
        sendHeaders: true,
        headerParameters: { parameters: [{ name: 'apikey', value: '={{ $env.EVO_API_KEY }}' }] },
        sendBody: true, contentType: 'json',
        jsonBody: `={{ JSON.stringify({ number: $json.phoneJid, text: $json.mensagem, delay: 2000 }) }}`,
        options: {}
      },
      type: 'n8n-nodes-base.httpRequest', typeVersion: 4.2, position: [200, 0],
      id: 'b0000005-0000-0000-0000-000000000005', name: 'Enviar Boas-Vindas'
    },
    {
      parameters: {
        dataTableId: { __rl: true, value: 'ComunidadeMembers', mode: 'name' },
        columns: {
          mappingMode: 'defineBelow', matchingColumns: [], schema: [],
          value: {
            nome: '={{ $json.nome }}', whatsapp: '={{ $json.phone }}',
            area: '={{ $json.area }}', groupJid: '={{ $json.groupJid }}',
            ingressoEm: '={{ $json.ingressoEm }}', ativo: true
          }
        }, options: {}
      },
      type: 'n8n-nodes-base.dataTable', typeVersion: 1.1, position: [400, 0],
      id: 'b0000006-0000-0000-0000-000000000006', name: 'Salvar Membro'
    }
  ],
  connections: {
    'Form Trigger': { main: [[{ node: 'Mapear Área', type: 'main', index: 0 }]] },
    'Mapear Área': { main: [[{ node: 'Adicionar ao Grupo', type: 'main', index: 0 }]] },
    'Adicionar ao Grupo': { main: [[{ node: 'Montar Boas-Vindas', type: 'main', index: 0 }]] },
    'Montar Boas-Vindas': { main: [[{ node: 'Enviar Boas-Vindas', type: 'main', index: 0 }]] },
    'Enviar Boas-Vindas': { main: [[{ node: 'Salvar Membro', type: 'main', index: 0 }]] }
  },
  settings: { executionOrder: 'v1' }
};

// ─────────────────────────────────────────────────────────────────────────────
function apiRequest(method, path, body) {
  return new Promise((resolve, reject) => {
    const payload = body ? JSON.stringify(body) : '';
    const options = {
      hostname: N8N_HOST, port: 443, path, method,
      headers: {
        'X-N8N-API-KEY': N8N_API_KEY, 'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload)
      }
    };
    const req = https.request(options, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, body: JSON.parse(data) }); }
        catch { resolve({ status: res.statusCode, body: data }); }
      });
    });
    req.on('error', reject);
    if (payload) req.write(payload);
    req.end();
  });
}

async function createWorkflow(wf) {
  // Check if it already exists
  const list = await apiRequest('GET', '/api/v1/workflows?limit=50', '');
  const existing = list.body.data?.find(w => w.name === wf.name);
  if (existing) {
    console.log(`  Atualizando "${wf.name}" (id: ${existing.id})...`);
    const res = await apiRequest('PUT', `/api/v1/workflows/${existing.id}`, wf);
    return res;
  }
  console.log(`  Criando "${wf.name}"...`);
  const res = await apiRequest('POST', '/api/v1/workflows', wf);
  return res;
}

async function main() {
  console.log('\n=== Setup Comunidade Aprovai ===\n');

  console.log('[1/2] Workflow: Onboarding Stripe → Email');
  const r1 = await createWorkflow(workflowOnboarding);
  if (r1.status === 200 || r1.status === 201) {
    console.log('  ✓ Criado. Ativando...');
    await apiRequest('POST', `/api/v1/workflows/${r1.body.id}/activate`, {});
    console.log('  ✓ Ativo. Webhook URL:');
    console.log(`    https://n8n.mentoriaaprovai.com.br/webhook/stripe-comunidade`);
  } else {
    console.error('  ✗ Erro:', JSON.stringify(r1.body, null, 2));
  }

  console.log('\n[2/2] Workflow: Form → WhatsApp');
  const r2 = await createWorkflow(workflowForm);
  if (r2.status === 200 || r2.status === 201) {
    console.log('  ✓ Criado. Ativando...');
    await apiRequest('POST', `/api/v1/workflows/${r2.body.id}/activate`, {});
    console.log('  ✓ Ativo. Formulário URL:');
    console.log(`    https://n8n.mentoriaaprovai.com.br/form/comunidade-form-webhook`);
  } else {
    console.error('  ✗ Erro:', JSON.stringify(r2.body, null, 2));
  }

  console.log('\n=== Próximos passos ===');
  console.log('1. Instalar Evolution API no VPS (setup-evolution-api.sh)');
  console.log('2. Criar grupos WhatsApp por área no Evolution API');
  console.log('3. Atualizar GROUP_JIDS neste arquivo com os JIDs reais');
  console.log('4. Adicionar variável EVO_API_KEY nas n8n Variables');
  console.log('5. Adicionar endpoint stripe-comunidade no Stripe Dashboard\n');
}

main().catch(console.error);
