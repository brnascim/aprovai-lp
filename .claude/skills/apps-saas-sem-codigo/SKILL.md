---
name: apps-saas-sem-codigo
description: >
  Guia quem NÃO SABE PROGRAMAR a transformar uma ideia em aplicativo, ferramenta ou
  micro-SaaS funcionando e vendável — escrevendo a especificação certa e deixando a IA
  construir. Use SEMPRE que o usuário disser "quero criar um app", "não sei programar
  mas quero", "criar um SaaS", "micro-SaaS", "ferramenta para o meu nicho",
  "calculadora online", "sistema para meus clientes", "transformar minha planilha em
  app", "criar um aplicativo com IA", "no-code", "low-code", "Lovable", "Bolt", "v0",
  "Replit", "Supabase", "vibe coding", "quanto custa fazer um app", "como cobro
  assinatura", "MVP", "validar meu app" ou pedir para virar produto uma ferramenta que
  ele já usa no Excel. Use também quando a skill produto-digital-ideias tiver apontado
  formato "ferramenta/SaaS". Esta skill cobre da especificação ao lançamento, incluindo
  cobrança, limites e o que fazer quando a IA trava. Para arquitetura e implementação
  avançada com stack completa, encaminhe para a skill fullstack-saas-pwa.
---

# Apps e SaaS sem saber programar

Hoje, a barreira para construir software não é sintaxe — é **especificação**. Quem descreve
com precisão o que quer, consegue. Quem pede "faz um app de gestão" recebe um app genérico
que não serve para ninguém.

Esta skill entrega duas coisas: a **especificação que a IA consegue executar** e o **caminho
até o produto vendido**, incluindo cobrança, limites, suporte e o momento certo de chamar um
programador humano.

Regra que organiza tudo: **software é a parte fácil; usuário pagante é a parte difícil.**
Se a ferramenta não resolve uma dor específica de um público específico, ela não vira produto
— vira portfólio.

## Entrada esperada

1. **O problema** e quem tem esse problema (público específico)
2. **Como é resolvido hoje** — planilha, papel, WhatsApp, ferramenta cara
3. **O resultado observável** que o app entrega
4. **Quem paga** e quanto pagaria
5. **Restrições:** prazo, dinheiro, dados sensíveis envolvidos

Vindo de `produto-digital-ideias`/`produto-digital-concepcao`, isso já está pronto. Sem isso,
colete antes de escrever qualquer linha de spec — app sem público é o erro mais caro aqui.

## Fluxo

### 1. Escolher o menor formato que resolve

Antes de "app", verifique se algo mais simples entrega o mesmo resultado:

| Se o problema é… | Comece por |
|------------------|------------|
| Cálculo ou decisão pontual | **Calculadora/página única** — 1 dia |
| Preencher e gerar documento | **Gerador de documento** — 2 dias |
| Organizar dados de clientes | **Planilha bem feita + automação** — 2 dias |
| Acompanhar processo com várias pessoas | **App com login** — 1–3 semanas |
| Serviço contínuo com cobrança recorrente | **SaaS** — 3–8 semanas |

**Sério: comece pelo menor.** Uma calculadora que resolve e vende hoje vale mais que um SaaS
completo em três meses. E ela vira a isca do SaaS depois.

### 2. Escrever a especificação (a etapa que decide tudo)

`references/spec-primeiro.md` traz o modelo completo e a diferença entre pedido vago e spec
executável. O template está em `templates/prd.md`. A spec mínima tem seis blocos:

```
1. Uma frase       — o que o app faz, para quem
2. Usuários        — quem entra e o que cada um pode fazer
3. Telas           — lista, com o que aparece em cada uma
4. Dados           — que informações são guardadas, e por quanto tempo
5. Regras          — o que pode, o que não pode, o que acontece quando dá erro
6. Fora do escopo  — o que NÃO faz (o bloco mais importante e o mais esquecido)
```

O bloco 6 é o que impede a IA de inventar funcionalidade e o projeto de crescer sem parar.

### 3. Construir

`references/ferramentas.md` compara os caminhos (geradores de app por IA, plataformas
no-code, backend pronto, Claude Code) com custo, teto de complexidade e o momento em que
cada um trava.

Recomendação padrão para quem não programa:

