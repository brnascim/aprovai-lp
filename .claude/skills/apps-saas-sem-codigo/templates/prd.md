# Especificação — [NOME DO APP]

> Este documento é o que você entrega para a IA construir. Preencha os 6 blocos antes de
> pedir qualquer código. Bloco vazio = funcionalidade inventada depois.

**Versão:** 1 · **Data:** [ ] · **Formato escolhido:** ( ) calculadora ( ) gerador
( ) app com login ( ) SaaS

---

## 1. Uma frase

> **[Público] usa [nome] para [resultado observável].**

**Problema que resolve:**
**Como é resolvido hoje:**
**Por que o jeito atual é ruim:**

---

## 2. Usuários e permissões

| Usuário | Pode | Não pode |
|---------|------|----------|
| Visitante | | |
| Cliente | | |
| Admin | | |

> **Regra obrigatória:** cada usuário só lê e escreve os próprios dados. Validado no
> servidor, não só na tela.

---

## 3. Telas

| Rota | O que aparece | Ações disponíveis |
|------|---------------|-------------------|
| `/` | | |
| `/` | | |
| `/` | | |

---

## 4. Dados

| Entidade | Campos | Retenção |
|----------|--------|----------|
| | | |
| | | |

**Dado sensível envolvido?** ( ) não ( ) sim → qual: __________
*(se sim, leia `../references/seguranca-e-limites.md` antes de continuar)*

---

## 5. Regras

**Cálculos e lógica**
-

**Limites por plano**
-

**O que acontece quando dá errado**
| Situação | Comportamento esperado |
|----------|------------------------|
| Campo obrigatório vazio | |
| Valor fora do intervalo | |
| Conexão cai ao salvar | |
| Sessão expirada | |
| Limite do plano atingido | |

---

## 6. Fora do escopo (nesta versão)

- [ ] NÃO faz:
- [ ] NÃO faz:
- [ ] NÃO faz:
- [ ] NÃO faz:
- [ ] NÃO faz:

---

## Construção

| Camada | Ferramenta escolhida | Custo/mês |
|--------|----------------------|-----------|
| Interface e lógica | | |
| Dados e login | | |
| Pagamento | | |
| Automação | | |
| Publicação | | |
| **Total** | | **R$** |

**Ordem de construção (uma etapa por vez):**
1.
2.
3.
4.
5.

---

## Monetização

- **Modelo:**
- **Preço:** R$ ___/mês (básico) · R$ ___/mês (pro)
- **Custo variável por usuário:** R$ ___
- **Margem por usuário:** R$ ___
- **Limite de uso por plano:**
- **Como o preço foi validado:**

---

## Segurança — antes do primeiro usuário

- [ ] Teste de duas contas passou (nenhum vazamento)
- [ ] Nenhuma chave no navegador
- [ ] HTTPS
- [ ] Backup automático + restauração testada
- [ ] Validação no servidor
- [ ] Limite de uso e alerta de gasto
- [ ] Política de Privacidade e Termos publicados
- [ ] Exclusão de conta apaga os dados

---

## Quando chamar um programador

Gatilhos específicos deste projeto:
-
-
