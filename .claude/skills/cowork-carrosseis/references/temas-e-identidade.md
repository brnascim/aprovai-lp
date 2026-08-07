# Temas e identidade visual

## Os 5 temas prontos

| Tema | Fundo | Destaque | Quando usar |
|------|-------|----------|-------------|
| `grafite` | grafite azulado | azul `#4da3ff` | Padrão. B2B, tecnologia, serviços, finanças educativas |
| `claro` | branco/cinza | azul `#0b62d6` | Público mais tradicional, jurídico, contábil, saúde |
| `ambar` | marrom escuro | âmbar `#f5a524` | Artesanal, gastronomia, moda, beleza |
| `verde` | verde profundo | verde `#2ecc8f` | Bem-estar, sustentabilidade, produtividade |
| `roxo` | roxo escuro | lilás `#a97bff` | Criativo, educação, público jovem |

Cada tema define quatro cores: `fundo` (gradiente), `texto`, `destaque` (números, botões,
barras) e `suave` (subtítulos e rodapé).

## Criar um tema próprio

Edite o objeto `TEMAS` no topo de `../scripts/carrossel_render.mjs`:

```js
minhamarca: {
  fundo: "linear-gradient(160deg, #0d1b2a 0%, #1b263b 100%)",
  texto: "#e8eef5",
  destaque: "#ff6b35",
  suave: "#8fa3b8",
  fonte: "'Inter', 'Segoe UI', system-ui, sans-serif",
},
```

Depois: `node scripts/carrossel_render.mjs lote.json --tema minhamarca`

## Como derivar o tema da identidade do produto

1. **Fundo** — a cor escura (ou clara) predominante da marca. Gradiente sutil entre dois
   tons próximos dá profundidade sem virar enfeite.
2. **Texto** — quase branco (`#f5f7fa`) sobre fundo escuro, quase preto (`#14171f`) sobre
   claro. Branco puro sobre preto puro cansa a vista e "vibra" na tela.
3. **Destaque** — a cor de ação da marca. Precisa contrastar com o fundo **e** com o texto:
   é ela que guia o olho.
4. **Suave** — o texto em ~60% de opacidade visual. Serve para hierarquia, nunca para
   informação essencial.

Regra de ouro: **duas cores dominantes + uma de acento.** Mais que isso vira ruído na
miniatura do feed.

## Contraste — o que checar

- **Texto principal:** contraste mínimo 4.5:1 com o fundo (WCAG AA). Em corpo grande
  (≥ 24px em tela real), 3:1 já é aceitável — mas 4.5:1 é a meta.
- **Destaque sobre fundo:** também ≥ 3:1, senão o número gigante some.
- **Texto do botão:** o botão usa a cor de destaque como fundo e um texto quase preto —
  se o seu destaque for escuro, troque o texto do botão para claro no CSS.

Teste rápido: abra o PNG, reduza para 20% e vire a tela para o lado. Se o slide 1 ainda
comunica, o contraste está bom.

## Tipografia

O script usa a pilha `Inter → Segoe UI → system-ui → sans-serif`. Sem Inter instalada, o
sistema escolhe a mais próxima — o layout não quebra, só muda o desenho da letra.

Para usar outra fonte:

```js
fonte: "'Poppins', 'Inter', system-ui, sans-serif",
```

A fonte precisa estar **instalada na máquina** que renderiza. O script não busca fonte na
internet de propósito: renderização sem rede é previsível e não depende de terceiros.

Escolha de fonte, em uma linha: **sem serifa, peso 800 nos títulos, 400–600 no corpo.**
Fonte decorativa em título de carrossel reduz legibilidade no feed.

## Ajuste fino sem mexer no script

Cada slide gera um `.html` ao lado do `.png`. Para um ajuste pontual:

1. Abra o `NN.html` da pasta de saída
2. Edite o CSS embutido (tamanho, posição, cor)
3. Capture de novo:

```bash
CH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome   # ou o seu Chrome
"$CH" --headless --disable-gpu --no-sandbox --hide-scrollbars \
      --window-size=1080,1550 --screenshot=novo.png file://$PWD/03.html
```

(a altura extra na janela compensa a moldura do headless; recorte para 1350 depois, ou
rode o script inteiro de novo, que já faz isso).

Se o mesmo ajuste se repetir em vários lotes, ele deveria estar no tema — não no HTML.

## Elementos fixos do layout

| Elemento | Comportamento |
|----------|---------------|
| Barra de progresso | Pontos no rodapé, um por slide, o atual em destaque |
| Rodapé | `marca` à esquerda, progresso ao centro, `N/total` à direita |
| "arrasta →" | Só no slide de capa, na cor de destaque |
| Brilho de fundo | Halo sutil da cor de destaque no canto superior direito |
| Margens | ~8,5% na horizontal e ~9% na vertical — área segura para a interface do app |

Esses elementos existem porque cumprem função (orientação, marca, continuidade). Se quiser
removê-los, edite a seção `.rodape` do CSS no script.
