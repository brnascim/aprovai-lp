---
name: cowork-carrosseis
description: >
  Automatiza a PRODUÇÃO EM LOTE de carrosséis: transforma um roteiro (ou vários) em
  arquivos PNG prontos para publicar — 1080×1350, 1080×1080 ou 1080×1920 — sem abrir
  editor de imagem, usando um pipeline JSON → HTML → PNG que roda local. Use SEMPRE que
  o usuário disser "automatizar carrossel", "carrossel em lote", "gerar as artes do
  carrossel", "criar 10 carrosséis", "montar os slides", "transformar o roteiro em
  imagem", "exportar carrossel em PNG", "não quero fazer no Canva", "produzir conteúdo
  em escala", "calendário de carrosséis", "fábrica de conteúdo", "carrossel
  automatizado" ou mencionar Cowork/pipeline/automação para produção de posts. Use
  também quando ele já tiver a copy pronta e o gargalo for o design, ou quando quiser
  padronizar identidade visual em vários posts de uma vez. Para escrever a copy e a
  estrutura do carrossel, use antes a skill anuncios-estaticos-carrossel.
---

# Cowork — automatização de carrosséis

Resolve o gargalo real de quem produz conteúdo: **a copy fica pronta em 20 minutos e o
design leva 3 horas.** Aqui, um arquivo JSON com o texto dos slides vira um lote de PNGs
prontos, com identidade consistente, em segundos.

```
Roteiro (skill 3)  →  lote.json  →  carrossel_render.mjs  →  PNGs prontos
                                     HTML (editável)          01.png … 10.png
```

Nenhuma dependência para instalar: o script usa o Chromium/Chrome que já existe na máquina.
Sem navegador disponível, ele gera o HTML — que abre em qualquer lugar e pode ser capturado
manualmente.

## Entrada esperada

1. **Roteiro dos slides** — de `anuncios-estaticos-carrossel` ou escrito na hora
2. **Identidade:** tema (5 prontos) ou cores próprias, @ do perfil
3. **Formato:** 4:5 (feed, padrão), 1:1 ou 9:16 (stories)
4. **Quantidade:** um carrossel ou um lote (semana/mês inteiro)

Se o usuário trouxer só o tema do conteúdo, escreva a copy primeiro seguindo
`../anuncios-estaticos-carrossel/references/anatomia-carrossel.md` — **não gere arte para
copy fraca.** Design bom não salva slide 1 ruim.

## Fluxo

### 1. Montar o lote

```bash
node scripts/carrossel_render.mjs --exemplo > lote.json   # estrutura comentada
node scripts/carrossel_render.mjs --temas                 # temas disponíveis
```

Estrutura mínima:

```json
{
  "tema": "grafite",
  "formato": "4:5",
  "marca": "@seuperfil",
  "carrosseis": [
    { "nome": "folha-em-1-dia", "slides": [ { "tipo": "capa", "titulo": "..." } ] }
  ]
}
```

Os **6 tipos de slide** (`capa`, `texto`, `numero`, `lista`, `citacao`, `cta`) e todos os
campos aceitos estão em `references/formato-do-lote.md`. Cada tipo tem um papel narrativo —
não escolha por estética, escolha pela função do slide no roteiro.

### 2. Renderizar

```bash
node scripts/carrossel_render.mjs lote.json
node scripts/carrossel_render.mjs lote.json --saida ./posts --formato 9:16 --tema claro
node scripts/carrossel_render.mjs lote.json --so-html      # sem navegador
```

Saída: uma pasta por carrossel, com `01.png … NN.png` numerados na ordem de publicação e o
HTML de cada slide ao lado (útil para ajuste fino manual).

### 3. Conferir antes de publicar

Abra o `01.png` **reduzido a 20%**: se o texto principal não é legível assim, o slide 1
falha no feed. Checklist completo em `references/pipeline.md`.

### 4. Produzir em lote de verdade

O ganho real aparece a partir de 5 carrosséis. O ritmo recomendado
(`references/pipeline.md`): escrever a semana inteira de uma vez, renderizar tudo num
comando, revisar em bloco, agendar. Uma sessão de 90 minutos rende o conteúdo da semana.

## Personalização visual

**Temas prontos:** `grafite` (padrão), `claro`, `ambar`, `verde`, `roxo`.

**Tema próprio:** edite o objeto `TEMAS` no topo do script — quatro cores (`fundo`, `texto`,
`destaque`, `suave`) e a família tipográfica. `references/temas-e-identidade.md` explica
como derivar um tema da identidade do produto e o que checa contraste.

**Ajuste fino:** o HTML de cada slide fica na pasta de saída. Editar o CSS ali e recapturar
resolve casos pontuais sem mexer no script.

## Regras

- **Copy antes de arte.** Se o roteiro não passa no checklist de
  `../anuncios-estaticos-carrossel/references/anatomia-carrossel.md`, volte para a copy.
- **Um slide, uma ideia.** O layout foi feito para pouco texto. Slide que estoura o espaço
  é sinal de que deveriam ser dois.
- **Consistência é a identidade.** Mesmo tema em todo o lote. Trocar tema a cada post
  destrói o reconhecimento visual.
- **Sem prova inventada.** Slide de `citacao` só com depoimento real e autorizado — inclua
  o contexto no campo `autor`. Sem autorização, não renderize.
- **Sem promessa de renda, atributo pessoal ou escassez falsa** nos slides — as políticas de
  `../anuncios-estaticos-carrossel/references/politicas-meta.md` valem igual aqui. Rode
  `validar_copy.py` no roteiro antes de renderizar.
- **Máximo 20 slides** (limite do Instagram); o ideal continua sendo 6–10.
- **Não sobrescreva sem avisar.** A pasta de saída é reutilizada; confirme antes de rodar
  sobre um lote já publicado.

## Referências

| Arquivo | Quando ler |
|---------|-----------|
| `references/formato-do-lote.md` | Ao montar o JSON — tipos de slide e todos os campos |
| `references/pipeline.md` | Para produzir em escala — ritmo, revisão, agendamento |
| `references/temas-e-identidade.md` | Para criar tema próprio e checar contraste |

## Handoff

- **Copy do carrossel** ← `anuncios-estaticos-carrossel`
- **Plano de quantos e quais carrosséis** ← `mandala-anuncios-reels`
- **PNGs prontos** → publicação orgânica ou upload como criativo de carrossel no Meta

Se o carrossel for anúncio pago, valide antes com
`../anuncios-estaticos-carrossel/scripts/validar_copy.py` — reprovação por texto do slide é
comum e evitável.
