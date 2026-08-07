# Suíte de Skills — Produto Digital, Anúncios e Apps com IA

Seis skills encadeadas que cobrem o ciclo completo de um negócio digital perpétuo:
da ideia do produto até o app que sustenta a entrega.

```
┌─────────────────────┐   ┌──────────────────────┐   ┌───────────────────────────┐
│ 1. produto-digital- │──▶│ 2. produto-digital-  │──▶│ 3. anuncios-estaticos-    │
│    ideias           │   │    concepcao         │   │    carrossel              │
│ o QUE vender        │   │ promessa/público/preço│  │ imagem + copy (estático   │
│                     │   │                      │   │ e carrossel)              │
└─────────────────────┘   └──────────────────────┘   └───────────┬───────────────┘
                                     │                           │
                                     ▼                           ▼
                          ┌──────────────────────┐   ┌───────────────────────────┐
                          │ 6. apps-saas-sem-    │   │ 4. mandala-anuncios-reels │
                          │    codigo            │   │ grade de criativos +      │
                          │ entrega/ferramenta   │   │ roteiros de vídeo         │
                          │ que vira produto     │   └───────────┬───────────────┘
                          └──────────────────────┘               │
                                                                 ▼
                                                     ┌───────────────────────────┐
                                                     │ 5. cowork-carrosseis      │
                                                     │ produção em lote:         │
                                                     │ JSON → HTML → PNG         │
                                                     └───────────────────────────┘
```

## As seis skills

| # | Skill | Resolve | Entregável principal |
|---|-------|---------|----------------------|
| 1 | [`produto-digital-ideias`](produto-digital-ideias/SKILL.md) | "não sei o que vender" | 10–20 ideias pontuadas + 3 finalistas |
| 2 | [`produto-digital-concepcao`](produto-digital-concepcao/SKILL.md) | "não sei prometer, pra quem, por quanto" | One-page de conceito + tabela de preço |
| 3 | [`anuncios-estaticos-carrossel`](anuncios-estaticos-carrossel/SKILL.md) | "não sei fazer anúncio que para o scroll" | Kit de criativos (copy + prompt de imagem) |
| 4 | [`mandala-anuncios-reels`](mandala-anuncios-reels/SKILL.md) | "acabam minhas ideias de criativo" | Plano de N criativos + roteiros de Reels |
| 5 | [`cowork-carrosseis`](cowork-carrosseis/SKILL.md) | "carrossel demora demais pra montar" | PNGs 1080×1350 renderizados em lote |
| 6 | [`apps-saas-sem-codigo`](apps-saas-sem-codigo/SKILL.md) | "quero um app/SaaS e não programo" | PRD executável + app rodando |

Cada skill funciona sozinha. Encadeadas, cada uma consome o artefato da anterior —
as seções **"Entrada esperada"** e **"Handoff"** de cada `SKILL.md` definem o contrato.

## Como usar

As skills ficam em `.claude/skills/` e o Claude Code as carrega automaticamente neste
projeto. Para usar em qualquer pasta, copie para `~/.claude/skills/`:

```bash
cp -r .claude/skills/* ~/.claude/skills/
```

Você não precisa citar o nome da skill. Frases como *"me ajuda a decidir o que vender"*,
*"faz 5 criativos pro meu produto"* ou *"quero um app pra isso"* já disparam a skill certa.
Para forçar, use o nome: *"usa a skill mandala-anuncios-reels"*.

## Base metodológica

O vocabulário operacional vem de referências públicas do mercado digital brasileiro e
internacional, com destaque para o método **VTSD (Venda Todo Santo Dia)**, de **Leandro
Ladeira** — perpétuo, escada de produtos e a **Mandala de Anúncios** (fase da campanha ×
momento × tipo de criativo). Outras influências reconhecíveis: Eugene Schwartz (níveis de
consciência), Alex Hormozi (equação de valor e oferta), Russell Brunson (escada de valor),
Donald Miller (StoryBrand), Pedro Sobral (leitura de métricas de tráfego), Ícaro de
Carvalho (narrativa e autoridade).

Nada aqui reproduz material de curso. Os frameworks citados são de domínio público do
mercado; checklists, rubricas, prompts e scripts foram escritos do zero para esta suíte.
Trate as atribuições como *"na linha de"*, não como conteúdo oficial de nenhum programa.

## Regras que valem para as seis skills

Estão detalhadas em cada skill, mas resumindo o inegociável:

1. **Nunca invente prova.** Depoimento, número de alunos, faturamento e print só entram se
   o usuário fornecer. Onde falta prova, o texto usa `[PROVA: ...]` como marcador visível.
2. **Nunca prometa resultado garantido.** Sem "ganhe R$ X em Y dias", sem renda garantida,
   sem cura. Ver `produto-digital-concepcao/references/compliance-promessas-br.md`.
3. **Respeite CDC e políticas de plataforma.** Garantia mínima de 7 dias em compra online,
   preço e condições sem letra miúda enganosa, políticas do Meta em
   `anuncios-estaticos-carrossel/references/politicas-meta.md`.
4. **Não copie concorrente.** Referência serve para ler estrutura e ângulo, nunca para
   duplicar texto, layout ou identidade de terceiros.
5. **Diga o que falta.** Se um dado essencial não existe, a skill assume um default
   explícito e marca a suposição — não finge que sabe.

## Scripts

Todos rodam sem instalar nada além do que já existe no ambiente (Python 3.9+ / Node 18+).

| Script | Skill | O que faz |
|--------|-------|-----------|
| `score_ideias.py` | 1 | Pontua e ranqueia ideias de produto por 6 critérios ponderados |
| `precificacao.py` | 2 | Preço, margem, projeção, CPA máximo e escada de produtos |
| `validar_copy.py` | 3 | Audita copy: tamanho, promessa proibida, prova sem lastro |
| `mandala_plano.py` | 4 | Gera a grade de criativos priorizada (CSV + Markdown) |
| `carrossel_render.mjs` | 5 | JSON → HTML → PNG 1080×1350 em lote, via Chromium headless |

Cada script aceita `--help` e roda em modo demo sem argumentos.
