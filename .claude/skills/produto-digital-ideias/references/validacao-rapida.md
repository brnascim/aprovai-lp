# 6 testes de validação (< R$ 200, < 7 dias)

A regra que sustenta esta skill: **nada é produzido antes de um sinal de mercado.** Escolha
UM teste, defina o critério numérico antes de rodar e respeite o resultado.

Ordem de força do sinal, do mais fraco ao mais forte:

```
curtida  <  comentário  <  e-mail  <  clique no checkout  <  PAGAMENTO
                                                             └─ único que vale de verdade
```

---

## Teste 1 — Enquete de dor
**Custo** R$ 0 · **Prazo** 2 dias · **Valida** critério "Dor"

Story/post/mensagem para 20–50 pessoas do público: *"O que mais te trava hoje em [tema]?"*
com 3 opções + "outro".

**Critério de aprovação:** ≥ 40% escolhem a mesma dor **e** ≥ 5 pessoas descrevem a dor
espontaneamente com palavras próprias (essas palavras viram a copy depois).
**Limitação:** valida tema, não valida compra. Nunca produza só com isso.

## Teste 2 — Post de oferta (sem produto)
**Custo** R$ 0 · **Prazo** 3 dias · **Valida** interesse + linguagem

Publique a promessa como se o produto existisse, peça para comentar uma palavra-chave.

**Critério:** ≥ 15 comentários/DMs em audiência pequena (<3k), ou ≥ 1% da audiência.
**Regra ética:** não afirme que o produto está pronto se não está. Diga *"estou montando"*.
Prometer disponibilidade inexistente é propaganda enganosa.

## Teste 3 — Lista de espera
**Custo** R$ 0–50 · **Prazo** 5 dias · **Valida** interesse com fricção

Página simples com promessa + campo de e-mail/WhatsApp.

**Critério:** ≥ 30% de conversão dos visitantes **e** ≥ 30 inscritos.
**Limitação:** e-mail é barato de dar. Sinal médio.

## Teste 4 — Pré-venda (o teste padrão)
**Custo** R$ 0–100 · **Prazo** 7 dias · **Valida** dor + poder de compra + promessa

Venda antes de produzir, com data de entrega explícita e preço de pré-lançamento.

**Critério:** ≥ 3 pagamentos em 5 dias para audiência pequena; ≥ 10 para lista de 1.000+.
**Obrigatório:** informe que a entrega começa em `[data]`, ofereça reembolso integral se
não entregar, e **entregue**. Pré-venda sem entrega é fraude, não é teste.
**É o teste que a skill recomenda por padrão** — é o único que troca dinheiro por promessa.

## Teste 5 — Piloto pago ao vivo
**Custo** R$ 0 · **Prazo** 7 dias para vender · **Valida** tudo + gera o material

Venda uma turma pequena ao vivo por preço reduzido, entregue ao vivo e grave. Sai com:
receita, depoimento, gravação (que vira o curso) e as dúvidas reais (que viram o módulo
que faltava).

**Critério:** ≥ 5 matrículas pagas.
**Melhor caminho para curso gravado** — evita gravar 40 aulas para o vazio.

## Teste 6 — Anúncio de fumaça (smoke test)
**Custo** R$ 100–200 · **Prazo** 3 dias · **Valida** alcançabilidade + CPA

Rode 2–3 criativos para uma página de captura/checkout. Mede se dá para comprar atenção
desse público a preço viável.

**Critério:** CTR ≥ 1% e custo por lead ≤ 20% do ticket pretendido.
**Regra ética:** a página deve descrever o produto honestamente e permitir compra ou
inscrição real. Cobrar por algo que não existirá é fraude; captar interesse declarando
"em breve" é legítimo.

---

## Escolha do teste pelo critério mais fraco

| Critério fraco na matriz | Teste indicado |
|--------------------------|----------------|
| Dor | 1 → depois 4 |
| Poder de compra | 4 ou 5 |
| Capacidade de entrega | 5 (entregar ao vivo revela o buraco) |
| Alcançabilidade | 6 |
| Diferenciação | 2 (o ângulo puxa reação ou não) |
| Velocidade | 4 |

## Ficha do teste (obrigatória na saída)

```markdown
**Teste:** pré-venda
**Oferta:** [promessa em 1 linha] por R$ 97, entrega a partir de [data]
**Onde:** [canal]
**Custo:** R$ 0
**Prazo:** 5 dias
**Aprovado se:** ≥ 3 pagamentos
**Se reprovar:** [o que muda — público, promessa, preço ou formato]
```

O campo "se reprovar" é o mais importante e o mais pulado. Um teste sem plano de reprovação
vira desculpa para produzir assim mesmo.

## Leitura do resultado

- **Aprovou** → produza a v1 no menor escopo que cumpre a promessa. Entregue no prazo.
- **Reprovou por promessa** (clicam, não compram) → mesma ideia, promessa mais concreta.
  Volte para `produto-digital-concepcao`.
- **Reprovou por público** (ninguém clica) → mesma promessa, público mais estreito.
- **Reprovou por preço** (querem, acham caro) → produto de entrada mais barato primeiro.
- **Ninguém reagiu** → a dor não existe nessa intensidade. Volte à etapa 2 e troque de ideia.
  Insistir aqui é o erro mais caro do mercado digital.
