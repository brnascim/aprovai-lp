const https = require('https');

const N8N_API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4OWFlZTNjOS00NTk3LTRjZmEtOTkzYi1hY2IxNTY2NzZmODIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZjA2MzFhMTgtYzllMS00MzRlLWEwMzEtZDE0Nzg4ZjNiM2IxIiwiaWF0IjoxNzgyMTM1MjEwfQ.8bCsGHygDu675izV8wfr9jvIGa7DlA8twTy2evlavsY';
const WORKFLOW_ID = 'lf5tQEsgZD8AJ0Q8';
const SMTP_CRED_ID = 'XBSdqZXVz8C2kq5Q';

const GERAR_TOKEN_CODE = `const session = $json.body.data.object;

function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = Math.random() * 16 | 0;
    return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
  });
}

const token = uuidv4();
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
}];`;

const EMAIL_HTML = `<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#0A0D12;font-family:Inter,Helvetica,Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#0A0D12">
<tr><td align="center" style="padding:40px 20px">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;background:#13171E;border-radius:16px;overflow:hidden;border:1px solid rgba(255,255,255,0.08)">
<tr><td style="background:linear-gradient(135deg,#FF7A1A,#FFB02E);padding:24px 32px;text-align:center">
<p style="margin:0;font-size:22px;font-weight:700;color:#0A0D12">Aprovai</p>
<p style="margin:6px 0 0;font-size:13px;color:rgba(10,13,18,0.7)">Motor Anti-ATS</p>
</td></tr>
<tr><td style="padding:32px">
<p style="margin:0 0 8px;font-size:22px;font-weight:700;color:#EEF1F6">Seu acesso esta liberado!</p>
<p style="margin:0 0 24px;font-size:15px;color:#98A2B2;line-height:1.6">Obrigado pela compra. O Motor Anti-ATS esta pronto para reescrever seu curriculo, carta de apresentacao e LinkedIn para passar pela triagem automatica em 2 minutos.</p>
<table cellpadding="0" cellspacing="0" style="margin:0 0 28px">
<tr><td style="background:linear-gradient(135deg,#FF7A1A,#FFB02E);border-radius:12px">
<a href="https://mentoriaaprovai.com.br/acesso.html?tk={{ $json.token }}" style="display:block;padding:16px 32px;font-size:16px;font-weight:700;color:#0A0D12;text-decoration:none">Acessar o Motor Anti-ATS &rarr;</a>
</td></tr></table>
<p style="margin:0 0 12px;font-size:13px;font-weight:600;color:#EEF1F6;text-transform:uppercase;letter-spacing:.06em">Como usar em 3 passos:</p>
<table cellpadding="0" cellspacing="0" width="100%">
<tr><td style="padding:8px 0;border-top:1px solid rgba(255,255,255,0.06);font-size:14px;color:#98A2B2"><b style="color:#FF7A1A">1.</b> Cole o texto completo da vaga</td></tr>
<tr><td style="padding:8px 0;border-top:1px solid rgba(255,255,255,0.06);font-size:14px;color:#98A2B2"><b style="color:#FF7A1A">2.</b> Cole o conteudo do seu curriculo atual</td></tr>
<tr><td style="padding:8px 0;border-top:1px solid rgba(255,255,255,0.06);font-size:14px;color:#98A2B2"><b style="color:#FF7A1A">3.</b> Receba o curriculo otimizado para ATS em 2 minutos</td></tr>
</table>
</td></tr>
<tr><td style="padding:20px 32px;border-top:1px solid rgba(255,255,255,0.06)">
<p style="margin:0;font-size:12px;color:#5A6272;text-align:center">Problemas? Responda este e-mail ou escreva para <a href="mailto:contato@mentoriaaprovai.com.br" style="color:#FF7A1A">contato@mentoriaaprovai.com.br</a></p>
<p style="margin:8px 0 0;font-size:11px;color:#3A4050;text-align:center">2026 Aprovai &middot; mentoriaaprovai.com.br</p>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>`;

