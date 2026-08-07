# Matriz de decisão — 6 critérios

Pontue cada ideia de 0 a 5 em cada critério. O script `../scripts/score_ideias.py` aplica os
pesos, ranqueia e marca eliminações.

| # | Critério | Peso | Pergunta que decide a nota |
|---|----------|------|----------------------------|
| 1 | Dor | 3 | O público perde dinheiro, tempo ou status **agora** por não resolver isso? |
| 2 | Poder de compra | 3 | Esse público já paga por soluções nessa faixa de preço? |
| 3 | Capacidade de entrega | 2 | O usuário consegue entregar o resultado com o que já sabe e tem? |
| 4 | Alcançabilidade | 2 | Dá para achar essas pessoas de forma barata e repetível? |
| 5 | Diferenciação | 1 | Existe um ângulo que só o usuário tem? |
| 6 | Velocidade até a 1ª venda | 1 | Dá para ter dinheiro na conta em até 30 dias? |

**Nota máxima ponderada: 60.**

## Régua de pontuação

Não invente notas intermediárias por conforto. Use as âncoras.

### 1. Dor (peso 3)
- **5** — a pessoa perde dinheiro toda semana e já tentou resolver sozinha e falhou
- **4** — dor recorrente, com prazo ("preciso disso até o fim do mês")
- **3** — incômodo real, mas adiável
- **2** — melhoria desejável ("seria legal")
- **1** — curiosidade
- **0** — o público não reconhece isso como problema → **elimina**

### 2. Poder de compra (peso 3)
- **5** — já compra soluções similares acima de R$ 1.000
- **4** — compra na faixa R$ 300–1.000
- **3** — compra até R$ 300
- **2** — compra, mas resiste muito a preço
- **1** — só consome grátis
- **0** — não tem dinheiro para isso → **elimina**

### 3. Capacidade de entrega (peso 2)
- **5** — já entregou esse resultado para outras pessoas, com prova
- **4** — entregou para si mesmo, com resultado
- **3** — sabe fazer, nunca ensinou
- **2** — precisa estudar algumas semanas
- **1** — precisa de meses de estudo
- **0** — exige credencial/registro que ele não tem → **elimina** (ver `nichos-sensiveis.md`)

### 4. Alcançabilidade (peso 2)
- **5** — público concentrado e segmentável (grupo, evento, ferramenta, cargo no LinkedIn)
- **4** — segmentável por interesse em tráfego pago
- **3** — alcançável por conteúdo orgânico com esforço
- **2** — disperso, sem lugar óbvio
- **1** — só por indicação
- **0** — não dá para identificar quem é → **elimina**

### 5. Diferenciação (peso 1)
- **5** — método próprio + case exclusivo + história que ninguém repete
- **4** — combinação incomum de competências
- **3** — recorte de público que ninguém atende bem
- **2** — mesma coisa, mais bem executada
- **1** — cópia
- **0** — cópia de material de terceiro → **elimina** (além de ilegal)

### 6. Velocidade (peso 1)
- **5** — v1 em até 7 dias
- **4** — 2 semanas
- **3** — 1 mês
- **2** — 2 meses
- **1** — 3+ meses
- **0** — não dá para estimar

## Como não enviesar

- **Pontue o pior caso, não o melhor.** Se você hesitou entre 4 e 5, é 4.
- **Nota 5 exige evidência citável.** Sem evidência, teto 3 em Dor, Poder de compra e
  Capacidade de entrega.
- **Não conserte a nota, conserte a ideia.** Se Alcançabilidade ficou 2, reescreva a ideia
  estreitando o público — e pontue a versão nova como ideia separada.
- **O critério mais fraco do finalista vira o teste de validação.** Dor baixa → teste de
  enquete/dor. Poder de compra baixo → teste de pré-venda paga. Alcançabilidade baixa →
  teste de anúncio de fumaça.

## Interpretação do resultado

| Nota ponderada | Leitura |
|----------------|---------|
| 48–60 | Ataque agora |
| 38–47 | Boa — valide o critério mais fraco antes de produzir |
| 28–37 | Precisa de reescrita (estreitar público ou trocar formato) |
| < 28 | Descarte |
| Qualquer 0 | Eliminada, independente do total |

Empate técnico (diferença ≤ 3 pontos): desempate por **velocidade até a primeira venda**.
Caixa cedo compra tempo para tudo o mais.
