#!/usr/bin/env node
/**
 * Renderiza carrosséis em lote: JSON → HTML → PNG.
 *
 * Uso:
 *   node carrossel_render.mjs lote.json
 *   node carrossel_render.mjs lote.json --saida ./out --formato 4:5
 *   node carrossel_render.mjs --exemplo > lote.json
 *   node carrossel_render.mjs lote.json --so-html      (não precisa de navegador)
 *   node carrossel_render.mjs --temas                  (lista os temas disponíveis)
 *
 * Sem dependências: usa o Chromium/Chrome já instalado na máquina para a captura.
 * Se nenhum navegador for encontrado, o HTML é gerado assim mesmo e o caminho é
 * informado — dá para abrir e imprimir/capturar manualmente.
 *
 * Formato do lote e campos aceitos: ../references/formato-do-lote.md
 */

import { execFile } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync, rmSync } from "node:fs";
import { basename, join, resolve } from "node:path";
import { promisify } from "node:util";
import zlib from "node:zlib";

const execFileAsync = promisify(execFile);

/**
 * O Chromium headless entrega uma viewport menor que a janela pedida (reserva o
 * espaço da moldura), e o PNG sai do tamanho da JANELA — o que deixaria uma faixa
 * vazia embaixo. Renderizamos com folga e recortamos a altura exata.
 */
const FOLGA_JANELA = 200;

const FORMATOS = {
  "4:5": { largura: 1080, altura: 1350 },
  "1:1": { largura: 1080, altura: 1080 },
  "9:16": { largura: 1080, altura: 1920 },
};

const TEMAS = {
  grafite: {
    fundo: "linear-gradient(160deg, #12141a 0%, #1d2230 100%)",
    texto: "#f5f7fa", destaque: "#4da3ff", suave: "#9aa4b2",
    fonte: "'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif",
  },
  claro: {
    fundo: "linear-gradient(160deg, #ffffff 0%, #eef1f6 100%)",
    texto: "#14171f", destaque: "#0b62d6", suave: "#5b6472",
    fonte: "'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif",
  },
  ambar: {
    fundo: "linear-gradient(160deg, #1a1408 0%, #2c2110 100%)",
    texto: "#fdf6e8", destaque: "#f5a524", suave: "#b8a888",
    fonte: "'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif",
  },
  verde: {
    fundo: "linear-gradient(160deg, #0b1f18 0%, #123227 100%)",
    texto: "#eefaf3", destaque: "#2ecc8f", suave: "#8fae9f",
    fonte: "'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif",
  },
  roxo: {
    fundo: "linear-gradient(160deg, #170f2b 0%, #241640 100%)",
    texto: "#f6f2ff", destaque: "#a97bff", suave: "#a99cc4",
    fonte: "'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif",
  },
};

const CAMINHOS_NAVEGADOR = [
  process.env.CHROME_PATH,
  "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
  "/usr/bin/chromium",
  "/usr/bin/chromium-browser",
  "/usr/bin/google-chrome",
  "/usr/bin/google-chrome-stable",
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/Applications/Chromium.app/Contents/MacOS/Chromium",
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
];

const EXEMPLO = {
  tema: "grafite",
  formato: "4:5",
  marca: "@seuperfil",
  carrosseis: [
    {
      nome: "folha-em-1-dia",
      slides: [
        { tipo: "capa", titulo: "4 dias fechando folha é opcional", subtitulo: "Escritório de contabilidade com até 5 pessoas" },
        { tipo: "texto", titulo: "Não é volume", corpo: "É retrabalho: o mesmo dado conferido três vezes." },
        { tipo: "numero", numero: "12h", corpo: "por mês só reconferindo o que já estava certo" },
        { tipo: "texto", titulo: "Trocar de sistema não resolve", corpo: "O problema está na ordem das etapas." },
        { tipo: "lista", titulo: "O método das 3 colunas", itens: ["Entrada", "Conferência única", "Fechamento"] },
        { tipo: "citacao", corpo: "Mesmo sistema, mesma equipe. Fechou às 11h20.", autor: "case real — com autorização" },
        { tipo: "cta", titulo: "O processo completo está no link", subtitulo: "Toque em Saiba mais" },
      ],
    },
  ],
};

