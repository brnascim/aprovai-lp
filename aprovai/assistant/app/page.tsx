"use client";

import { useMemo, useState } from "react";

type Result = { curriculo: string; carta: string; linkedin: string };

const STOP = new Set([
  "para","como","sobre","entre","quando","porque","todos","todas","esses","essas","aquele","muito",
  "nossa","nosso","suas","seus","será","você","voce","cada","onde","pela","pelo","pelos","pelas",
  "ainda","desde","deste","desta","esta","este","isso","aqui","mais","menos","também","tambem",
]);

function adherence(vaga: string, cv: string): number {
  if (!vaga || !cv) return 0;
  const norm = (s: string) =>
    s.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  const cvN = norm(cv);
  const words = Array.from(
    new Set(norm(vaga).split(/[^a-z0-9]+/).filter((w) => w.length > 4 && !STOP.has(w)))
  );
  if (words.length === 0) return 0;
  const hit = words.filter((w) => cvN.includes(w)).length;
  return Math.round((hit / words.length) * 100);
}

function Card({ title, text }: { title: string; text: string }) {
  const [copied, setCopied] = useState(false);
  if (!text) return null;
  const copy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };
  const download = () => {
    const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `aprovai-${title.toLowerCase()}.txt`;
    a.click();
    URL.revokeObjectURL(a.href);
  };
  return (
    <div className="rounded-2xl border border-line bg-surface p-5">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="font-display text-lg font-semibold">{title}</h3>
        <div className="flex gap-2">
          <button onClick={copy} className="rounded-lg border border-line px-3 py-1.5 text-sm hover:bg-surface2">
            {copied ? "Copiado!" : "Copiar"}
          </button>
          <button onClick={download} className="rounded-lg border border-line px-3 py-1.5 text-sm hover:bg-surface2">
            Baixar
          </button>
        </div>
      </div>
      <pre className="whitespace-pre-wrap break-words font-body text-sm leading-relaxed text-muted">{text}</pre>
    </div>
  );
}

export default function Page() {
  const [area, setArea] = useState("");
  const [vaga, setVaga] = useState("");
  const [exp, setExp] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [res, setRes] = useState<Result | null>(null);

  const score = useMemo(() => (res ? adherence(vaga, res.curriculo) : 0), [res, vaga]);

  const submit = async () => {
    setError(""); setRes(null); setLoading(true);
    try {
      const r = await fetch("/api/generate", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ area, vaga, experiencia: exp }),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.error || "Falha ao gerar.");
      setRes(data);
    } catch (e: any) {
      setError(e.message || "Erro inesperado.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto min-h-screen max-w-3xl px-5 py-10">
      <header className="mb-8 flex items-center gap-2">
        <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-accent text-bg">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12" /></svg>
        </span>
        <div>
          <p className="font-display text-lg font-bold leading-none">Aprova<span className="text-accent">í</span></p>
          <p className="text-xs text-muted">Motor Anti-ATS</p>
        </div>
      </header>

      <h1 className="mb-2 font-display text-2xl font-bold sm:text-3xl">
        Cole a vaga e a sua experiência
      </h1>
      <p className="mb-6 text-muted">
        O assistente reescreve currículo, carta e LinkedIn otimizados para a triagem automática daquela vaga.
      </p>

      <div className="space-y-4">
        <div>
          <label className="mb-1 block text-sm text-muted">Área</label>
          <select value={area} onChange={(e) => setArea(e.target.value)}
            className="w-full rounded-xl border border-line bg-surface px-3 py-3 text-ink">
            <option value="">Selecione…</option>
            <option>Tecnologia / TI</option><option>Saúde</option><option>Vendas / Comercial</option>
            <option>Administrativo</option><option>Logística</option><option>Marketing</option>
            <option>Financeiro</option><option>Outra</option>
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm text-muted">Descrição da vaga</label>
          <textarea value={vaga} onChange={(e) => setVaga(e.target.value)} rows={6}
            placeholder="Cole aqui a descrição completa da vaga…"
            className="w-full rounded-xl border border-line bg-surface px-3 py-3 text-ink placeholder:text-muted/60" />
        </div>
        <div>
          <label className="mb-1 block text-sm text-muted">Sua experiência</label>
          <textarea value={exp} onChange={(e) => setExp(e.target.value)} rows={6}
            placeholder="Seu histórico, cargos, formação e habilidades (em texto livre)…"
            className="w-full rounded-xl border border-line bg-surface px-3 py-3 text-ink placeholder:text-muted/60" />
        </div>

        <button onClick={submit} disabled={loading || !vaga || !exp}
          className="w-full rounded-xl bg-accent py-4 font-bold text-bg transition hover:brightness-110 disabled:opacity-40">
          {loading ? "Otimizando…" : "Gerar versão otimizada"}
        </button>

        {error && <p className="rounded-xl border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger">{error}</p>}
      </div>

      {res && (
        <section className="mt-10 space-y-5">
          <div className="flex items-center justify-between rounded-2xl border border-trust/30 bg-trust/10 px-5 py-4">
            <div>
              <p className="font-display text-sm font-semibold text-trust">Estimativa de aderência</p>
              <p className="text-xs text-muted">palavras-chave da vaga presentes no currículo (estimativa, não garantia)</p>
            </div>
            <p className="font-display text-3xl font-bold text-trust">{score}%</p>
          </div>

          <Card title="Currículo" text={res.curriculo} />
          <Card title="Carta" text={res.carta} />
          <Card title="LinkedIn" text={res.linkedin} />

          <p className="text-center text-xs text-muted">
            O Aprovaí otimiza seu currículo para a triagem automática. Não garantimos contratação — revise tudo antes de enviar.
          </p>
        </section>
      )}
    </main>
  );
}
