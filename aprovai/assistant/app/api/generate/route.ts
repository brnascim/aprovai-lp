// Rota server-side. A chave da API NUNCA vai ao client.
// Fonte de verdade dos headers/versão atuais: https://docs.claude.com/en/api/overview

export const runtime = "nodejs";

import { createHmac, timingSafeEqual } from "node:crypto";
import { trackCvGenerated } from "@/lib/tracking";

const MAX = 8000;

function section(text: string, tag: string): string {
  const re = new RegExp(`\\[${tag}\\]([\\s\\S]*?)(?=\\n\\[[A-Z]|$)`, "i");
  const m = text.match(re);
  return m ? m[1].trim() : "";
}

// Gate de acesso server-side (mesmo esquema HMAC do endpoint web/api/otimizar.js).
// Fail-closed: sem ACCESS_TOKEN_SECRET, nega — salvo ALLOW_UNVERIFIED_ACCESS=true (dev).
function verifyAccessToken(token: string): boolean {
  const secret = process.env.ACCESS_TOKEN_SECRET;
  if (!secret) return process.env.ALLOW_UNVERIFIED_ACCESS === "true";
  if (!token || token.indexOf(".") === -1) return false;
  const [payloadB64, sigB64] = token.split(".");
  if (!payloadB64 || !sigB64) return false;
  try {
    const expected = createHmac("sha256", secret)
      .update(payloadB64)
      .digest("base64url");
    const a = Buffer.from(expected);
    const b = Buffer.from(sigB64);
    if (a.length !== b.length || !timingSafeEqual(a, b)) return false;
    const payload = JSON.parse(Buffer.from(payloadB64, "base64url").toString("utf8"));
    if (payload && typeof payload.exp === "number" && Math.floor(Date.now() / 1000) > payload.exp) {
      return false;
    }
    return true;
  } catch {
    return false;
  }
}

function extractToken(req: Request, body: { token?: unknown }): string {
  const auth = req.headers.get("authorization") || "";
  if (auth.toLowerCase().startsWith("bearer ")) return auth.slice(7).trim();
  if (body && typeof body.token === "string") return body.token.trim();
  return "";
}

export async function POST(req: Request) {
  const _start = Date.now();
  try {
    const body = await req.json();
    const { vaga, experiencia, area } = body;
    const distinctId = req.headers.get("x-ph-distinct-id") || "anonymous";

    if (!verifyAccessToken(extractToken(req, body))) {
      return Response.json(
        { error: "Acesso não autorizado. Verifique o link de acesso enviado por e-mail." },
        { status: 401 },
      );
    }

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

    const result = {
      curriculo: section(text, "CURRICULO") || text,
      carta: section(text, "CARTA"),
      linkedin: section(text, "LINKEDIN"),
    };

    if (process.env.POSTHOG_API_KEY) {
      await trackCvGenerated(distinctId, {
        job_area: area || null,
        vaga_length_chars: String(vaga).length,
        experiencia_length_chars: String(experiencia).length,
        duration_ms: Date.now() - _start,
        success: true,
      }).catch(() => {});
    }

    return Response.json(result);
  } catch (e: any) {
    if (process.env.POSTHOG_API_KEY) {
      await trackCvGenerated("anonymous", {
        vaga_length_chars: 0,
        experiencia_length_chars: 0,
        duration_ms: Date.now() - _start,
        success: false,
        error_type: "unexpected",
      }).catch(() => {});
    }
    return Response.json({ error: "Erro inesperado.", detail: String(e).slice(0, 200) }, { status: 500 });
  }
}
