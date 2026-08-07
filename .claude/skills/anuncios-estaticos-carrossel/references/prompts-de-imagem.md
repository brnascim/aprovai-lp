# Prompts de imagem para criativos

A imagem tem uma função: **fazer a pessoa certa parar e criar contexto para o texto.** Não é
enfeite, e não precisa ser bonita — precisa ser reconhecível pelo público.

## Anatomia do prompt

```
[sujeito] + [ação/estado] + [ambiente] + [enquadramento] + [luz] +
[estilo] + [paleta] + [espaço reservado para texto] + [proporção] + [negativos]
```

**Exemplo completo:**

> Homem de 40 anos, camisa social azul clara sem gravata, sentado à mesa de escritório
> pequeno olhando cansado para três planilhas impressas espalhadas; ambiente real de
> escritório de contabilidade brasileiro, arquivos e pastas ao fundo levemente desfocados;
> plano médio, câmera na altura dos olhos, sujeito posicionado no terço inferior direito;
> luz natural de janela lateral, manhã, sombras suaves; fotografia editorial realista, lente
> 50mm, f/2.8, grão sutil; paleta azul-acinzentada com um ponto de âmbar; **terço superior
> esquerdo limpo e uniforme para receber texto**; proporção 4:5.
> Negativos: sem texto, sem letras, sem logotipos, sem marcas, sem rosto de pessoa famosa,
> sem mãos deformadas, sem elementos de stock genérico sorrindo para a câmera.

## As regras que mais importam

### 1. Espaço negativo planejado
Diga onde o texto vai entrar: *"terço superior limpo"*, *"parede lisa à esquerda"*,
*"fundo desfocado uniforme no topo"*. Imagem sem lugar para o texto é retrabalho garantido.

### 2. Zero texto gerado por IA
Modelos ainda erram letra em português — e mesmo quando acertam, você perde controle de
tipografia e de teste. Peça explicitamente "sem texto" e coloque o texto na edição (ou
renderize com `cowork-carrosseis`).

### 3. Realismo reconhecível > perfeição
Público brasileiro reconhece cenário brasileiro. Peça: escritório pequeno real, cozinha de
casa, loja de rua, consultório simples. Stock americano sorridente tem cara de anúncio e é
ignorado.

### 4. Uma pessoa, um foco
Cena com muita gente e muito objeto não sobrevive à miniatura do feed.

### 5. Contraste na miniatura
Antes de aprovar, reduza a arte para 20%: dá para entender o assunto e ler o bloco
principal? Se não, refaça.

## Estilos por objetivo

| Objetivo | Estilo | Prompt-chave |
|----------|--------|--------------|
| Parar scroll (frio) | Fotografia documental realista | "fotografia editorial realista, luz natural, sem pose" |
| Autoridade | Retrato profissional | "retrato editorial, fundo neutro, luz suave de estúdio" |
| Explicação | Ilustração vetorial simples | "ilustração vetorial plana, 2 cores, formas simples, fundo sólido" |
| Comparação | Diagrama limpo | "diagrama minimalista, duas colunas, ícones simples, fundo claro" |
| Produto/tela | Mockup | "mockup de notebook em mesa de madeira, tela em ângulo, luz difusa" |
| Frase pura | Fundo abstrato | "gradiente suave azul-escuro, textura de papel sutil, sem elementos" |
| Metáfora | Objeto isolado | "objeto isolado em fundo sólido, sombra dura, foto de produto" |

## Paleta

Puxe da identidade do produto. Sem identidade definida:

- **Confiança / B2B:** azul profundo + cinza claro + um acento âmbar
- **Urgência / oferta:** grafite + um vermelho/laranja usado com parcimônia
- **Saúde / bem-estar:** verde suave + areia + branco
- **Criativo / jovem:** roxo + coral + off-white
- **Financeiro:** azul-marinho + verde-escuro + dourado discreto (sem dinheiro na imagem)

Regra: **duas cores dominantes + uma de acento.** Mais que isso vira ruído na miniatura.

## Negativos padrão (cole em todo prompt)

```
sem texto, sem letras, sem números, sem logotipos, sem marcas registradas,
sem rostos de pessoas reais conhecidas, sem mãos com dedos deformados,
sem watermark, sem moldura, sem colagem, sem elementos de interface falsos
```

## Proibido gerar

- **Print falso** de rede social, extrato bancário, conversa de WhatsApp ou notícia — é
  prova fabricada, viola política de plataforma e é enganoso mesmo quando "ilustrativo".
- **Antes/depois corporal** — reprovado no Meta e problemático em saúde.
- **Rosto de pessoa real** (celebridade, cliente sem autorização) ou personagem/marca
  protegida.
- **Símbolos de riqueza como promessa** — maço de dinheiro, carro de luxo, jatinho.
  Converte mal, atrai o pior lead, chama moderação.
- **Imagem que sugere atributo pessoal** — foto de pessoa chorando com texto "endividado?".

## Variação para teste

Ao gerar variações, mude **uma** dimensão por vez:

```
Base:  pessoa em escritório, luz natural, 4:5
V1:    mesmo prompt, ilustração vetorial      ← testa estilo
V2:    mesmo prompt, plano fechado no objeto  ← testa enquadramento
V3:    mesmo prompt, paleta escura            ← testa contraste no feed
```

## Ficha de entrega

```markdown
**Prompt:** [texto completo]
**Negativos:** [lista]
**Proporção:** 4:5 | 1:1 | 9:16
**Área reservada para texto:** [onde]
**Paleta:** [duas + acento]
**Alternativa sem IA:** [que foto/print real substitui, se o usuário preferir]
```

O campo "alternativa sem IA" importa: em muitos nichos, a foto real do usuário no ambiente
dele converte mais que qualquer imagem gerada — porque é a única que ninguém mais tem.
