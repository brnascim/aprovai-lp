// examples/generate.ts — REFERÊNCIA da rota server-side (Next.js App Router).
// Verifique sempre os headers/versão atuais em https://docs.claude.com/en/api/overview
// A chave NUNCA vai para o client. Roda apenas no servidor.

export async function POST(req: Request) {
  const { vaga, experiencia, area } = await req.json();

  if (!vaga || !experiencia) {
    return new Response(JSON.stringify({ error: "Campos obrigatórios" }), { status: 400 });
  }

  const system =
    "Você é especialista em otimização de currículos para sistemas ATS no Brasil. " +
    "Reescreva para maximizar correspondência de palavras-chave e legibilidade por máquina, " +
    "mantendo tudo verdadeiro. NÃO invente experiências, números ou certificações.";

  const user =
    `ÁREA: ${area}\n\nVAGA:\n${vaga}\n\nEXPERIÊNCIA DO CANDIDATO:\n${experiencia}\n\n` +
    "Devolva 3 seções marcadas: [CURRICULO], [CARTA], [LINKEDIN].";

  const resp = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": process.env.ANTHROPIC_API_KEY!,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model: process.env.ANTHROPIC_MODEL ?? "claude-sonnet-4-6",
      max_tokens: 2000,
      system,
      messages: [{ role: "user", content: user }],
    }),
  });

  const data = await resp.json();
  const text = (data.content ?? [])
    .filter((b: any) => b.type === "text")
    .map((b: any) => b.text)
    .join("\n");

  return new Response(JSON.stringify({ result: text }), {
    headers: { "content-type": "application/json" },
  });
}