// ---------------------------------------------------------------- utilidades

function esc(texto = "") {
  return String(texto)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/** Corpo de texto cresce a fonte quando é curto e encolhe quando é longo. */
function escala(texto = "", base, min, max) {
  const n = String(texto).length;
  const valor = base * (n > 90 ? 0.72 : n > 55 ? 0.85 : n > 30 ? 1 : 1.15);
  return Math.round(Math.max(min, Math.min(max, valor)));
}

function slugificar(texto) {
  return String(texto).normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "carrossel";
}

// ---------------------------------------------------------------- renderização

function corpoDoSlide(slide, tema) {
  const tipo = slide.tipo || "texto";

  switch (tipo) {
    case "capa":
      return `
        <div class="bloco capa">
          ${slide.selo ? `<div class="selo">${esc(slide.selo)}</div>` : ""}
          <h1 style="font-size:${escala(slide.titulo, 96, 56, 108)}px">${esc(slide.titulo)}</h1>
          ${slide.subtitulo ? `<p class="sub">${esc(slide.subtitulo)}</p>` : ""}
        </div>`;

    case "numero":
      return `
        <div class="bloco centro">
          <div class="numero">${esc(slide.numero)}</div>
          <p class="corpo" style="font-size:${escala(slide.corpo, 46, 32, 54)}px">${esc(slide.corpo)}</p>
        </div>`;

    case "lista":
      return `
        <div class="bloco">
          ${slide.titulo ? `<h2 style="font-size:${escala(slide.titulo, 68, 44, 78)}px">${esc(slide.titulo)}</h2>` : ""}
          <ul class="lista">
            ${(slide.itens || []).map((item, i) =>
              `<li><span class="marca">${i + 1}</span><span>${esc(item)}</span></li>`).join("")}
          </ul>
        </div>`;

    case "citacao":
      return `
        <div class="bloco centro">
          <div class="aspas">"</div>
          <p class="citacao" style="font-size:${escala(slide.corpo, 60, 38, 70)}px">${esc(slide.corpo)}</p>
          ${slide.autor ? `<p class="autor">— ${esc(slide.autor)}</p>` : ""}
        </div>`;

    case "cta":
      return `
        <div class="bloco centro cta">
          <h2 style="font-size:${escala(slide.titulo, 76, 48, 88)}px">${esc(slide.titulo)}</h2>
          ${slide.subtitulo ? `<div class="botao">${esc(slide.subtitulo)}</div>` : ""}
        </div>`;

    case "texto":
    default:
      return `
        <div class="bloco">
          ${slide.titulo ? `<h2 style="font-size:${escala(slide.titulo, 74, 46, 84)}px">${esc(slide.titulo)}</h2>` : ""}
          ${slide.corpo ? `<p class="corpo" style="font-size:${escala(slide.corpo, 46, 30, 54)}px">${esc(slide.corpo)}</p>` : ""}
        </div>`;
  }
}

function htmlDoSlide(slide, indice, total, tema, formato, marca) {
  const { largura, altura } = formato;
  const ehCapa = (slide.tipo || "texto") === "capa";

  return `<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>slide ${indice + 1}</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html, body { width:${largura}px; overflow:hidden; background:#000; }
  /* o slide é quem define o tamanho da captura — não depende da viewport */
  .slide {
    width:${largura}px; height:${altura}px; overflow:hidden;
    background:${tema.fundo}; color:${tema.texto}; font-family:${tema.fonte};
    display:flex; flex-direction:column; justify-content:center;
    padding:${Math.round(altura * 0.09)}px ${Math.round(largura * 0.085)}px;
    position:relative; -webkit-font-smoothing:antialiased;
  }
  .slide::after {
    content:""; position:absolute; inset:0;
    background:radial-gradient(circle at 78% 12%, ${tema.destaque}1f 0%, transparent 55%);
    pointer-events:none;
  }
  .bloco { position:relative; z-index:1; display:flex; flex-direction:column; gap:34px; }
  .centro { align-items:flex-start; }
  h1, h2 { line-height:1.08; font-weight:800; letter-spacing:-0.02em; }
  h1 { max-width:96%; }
  .capa h1 { border-left:10px solid ${tema.destaque}; padding-left:32px; }
  .sub { font-size:40px; color:${tema.suave}; line-height:1.35; max-width:88%; }
  .selo {
    align-self:flex-start; font-size:28px; font-weight:700; letter-spacing:.14em;
    text-transform:uppercase; color:${tema.destaque};
    border:2px solid ${tema.destaque}66; border-radius:999px; padding:12px 26px;
  }
  .corpo { line-height:1.4; color:${tema.texto}e6; max-width:94%; }
  .numero {
    font-size:220px; font-weight:800; line-height:1; color:${tema.destaque};
    letter-spacing:-0.04em;
  }
  .lista { list-style:none; display:flex; flex-direction:column; gap:28px; }
  .lista li { display:flex; align-items:center; gap:26px; font-size:46px; line-height:1.25; }
  .marca {
    flex:0 0 auto; width:66px; height:66px; border-radius:50%;
    background:${tema.destaque}; color:#0b0d12; font-size:34px; font-weight:800;
    display:flex; align-items:center; justify-content:center;
  }
  .aspas { font-size:160px; line-height:.7; color:${tema.destaque}; font-weight:800; }
  .citacao { line-height:1.25; font-weight:600; }
  .autor { font-size:32px; color:${tema.suave}; }
  .cta { gap:44px; }
  .botao {
    align-self:flex-start; background:${tema.destaque}; color:#0b0d12;
    font-size:40px; font-weight:800; padding:26px 54px; border-radius:18px;
  }
  .rodape {
    position:absolute; left:${Math.round(largura * 0.085)}px;
    right:${Math.round(largura * 0.085)}px; bottom:${Math.round(altura * 0.05)}px;
    display:flex; justify-content:space-between; align-items:center;
    font-size:28px; color:${tema.suave}; z-index:1;
  }
  .progresso { display:flex; gap:10px; }
  .ponto { width:34px; height:6px; border-radius:3px; background:${tema.suave}55; }
  .ponto.ativo { background:${tema.destaque}; }
  .arrasta { font-weight:700; color:${tema.destaque}; }
</style></head>
<body>
  <div class="slide">
    ${corpoDoSlide(slide, tema)}
    <div class="rodape">
      <span>${esc(marca || "")}</span>
      <div class="progresso">
        ${Array.from({ length: total }, (_, i) =>
          `<span class="ponto${i === indice ? " ativo" : ""}"></span>`).join("")}
      </div>
      <span class="${ehCapa ? "arrasta" : ""}">${
        ehCapa ? "arrasta →" : `${indice + 1}/${total}`}</span>
    </div>
  </div>
</body></html>`;
}

// ---------------------------------------------------------------- navegador

function acharNavegador() {
  for (const caminho of CAMINHOS_NAVEGADOR) {
    if (caminho && existsSync(caminho)) return caminho;
  }
  return null;
}

const CRC_TABELA = (() => {
  const t = new Int32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    t[n] = c;
  }
  return t;
})();

