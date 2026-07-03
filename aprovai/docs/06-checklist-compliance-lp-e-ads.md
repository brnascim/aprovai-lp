# Checklist de compliance - LP, legais e Meta Ads

Objetivo: concentrar o que pode ir ao ar no Aprovai sem reabrir risco de CDC, LGPD ou reprovação de mídia.

Status desta revisão: 3 de julho de 2026.

Leitura operacional desta data:

- as URLs públicas `https://www.mentoriaaprovai.com.br/`, `/privacidade.html`, `/termos.html` e `/reembolso.html` estão no ar, mas ainda servem a versão antiga da copy;
- o `web/index.html` local foi revisado para reduzir risco de escassez falsa, promessa de entrega imediata e texto desalinhado com a política de reembolso;
- `web/privacidade.html`, `web/termos.html` e `web/reembolso.html` locais estão prontos para substituir as versões antigas hoje publicadas.

## 1. Claims permitidos na LP e nos anúncios

- falar em triagem automática, ATS, adaptação por vaga e clareza do material;
- dizer que o produto reorganiza currículo, carta e LinkedIn com base na vaga informada;
- usar promessa operacional defensável, como `pagamento único`, `garantia de 7 dias` e `acesso por e-mail após confirmação do pagamento`;
- deixar explícito que o usuário deve revisar o material antes de usar em candidatura real.

## 2. Claims proibidos

- prometer emprego, contratação, renda ou aumento salarial;
- insinuar garantia de entrevista, aprovação ou resultado em processo seletivo;
- usar depoimento sem autorização expressa;
- publicar número não comprovado como estatística factual do produto;
- usar escassez artificial, contador falso ou preço que "vai subir" sem regra operacional real e documentada;
- afirmar atributos pessoais sensíveis do leitor em criativos de Meta, como desemprego, idade, maternidade, renda ou saúde.

## 3. Páginas legais mínimas

- `aprovai/web/privacidade.html`: pronta para publicação com foco em LGPD, uso de IA e operadores;
- `aprovai/web/termos.html`: pronta para publicação com escopo do produto, limites de uso e ausência de promessa de resultado;
- `aprovai/web/reembolso.html`: revisada para 7 dias corridos de arrependimento em compra online, sem garantia de resultado em 30 dias.
- status em produção em 3 de julho de 2026: as três URLs responderam `200 OK`, mas a inspeção do HTML mostrou que ainda estão com a versão antiga e precisam de novo deploy.

## 4. Meta Ads - categoria especial

- toda campanha do Aprovai deve ser marcada como `Categoria Especial de Emprego`;
- evitar segmentação ou copy que infira atributo pessoal do usuário;
- usar ângulos criativos centrados em processo e material, não em condição pessoal;
- manter a checagem listada em `aprovai/docs/05-painel-minimo-metricas-e-plano-trafego.md` antes de subir verba.

## 5. Checklist antes de publicar

- revisar a LP final contra esta lista;
- confirmar que Privacidade, Termos e Reembolso publicados batem com os arquivos revisados no repositório;
- validar que os links do checkout e das páginas legais estão funcionando;
- confirmar que o fluxo de entrega real corresponde ao texto exibido na página;
- só adicionar depoimento depois de autorização expressa e contexto verificável.

## 6. Pendência fora deste escopo

- a homepage e as páginas legais em produção ainda precisam de novo deploy para refletir a revisão local de compliance; enquanto isso, o conteúdo ao vivo continua com copy antiga.
- esta revisão fecha o conteúdo e a base de compliance do repositório, não substitui o passo operacional de publicar a home revisada.
