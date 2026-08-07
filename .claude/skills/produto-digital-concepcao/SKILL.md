---
name: produto-digital-concepcao
description: >
  Define os três pilares que fazem um produto digital vender: PROMESSA (o que transforma,
  em quanto tempo, para quem), PÚBLICO-ALVO (avatar, nível de consciência, dores e
  objeções reais) e PREÇO (ticket, ancoragem, escada de produtos, margem e CPA máximo).
  Use SEMPRE que o usuário falar em "promessa do produto", "qual minha promessa",
  "definir público-alvo", "avatar", "persona", "ICP", "por quanto vender", "quanto
  cobrar", "precificar meu curso/mentoria/produto", "meu produto não vende", "acham
  caro", "montar oferta", "estruturar oferta", "bônus", "garantia", "posicionamento",
  "diferencial", "nível de consciência", "escada de produtos", "ticket médio" ou
  "reformular meu produto". Use também quando ele já tiver um produto pronto e quiser
  revisar promessa/preço, ou quando trouxer o resultado da skill produto-digital-ideias.
  Não use para gerar ideias de produto do zero — isso é a skill produto-digital-ideias.
---

# Concepção: promessa, público e preço

Pega uma ideia validada e devolve **um one-page de conceito** que qualquer criativo, página
ou vídeo pode usar sem inventar nada: promessa cravada, avatar com linguagem própria,
oferta montada e preço com conta fechada.

Regra que organiza tudo: **promessa, público e preço são a mesma decisão vista de três
ângulos.** Mudar o público muda a promessa e o preço. Se algo não fecha, é aqui que se
conserta — não na copy do anúncio.

## Entrada esperada

Vinda de `produto-digital-ideias` ou do usuário direto:

1. Ideia em uma linha (público + resultado + prazo + sem-o-quê)
2. Tipo e formato do produto
3. Prova disponível: cases, depoimentos, números, credenciais — **o que existe de verdade**
4. Concorrentes/referências que o público já conhece
5. Restrições: prazo, verba de tráfego, capacidade de atendimento

Sem prova nenhuma? Siga assim mesmo e marque cada afirmação sem lastro com `[PROVA: ...]`.
**Nunca preencha prova inventada** — nem como exemplo, nem como rascunho.

## Fluxo

### 1. Público antes de promessa

Quem paga define o que se promete. Produza o avatar segundo `references/publico-e-avatar.md`,
que exige quatro coisas:

