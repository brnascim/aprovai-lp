# Pipeline de produção em escala

O ganho aparece a partir de 5 carrosséis por rodada. Fazer um de cada vez não compensa o
setup — e é exatamente por isso que o design vira gargalo.

## Sessão de 90 minutos = uma semana de conteúdo

```
0-15min   PLANEJAR   Quais 5 carrosséis? (plano da mandala ou calendário editorial)
15-45min  ESCREVER   Os 5 roteiros, em texto puro, sem pensar em design
45-55min  ESTRUTURAR Transformar os roteiros no lote.json
55-60min  RENDERIZAR node carrossel_render.mjs lote.json
60-75min  REVISAR    Conferir os PNGs (checklist abaixo)
75-90min  AGENDAR    Subir, escrever legendas, programar
```

A ordem importa: **escrever tudo antes de desenhar qualquer coisa.** Alternar entre escrever
e desenhar é o que faz a produção levar 3 horas por post.

## Regras de lote

1. **Um tema por lote.** Consistência visual é o que faz o público reconhecer o perfil no
   feed antes de ler o @.
2. **Nomes descritivos**, não `carrossel-1`: o nome vira pasta e é como você acha o arquivo
   três semanas depois.
3. **Um lote por semana**, não por post.
4. **Guarde o `lote.json`** junto com os PNGs — reaproveitar um carrossel que funcionou é
   trocar 3 linhas, não refazer tudo.

## Estrutura de arquivos sugerida

```
conteudo/
├── 2026-08-semana-32/
│   ├── lote.json
│   ├── folha-em-1-dia/          01.png … 07.png
│   ├── 3-erros-de-precificacao/ 01.png … 08.png
│   └── legendas.md
└── 2026-08-semana-33/
```

O `legendas.md` guarda o texto que acompanha cada post — o carrossel é a arte, mas a legenda
é onde mora o CTA e a maior parte da conversão orgânica.

## Checklist de revisão (antes de publicar)

**Por carrossel**
- [ ] Slide 1 legível com a imagem reduzida a 20%
- [ ] Slide 1 diz **para quem** é
- [ ] Cada slide tem uma ideia só
- [ ] Nenhum texto estourou o espaço
- [ ] Último slide pede **uma** ação
- [ ] 6 a 10 slides (máximo 20)
- [ ] Numeração dos arquivos corresponde à ordem de leitura

**Por lote**
- [ ] Mesmo tema em todos
- [ ] Nenhuma promessa de renda, atributo pessoal ou escassez falsa
- [ ] Toda citação é real e autorizada
- [ ] `validar_copy.py` rodado nos roteiros, sem bloqueio

## Reaproveitamento

Um carrossel que funcionou vira, com pouco esforço:

| Derivado | Como |
|----------|------|
| Reels | Cada slide vira um corte de 3–4s com narração |
| Estático | O slide de maior impacto, isolado |
| Story em série | Mesmo conteúdo em 9:16 (`--formato 9:16`) |
| Anúncio de carrossel | Os mesmos PNGs no Meta Ads (valide a copy antes) |
| E-mail | O roteiro vira o corpo do e-mail |
| Thread | Um slide por post |

Trocar o `--formato` e rodar de novo custa segundos — é o melhor retorno do pipeline.

## Quando NÃO usar este pipeline

- **Post que depende de foto real** (bastidor, produto, pessoa) — a força está na foto, não
  no layout
- **Carrossel com print de tela/dado real** — inclua as imagens manualmente
- **Peça de identidade complexa** (ilustração autoral, animação) — aqui o editor manual ganha
- **Copy ainda não validada** — não industrialize o que ainda não se provou

## Automação além do lote

Quem produz muito costuma dar dois passos a mais:

1. **Planilha → JSON**: mantenha os roteiros numa planilha (uma linha por slide) e converta
   para `lote.json` com um script pequeno. Bom para quem trabalha com equipe.
2. **Rodada agendada**: um comando semanal que lê a planilha, renderiza e deixa os PNGs
   prontos na pasta da semana.

Ambos são incrementos do mesmo pipeline — o formato do `lote.json` é o contrato estável.
