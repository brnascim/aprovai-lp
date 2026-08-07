# Caminhos de construção — o que usar e onde cada um trava

> O mercado de ferramentas muda rápido. Nomes específicos são exemplos das **categorias**;
> antes de decidir, confirme preço e limites na página oficial de cada uma.

## As 4 categorias

### 1. Gerador de app por IA (descrição em português)
*Exemplos: Lovable, Bolt, v0, Replit Agent*

| | |
|---|---|
| **Como funciona** | Você descreve, ele gera o app inteiro e publica |
| **Custo** | Faixa de US$ 20–50/mês nos planos de entrada |
| **Bom para** | Interface, telas, protótipo, MVP, app pequeno completo |
| **Trava quando** | A lógica fica complexa, o app cresce, o erro se repete em ciclo |
| **Cuidado** | Costuma gerar código com falha de permissão — **peça e teste isolamento de dados** |

**Recomendado para começar.** Do zero a algo funcionando em horas.

### 2. Plataforma no-code visual
*Exemplos: Bubble, FlutterFlow, Softr, Glide*

| | |
|---|---|
| **Como funciona** | Você monta arrastando componentes e configurando lógica |
| **Custo** | US$ 25–100/mês, sobe com uso |
| **Bom para** | App com regras e telas bem definidas; quem prefere clicar a descrever |
| **Trava quando** | Precisa de algo fora do que a plataforma prevê |
| **Cuidado** | Migrar para fora depois é caro — você fica preso à plataforma |

### 3. Backend pronto
*Exemplos: Supabase, Firebase, Xano, Airtable*

| | |
|---|---|
| **Como funciona** | Banco de dados, login e API prontos; você conecta na interface |
| **Custo** | Camada gratuita generosa; US$ 25/mês nos planos pagos iniciais |
| **Bom para** | A parte que a IA erra mais: guardar dados com segurança e controlar acesso |
| **Trava quando** | O volume cresce muito (aí é bom — significa que deu certo) |
| **Cuidado** | Configure as regras de acesso por linha; o padrão pode deixar tudo aberto |

**Combine com a categoria 1.** Interface pela IA + dados aqui é a dupla mais confiável.

### 4. Claude Code / assistente no seu computador
| | |
|---|---|
| **Como funciona** | A IA escreve e roda o código no seu projeto, com você conversando |
| **Custo** | Assinatura do assistente |
| **Bom para** | Controle total, código seu, projeto que vai crescer, sem prisão de plataforma |
| **Trava quando** | Exige entender minimamente o que está acontecendo |
| **Cuidado** | Você é responsável por publicar, fazer backup e manter |

**Melhor custo-benefício a médio prazo** — o código é seu e migra para onde quiser.

## Complementos

| Necessidade | Opções | Observação |
|-------------|--------|-----------|
| **Pagamento** | Stripe · plataformas nacionais de checkout | Use checkout **hospedado**: você não guarda cartão |
| **Assinatura recorrente** | Stripe Billing · gateways nacionais | Confira taxa por transação **e** por parcelamento |
| **Automação** | n8n (pode ser auto-hospedado) · Make · Zapier | Resolve integração sem código |
| **E-mail transacional** | Resend · SendGrid · Brevo | Não envie e-mail em massa pelo mesmo canal |
| **Publicar** | Vercel · Netlify · Railway | Camada gratuita atende os primeiros usuários |
| **Domínio** | Registro.br (.com.br) · registradores internacionais | ~R$ 40/ano |
| **Recurso de IA dentro do app** | API do modelo | **Cuidado com o custo variável** — veja abaixo |

## Combinação recomendada (quem não programa)

```
Interface + lógica    →  gerador de app por IA
Dados + login         →  backend pronto
Pagamento             →  checkout hospedado
Automação             →  n8n / Make
Publicação            →  a própria plataforma do gerador, ou Vercel
```

Custo típico para começar: **US$ 20–70/mês** + domínio. Cabe no bolso antes do primeiro
cliente — e já deve ser coberto pelos primeiros 3 a 5 assinantes.

## Custo por usuário — a conta que quebra micro-SaaS

Antes de abrir venda, calcule:

```
custo por usuário/mês =
    infra (hospedagem + banco) ÷ nº de usuários
  + custo de IA por usuário (se o app usa modelo de linguagem)
  + taxa do gateway por cobrança
  + suporte (seu tempo × valor da sua hora ÷ nº de usuários)
```

Se o app chama um modelo de IA a cada uso, **esse é o item que sai do controle**. Defesas:

- **Limite de uso por plano** (ex.: 50 gerações/mês no plano básico)
- **Cache** de respostas repetidas
- **Modelo menor** para tarefas simples
- **Alerta de gasto** na conta da API, desde o primeiro dia

Ferramenta com IA e assinatura ilimitada de R$ 29 é o caminho mais rápido para faturar e
perder dinheiro ao mesmo tempo.

## Quando chamar um programador

Não é fracasso — é economia. Chame quando:

1. O app lida com **dado sensível** (saúde, financeiro de terceiros, dados de menores)
2. Você precisa de **integração com sistema externo** que não tem conector pronto
3. O mesmo erro **se repete há dias** sem sair do lugar
4. Passou de **~100 usuários pagantes** — vale profissionalizar
5. Precisa de **app nativo de verdade** nas lojas, com recursos do aparelho
6. Você não consegue **explicar o que o sistema faz** com os dados dos clientes

Como contratar bem: leve a **spec pronta** (o documento dos 6 blocos), peça orçamento por
escopo definido, e exija que o código fique com você (repositório no seu nome).

## Armadilhas comuns

| Armadilha | Consequência |
|-----------|--------------|
| Escolher a plataforma antes da spec | Refazer tudo quando descobre o limite |
| Ficar preso a uma plataforma cara | Migração dolorosa quando o preço sobe |
| Construir 6 meses sem mostrar a ninguém | Produto que ninguém quer |
| Ignorar o custo por usuário | Escala vira prejuízo |
| Não fazer backup | Um erro apaga o trabalho de meses |
| Guardar chave de API no navegador | Terceiros gastando na sua conta |
| Não ler o preço além do plano de entrada | Conta multiplicada quando o app cresce |