const workflow = {
  name: "Aprovai - Entrega Pos-Pagamento",
  nodes: [
    {
      parameters: {
        httpMethod: "POST",
        path: "stripe-aprovai",
        responseMode: "responseNode",
        options: {}
      },
      type: "n8n-nodes-base.webhook",
      typeVersion: 2.1,
      position: [-144, -144],
      id: "9440fec5-5f7c-4860-812b-e12fff51ebfb",
      name: "Webhook",
      webhookId: "332a07fc-6b0a-46f7-b6ba-f742b18f4ab5"
    },
    {
      parameters: {
        conditions: {
          options: { caseSensitive: true, leftValue: "", typeValidation: "strict", version: 3 },
          conditions: [{
            id: "278a6c5b-c9a6-4f20-966a-6edbb3423b06",
            leftValue: "={{ $json.body.type }}",
            rightValue: "checkout.session.completed",
            operator: { type: "string", operation: "equals", name: "filter.operator.equals" }
          }],
          combinator: "and"
        },
        options: {}
      },
      type: "n8n-nodes-base.if",
      typeVersion: 2.3,
      position: [64, -144],
      id: "b8af6c91-5e36-4589-a8da-50007291ecbd",
      name: "If"
    },
    {
      parameters: { jsCode: GERAR_TOKEN_CODE },
      type: "n8n-nodes-base.code",
      typeVersion: 2,
      position: [272, -144],
      id: "23ec952c-468a-4297-8b73-dc96d82356a0",
      name: "Gerar Token"
    },
    {
      parameters: {
        dataTableId: { __rl: true, value: "KgsVZRLRNB3WINee", mode: "list" },
        columns: {
          mappingMode: "defineBelow",
          matchingColumns: [],
          schema: [],
          value: {
            valorPago: "={{ $json.valorPago }}",
            sessionId: "={{ $json.sessionId }}",
            token: "={{ $json.token }}",
            email: "={{ $json.email }}",
            nome: "={{ $json.nome }}",
            criadoEm: "={{ $json.criadoEm }}",
            usado: "={{ $json.usado }}"
          }
        },
        options: {}
      },
      type: "n8n-nodes-base.dataTable",
      typeVersion: 1.1,
      position: [480, -144],
      id: "50e7417c-757b-43e5-b801-3271a5b55129",
      name: "Insert row"
    },
    {
      parameters: {
        fromEmail: "br.boulder1@gmail.com",
        toEmail: "={{ $json.email }}",
        subject: "Seu acesso ao Motor Anti-ATS esta liberado",
        message: EMAIL_HTML,
        options: { allowUnauthorizedCerts: false }
      },
      credentials: {
        smtp: { id: SMTP_CRED_ID, name: "Gmail SMTP" }
      },
      type: "n8n-nodes-base.emailSend",
      typeVersion: 2.1,
      position: [700, -144],
      id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      name: "Enviar Email"
    },
    {
      parameters: {
        respondWith: "json",
        responseBody: "={{ JSON.stringify({ received: true }) }}",
        options: {}
      },
      type: "n8n-nodes-base.respondToWebhook",
      typeVersion: 1.1,
      position: [900, -144],
      id: "f0e1d2c3-b4a5-6789-0fed-cba987654321",
      name: "Respond 200"
    }
  ],
  connections: {
    "Webhook": { main: [[{ node: "If", type: "main", index: 0 }]] },
    "If": { main: [[{ node: "Gerar Token", type: "main", index: 0 }]] },
    "Gerar Token": { main: [[{ node: "Insert row", type: "main", index: 0 }]] },
    "Insert row": { main: [[{ node: "Enviar Email", type: "main", index: 0 }]] },
    "Enviar Email": { main: [[{ node: "Respond 200", type: "main", index: 0 }]] }
  },
  settings: { executionOrder: "v1" }
};

function apiRequest(method, path, body) {
  return new Promise((resolve, reject) => {
    const payload = JSON.stringify(body);
    const options = {
      hostname: 'n8n.mentoriaaprovai.com.br',
      port: 443,
      path,
      method,
      headers: {
        'X-N8N-API-KEY': N8N_API_KEY,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload)
      }
    };
    const req = https.request(options, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        console.log('HTTP', res.statusCode);
        try { resolve({ status: res.statusCode, body: JSON.parse(data) }); }
        catch { resolve({ status: res.statusCode, body: data }); }
      });
    });
    req.on('error', reject);
    req.write(payload);
    req.end();
  });
}

async function main() {
  console.log('Atualizando workflow...');
  const res = await apiRequest('PUT', `/api/v1/workflows/${WORKFLOW_ID}`, workflow);

  if (res.status === 200) {
    console.log('Workflow atualizado. Ativando...');
    const act = await apiRequest('POST', `/api/v1/workflows/${WORKFLOW_ID}/activate`, {});
    console.log('Ativacao:', act.status);
    console.log('Nodes no workflow:', res.body.nodes?.length);
    console.log('Status ativo:', res.body.active);
  } else {
    console.error('Erro ao atualizar:', JSON.stringify(res.body, null, 2));
  }
}

main().catch(console.error);
