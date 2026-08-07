---
name: produto-digital-ideias
description: >
  Gera, filtra e pontua ideias de produto digital e define o TIPO e o FORMATO certo de
  entrega (ebook, curso, mentoria, comunidade, template, planilha, SaaS, serviço
  produtizado). Use SEMPRE que o usuário disser que quer "criar um produto digital",
  "não sei o que vender", "que infoproduto eu faço", "tenho conhecimento mas não sei
  transformar em produto", "escolher nicho", "achar sub-nicho", "validar ideia",
  "testar demanda", "que formato usar", "curso ou mentoria", "produto de entrada",
  "produto isca", "escada de produtos", "monetizar minha audiência" ou "monetizar meu
  conhecimento". Use também quando ele trouxer uma lista de ideias soltas e quiser
  decidir qual atacar primeiro, ou quando mencionar VTSD, perpétuo, infoproduto,
  Hotmart, Kiwify, Eduzz ou nicho digital sem saber ainda o que vender. Não use para
  definir promessa, público e preço de um produto já escolhido — isso é a skill
  produto-digital-concepcao.
---

# Ideias, tipos e formatos de produto digital

Transforma "quero vender algo online" em **3 ideias finalistas pontuadas**, cada uma com
tipo e formato definidos e um teste de validação barato antes de produzir qualquer coisa.

O erro que esta skill existe para evitar: produzir um curso de 40 aulas por 3 meses e
descobrir na venda que ninguém queria aquilo. Aqui a ordem é **demanda → oferta →
produção**, nunca o contrário.

## Entrada esperada

Colete estas cinco coisas antes de gerar ideia. Se o usuário já deu no pedido, não
pergunte de novo — repita o que entendeu em uma linha e siga.

1. **Repertório** — o que ele sabe fazer, já fez, ou já foi pago para fazer.
2. **Ativos** — audiência (tamanho e onde), lista, portfólio, cases, autoridade, tempo.
3. **Restrições** — horas por semana, dinheiro disponível, aparece em vídeo ou não,
   prazo até precisar faturar.
4. **Objetivo financeiro** — quanto quer faturar por mês e em quanto tempo.
5. **Vetos** — o que ele não quer fazer de jeito nenhum (atendimento 1a1, aparecer, etc).

Faltou algo? Assuma o default mais comum (`10h/semana`, `sem audiência`, `sem verba de
tráfego`, `aparece em vídeo`) e **declare a suposição em texto** antes de continuar.

## Fluxo

### 1. Mapa de território (não pule)

Antes de gerar ideias, escreva o mapa em 3 blocos curtos:

- **Dores que ele já resolveu para alguém** — dor real, com nome e situação, não abstração.
- **Onde essa dor já move dinheiro** — quem já vende para esse público, em que formato,
  faixa de preço. Se houver acesso a busca, verifique; senão, marque como hipótese.
- **Ângulo de vantagem** — por que ele especificamente, e não qualquer outro.

Regra dura: **dor sem mercado é hobby, mercado sem ângulo é commodity.** Uma ideia só
avança se marcar os três blocos.

### 2. Gerar em quantidade (12 a 20 ideias)

Use as lentes de `references/geracao-de-ideias.md` — são 8 lentes que produzem ideias
estruturalmente diferentes, não 20 variações da mesma coisa. Cobrir no mínimo:

- 4 ideias de **sub-nicho** (mesma dor, público mais estreito e mais caro)
- 3 ideias de **formato inusitado** (a mesma solução entregue de outro jeito)
- 3 ideias de **produto de entrada** (baixo ticket, resolve UM problema em dias)
- 2 ideias de **recorrência** (comunidade, atualização, acompanhamento)
- 2 ideias de **ferramenta** (planilha, template, app — entrega sem tempo do criador)

Cada ideia em uma linha no formato:
`[Público específico] consegue [resultado concreto] em [prazo] sem [dor do caminho atual]`

### 3. Pontuar e cortar

Rode o script:

```bash
python3 scripts/score_ideias.py minhas-ideias.json
python3 scripts/score_ideias.py --demo          # exemplo preenchido
python3 scripts/score_ideias.py --template > minhas-ideias.json
```

