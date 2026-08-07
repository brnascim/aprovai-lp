# A especificação que a IA consegue executar

A diferença entre quem constrói e quem desiste não é técnica — é **precisão do pedido**.

```
❌ "Faz um app de gestão financeira pra confeiteira"
   → app genérico, com 40 telas que ninguém pediu e nenhuma que resolve

✅ "Uma página onde a confeiteira cadastra os ingredientes com preço e rendimento,
    monta uma receita escolhendo ingredientes e quantidades, informa quantas horas
    levou, e recebe o preço de venda sugerido com a margem que ela escolher.
    Sem login. Os dados ficam no navegador dela."
   → funciona na primeira tentativa
```

## Os 6 blocos

### 1. Uma frase
`[Público] usa [nome] para [resultado observável].`

> "Confeiteira que vende pelo WhatsApp usa a Calculadora de Bolo para descobrir o preço
> certo de cada receita."

Se você não consegue escrever esta frase, o problema não é o app.

### 2. Usuários e permissões
Quem entra e o que cada um pode fazer. Mesmo com um só tipo, escreva:

```
Visitante  — vê a página inicial e a demonstração
Cliente    — cria, edita e apaga as próprias receitas; exporta em PDF
Admin (eu) — vê a lista de clientes e o status de assinatura
```

**A regra de ouro:** "cada usuário só enxerga os próprios dados". Escreva isso na spec —
é o erro de segurança nº 1 de app gerado por IA, e ele só é evitado quando é pedido.

### 3. Telas
Liste cada tela e o que aparece nela. Não descreva design; descreva **conteúdo e ações**.

```
/ (início)     — explicação em 3 linhas, botão "Começar"
/ingredientes  — tabela (nome, preço, unidade, rendimento) + botão "Adicionar"
/receita       — escolher ingredientes, quantidade, horas; mostra custo e preço sugerido
/receitas      — lista das receitas salvas, com ação de abrir e apagar
/assinar       — planos e botão de pagamento
```

### 4. Dados
Que informações são guardadas, com que campos, e por quanto tempo.

```
Ingrediente: nome (texto), preço (número), unidade (kg/l/un), rendimento (número)
Receita: nome, lista de ingredientes com quantidade, horas, margem desejada
Usuário: e-mail, senha (nunca em texto puro), plano, data de assinatura

Guardar enquanto a conta existir. Excluir tudo em até 30 dias após o cancelamento.
```

Esse bloco é o que resolve LGPD e evita o app que guarda coisa demais "por precaução".

### 5. Regras
O comportamento nas bordas — onde a maioria dos apps gerados por IA falha.

```
- Preço sugerido = (custo dos ingredientes + horas × valor da hora) ÷ (1 − margem)
- Margem entre 0% e 90%; fora disso, mostrar aviso e não calcular
- Ingrediente sem preço não entra no cálculo — destacar em vermelho na lista
- Plano gratuito: até 3 receitas salvas; ao tentar a 4ª, oferecer o plano pago
- Se a conexão cair ao salvar, avisar e manter o formulário preenchido
- Nada é apagado sem confirmação
```

Regra prática: **para cada ação, escreva o que acontece quando dá errado.** É isso que
separa protótipo de produto.

### 6. Fora do escopo
O bloco mais importante e o mais esquecido.

```
NÃO faz nesta versão:
- controle de estoque
- emissão de nota fiscal
- app para celular nas lojas (é site que abre no celular)
- integração com WhatsApp
- múltiplos usuários por conta
```

Sem este bloco, a IA inventa funcionalidade, o projeto incha e nada fica pronto.

## Como pedir para a IA construir

**Uma tela por vez.** Sequência que funciona:

```
1. "Crie a estrutura do projeto e a tela inicial conforme a spec abaixo: [spec]"
2. "Agora a tela /ingredientes, só ela, seguindo os dados definidos"
3. "Agora o cálculo do preço, com as regras 1 a 3"
4. "Agora salvar no navegador"
5. "Agora login e cada usuário vendo só os próprios dados"
6. "Agora a cobrança"
```

Pedir tudo de uma vez gera um resultado grande, quebrado e impossível de depurar — inclusive
pela própria IA.

**Depois de cada etapa:** teste no navegador, e só avance quando funcionar. Se quebrou,
volte para o último ponto que funcionava em vez de empilhar correção sobre correção.

## Vocabulário útil (o mínimo)

| Palavra | O que é, em português |
|---------|-----------------------|
| **Front-end** | O que o usuário vê e clica |
| **Back-end** | O que roda no servidor: guarda dados, faz contas, controla acesso |
| **Banco de dados** | Onde as informações ficam guardadas |
| **API** | O jeito de dois sistemas conversarem |
| **Autenticação** | Login: provar quem é você |
| **Autorização** | Permissão: o que você pode fazer depois de logado |
| **Deploy** | Publicar para o mundo acessar |
| **Ambiente** | Cópia do sistema: teste (você) × produção (clientes) |
| **Variável de ambiente** | Onde ficam senhas e chaves, fora do código |
| **Webhook** | Um sistema avisando o outro que algo aconteceu (ex.: pagamento aprovado) |

Você não precisa saber programar, mas precisa saber **nomear** — é assim que se pede a coisa
certa e se entende a resposta.

## Erros de spec que custam caro

| Erro | Consequência | Correção |
|------|--------------|----------|
| Descrever design em vez de comportamento | App bonito que não faz nada | Descreva ações e regras |
| Esquecer o "fora do escopo" | Projeto que nunca termina | Liste 5 não-fazeres |
| Não definir permissões | Usuário vendo dado de outro | "cada um só vê o próprio" |
| Não definir erro | App trava sem explicar | O que acontece quando falha |
| Pedir tudo de uma vez | Código impossível de depurar | Uma tela por vez |
| Copiar spec de outro produto | Ferramenta que não resolve a sua dor | Parta da dor real do seu público |
