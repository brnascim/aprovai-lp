---
name: mandala-anuncios-reels
description: >
  Gera a MANDALA DE ANÚNCIOS — a grade que combina fase da campanha × momento × tipo de
  criativo × ângulo — para nunca mais ficar sem ideia de anúncio, e escreve os ROTEIROS
  DE REELS/vídeo criativo prontos para gravar (gancho de 3 segundos, corte a corte,
  legenda, CTA). Use SEMPRE que o usuário disser "mandala", "mandala de anúncios",
  "mandala de criativos", "acabaram minhas ideias de anúncio", "preciso de mais
  criativos", "quantos criativos eu faço", "plano de criativos", "matriz de criativos",
  "roteiro de Reels", "roteiro de vídeo", "vídeo para anúncio", "VSL curta", "criativo
  em vídeo", "UGC", "gravar anúncio", "gancho de 3 segundos", "meu criativo saturou",
  "criativo cansou", "quando matar um criativo" ou "como escalar criativo". Use também
  quando ele tiver um único anúncio funcionando e quiser multiplicar em variações
  estruturadas, ou pedir calendário/lote de produção de criativos. Para uma peça
  estática ou um carrossel isolado, use a skill anuncios-estaticos-carrossel.
---

# Mandala de anúncios e Reels criativos

Resolve o problema que quebra toda conta de tráfego: **criativo satura, e quem depende de
inspiração para** *(quando o CPA sobe)* **para de escalar.** A mandala transforma criação de
anúncio em processo combinatório — você nunca começa de uma folha em branco.

Ideia central (na linha da Mandala de Anúncios do método VTSD, de Leandro Ladeira): um
criativo é a combinação de **quatro eixos**. Trocar um eixo gera um anúncio genuinamente
diferente — não uma variação cosmética.

```
        FASE DA CAMPANHA          MOMENTO             TIPO DE CRIATIVO        ÂNGULO
        (quem vê)                 (o que ele sente)   (como é contado)        (o que ataca)
        ─────────────────         ─────────────────   ────────────────────    ──────────────
        Descoberta (frio)         Prontidão           Problema→Solução        Dor
        Relacionamento (morno)    Oportunidade        História                Objeção 1
        Conversão (quente)                            Dilema                  Objeção 2
        Remarketing (visitou)                         Comparação              Objeção 3
                                                      Prova                   Mecanismo
                                                      Explicação              Identidade
                                                      Apelo emocional         Custo de adiar
                                                      Exagero/humor
                                                      Impacto visual
```

4 × 2 × 9 × 7 = **504 combinações possíveis.** Você não precisa de 504 — precisa das 12 a 20
que fazem sentido para o seu momento, priorizadas. É isso que o script entrega.

## Entrada esperada

Do one-page de `produto-digital-concepcao`:

1. Promessa e mecanismo
2. Avatar + nível de consciência dominante
3. Top 3 objeções
4. Prova real disponível
5. **Situação atual da conta**: já roda tráfego? qual verba/dia? o que já funcionou e o que
   morreu? (isso muda completamente a priorização)
6. Capacidade de produção: quantos vídeos por semana, aparece em vídeo, tem material bruto

Sem histórico de conta, o plano começa pelo **kit de partida** (etapa 3).

## Fluxo

### 1. Ler os eixos

`references/mandala.md` define os quatro eixos, o que cada valor significa, quando usar e
qual combinação é incoerente (ex.: "Exagero/humor" + "Remarketing de checkout" quase nunca
funciona). Leia antes de gerar — a mandala mal usada vira lista aleatória.

### 2. Gerar o plano

```bash
python3 scripts/mandala_plano.py --n 12
python3 scripts/mandala_plano.py --n 20 --fase descoberta --csv plano.csv
python3 scripts/mandala_plano.py --kit-inicial          # 8 criativos de partida
python3 scripts/mandala_plano.py --n 12 --objecoes "acho caro,não tenho tempo,já tentei"
```

O script cobre os eixos de forma equilibrada (não sorteia repetido), marca combinações
incoerentes, prioriza por fase e devolve, para cada criativo: fase, momento, tipo, ângulo,
formato sugerido, esboço de gancho e o que aquele criativo testa.

O plano é o **esqueleto**. A copy final de cada peça sai desta skill (vídeo) ou de
`anuncios-estaticos-carrossel` (estático/carrossel).

### 3. Kit inicial — quando não há nada rodando

8 criativos que cobrem o essencial antes de saber o que funciona:

| # | Fase | Tipo | Por que está no kit |
|---|------|------|---------------------|
| 1 | Descoberta | Problema→Solução | O criativo mais previsível do mercado; é a linha de base |
| 2 | Descoberta | História | Testa conexão; costuma ter o melhor custo por lead |
| 3 | Descoberta | Impacto visual | Testa se o público responde a visual antes de argumento |
| 4 | Relacionamento | Explicação (mecanismo) | Testa se o diferencial se sustenta |
| 5 | Relacionamento | Comparação | Ataca "por que você e não o outro" |
| 6 | Conversão | Prova | Testa se a prova disponível é forte o bastante |
| 7 | Conversão | Dilema | Ataca a objeção nº 1 direto |
| 8 | Remarketing | Oferta/objeção | Recupera quem chegou perto |