function crc32(buf) {
  if (typeof zlib.crc32 === "function") return zlib.crc32(buf) >>> 0;
  let c = -1;
  for (let i = 0; i < buf.length; i++) c = CRC_TABELA[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  return (c ^ -1) >>> 0;
}

function pedaco(tipo, dados) {
  const cabecalho = Buffer.alloc(8);
  cabecalho.writeUInt32BE(dados.length, 0);
  cabecalho.write(tipo, 4, "ascii");
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(Buffer.concat([Buffer.from(tipo, "ascii"), dados])), 0);
  return Buffer.concat([cabecalho, dados, crc]);
}

/**
 * Recorta a ALTURA de um PNG mantendo a largura. Como cada linha só depende da
 * linha anterior, basta truncar as linhas filtradas — nenhuma reamostragem.
 * Devolve false (sem alterar o arquivo) se o PNG não for 8-bit RGB/RGBA simples.
 */
function recortarAltura(caminho, novaAltura) {
  const png = readFileSync(caminho);
  if (png.readUInt32BE(0) !== 0x89504e47) return false;

  const largura = png.readUInt32BE(16);
  const altura = png.readUInt32BE(20);
  const profundidade = png[24];
  const tipoCor = png[25];
  const entrelacado = png[28];

  if (profundidade !== 8 || ![2, 6].includes(tipoCor) || entrelacado !== 0) return false;
  if (novaAltura >= altura) return false;

  const canais = tipoCor === 2 ? 3 : 4;
  const passo = largura * canais + 1;

  const partes = [];
  let i = 8;
  while (i < png.length) {
    const tamanho = png.readUInt32BE(i);
    const tipo = png.toString("ascii", i + 4, i + 8);
    if (tipo === "IDAT") partes.push(png.subarray(i + 8, i + 8 + tamanho));
    i += 12 + tamanho;
  }

  const bruto = zlib.inflateSync(Buffer.concat(partes));
  const cortado = bruto.subarray(0, passo * novaAltura);

  const ihdr = Buffer.from(png.subarray(16, 16 + 13));
  ihdr.writeUInt32BE(novaAltura, 4);

  writeFileSync(caminho, Buffer.concat([
    png.subarray(0, 8),
    pedaco("IHDR", ihdr),
    pedaco("IDAT", zlib.deflateSync(cortado, { level: 9 })),
    pedaco("IEND", Buffer.alloc(0)),
  ]));
  return true;
}

