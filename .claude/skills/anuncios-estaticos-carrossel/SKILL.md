---
name: anuncios-estaticos-carrossel
description: >
  Cria anúncios ESTÁTICOS (imagem única) e CARROSSÉIS completos — copy do criativo, texto
  primário, headline, CTA, roteiro slide a slide e prompt de imagem pronto para IA
  generativa ou para o designer. Use SEMPRE que o usuário pedir "criar anúncio",
  "anúncio estático", "criativo", "carrossel", "post para vender", "copy de anúncio",
  "texto primário", "headline de anúncio", "arte de anúncio", "prompt de imagem para
  anúncio", "meu anúncio não converte", "preciso de variações de criativo", "anúncio
  para Meta Ads / Facebook / Instagram", "gancho", "hook", "parar o scroll", "criativo
  de conversão" ou "carrossel de vendas". Use também quando ele trouxer um one-page de
  conceito, uma promessa ou um produto e quiser transformar em peças de anúncio, e
  quando pedir para auditar/melhorar um criativo existente. Para vídeo, Reels e para a
  GRADE de criativos, use a skill mandala-anuncios-reels. Para renderizar carrossel em
  lote como PNG, use a skill cowork-carrosseis.
---

# Anúncios estáticos e carrossel

Produz peças prontas para subir: **copy + estrutura visual + prompt de imagem**, com
variação suficiente para testar e critério para saber o que matar.

Princípio que governa tudo: **o criativo não vende o produto, ele compra a atenção certa.**
O primeiro segundo (ou o primeiro slide) tem uma única tarefa: fazer a pessoa **certa**
parar e continuar. Gancho que para todo mundo traz lead ruim e destrói o CPA.

## Entrada esperada

Do one-page de `produto-digital-concepcao` (peça se não tiver):

1. Promessa (uma frase)
2. Avatar + **nível de consciência** do público que vai ver o anúncio
3. 10 frases de linguagem literal
4. Top 3 objeções
5. Mecanismo único
6. Prova disponível — apenas a real
7. Destino do clique (página de vendas, captura, WhatsApp, checkout)
8. Formato desejado e onde vai rodar (feed, stories, orgânico ou pago)

Faltando o one-page, colete o mínimo: promessa, público, prova e destino. **Não invente
prova, número ou depoimento em hipótese nenhuma** — use `[PROVA: ...]` no lugar.

## Fluxo

### 1. Definir o alvo da peça

Três decisões antes de escrever uma palavra:

| Decisão | Opções | Consequência |
|---------|--------|--------------|
| **Nível de consciência** | 1–2 frio · 3 morno · 4–5 quente | Define a abertura (ver `references/anatomia-estatico.md`) |
| **Objetivo** | parar o scroll · educar · quebrar objeção · converter | Define o CTA e o que medir |
| **Formato** | estático 1:1 · estático 4:5 · carrossel · story 9:16 | Define quantidade de texto e composição |

Anúncio para público frio com CTA de "compre agora" é o erro mais caro e mais comum.
Se o usuário pedir isso, entregue e **avise** por que a conversão tende a ser baixa.

### 2. Gancho

O gancho é 80% do resultado. Gere **10 ganchos** usando as 12 famílias de
`references/biblioteca-de-ganchos.md`, cobrindo no mínimo 4 famílias diferentes.

Filtro obrigatório — descarte o gancho que:
- serve para qualquer produto do mercado (genérico);
- promete o que a peça não entrega (isca furada, gera lead ruim);
- usa "atributo pessoal" ("você está endividado?") — reprovação garantida no Meta;
- só faz sentido para quem já conhece o produto, quando o público é frio.

### 3. Escrever a peça

**Estático** → `references/anatomia-estatico.md`
Blocos: texto na imagem (≤ 8 palavras no bloco principal) · texto primário · headline ·
descrição · CTA. Cada bloco tem função distinta; repetir a mesma frase nos quatro é
desperdício de espaço.

**Carrossel** → `references/anatomia-carrossel.md`
Estruturas testadas por objetivo (dor→solução, lista, passo a passo, mito×verdade,
antes/depois, história, comparação), com a regra de ouro: **um slide, uma ideia**, e cada
slide terminando com motivo para deslizar o próximo (loop aberto).

### 4. Prompt de imagem

Todo criativo sai com prompt pronto (`references/prompts-de-imagem.md`), estruturado em:
`sujeito + ação + ambiente + enquadramento + luz + estilo + paleta + espaço reservado para
texto + proporção`.

