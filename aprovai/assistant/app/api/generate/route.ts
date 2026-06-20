// Rota server-side. A chave da API NUNCA vai ao client.
// Fonte de verdade dos headers/versão atuais: https://docs.claude.com/en/api/overview

export const runtime = "nodejs";

const MAX = 8000;

function section(text: string, tag: string): string {
  const re = new RegExp(`\\[${tag}\\]([\\s\\S]*?)(?=\\n\\[[A-Z]|$)`, "i");
  const m = text.match(re);
  return m ? m[1].trim() : "";
}

export async function POST(req: Request) {
  try {
    const { vaga, experiencia, area } = await req.json();

    if (!vaga || !experiencia) {
      return Response.json({ error: "Preencha a vaga e a sua experiência." }, { status: 400 });
    }
    if (String(vaga).length > MAX || String(experiencia).length > MAX) {
      return Response.json({ error: "Texto muito longo. Resuma um pouco." }, { status: 400 });
    }
    if (!process.env.ANTHROPIC_API_KEY) {
      return Response.json({ error: "Servidor sem ANTHROPIC_API_KEY configurada." }, { status: 500 });
    }

    const system =
      "Você é especialista em otimização de currículos para sistemas ATS no Brasil. " +
      "Reescreva para maximizar a correspondência de palavras-chave da vaga e a legibilidade por máquina " +
      "(sem tabelas, colunas ou caracteres exóticos), mantendo TUDO verdadeiro. " +
      "NUNCA invente experiências, números, cargos ou certificações que o candidato não forneceu. " +
      "Não prometa emprego nem faça promessas de resultado. Escreva em pt-BR.";

    const user =
      `ÁREA: ${area || "não informada"}\n\n` +
      `DESCRIÇÃO DA VAGA:\n${vaga}\n\n` +
      `EXPERIÊNCIA DO CANDIDATO:\n${experiencia}\n\n` +
      "Devolva exatamente três seções, cada uma começando com o marcador entre colchetes, nesta ordem:\n" +
      "[CURRICULO]\n(currículo otimizado para ATS)\n" +
      "[CARTA]\n(carta de apresentação curta)\n" +
      "[LINKEDIN]\n(headline + seção 'Sobre')\n";

    const resp = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": process.env.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: process.env.ANTHROPIC_MODEL ?? "claude-sonnet-4-6",
        max_tokens: 2500,
        system,
        messages: [{ role: "user", content: user }],
      }),
    });

    if (!resp.ok) {
      const t = await resp.text();
      return Response.json({ error: "Falha ao gerar. Tente novamente.", detail: t.slice(0, 300) }, { status: 502 });
    }

    const data = await resp.json();
    const text: string = (data.content ?? [])
      .filter((b: any) => b.type === "text")
      .map((b: any) => b.text)
      .join("\n");

    return Response.json({
      curriculo: section(text, "CURRICULO") || text,
      carta: section(text, "CARTA"),
      linkedin: section(text, "LINKEDIN"),
    });
  } catch (e: any) {
    return Response.json({ error: "Erro inesperado.", detail: String(e).slice(0, 200) }, { status: 500 });
  }
}