- **Situação atual em uma cena concreta** (não adjetivo: "abre o Excel toda segunda às 7h e
  copia dados na mão por 3 horas", não "profissional desorganizado")
- **Nível de consciência** (Schwartz: inconsciente → consciente do problema → consciente da
  solução → consciente do produto → mais consciente). Isso define a **abertura** de toda
  comunicação e é o erro nº 1 de quem não vende.
- **Linguagem literal**: 10 frases que ele usaria. Se houver material do usuário (DMs,
  comentários, respostas de enquete), extraia de lá. Senão, marque como hipótese a validar.
- **Objeções reais**, priorizadas — as 6 famílias estão na referência.

### 2. Promessa

Use `references/promessa.md`. A promessa segue a estrutura:

```
[Público] consegue [resultado observável] em [prazo realista]
mesmo [obstáculo que ele acha que o desqualifica],
sem [o custo que ele mais teme]
```

Gere **5 variações** em níveis diferentes de agressividade e escolha uma. A escolhida
precisa passar nos 6 testes da referência (observável, temporal, do público, honesta,
diferenciada, memorável). Reprovou em algum → reescreva, não negocie.

Promessa não é slogan. Se não dá para saber, olhando o cliente daqui a X dias, se ela foi
cumprida, ainda não é promessa.

### 3. Oferta

Promessa é o que ele ganha; oferta é a pilha do que ele recebe e por que agora.
`references/oferta-e-bonus.md` cobre: núcleo, bônus (cada um matando UMA objeção específica),
garantia, escassez legítima e o que **não** fazer (escassez falsa, bônus de enchimento).

Ordem correta: **promessa → objeções → bônus.** Bônus escolhido antes das objeções é
enchimento e derruba a conversão em vez de subir.

### 4. Preço

Rode o script:

```bash
python3 scripts/precificacao.py --interativo
python3 scripts/precificacao.py --demo
python3 scripts/precificacao.py --ticket 497 --meta-mensal 30000 --conversao 1.5 \
    --custo-plataforma 9.9 --custo-entrega 12 --margem-alvo 70
```

Ele calcula: margem por venda, vendas necessárias para a meta, **CPA máximo sustentável**,
ROAS de equilíbrio, preço sugerido por três métodos (valor, concorrência, custo+margem) e a
escada de produtos coerente com o ticket.

A leitura estratégica — quando subir preço, quando parcelar, order bump, quando o ticket
está incompatível com o público — está em `references/precificacao-e-oferta.md`.

Regra dura: **se o CPA máximo for menor que o CPA realista do nicho, o problema é o preço
ou o público, não o anúncio.** Diga isso explicitamente ao usuário antes que ele gaste em
tráfego.

### 5. Auditoria de conformidade

Antes de fechar, passe a promessa e a oferta por
`references/compliance-promessas-br.md`. Qualquer promessa com número de renda, resultado
garantido, prazo impossível, prova de terceiro sem autorização ou garantia abaixo de 7 dias
volta para reescrita. Não é opcional, e não é "depois a gente ajusta".

## Saída — one-page de conceito

Sempre este formato (o template completo está em `templates/one-page-conceito.md`):

```markdown
# [Nome do produto]

## Promessa
> [uma frase]
Variações testadas: 5 · escolhida por: [motivo]

## Público
- Avatar: [nome fictício], [cena concreta do dia]
- Nível de consciência: [nível] → abertura da comunicação deve ser [regra do nível]
- Linguagem dele: "..." · "..." · "..." (10 frases)
- Top 3 objeções: [obj] → [resposta] → [prova que sustenta ou [PROVA: falta]]

## Oferta
| Item | O que é | Objeção que mata | Valor percebido |
Garantia: [prazo e condição]
Escassez: [motivo real ou "nenhuma"]

## Preço
- Ticket: R$ X (à vista) / 12× R$ Y
- Margem líquida por venda: R$ Z (N%)
- Vendas/mês para a meta de R$ M: N
- CPA máximo: R$ C · ROAS de equilíbrio: R
- Escada: entrada R$ A → núcleo R$ B → alto ticket R$ C

## Riscos e suposições
- [o que foi assumido sem dado]
- [o que precisa ser validado antes de escalar]
```

## Regras

- **Uma promessa, não três.** Produto que promete tudo não promete nada.
- **Prova nunca é inventada.** Marcador `[PROVA: precisa de depoimento sobre X]` fica visível
  no entregável até o usuário preencher.
- **Sem número de renda na promessa principal.** Ver compliance.
- **Preço redondo e defensável.** Se o usuário não consegue justificar o preço em uma frase
  para o cliente, o preço está errado — não a frase.
- **Público estreito, promessa específica.** Se a promessa serve para "qualquer pessoa",
  volte à etapa 1.
- **Se o produto já existe e não vende**, o diagnóstico segue esta ordem: público errado →
  promessa vaga → oferta fraca → preço incompatível → tráfego. Tráfego é o **último**
  suspeito, quase nunca o primeiro.

## Referências

| Arquivo | Quando ler |
|---------|-----------|
| `references/publico-e-avatar.md` | Etapa 1 — avatar, níveis de consciência, objeções |
| `references/promessa.md` | Etapa 2 — estrutura, 5 variações, 6 testes, exemplos bons e ruins |
| `references/oferta-e-bonus.md` | Etapa 3 — pilha de valor, bônus por objeção, garantia |
| `references/precificacao-e-oferta.md` | Etapa 4 — leitura estratégica de preço e escada |
| `references/compliance-promessas-br.md` | Etapa 5 — CDC, conselhos, plataformas. Obrigatório |

## Handoff

O one-page alimenta diretamente:
- **`anuncios-estaticos-carrossel`** — promessa, objeções e linguagem viram gancho e copy
- **`mandala-anuncios-reels`** — objeções e nível de consciência definem os eixos da mandala
- **`apps-saas-sem-codigo`** — se o formato escolhido foi ferramenta/SaaS

Passe o arquivo inteiro. As skills seguintes não devem reinventar promessa nem avatar — se
elas precisarem inventar, o one-page está incompleto.
