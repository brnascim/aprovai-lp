# Roadmap de 14 dias — do zero ao primeiro cliente pagante

Ritmo pensado para 2–3 horas por dia. Se tiver menos tempo, estique os prazos — mas
**mantenha a ordem**. Ela existe para você não construir duas semanas antes de descobrir que
ninguém quer.

## Dias 1–2 — Especificar

- [ ] Preencher os 6 blocos de `prd.md`
- [ ] Definir o menor formato que resolve (não pule para "app" por padrão)
- [ ] Escolher as ferramentas e somar o custo mensal
- [ ] Definir preço e calcular o custo variável por usuário

**Entregável:** spec completa. Sem ela, não avance.

## Dias 3–4 — Validar antes de construir

- [ ] Falar com 5 pessoas do público: descrever a ferramenta e perguntar o que fariam
- [ ] Mostrar o preço e observar a reação
- [ ] Perguntar: "o que você faz hoje para resolver isso?"
- [ ] Ajustar a spec com o que ouviu

**Critério:** se 3 de 5 disserem "quando fica pronto?", siga. Se ninguém reagir, mude a
ideia agora — custou 2 dias, não 2 meses.

## Dias 5–8 — Construir o núcleo

- [ ] Dia 5: estrutura + tela principal
- [ ] Dia 6: a funcionalidade que entrega a promessa (só ela)
- [ ] Dia 7: salvar dados + login
- [ ] Dia 8: testar com duas contas (isolamento) e corrigir

**Regra:** uma etapa por vez, testando no navegador antes de avançar. Salve uma cópia toda
vez que algo funcionar.

**Entregável:** dá para fazer, do início ao fim, o que o app promete.

## Dias 9–10 — Testar com gente

- [ ] 3 pessoas do público usam sem você explicar nada
- [ ] Você fica em silêncio e anota onde travam
- [ ] Corrigir os 3 travamentos mais frequentes
- [ ] Rodar o roteiro de teste de `../references/testes-e-erros.md`

**Entregável:** app que um estranho consegue usar sozinho.

## Dias 11–12 — Cobrar

- [ ] Configurar o checkout hospedado
- [ ] Testar assinatura ponta a ponta (aprovado, recusado, cancelamento)
- [ ] Confirmar que o webhook libera o acesso automaticamente
- [ ] Publicar Política de Privacidade e Termos de Uso
- [ ] Configurar limite de uso e alerta de gasto

**Entregável:** alguém consegue pagar e usar sem você no meio.

## Dia 13 — Página de venda

- [ ] Promessa em uma frase (use `produto-digital-concepcao`)
- [ ] O que faz, em 3 blocos
- [ ] Demonstração (vídeo curto de tela ou versão de teste)
- [ ] Preço e planos
- [ ] Garantia de 7 dias
- [ ] Contato e identificação do vendedor

## Dia 14 — Vender

- [ ] Falar com as 5 pessoas dos dias 3–4 (é aqui que sai a primeira venda)
- [ ] Publicar nos canais onde o público está
- [ ] 3 criativos (use `anuncios-estaticos-carrossel`)
- [ ] Meta honesta: **1 cliente pagante**

---

## Checklist final

- [ ] Teste de duas contas: sem vazamento
- [ ] Backup testado
- [ ] Cobrança funcionando
- [ ] Documentos legais publicados
- [ ] Limite de gasto ativo
- [ ] Uma pessoa que não é você já usou e entendeu

## Depois do dia 14

| Semana | Foco |
|--------|------|
| 3–4 | Falar com quem pagou; corrigir o que atrapalha o primeiro uso |
| 5–6 | O recurso mais pedido — só o mais pedido |
| 7–8 | Aquisição: conteúdo, tráfego, parceria |
| 9+ | Só então: novos planos, integrações, escala |

**Não adicione funcionalidade antes de ter 10 clientes pagantes.** Até lá, o que falta é
distribuição, não recurso.
