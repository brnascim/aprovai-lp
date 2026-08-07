# Testar sem saber programar (e o que fazer quando a IA trava)

## Como testar

Você não precisa saber ler código. Precisa **usar o app como o pior usuário possível**.

### Roteiro de teste — 20 minutos, antes de qualquer cliente

**Caminho feliz**
- [ ] Fazer o que o app promete, do início ao fim, como um cliente faria
- [ ] Refazer no celular
- [ ] Fechar o navegador no meio e voltar: o que estava salvo continua lá?

**Caminho torto (onde tudo quebra)**
- [ ] Enviar formulário vazio
- [ ] Digitar texto onde se espera número; número negativo; número gigante
- [ ] Clicar duas vezes rápido no botão de salvar (duplicou?)
- [ ] Apertar "voltar" do navegador no meio do fluxo
- [ ] Colar um texto enorme num campo pequeno
- [ ] Usar acento, emoji e aspas nos campos de texto
- [ ] Deixar aberto 30 minutos e tentar salvar (a sessão expirou sem avisar?)

**Permissões (o teste mais importante)**
- [ ] Criar duas contas diferentes, em dois navegadores
- [ ] Cadastrar dados na conta A
- [ ] Na conta B, **tentar** ver os dados de A — inclusive colando o link direto de A
- [ ] Deslogar e colar o link direto: pede login?

Se a conta B enxergar qualquer coisa da conta A, **pare tudo e conserte antes de qualquer
usuário real.** É a falha mais comum de app gerado por IA e a mais grave.

**Pagamento**
- [ ] Assinar de verdade (use o modo de teste do gateway)
- [ ] O acesso liberou automaticamente?
- [ ] Cancelar: o acesso é revogado quando deve?
- [ ] Cartão recusado: a mensagem faz sentido?

**Dados**
- [ ] Existe backup? Você sabe restaurar?
- [ ] Excluir a conta apaga mesmo os dados?

### Teste com gente de verdade
Antes de vender, coloque **3 pessoas do público** para usar sem você explicar nada. Fique em
silêncio e anote onde travam. Cada travamento é uma correção — e as palavras que elas usam
viram a copy da landing.

## Quando a IA trava

Acontece com todo mundo. O que separa quem resolve de quem desiste é o **protocolo**.

### 1. Descreva o erro direito

```
❌ "não tá funcionando"
❌ "deu erro"

✅ "Quando clico em 'Salvar receita' na tela /receita, a página fica carregando e nada
    acontece. No console aparece: 'TypeError: Cannot read properties of undefined
    (reading map)'. Funcionava até eu pedir o campo de margem. Esperado: salvar e
    voltar para a lista."
```

Modelo: **onde clicou → o que aconteceu → mensagem de erro → o que funcionava antes → o que
esperava.**

Para achar a mensagem: `F12` no navegador → aba **Console** → copie o texto em vermelho.

### 2. Não empilhe correção

Se três tentativas não resolveram, **volte ao último ponto que funcionava** em vez de pedir
mais uma correção. Cada camada de conserto sobre código quebrado torna o problema mais
difícil — para você e para a IA.

Por isso: **salve versões**. Toda vez que algo funciona, guarde uma cópia (o próprio
histórico da plataforma, ou uma pasta datada). É o seu botão de desfazer.

### 3. Isole o problema

```
"Ignora o resto do app. Escreve só uma página que faz [X], sem login e sem banco de dados,
 só para eu ver se essa parte funciona."
```

Funcionou isolado? O problema está na integração. Não funcionou? O problema está na lógica.
Essa separação resolve a maioria dos travamentos.

### 4. Peça explicação em português

```
"Explica em português, sem termo técnico, o que esse trecho faz e por que ele quebra
 quando o campo de margem está vazio."
```

Entender o mecanismo permite pedir a correção certa — e é assim que você aprende sem curso.

### 5. Sinais de que é hora de um humano

- O mesmo erro há **mais de 2 dias**
- A IA "conserta" e quebra outra coisa, em ciclo
- Você não consegue explicar o que o app faz com os dados dos clientes
- Envolve dinheiro de terceiros ou dado sensível
- Você já tem clientes pagantes e o problema afeta o serviço

## Erros mais comuns em app gerado por IA

| Erro | Como perceber | O que pedir |
|------|---------------|-------------|
| **Dados de um usuário aparecendo para outro** | Teste de duas contas | "Aplique regra de acesso por linha: cada usuário só lê e escreve os próprios registros" |
| **Chave de API no navegador** | Aparece no código da página | "Mova a chave para variável de ambiente e chame a API pelo servidor" |
| **Sem validação** | Aceita texto onde é número | "Valide todos os campos no servidor, não só na tela" |
| **Perde dados ao recarregar** | Some ao dar F5 | "Salve no banco, não só na memória da página" |
| **Sem tratamento de erro** | Tela branca | "Mostre mensagem clara ao usuário em qualquer falha" |
| **Não funciona no celular** | Layout quebrado | "Torne responsivo; teste em tela de 375px" |
| **Envia e-mail para o endereço de teste** | Cliente não recebe | Confira as variáveis de ambiente de produção |
| **Sem limite de uso** | Conta de API explode | "Adicione limite por usuário e por plano" |

## Antes de abrir para o público

- [ ] Teste de duas contas passou
- [ ] Nenhuma chave/senha no código do navegador
- [ ] HTTPS ativo
- [ ] Backup automático + restauração testada **uma vez**
- [ ] Mensagem de erro amigável em todas as falhas
- [ ] Funciona no celular
- [ ] Política de privacidade e termos publicados
- [ ] Canal de contato visível
- [ ] Cobrança testada ponta a ponta, incluindo cancelamento
- [ ] Limite de uso configurado (se houver custo variável)
- [ ] Alerta de gasto ativo nas contas de API