Rode os 8, deixe rodar até ter dado (`references/metricas-e-escala.md`), e só então
multiplique os vencedores.

### 4. Escrever os roteiros de vídeo

`references/roteiros-reels.md` traz **9 estruturas de roteiro**, uma por tipo de criativo,
em formato corte a corte:

```
[0-3s]   GANCHO       — fala + o que aparece na tela + texto na tela
[3-10s]  CONTEXTO     — por que continuar assistindo
[10-25s] DESENVOLVIMENTO — o argumento/mecanismo/prova
[25-35s] VIRADA       — o que muda
[35-45s] CTA          — uma ação
```

Regras de roteiro que valem para todos:
- **Os 3 primeiros segundos decidem tudo.** Sem vinheta, sem "oi pessoal", sem apresentação.
  Comece na frase que interessa.
- **Fala natural, não texto lido.** Escreva como se fala: frases curtas, contração,
  repetição proposital.
- **Corte a cada 2–4 segundos.** Mudança de plano, de enquadramento ou de tela.
- **Legenda sempre** — a maioria assiste sem som.
- **Uma ideia por vídeo.** 45s é o teto de conforto para anúncio frio.

### 5. Produção

`references/producao-e-edicao.md` cobre: gravação sem equipamento, iluminação e áudio (o
áudio importa mais que a imagem), uso de IA em vídeo (o que já funciona e o que ainda
denuncia), legendas, e a regra de **hook stacking** — gravar 3 aberturas diferentes para o
mesmo corpo de vídeo, gerando 3 criativos pelo preço de um.

### 6. Leitura e rotação

`references/metricas-e-escala.md` define, com números: quando um criativo está aprovado,
quando matar, quando escalar, o que é fadiga de criativo (frequência subindo + CTR caindo +
CPA subindo) e o ritmo de reposição sustentável.

Regra prática: **a cada semana, reponha o número de criativos que morreu na semana anterior
+ 1.** É isso que mantém a conta escalando sem depender de "inspiração".

## Saída

```markdown
## Plano de criativos — [período]

*(tabela do script)*
| # | Fase | Momento | Tipo | Ângulo | Formato | Gancho esboçado | Testa |

## Roteiros prontos
Para cada criativo em vídeo:

### Criativo [n] — [tipo] · [fase]
**Gancho (0-3s):** [fala] | tela: [o que aparece] | texto: [≤6 palavras]
**Corte a corte:**
| Tempo | Fala | Imagem | Texto na tela |
**CTA:** [uma ação]
**Duração alvo:** Ns
**Objeção atacada:** [qual]
**Variações de gancho para hook stacking:** 3 aberturas alternativas

## Cronograma de produção
| Semana | Gravar | Editar | Subir | Matar |
```

## Regras

- **Nunca entregue criativo solto.** Toda peça pertence a uma célula da mandala e tem uma
  hipótese declarada. Sem hipótese, não há aprendizado — só gasto.
- **Cubra os quatro eixos.** Plano com 12 criativos todos de "Conversão/Problema→Solução"
  não é mandala, é repetição.
- **Respeite as incoerências** marcadas em `references/mandala.md`.
- **Prova real ou marcador.** Nenhum roteiro inventa depoimento, número ou case.
- **Roteiro que o usuário consegue gravar.** Se ele não aparece em vídeo, use as variantes
  sem rosto (tela, mãos, voz sobre imagem, texto animado) — todas listadas na referência.
- **Sem promessa de renda, sem atributo pessoal, sem antes/depois corporal** — as políticas
  em `../anuncios-estaticos-carrossel/references/politicas-meta.md` valem igual para vídeo.
- **Não escale o que não tem dado.** Escalar com 3 conversões é ler ruído.

## Referências

| Arquivo | Quando ler |
|---------|-----------|
| `references/mandala.md` | Etapa 1 — os 4 eixos, significados e combinações incoerentes |
| `references/roteiros-reels.md` | Etapa 4 — 9 estruturas de roteiro corte a corte |
| `references/producao-e-edicao.md` | Etapa 5 — gravação, áudio, IA em vídeo, hook stacking |
| `references/metricas-e-escala.md` | Etapa 6 — quando matar, quando escalar, fadiga |

## Handoff

- Células de **estático/carrossel** do plano → `anuncios-estaticos-carrossel` escreve as peças
- Carrosséis aprovados → `cowork-carrosseis` renderiza em lote
- Se **todos** os criativos performam mal em todas as células, o problema não é criativo:
  volte para `produto-digital-concepcao`. Nenhuma mandala salva promessa errada.
