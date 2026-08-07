# Segurança e limites — o mínimo inegociável

Você não precisa ser especialista. Precisa fazer o básico **antes do primeiro usuário real**
— porque o prejuízo aqui não é técnico, é de confiança e jurídico.

## Os 7 itens obrigatórios

### 1. Isolamento de dados entre usuários
**O erro nº 1 de app gerado por IA.** O código costuma buscar "todos os registros" em vez de
"os registros deste usuário".

Como testar: duas contas, dois navegadores, tente ver os dados da outra — inclusive colando
o link direto.

O que pedir:
```
"Aplique regra de acesso no banco: cada usuário só pode ler e escrever registros onde o
 dono é ele mesmo. Valide isso no servidor, não só na tela. Teste com duas contas."
```

### 2. Chaves e senhas fora do navegador
Qualquer coisa que apareça no código da página é público — inclusive chave de API.

Como verificar: `Ctrl+U` na página e procurar por `key`, `secret`, `token`, `password`.

Correção: variáveis de ambiente no servidor; a chamada à API externa acontece no back-end.
Se uma chave já vazou, **revogue e gere outra** — trocar de lugar não basta.

### 3. Senha guardada com hash
Senha nunca é guardada em texto. Use o sistema de login pronto do backend escolhido em vez
de escrever o seu — é a decisão que mais reduz risco.

### 4. HTTPS
Cadeado no navegador. As plataformas modernas já entregam por padrão; confirme no domínio
próprio.

### 5. Backup + restauração testada
Backup que nunca foi restaurado não é backup.

- Backup automático diário
- **Restaure uma vez**, de verdade, para saber que funciona
- Guarde uma cópia fora da plataforma principal

### 6. Validação no servidor
Validar só na tela não protege nada — dá para burlar. Toda regra crítica (limite de plano,
permissão, cálculo que envolve dinheiro) precisa ser conferida no servidor.

### 7. Limite de uso e alerta de gasto
- Limite por usuário e por plano
- Alerta de gasto nas contas de API e de infra
- Corte automático ao estourar, com aviso claro ao usuário

Sem isso, um usuário (ou um robô) pode gerar uma conta impagável em um fim de semana.

---

## LGPD — o essencial

| Obrigação | Na prática |
|-----------|-----------|
| **Minimização** | Só colete o que o app usa. Não peça CPF "por precaução" |
| **Finalidade** | Diga para que serve cada dado, na política de privacidade |
| **Base legal** | Execução do contrato (o serviço) ou consentimento (marketing) |
| **Consentimento separado** | Aceitar os termos ≠ aceitar receber e-mail promocional |
| **Direito de acesso** | O usuário pode pedir os dados dele |
| **Direito de exclusão** | Conta excluída = dados apagados (prazo declarado) |
| **Segurança** | Medidas razoáveis: acesso restrito, criptografia em trânsito |
| **Incidente** | Vazamento → comunicar titulares e a ANPD |
| **Encarregado** | Um contato responsável, publicado no site |

Documentos mínimos publicados: **Política de Privacidade** e **Termos de Uso**.

### Dados que exigem cuidado extra
Saúde, biometria, dados financeiros de terceiros, origem racial, religião, opinião política,
dados de crianças e adolescentes. Se o app toca nisso e você não domina o assunto,
**contrate ajuda antes de lançar.** Não é conservadorismo: é o cenário em que o erro custa
mais caro.

---

## O que NÃO fazer sem ajuda profissional

| Situação | Por quê |
|----------|---------|
| Guardar dado de cartão | PCI-DSS. Use checkout hospedado, sempre |
| Prontuário, exame, dado de saúde | Dado sensível + regras do setor |
| Movimentar dinheiro de terceiros | Regulação do Banco Central |
| Dados de menores de idade | Regime especial da LGPD + ECA |
| Assinatura digital com valor legal | ICP-Brasil |
| Integrar com sistema de governo | Requisitos técnicos e responsabilidade |

Nesses casos, o caminho é: construa o resto com IA, contrate um profissional para a parte
regulada.

---

## Limites honestos do "sem programar"

Diga isso ao usuário quando for o caso — é mais útil que otimismo:

**Funciona bem:**
- Ferramentas de cálculo, formulário, geração de documento
- CRUD (cadastrar, listar, editar, apagar) com login
- Dashboards e relatórios
- Automação entre serviços
- MVP para validar antes de investir
- Ferramenta interna de um negócio pequeno

**Funciona com esforço:**
- Assinatura com vários planos e regras
- Integração com API de terceiro sem conector pronto
- Multi-usuário com papéis e permissões variadas
- Volume de dados grande

**Precisa de programador:**
- App nativo com recursos do aparelho
- Tempo real com muitos usuários simultâneos
- Regra de negócio complexa e crítica (cálculo fiscal, folha, financeiro regulado)
- Escala com milhares de usuários pagantes
- Qualquer coisa em setor regulado

---

## Checklist final — antes do primeiro usuário real

- [ ] Teste de duas contas: nenhum vazamento entre usuários
- [ ] Nenhuma chave, senha ou token no código do navegador
- [ ] Login com sistema pronto, senha com hash
- [ ] HTTPS ativo
- [ ] Backup automático + **restauração testada uma vez**
- [ ] Validação no servidor das regras que envolvem dinheiro e permissão
- [ ] Limite de uso + alerta de gasto configurados
- [ ] Política de Privacidade e Termos publicados
- [ ] Canal de contato visível
- [ ] Exclusão de conta apaga os dados
- [ ] Cobrança testada ponta a ponta, incluindo cancelamento
- [ ] Você consegue explicar, em uma frase, o que o app faz com os dados do cliente

O último item é o melhor teste de todos. Se você não consegue explicar, ainda não está
pronto para receber dados de outra pessoa.