Os 6 critérios (0–5) e seus pesos estão em `references/matriz-de-decisao.md`. O script
ranqueia, marca eliminações automáticas (qualquer critério `0` mata a ideia) e aponta o
critério mais fraco de cada finalista — que vira o item a testar.

Nunca pontue "no olho" e nunca ajuste nota para salvar uma ideia querida. Se o usuário
discordar de uma nota, mude a nota **e rode de novo** — o ranking é a saída, não sua
opinião.

### 4. Definir tipo e formato dos 3 finalistas

`references/tipos-e-formatos.md` traz 14 tipos de produto com: esforço de produção,
faixa de ticket praticada no Brasil, tempo até a primeira venda, exigência de audiência
e o modo de falha típico de cada um.

A decisão sai de duas perguntas, nessa ordem:

1. **Qual o menor formato que entrega o resultado prometido?** Se um checklist de 4
   páginas resolve, não faça curso. Formato inflado mata margem e atrasa o caixa.
2. **Esse formato cabe nas restrições dele?** Sem audiência + sem verba pede formato que
   se vende por conteúdo orgânico; sem tempo pede formato assíncrono.

### 5. Teste de validação antes de produzir

Toda ideia finalista sai com **um teste que custa menos de R$ 200 e menos de 7 dias**.
Os seis testes aceitos estão em `references/validacao-rapida.md` (do mais barato ao mais
caro: enquete de dor, post de oferta, lista de espera, pré-venda, piloto pago ao vivo,
anúncio de fumaça). Prescreva um teste e o **critério numérico de aprovação** — ex.:
"aprovado se 3 pessoas pagarem R$ 97 em 5 dias".

Sem critério numérico, o teste não conta.

## Saída

Sempre este formato:

```markdown
## Mapa de território
Dor · Mercado · Ângulo (3 linhas)

## Ideias geradas (N)
Tabela: ideia | lente | público | resultado prometido

## Ranking
Tabela do script: posição | ideia | nota | critério mais fraco

## 3 finalistas
Para cada uma:
- **Ideia:** frase de uma linha
- **Tipo e formato:** X, porque [restrição/margem/prazo]
- **Ticket estimado:** R$ Y (faixa de referência do tipo)
- **Esforço até a v1:** N dias
- **Teste de validação:** o quê, quanto custa, critério de aprovação
- **Maior risco:** o critério mais fraco e como reduzi-lo

## Recomendação
Uma escolha, com o porquê em 3 linhas. Sem "depende".
```

## Regras

- **Especificidade vence.** "Curso de Excel" é ruído; "Excel para escritório de contabilidade
  fechar folha em metade do tempo" é produto. Recuse ideias genéricas — reescreva-as
  estreitando público ou situação.
- **Nunca invente números de mercado.** Sem pesquisa, escreva "hipótese a validar", não
  "mercado de R$ X bilhões".
- **Nada de nicho que exige credencial que o usuário não tem.** Saúde, medicação,
  investimento com promessa de retorno e jurídico têm barreira legal — `references/nichos-sensiveis.md`.
- **Uma recomendação, não um cardápio.** Terminar com "as três são boas" é falha da skill.
- **Produção só depois do teste.** Se o usuário pedir para já produzir o conteúdo, entregue
  o teste primeiro e diga por quê.

## Referências

| Arquivo | Quando ler |
|---------|-----------|
| `references/geracao-de-ideias.md` | Na etapa 2 — as 8 lentes com exemplos |
| `references/tipos-e-formatos.md` | Na etapa 4 — os 14 tipos com ticket, esforço e falha típica |
| `references/matriz-de-decisao.md` | Na etapa 3 — critérios, pesos e como pontuar sem viés |
| `references/validacao-rapida.md` | Na etapa 5 — os 6 testes com custo e critério |
| `references/nichos-sensiveis.md` | Sempre que a ideia tocar saúde, dinheiro, jurídico ou menores |

## Handoff

Com o finalista escolhido, siga para **`produto-digital-concepcao`** passando:
ideia em uma linha, tipo/formato, público, ticket estimado e resultado do teste de
validação. Se o teste reprovou, volte para a etapa 2 com o aprendizado — não force a
concepção de uma ideia que o mercado recusou.
