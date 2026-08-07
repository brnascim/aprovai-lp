# Anatomia do carrossel

Carrossel entrega mais informação que o estático e sustenta mais tempo de atenção — por
isso costuma performar bem em conversão e em públicos de nível 2–4. O custo é que ele
tem **duas** barreiras: parar o scroll (slide 1) e sustentar o deslize (todos os outros).

## Regras que valem para qualquer estrutura

1. **Um slide, uma ideia.** Se o slide precisa de dois parágrafos, são dois slides.
2. **Loop aberto em cada slide.** Termine com pergunta, número incompleto ou tensão. Slide
   que se fecha em si mesmo é onde a pessoa sai.
3. **≤ 20 palavras por slide.** O carrossel é lido em movimento.
4. **Consistência visual.** Mesma paleta, tipografia e grade nos slides — a inconsistência
   parece amadora e derruba autoridade.
5. **6 a 10 slides.** Menos de 5 não constrói argumento; mais de 10 perde a maioria.
6. **Slide 1 e slide final são os únicos que 100% e ~30% veem.** Concentre gancho e CTA neles.
7. **Numere os slides** (1/8) quando a estrutura for lista ou passo a passo — a barra de
   progresso mental aumenta a conclusão.

## As 7 estruturas

### 1. Dor → Solução  *(nível 1–2, público frio)*
```
1  Gancho na dor, com a frase literal do público
2  A cena da dor (quando e onde acontece)
3  O custo real de continuar assim (número concreto)
4  Por que as tentativas comuns falham
5  A virada: existe outro caminho
6  O mecanismo, em uma frase
7  Prova de que funciona
8  CTA + o que fazer agora
```

### 2. Lista numerada  *(nível 1–3, ótimo para alcance)*
```
1  "N [coisas] que [público] faz e que [consequência]"
2..N  um item por slide: erro + correção em uma linha
N+1  Recapitulação (a lista inteira em um slide, salvável)
N+2  CTA
```
É a estrutura mais compartilhada e salva. Use quando o objetivo for alcance + lista.

### 3. Passo a passo  *(nível 2–3)*
```
1  "Como [resultado] em N passos"
2..N  Passo K: o que fazer + o erro comum
N+1  O que muda quando termina
N+2  CTA: "o passo 3 completo está em [destino]"
```
Entregue valor real nos passos. Passo a passo que esconde tudo gera raiva, não clique.

### 4. Mito × Verdade  *(nível 2–3, alta reação)*
```
1  "3 mentiras que te contaram sobre [tema]"
2  Mito 1 → por que é falso
3  Verdade 1 → o que fazer
... repetir
N  O que os três mitos têm em comum (seu mecanismo)
N+1 CTA
```
Cria conflito produtivo e posiciona autoridade. Não ataque pessoas nem concorrentes
nominalmente — ataque a prática.

### 5. Antes / Depois de processo  *(nível 3–4)*
```
1  "Como era" (cena concreta, ruim)
2  O que travava
3  A mudança feita
4  Como ficou (com número real, se houver)
5  O que exatamente causou a mudança
6  Prova
7  CTA
```
Só com case real e autorizado. Nunca antes/depois de corpo.

### 6. História  *(nível 1–2, marca e conexão)*
```
1  Cena de abertura, no meio da ação
2  Contexto: quem era, o que estava em jogo
3  O erro/queda
4  A descoberta
5  O que mudou na prática
6  O aprendizado transferível para quem lê
7  CTA suave
```
A história tem que servir ao leitor, não ao ego de quem escreve. Se o aprendizado não é
transferível, é diário pessoal.

### 7. Comparação  *(nível 3–4, quebra de objeção)*
```
1  "[Alternativa comum] × [seu jeito]"
2..N  Um critério por slide, lado a lado (tempo, custo, esforço, risco)
N+1  Quando cada um faz sentido (honestidade aumenta conversão)
N+2  CTA
```
Compare com **categorias** ("planilha manual", "contratar alguém"), não com concorrentes
por nome.

## Escolha da estrutura

| Objetivo | Nível | Estrutura |
|----------|-------|-----------|
| Alcance e salvamento | 1–2 | Lista numerada, Mito×Verdade |
| Gerar consciência de problema | 1–2 | Dor→Solução, História |
| Mostrar autoridade e método | 3 | Passo a passo, Comparação |
| Quebrar objeção específica | 3–4 | Comparação, Antes/Depois |
| Converter | 4–5 | Dor→Solução curta (6 slides), Antes/Depois |

## Slide 1 — a peça mais importante

Precisa cumprir três coisas em ~1 segundo: **quem** é o público, **o que** ele ganha (ou
perde), **por que** vale deslizar.

```
Bom:  "Contador de escritório pequeno: 4 dias fechando folha é opcional."
Bom:  "3 erros de precificação que fazem confeiteira trabalhar de graça"
Ruim: "Dicas de produtividade"       (sem público, sem tensão)
Ruim: "Arrasta pro lado 👉"          (pede sem dar motivo)
```

Sinais visuais que ajudam: seta discreta no canto, "1/8", corte de imagem que continua no
slide seguinte. Sinais que atrapalham: excesso de setas, emoji piscando, "ARRASTA!!!".

## Último slide

Uma única ação. Escolha conforme o objetivo:

| Objetivo | CTA |
|----------|-----|
| Conversão direta | "Toque em [botão] — acesso imediato, 7 dias de garantia" |
| Lead | "Comenta [PALAVRA] que eu te mando o material" |
| Engajamento | "Salva pra usar na próxima [situação]" |
| Autoridade | "Me segue se você é [público] e quer [resultado]" |

Nunca peça três coisas ("curte, salva, comenta e compartilha"). Divide a ação e não faz
nenhuma.

## Tabela de entrega (formato de saída)

| Slide | Texto (≤20 palavras) | Elemento visual | Função |
|-------|----------------------|-----------------|--------|
| 1 | | | gancho |
| 2 | | | |
| ... | | | |
| N | | | CTA |

Essa tabela é exatamente o que a skill `cowork-carrosseis` consome para renderizar os PNGs
em lote — mantenha o formato.