```
Interface + lógica    →  gerador de app por IA (descrição em português)
Banco de dados/login  →  backend pronto (Supabase ou equivalente)
Pagamento             →  Stripe ou plataforma nacional com checkout hospedado
Automação/integração  →  n8n, Make ou Zapier
```

Trabalhe **em iterações pequenas**: uma tela por vez, testando. Pedir o app inteiro de uma
vez produz um resultado que ninguém consegue depurar — inclusive a IA.

### 4. Testar como usuário, não como criador

`references/testes-e-erros.md` traz o roteiro de teste para quem não programa (o que
clicar, o que tentar quebrar) e o **protocolo de quando a IA trava**: como descrever o erro,
como voltar atrás, e o sinal de que chegou a hora de chamar um humano.

### 5. Cobrar

`references/monetizacao-e-billing.md` cobre modelos (assinatura, uso, licença vitalícia,
freemium), precificação de ferramenta, teste grátis vs. demonstração, e o essencial jurídico
brasileiro: nota fiscal, CDC, cancelamento, reembolso.

Regra: **o preço tem que cobrir o custo variável por usuário desde o primeiro dia.** Muita
ferramenta indie quebra porque o custo de infra e de IA por usuário passou do preço da
assinatura.

### 6. Segurança e limites — obrigatório, não opcional

`references/seguranca-e-limites.md`. O mínimo inegociável antes de qualquer usuário real:

- Login funcionando e **cada usuário só enxerga os próprios dados** (o erro nº 1 de app
  gerado por IA)
- Nenhuma chave, senha ou token no código do navegador
- HTTPS, backup automático e um jeito de restaurar
- LGPD: só coletar o necessário, dizer para que serve, permitir exclusão
- Dado sensível (saúde, financeiro, menor de idade) → padrão de cuidado mais alto; se o
  usuário não domina isso, **contrate ajuda**

## Saída

```markdown
## Decisão de formato
[calculadora / gerador / app / SaaS] porque [...]

## Especificação
*(templates/prd.md preenchido — 6 blocos)*

## Caminho de construção
| Etapa | Ferramenta | Prazo | Custo/mês |

## Roadmap de 14 dias
*(templates/roadmap-14-dias.md)*

## Monetização
Modelo · preço · custo variável por usuário · margem · o que valida o preço

## Checklist de segurança
*(references/seguranca-e-limites.md — antes do primeiro usuário real)*

## Quando chamar um programador
[os gatilhos específicos deste projeto]
```

## Regras

- **Spec antes de prompt.** Nunca comece a construir sem os 6 blocos preenchidos.
- **Menor escopo que resolve.** Cada funcionalidade a mais atrasa o lançamento e aumenta a
  chance de a IA travar.
- **Uma coisa por vez.** Uma tela, um teste, um ajuste.
- **Nada de dado sensível sem preparo.** Saúde, financeiro e dados de menores exigem
  cuidado que vai além do que se resolve com prompt.
- **Não prometa o que o app não faz.** A landing precisa descrever o produto real —
  `../produto-digital-concepcao/references/compliance-promessas-br.md` vale aqui também.
- **Custo antes de escala.** Calcule o custo por usuário (infra + IA + gateway) antes de
  abrir venda. É a conta que mais mata micro-SaaS.
- **Seja honesto sobre o limite.** Quando o projeto ultrapassa o que dá para fazer sem
  programar, diga — e diga o que exatamente exige um humano.

## Referências

| Arquivo | Quando ler |
|---------|-----------|
| `references/spec-primeiro.md` | Etapa 2 — como escrever a spec que a IA executa |
| `references/ferramentas.md` | Etapa 3 — caminhos, custos e onde cada um trava |
| `references/testes-e-erros.md` | Etapa 4 — testar sem saber programar; IA travada |
| `references/monetizacao-e-billing.md` | Etapa 5 — modelos, preço, custo por usuário, jurídico |
| `references/seguranca-e-limites.md` | Etapa 6 — obrigatório antes do primeiro usuário |

## Handoff

- **Arquitetura, stack e implementação avançada** → skill `fullstack-saas-pwa`
- **Promessa, público e preço do produto** → `produto-digital-concepcao`
- **Anúncios para vender a ferramenta** → `anuncios-estaticos-carrossel` e
  `mandala-anuncios-reels`
- **A ferramenta como isca** de um produto maior → `produto-digital-ideias` (lente 7)