Regras não negociáveis:
- **Espaço negativo planejado** para o texto — imagem bonita sem lugar para a headline é
  imagem inútil;
- **Nada de texto gerado por IA dentro da imagem** — a IA erra letra em português; o texto
  entra por cima, na edição ou no render;
- **Sem rosto de pessoa real, marca ou personagem protegido** no prompt;
- **Sem simular print de rede social, notícia ou conversa real** — parece prova falsa e
  viola política de plataforma.

### 5. Variação para teste

Nunca entregue 1 criativo. O padrão é **3 a 5 peças que variam UMA coisa por vez**:

```
Base:  gancho A + imagem A + CTA A
V1:    gancho B + imagem A + CTA A     ← testa gancho
V2:    gancho A + imagem B + CTA A     ← testa imagem
V3:    gancho A + imagem A + CTA B     ← testa CTA
V4:    formato diferente (carrossel vs. estático), mesmo gancho
```

Variar tudo ao mesmo tempo é gastar dinheiro sem aprender nada.
Para o **plano completo** de quantos criativos e de que tipo, use `mandala-anuncios-reels`.

### 6. Auditoria antes de publicar

```bash
python3 scripts/validar_copy.py anuncio.json
python3 scripts/validar_copy.py --demo
python3 scripts/validar_copy.py --texto "Ganhe R$ 10 mil por mês trabalhando de casa"
```

O script checa limites de caracteres, promessa proibida, atributo pessoal, prova sem
lastro, CTA ausente e excesso de texto na arte. Ele **não substitui** a leitura de
`references/politicas-meta.md` — mas pega o que mais reprova.

## Saída

Para cada criativo:

```markdown
### Criativo [n] — [tipo] · nível [x] · objetivo [y]

**Gancho:** [frase]  (família: [nome])

**Texto na imagem**
- Bloco principal: [≤ 8 palavras]
- Apoio: [≤ 12 palavras]
- Selo/CTA visual: [≤ 4 palavras]

**Texto primário**
[3–6 linhas, primeira linha resolvendo o "ver mais"]

**Headline:** [≤ 40 caracteres]
**Descrição:** [≤ 30 caracteres]
**CTA (botão):** [opção nativa da plataforma]

**Prompt de imagem**
> [prompt completo]

**Proporção:** 4:5 (feed) | 1:1 | 9:16 (stories)
**Objeção atacada:** [qual das 3]
**Hipótese do teste:** [o que este criativo prova ou refuta]
```

Carrossel usa o mesmo cabeçalho + tabela `slide | texto | elemento visual | função`.

## Regras

- **Uma ideia por peça.** Criativo que fala de 3 benefícios não fixa nenhum.
- **Fale com um, não com todos.** "Você que é contador em escritório pequeno" > "empresários".
- **A primeira linha do texto primário é headline também** — o resto fica escondido no
  "ver mais". Nunca comece com "Você sabia que...".
- **Prova real ou marcador.** Nunca gere depoimento, print ou número fictício, nem como
  exemplo de preenchimento.
- **Sem estética de golpe:** dinheiro voando, carro de luxo, seta vermelha por todo lado,
  print de saldo. Converte mal, atrai o pior lead e derruba conta.
- **Acessibilidade e legibilidade:** contraste alto, fonte grande, texto legível em tela
  pequena. A maioria vê no celular, rolando rápido, sem som.
- **Coerência com o destino.** O que o anúncio promete tem que estar na primeira dobra da
  página. Incoerência mata conversão e reprova anúncio.

## Referências

| Arquivo | Quando ler |
|---------|-----------|
| `references/anatomia-estatico.md` | Etapa 3 — blocos, limites, composição por proporção |
| `references/anatomia-carrossel.md` | Etapa 3 — 7 estruturas de carrossel slide a slide |
| `references/biblioteca-de-ganchos.md` | Etapa 2 — 12 famílias de gancho com exemplos |
| `references/prompts-de-imagem.md` | Etapa 4 — anatomia do prompt, estilos, erros |
| `references/politicas-meta.md` | Antes de publicar — o que reprova e como reescrever |

## Handoff

- **Carrossel aprovado** → `cowork-carrosseis` para renderizar os PNGs em lote
- **Precisa de plano/volume de criativos** → `mandala-anuncios-reels`
- **Copy fraca por conceito fraco** (promessa vaga, objeção não mapeada) → volte para
  `produto-digital-concepcao`. Criativo não conserta conceito ruim.