async function capturar(navegador, arquivoHtml, arquivoPng, { largura, altura }) {
  const perfil = join(process.env.TMPDIR || "/tmp", `carrossel-${process.pid}`);
  await execFileAsync(navegador, [
    "--headless",
    "--disable-gpu",
    "--no-sandbox",
    "--hide-scrollbars",
    "--force-device-scale-factor=1",
    `--user-data-dir=${perfil}`,
    `--window-size=${largura},${altura + FOLGA_JANELA}`,
    `--screenshot=${arquivoPng}`,
    `file://${resolve(arquivoHtml)}`,
  ], { timeout: 60_000 }).catch((erro) => {
    // o Chromium escreve avisos no stderr mesmo quando a captura funciona
    if (!existsSync(arquivoPng)) throw erro;
  });
  rmSync(perfil, { recursive: true, force: true });

  if (!recortarAltura(arquivoPng, altura)) {
    console.warn(`aviso: não foi possível recortar ${basename(arquivoPng)} para ` +
      `${largura}×${altura}; confira a altura antes de publicar`);
  }
}

// ---------------------------------------------------------------- principal

async function main() {
  const args = process.argv.slice(2);

  if (args.includes("--exemplo")) {
    console.log(JSON.stringify(EXEMPLO, null, 2));
    return 0;
  }
  if (args.includes("--temas")) {
    console.log("Temas disponíveis:\n" +
      Object.keys(TEMAS).map((t) => `  - ${t}`).join("\n"));
    return 0;
  }
  if (args.includes("--help") || args.includes("-h") || args.length === 0) {
    console.log(readFileSync(new URL(import.meta.url)).toString()
      .split("*/")[0].replace(/^\/\*\*?/, "").replace(/^ \* ?/gm, ""));
    return 0;
  }

  const arquivo = args.find((a) => !a.startsWith("--"));
  if (!arquivo || !existsSync(arquivo)) {
    console.error(`erro: arquivo de lote não encontrado: ${arquivo}`);
    return 1;
  }

  const opcao = (nome, padrao) => {
    const i = args.indexOf(nome);
    return i >= 0 && args[i + 1] ? args[i + 1] : padrao;
  };

  let lote;
  try {
    lote = JSON.parse(readFileSync(arquivo, "utf-8"));
  } catch (erro) {
    console.error(`erro: JSON inválido em ${arquivo}: ${erro.message}`);
    return 1;
  }

  const carrosseis = lote.carrosseis || (lote.slides ? [lote] : null);
  if (!carrosseis?.length) {
    console.error("erro: o lote precisa de 'carrosseis' (lista) ou de 'slides'");
    return 1;
  }

  const nomeFormato = opcao("--formato", lote.formato || "4:5");
  const formato = FORMATOS[nomeFormato];
  if (!formato) {
    console.error(`erro: formato inválido '${nomeFormato}'. Use: ${Object.keys(FORMATOS).join(", ")}`);
    return 1;
  }

  const nomeTema = opcao("--tema", lote.tema || "grafite");
  const tema = TEMAS[nomeTema];
  if (!tema) {
    console.error(`erro: tema inválido '${nomeTema}'. Use: ${Object.keys(TEMAS).join(", ")}`);
    return 1;
  }

  const saida = resolve(opcao("--saida", "./carrosseis"));
  const soHtml = args.includes("--so-html");
  const navegador = soHtml ? null : acharNavegador();

  if (!soHtml && !navegador) {
    console.warn("aviso: nenhum Chrome/Chromium encontrado. Gerando só o HTML.\n" +
      "       Defina CHROME_PATH=/caminho/do/chrome para capturar os PNGs.");
  }

  mkdirSync(saida, { recursive: true });
  let totalSlides = 0;
  const relatorio = [];

  for (const [i, carrossel] of carrosseis.entries()) {
    const nome = slugificar(carrossel.nome || `carrossel-${i + 1}`);
    const slides = carrossel.slides || [];
    if (!slides.length) {
      console.warn(`aviso: '${nome}' não tem slides — pulando`);
      continue;
    }
    if (slides.length > 20) {
      console.warn(`aviso: '${nome}' tem ${slides.length} slides; o limite do Instagram é 20`);
    }

    const pasta = join(saida, nome);
    mkdirSync(pasta, { recursive: true });
    const temaCarrossel = TEMAS[carrossel.tema] || tema;
    const marca = carrossel.marca || lote.marca || "";
    const arquivos = [];

    for (const [j, slide] of slides.entries()) {
      const prefixo = String(j + 1).padStart(2, "0");
      const html = join(pasta, `${prefixo}.html`);
      writeFileSync(html, htmlDoSlide(slide, j, slides.length, temaCarrossel, formato, marca));

      if (navegador) {
        const png = join(pasta, `${prefixo}.png`);
        try {
          await capturar(navegador, html, png, formato);
          arquivos.push(basename(png));
        } catch (erro) {
          console.error(`erro ao capturar ${nome}/${prefixo}: ${erro.message}`);
        }
      } else {
        arquivos.push(basename(html));
      }
      totalSlides++;
    }

    relatorio.push({ nome, pasta, slides: slides.length, arquivos: arquivos.length });
    console.log(`✔ ${nome} — ${arquivos.length}/${slides.length} arquivos em ${pasta}`);
  }

  console.log(`\n${relatorio.length} carrossel(éis) · ${totalSlides} slides · ` +
    `${formato.largura}×${formato.altura} · tema ${nomeTema}`);
  console.log(`Saída: ${saida}`);
  if (navegador) console.log(`Navegador: ${navegador}`);

  return 0;
}

main().then((codigo) => process.exit(codigo)).catch((erro) => {
  console.error(`falha: ${erro.stack || erro.message}`);
  process.exit(1);
});
