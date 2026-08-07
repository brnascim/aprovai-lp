# Monetização de app e micro-SaaS

## Modelos

| Modelo | Como funciona | Bom para | Cuidado |
|--------|---------------|----------|---------|
| **Assinatura mensal** | R$ X/mês, acesso contínuo | Ferramenta de uso recorrente | Churn: precisa de valor todo mês |
| **Assinatura anual** | 2 meses de desconto, pago à vista | Caixa antecipado, menos churn | Reembolso proporcional se cancelar |
| **Por uso** | Paga pelo que consome | App com custo variável (IA, envio) | Cliente odeia surpresa — mostre o consumo |
| **Licença vitalícia** | Paga uma vez, usa sempre | Ferramenta simples e estável | Custo de infra é eterno; **precifique alto** |
| **Freemium** | Grátis limitado, pago libera | Produto com efeito de boca a boca | Grátis custa dinheiro; limite bem |
| **Teste grátis** | 7–14 dias completos, depois cobra | Ferramenta que precisa ser experimentada | Peça cartão só se o valor já ficou claro |
| **Serviço + ferramenta** | Consultoria com a ferramenta junto | Início sem escala | Ticket maior, cliente mais exigente |

**Recomendação para o primeiro produto:** assinatura mensal simples, um ou dois planos.
Preço complexo em produto novo confunde e derruba conversão.

## Preço

### Regra de partida
```
preço mínimo = custo variável por usuário × 5
```
Menos que isso, não sobra para tráfego, suporte e imprevisto.

### Ancoragem
Ferramenta se precifica pelo que **substitui**:

- Substitui 3h/mês de trabalho? A hora dele × 3 é o teto confortável.
- Substitui uma ferramenta de R$ 200/mês? Posicione em R$ 49–97.
- Substitui uma planilha manual? A âncora é o erro que ela evita, não a planilha.

### Faixas praticadas (Brasil, ferramenta de nicho)

| Público | Faixa mensal |
|---------|--------------|
| Pessoa física / hobby | R$ 9–29 |
| Profissional autônomo | R$ 29–97 |
| Pequeno negócio | R$ 97–297 |
| Empresa com equipe | R$ 297–997 |

**Cobre mais caro do que seu instinto manda.** Ferramenta barata demais atrai o cliente que
mais dá suporte e mais cancela.

### Dois planos, não cinco
```
Básico   R$ 49/mês  — o essencial, limite de uso definido
Pro      R$ 97/mês  — sem limite prático + o recurso que os melhores clientes pedem
```
Se precisar de um terceiro, seja "Sob consulta" para empresa.

## Custo variável — a conta que mais mata micro-SaaS

```
custo por usuário/mês =
    infra (hospedagem + banco) ÷ nº de usuários
  + custo de IA por usuário  ← o item que sai do controle
  + taxa do gateway
  + suporte (seu tempo × valor da hora ÷ nº de usuários)
```

Se o app chama um modelo de linguagem, meça o custo médio por operação e multiplique pelo
uso esperado do plano. Defesas obrigatórias:

- **Limite por plano** (ex.: 50 gerações/mês no básico)
- **Cache** de respostas repetidas
- **Modelo menor** onde a tarefa é simples
- **Alerta de gasto** na conta da API desde o primeiro dia
- **Corte automático** ao estourar o limite, com aviso ao usuário

Assinatura "ilimitada" com custo de IA por uso é a forma mais rápida de escalar prejuízo.

## Cobrança na prática

**Use checkout hospedado.** O cliente paga numa página do gateway; você nunca guarda dado de
cartão. Isso tira do seu colo a maior parte da responsabilidade de segurança.

Fluxo mínimo:
```
1. Cliente clica em Assinar
2. Vai para o checkout do gateway
3. Paga
4. O gateway avisa seu app (webhook) que o pagamento foi aprovado
5. Seu app libera o acesso
6. Todo mês o gateway cobra e avisa; falhou, o app bloqueia após o prazo de tolerância
```

Pontos que costumam quebrar:
- **Webhook não configurado** → cliente paga e não recebe acesso (o pior erro possível)
- **Sem tolerância para falha de cartão** → bloqueia cliente bom por cartão vencido; dê 3–7 dias
- **Cancelamento manual** → dê botão de cancelar; obrigar a mandar e-mail gera reclamação e chargeback
- **Sem ambiente de teste** → sempre teste no modo sandbox antes de abrir

## Jurídico e fiscal (Brasil)

- **Emitir nota fiscal** de serviço para cada cobrança — obrigação, não opção
- **CNPJ**: MEI pode não cobrir a atividade de software; verifique o CNAE antes
- **Impostos**: no Simples, a faixa de software costuma ficar em torno de 6% inicial —
  confirme com contador; entre no cálculo de preço desde o começo
- **CDC art. 49**: 7 dias de arrependimento em compra online, inclusive assinatura
- **Cancelamento**: tem que ser tão fácil quanto assinar
- **Reembolso**: defina a política e escreva na página; cumpra sem atrito
- **LGPD**: política de privacidade, base legal, direito de exclusão, contato do responsável
- **Termos de uso**: o que o serviço faz, o que não garante, limites de responsabilidade

## Como validar o preço antes de construir

1. **Pré-venda**: página descrevendo a ferramenta com data de entrega + checkout real.
   3 pagamentos = sinal verde. Entregue no prazo.
2. **Serviço primeiro**: entregue o resultado manualmente por R$ X. Se pagam pelo resultado,
   pagam pela ferramenta que o entrega — e você descobre as regras de negócio reais.
3. **Lista de espera com preço**: informe o preço na captura. Quem sai ao ver o preço já
   respondeu.

Nunca construa 3 meses para depois descobrir o preço. **O preço é parte da spec.**

## Métricas do primeiro ano

| Métrica | O que é | Referência inicial |
|---------|---------|--------------------|
| MRR | Receita recorrente mensal | a que importa |
| Churn | % que cancela por mês | < 5% é saudável; > 10% é problema de produto |
| LTV | Receita total por cliente | ticket ÷ churn |
| CAC | Custo para adquirir um cliente | precisa ser < ⅓ do LTV |
| Ativação | % que usa de verdade na 1ª semana | abaixo de 40%, o onboarding está ruim |

Churn alto quase nunca é preço: é o cliente não conseguir extrair valor na primeira semana.
Antes de baixar o preço, conserte o primeiro uso.
