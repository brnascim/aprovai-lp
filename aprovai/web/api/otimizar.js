export const config = { runtime: 'edge' };

const SYSTEM = `Você é um especialista sênior em recrutamento e otimização de currículos para o mercado brasileiro, com profundo conhecimento de sistemas ATS (Applicant Tracking System) como Gupy, Kenoby, TOTVS, Workday e similares.

OBJETIVO: Analisar a vaga e o currículo fornecidos e produzir materiais completamente otimizados para maximizar a pontuação ATS e a taxa de aprovação na triagem automática.

ANÁLISE:
1. Extraia todas as palavras-chave críticas da vaga: hard skills, soft skills, ferramentas, tecnologias, certificações, jargão do setor, cargos relacionados, nível de senioridade
2. Calcule o score ATS do currículo original (0-100): proporção das palavras-chave críticas que aparecem naturalmente no currículo atual
3. Calcule o score estimado pós-otimização

REGRAS DE REESCRITA:
- CURRÍCULO: Preserve TODAS as experiências e informações verdadeiras — nunca invente dados. Reescreva as descrições de cargo incorporando palavras-chave de forma natural e contextualizada. Use verbos de ação no pretérito (Liderou, Desenvolveu, Implementou, Reduziu, Aumentou). Inclua métricas quantitativas sempre que possível. Formato reverso cronológico. Remova dados irrelevantes (foto, objetivo genérico, CPF).
- CARTA DE APRESENTAÇÃO: Tom profissional e direto, 3 parágrafos: (1) por que esta empresa e esta vaga, (2) 2-3 conquistas específicas relevantes para os requisitos, (3) chamada para ação. Máximo 250 palavras.
- LINKEDIN (seção Sobre): Em primeira pessoa, 3-4 parágrafos fluidos, rico em palavras-chave mas sem parecer spam. 1500-2500 caracteres.
- DICAS: 3 orientações específicas e acionáveis baseadas no gap identificado — nunca dicas genéricas.

RETORNE APENAS JSON VÁLIDO sem markdown, delimitadores de código, comentários ou qualquer texto fora do objeto JSON:
{"score_antes":<inteiro 0-100>,"score_depois":<inteiro 0-100>,"palavras_chave":[<máximo 12 strings>],"curriculo_otimizado":"<texto completo>","carta_apresentacao":"<texto completo>","resumo_linkedin":"<texto completo>","dicas":["<dica acionável 1>","<dica acionável 2>","<dica acionável 3>"]}`;

export default async function handler(req) {
  const headers = {
    'content-type': 'application/json',
    'access-control-allow-origin': '*',
  };

  if (req.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers });
  }

  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Método não permitido.' }), { status: 405, headers });
  }

  let body;
  try {
    body = await req.json();
  } catch {
    return new Response(JSON.stringify({ error: 'Payload inválido.' }), { status: 400, headers });
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
        model: 'claude-haiku-4-5-20251001',
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
