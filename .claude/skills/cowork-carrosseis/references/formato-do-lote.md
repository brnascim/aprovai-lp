# Formato do lote (JSON)

## Estrutura

```json
{
  "tema": "grafite",
  "formato": "4:5",
  "marca": "@seuperfil",
  "carrosseis": [
    {
      "nome": "folha-em-1-dia",
      "tema": "ambar",
      "marca": "@outroperfil",
      "slides": [ /* ... */ ]
    }
  ]
}
```

| Campo | Nível | Obrigatório | Valores |
|-------|-------|-------------|---------|
| `tema` | lote e carrossel | não (padrão `grafite`) | `grafite`, `claro`, `ambar`, `verde`, `roxo` |
| `formato` | lote | não (padrão `4:5`) | `4:5` (1080×1350), `1:1` (1080×1080), `9:16` (1080×1920) |
| `marca` | lote e carrossel | não | texto do rodapé (ex.: `@seuperfil`) |
| `nome` | carrossel | não | vira o nome da pasta (é normalizado para minúsculas sem acento) |
| `slides` | carrossel | **sim** | lista de 1 a 20 slides |

Campos definidos no carrossel sobrescrevem os do lote — útil para produzir para perfis
diferentes no mesmo arquivo.

Atalho: um JSON com `slides` na raiz (sem `carrosseis`) é tratado como carrossel único.

---

## Os 6 tipos de slide

### `capa` — sempre o slide 1
```json
{ "tipo": "capa",
  "selo": "GUIA RÁPIDO",
  "titulo": "4 dias fechando folha é opcional",
  "subtitulo": "Escritório de contabilidade com até 5 pessoas" }
```
Título com barra de destaque à esquerda, rodapé com "arrasta →".
**Limite prático:** título ≤ 8 palavras · subtítulo ≤ 12 palavras · selo ≤ 3 palavras.
O `selo` é opcional e serve para nomear o público ou o formato.

### `texto` — o slide de trabalho (padrão)
```json
{ "tipo": "texto",
  "titulo": "Não é volume",
  "corpo": "É retrabalho: o mesmo dado conferido três vezes." }
```
Ambos os campos são opcionais — só título funciona como slide de impacto.
**Limite:** título ≤ 6 palavras · corpo ≤ 20 palavras.

### `numero` — dado que ancora o argumento
```json
{ "tipo": "numero", "numero": "12h", "corpo": "por mês só reconferindo o que já estava certo" }
```
Número gigante na cor de destaque. Use para tempo, quantidade e proporção.
**Nunca** para promessa de renda ("R$ 10 mil") — ver políticas.

### `lista` — 3 a 5 itens numerados
```json
{ "tipo": "lista", "titulo": "O método das 3 colunas",
  "itens": ["Entrada", "Conferência única", "Fechamento"] }
```
**Limite:** 5 itens · cada item ≤ 5 palavras. Mais que isso, quebre em dois slides.

### `citacao` — prova real
```json
{ "tipo": "citacao",
  "corpo": "Mesmo sistema, mesma equipe. Fechou às 11h20.",
  "autor": "Marcos, escritório em Contagem — com autorização" }
```
**Só com depoimento real e autorizado.** O campo `autor` deve trazer contexto suficiente
para o leitor saber de quem é. Depoimento genérico ou inventado não entra.

### `cta` — sempre o último slide
```json
{ "tipo": "cta", "titulo": "O processo completo está no link", "subtitulo": "Toque em Saiba mais" }
```
O `subtitulo` vira um botão visual. **Uma ação só** — nunca "curte, salva e compartilha".

---

## Exemplo completo (estrutura dor → solução)

```json
{
  "tema": "grafite",
  "formato": "4:5",
  "marca": "@seuperfil",
  "carrosseis": [{
    "nome": "folha-em-1-dia",
    "slides": [
      { "tipo": "capa",  "titulo": "4 dias fechando folha é opcional",
        "subtitulo": "Escritório de contabilidade com até 5 pessoas" },
      { "tipo": "texto", "titulo": "Não é volume",
        "corpo": "É retrabalho: o mesmo dado conferido três vezes." },
      { "tipo": "numero","numero": "12h",
        "corpo": "por mês só reconferindo o que já estava certo" },
      { "tipo": "texto", "titulo": "Trocar de sistema não resolve",
        "corpo": "O problema está na ordem das etapas." },
      { "tipo": "lista", "titulo": "O método das 3 colunas",
        "itens": ["Entrada", "Conferência única", "Fechamento"] },
      { "tipo": "citacao","corpo": "Mesmo sistema, mesma equipe. Fechou às 11h20.",
        "autor": "case real — com autorização" },
      { "tipo": "cta",   "titulo": "O processo completo está no link",
        "subtitulo": "Toque em Saiba mais" }
    ]
  }]
}
```

## Comandos

```bash
node scripts/carrossel_render.mjs --exemplo > lote.json   # gera este exemplo
node scripts/carrossel_render.mjs --temas                 # lista os temas
node scripts/carrossel_render.mjs lote.json               # renderiza em ./carrosseis
node scripts/carrossel_render.mjs lote.json --saida ./posts
node scripts/carrossel_render.mjs lote.json --formato 9:16 --tema claro
node scripts/carrossel_render.mjs lote.json --so-html     # sem navegador
CHROME_PATH=/caminho/do/chrome node scripts/carrossel_render.mjs lote.json
```

## Saída

```
carrosseis/
└── folha-em-1-dia/
    ├── 01.html   ← editável para ajuste fino
    ├── 01.png    ← 1080×1350, pronto para publicar
    ├── 02.html
    ├── 02.png
    └── ...
```

A numeração segue a ordem de publicação — suba os arquivos na ordem alfabética e o
carrossel sai correto.

## Erros comuns

| Sintoma | Causa | Correção |
|---------|-------|----------|
| "JSON inválido" | vírgula sobrando antes de `}` ou `]` | valide o arquivo antes de rodar |
| "precisa de 'carrosseis' ou 'slides'" | estrutura fora do padrão | veja a estrutura no topo |
| Texto estourando o slide | texto longo demais | respeite os limites de cada tipo |
| Só HTML, sem PNG | navegador não encontrado | defina `CHROME_PATH` |
| Acento saindo errado | arquivo não está em UTF-8 | salve o JSON como UTF-8 |
| Fonte diferente do esperado | Inter não instalada | instale a fonte ou troque a família no tema |
