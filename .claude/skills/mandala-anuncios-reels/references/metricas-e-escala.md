# Métricas, rotação e escala

Sem critério numérico, "matar criativo" vira opinião — e a conta oscila conforme o humor de
quem olha o painel. Este arquivo define os critérios.

> Os números abaixo são **referências de partida** para infoproduto no Meta. Depois de 30
> dias de dados próprios, substitua pelos **seus** números: sua média é sempre melhor
> referência que a média do mercado.

## Métricas que importam, na ordem

```
1. CPA (custo por aquisição)     ← a única que paga a conta
2. ROAS                          ← retorno sobre o investimento
3. Taxa de conversão da página   ← separa problema de criativo × problema de página
4. CPC / CTR                     ← qualidade do criativo em prender e mover
5. Retenção (vídeo) 3s / 25% / 75%  ← onde o roteiro perde a pessoa
6. Frequência                    ← o termômetro da saturação
```

Curtida, alcance e visualização não pagam nada. Só entram como diagnóstico.

## Referências de partida

| Métrica | Ruim | Aceitável | Bom |
|---------|------|-----------|-----|
| CTR (link) frio | < 0,8% | 1–1,5% | > 2% |
| Retenção 3s (vídeo) | < 25% | 30–40% | > 45% |
| Retenção 25% | < 15% | 20–30% | > 35% |
| Conversão da página de vendas | < 0,7% | 1–2% | > 3% |
| Frequência (frio, 7 dias) | > 3 | 1,5–2,5 | < 1,5 |
| CPA | > CPA máximo | ≈ CPA máximo | < 50% do CPA máximo |

O **CPA máximo** vem do script de precificação
(`../../produto-digital-concepcao/scripts/precificacao.py`). É ele — não a média do mercado —
que define se um criativo é bom.

## Quando um criativo tem dado suficiente

Não decida antes de:

```
mínimo 1.000 impressões  E  (3 conversões  OU  gasto = 1,5 × ticket)
```

Matar antes disso é ler ruído. Manter muito além disso é queimar verba por indecisão.

Para campanhas de aprendizado, respeite a fase de aprendizagem antes de julgar: mexer em
orçamento/criativo no meio dela reinicia o processo e polui o teste.

## Matriz de decisão

| CTR | Conversão | Diagnóstico | Ação |
|-----|-----------|-------------|------|
| Alto | Alta | Vencedor | **Escale.** Duplique verba a cada 3–4 dias, +20–50% por vez |
| Alto | Baixa | Gancho atrai, oferta/página não segura | Mantenha o gancho, ataque página e prova. Cheque coerência anúncio × destino |
| Baixo | Alta | Gancho fraco, oferta forte | Troque só o gancho (hook stacking). Mantenha o corpo |
| Baixo | Baixa | Célula errada | Mate. Troque de célula na mandala |

**CTR alto + conversão baixa** é o caso mais comum e o mais mal diagnosticado: quase sempre
é isca furada (o gancho promete algo que a página não entrega) ou público errado atraído
por um gancho genérico demais.

## Fadiga de criativo

Três sinais **juntos** ao longo de 3–5 dias:

```
frequência subindo  +  CTR caindo  +  CPA subindo
```

Isso é saturação — não é "o criativo ficou ruim". Ações, na ordem:

1. **Trocar o gancho** mantendo o corpo (hook stacking) — resolve boa parte dos casos
2. **Trocar o ângulo** na mesma célula
3. **Trocar de célula** na mandala
4. **Ampliar o público** (se estiver estreito demais, a frequência sobe rápido)
5. **Pausar e reciclar** — criativo saturado costuma voltar a funcionar semanas depois

Vida útil típica em conta pequena: **7 a 21 dias** por criativo de descoberta. Quanto maior
a verba, mais rápido satura.

## Ritmo de reposição

**Regra:** a cada semana, reponha o número de criativos que morreu na semana anterior **+ 1**.

| Verba/dia | Criativos novos/semana | Criativos ativos |
|-----------|------------------------|------------------|
| até R$ 50 | 2–3 | 4–6 |
| R$ 50–200 | 4–6 | 8–12 |
| R$ 200–1.000 | 8–12 | 15–25 |
| R$ 1.000+ | 15+ | 30+ |

Quem não sustenta esse ritmo trava no teto de verba — e é exatamente aí que a mandala
justifica existir.

## Escala sem quebrar

- **Aumente 20–50% por vez**, com 2–3 dias de estabilização entre aumentos. Dobrar verba de
  uma vez costuma reiniciar aprendizado e piorar o CPA.
- **Escale o conjunto vencedor**, não o criativo isolado.
- **Escale horizontalmente também**: mesmo criativo, públicos/campanhas diferentes.
- **Não escale**: quando o CPA já está próximo do máximo (não há folga), quando a conversão
  da página é o gargalo, ou quando não há criativo novo na fila para repor.

## Diagnóstico geral: é criativo mesmo?

Antes de culpar o criativo, siga a ordem:

| Sintoma | Suspeito nº 1 |
|---------|---------------|
| Ninguém clica | Criativo/gancho |
| Clica e sai em 5s da página | Coerência anúncio × destino |
| Lê a página e não vai ao checkout | Prova, mecanismo, promessa |
| Vai ao checkout e não paga | Preço, parcelamento, garantia, fricção |
| Paga e pede reembolso | Promessa exagerada ou entrega ruim |
| **Todos os criativos vão mal em todas as células** | **Conceito** — volte à concepção |

A última linha é a mais importante desta skill: mandala nenhuma salva promessa errada, e
produzir mais criativo sobre um conceito quebrado é a forma mais cara de descobrir isso.

## Painel semanal mínimo

| Criativo (célula) | Gasto | Impr. | CTR | CPC | Conv. | CPA | Freq. | Decisão |
|-------------------|-------|-------|-----|-----|-------|-----|-------|---------|
| desc-pront-probsol-dor-v1 | | | | | | | | escalar / manter / matar |

Preencha toda sexta. O histórico de células mortas é o que impede repetir o mesmo erro no
mês seguinte — e é a informação que mais falta em conta que não escala.
