#!/usr/bin/env python3
"""Gera o plano de criativos a partir da mandala (fase × momento × tipo × ângulo).

Uso:
    python3 mandala_plano.py --kit-inicial
    python3 mandala_plano.py --n 12
    python3 mandala_plano.py --n 20 --fase descoberta --csv plano.csv
    python3 mandala_plano.py --n 12 --objecoes "acho caro,não tenho tempo,já tentei"
    python3 mandala_plano.py --rodou desc-pront-probsol-dor,conv-pront-prova-objecao1

Cobre os eixos de forma equilibrada, pula combinações incoerentes, prioriza pelas
combinações de maior retorno e sugere formato + esboço de gancho para cada célula.

Significado dos eixos: ../references/mandala.md
"""

import argparse
import csv
import random
import signal
import sys

FASES = {
    "descoberta": {"peso": 0.40, "publico": "frio", "nivel": "1-2", "sigla": "desc"},
    "relacionamento": {"peso": 0.25, "publico": "morno", "nivel": "2-3", "sigla": "rel"},
    "conversao": {"peso": 0.25, "publico": "quente", "nivel": "3-4", "sigla": "conv"},
    "remarketing": {"peso": 0.10, "publico": "visitou/abandonou", "nivel": "4-5", "sigla": "rmkt"},
}

MOMENTOS = {"prontidao": "pront", "oportunidade": "oport"}

TIPOS = {
    "problema-solucao": {"sigla": "probsol", "formato": "Reels 30-45s | estático"},
    "historia": {"sigla": "hist", "formato": "Reels 45-60s"},
    "dilema": {"sigla": "dilema", "formato": "Reels 30-40s | carrossel"},
    "comparacao": {"sigla": "comp", "formato": "carrossel | Reels 40s"},
    "prova": {"sigla": "prova", "formato": "Reels 30-45s (demonstração)"},
    "explicacao": {"sigla": "expl", "formato": "Reels 45-60s | carrossel"},
    "apelo-emocional": {"sigla": "emo", "formato": "Reels 30-40s"},
    "exagero-humor": {"sigla": "humor", "formato": "Reels 20-30s"},
    "impacto-visual": {"sigla": "visual", "formato": "Reels 15-25s | estático"},
}

ANGULOS = ["dor", "objecao1", "objecao2", "objecao3", "mecanismo", "identidade", "custo-adiar"]

# (fase, tipo) que não valem a produção — ver references/mandala.md
INCOERENTES = {
    ("remarketing", "exagero-humor"),
    ("conversao", "exagero-humor"),
    ("descoberta", "explicacao"),
    ("descoberta", "prova"),
    ("conversao", "apelo-emocional"),
    ("relacionamento", "impacto-visual"),
    ("descoberta", "dilema"),
}

# combinações de maior retorno — entram primeiro no plano
PRIORITARIAS = [
    ("descoberta", "prontidao", "problema-solucao", "dor"),
    ("descoberta", "oportunidade", "historia", "identidade"),
    ("descoberta", "oportunidade", "impacto-visual", "dor"),
    ("relacionamento", "prontidao", "explicacao", "mecanismo"),
    ("relacionamento", "oportunidade", "comparacao", "objecao1"),
    ("conversao", "prontidao", "prova", "objecao2"),
    ("conversao", "prontidao", "dilema", "objecao3"),
    ("remarketing", "prontidao", "prova", "custo-adiar"),
]

KIT_INICIAL = PRIORITARIAS

GANCHOS = {
    "problema-solucao": '"[Situação da dor] de novo?" → a causa não é o que você pensa',
    "historia": '"Eu [erro concreto que você cometeu]." → o que aprendi',
    "dilema": '"Ou [opção ruim A], ou [opção ruim B]." → tem uma terceira',
    "comparacao": '"[Jeito comum] × [seu jeito]. Critério por critério."',
    "prova": '"Isso aqui é [material real]. Olha o que acontece."',
    "explicacao": '"Em 30 segundos: por que [problema] acontece."',
    "apelo-emocional": '"[Consequência humana da dor, dita sem drama]"',
    "exagero-humor": '"[Cena exagerada da dor]" → e o problema real era outro',
    "impacto-visual": "[ação visual forte, sem fala] → \"[número]. Todo mês.\"",
}

TESTA = {
    "dor": "se a dor escolhida é a que o público reconhece",
    "objecao1": "se a objeção 1 é mesmo a principal barreira",
    "objecao2": "se a objeção 2 trava a compra",
    "objecao3": "se a objeção 3 aparece antes ou depois do preço",
    "mecanismo": "se o diferencial se sustenta sozinho",
    "identidade": "se o público responde a aspiração, não só a dor",
    "custo-adiar": "se a perda por inércia move mais que o ganho",
}


def coerente(fase, tipo):
    return (fase, tipo) not in INCOERENTES


def sigla(fase, momento, tipo, angulo):
    return f"{FASES[fase]['sigla']}-{MOMENTOS[momento]}-{TIPOS[tipo]['sigla']}-{angulo}"


def gerar(n, filtro_fase=None, ja_rodou=None, semente=None):
    """Monta o plano cobrindo os eixos de forma equilibrada."""
    rnd = random.Random(semente)
    ja_rodou = set(ja_rodou or [])
    plano, vistos = [], set(ja_rodou)

    fases = [filtro_fase] if filtro_fase else list(FASES)

    # 1) prioritárias que se encaixam no filtro e ainda não rodaram
    for combo in PRIORITARIAS:
        if len(plano) >= n:
            break
        fase, momento, tipo, angulo = combo
        if fase not in fases:
            continue
        cod = sigla(*combo)
        if cod in vistos:
            continue
        plano.append(combo)
        vistos.add(cod)

    # 2) preenche cobrindo eixos pouco usados
    todas = [(f, m, t, a) for f in fases for m in MOMENTOS for t in TIPOS for a in ANGULOS
             if coerente(f, t) and sigla(f, m, t, a) not in vistos]
    rnd.shuffle(todas)

    while len(plano) < n and todas:
        uso_tipo = {t: sum(1 for c in plano if c[2] == t) for t in TIPOS}
        uso_ang = {a: sum(1 for c in plano if c[3] == a) for a in ANGULOS}
        uso_fase = {f: sum(1 for c in plano if c[0] == f) for f in fases}

        # menor uso combinado primeiro; a cota de fase entra com peso
        def custo(c):
            f, _m, t, a = c
            cota = FASES[f]["peso"] * len(plano) if not filtro_fase else len(plano) / len(fases)
            return (uso_fase[f] - cota, uso_tipo[t], uso_ang[a])

        todas.sort(key=custo)
        escolha = todas.pop(0)
        plano.append(escolha)
        vistos.add(sigla(*escolha))

    return plano


def detalhar(plano, objecoes=None):
    objecoes = objecoes or {}
    linhas = []
    for i, (fase, momento, tipo, angulo) in enumerate(plano, 1):
        rotulo_ang = objecoes.get(angulo, angulo)
        linhas.append({
            "n": i,
            "codigo": sigla(fase, momento, tipo, angulo),
            "fase": fase,
            "publico": FASES[fase]["publico"],
            "nivel": FASES[fase]["nivel"],
            "momento": momento,
            "tipo": tipo,
            "angulo": rotulo_ang,
            "formato": TIPOS[tipo]["formato"],
            "gancho": GANCHOS[tipo],
            "testa": TESTA.get(angulo, "hipótese a definir"),
        })
    return linhas


def imprimir(linhas, plano):
    print(f"\n# Plano de criativos — {len(linhas)} peças\n")
    print("| # | Código | Fase (público) | Momento | Tipo | Ângulo | Formato |")
    print("|---|--------|----------------|---------|------|--------|---------|")
    for l in linhas:
        print(f"| {l['n']} | `{l['codigo']}` | {l['fase']} ({l['publico']}) | {l['momento']} "
              f"| {l['tipo']} | {l['angulo']} | {l['formato']} |")

    print("\n## Detalhamento\n")
    for l in linhas:
        print(f"**{l['n']}. `{l['codigo']}`** — nível de consciência {l['nivel']}  \n"
              f"Esboço de gancho: {l['gancho']}  \n"
              f"Ângulo: **{l['angulo']}** · Testa: {l['testa']}  \n"
              f"Formato: {l['formato']}\n")

    # cobertura
    print("## Cobertura dos eixos\n")
    for nome, idx, universo in (("Fase", 0, FASES), ("Momento", 1, MOMENTOS),
                                ("Tipo", 2, TIPOS), ("Ângulo", 3, ANGULOS)):
        contagem = {}
        for combo in plano:
            contagem[combo[idx]] = contagem.get(combo[idx], 0) + 1
        faltando = [v for v in universo if v not in contagem]
        usados = ", ".join(f"{k} ({v})" for k, v in sorted(contagem.items()))
        print(f"- **{nome}:** {usados}")
        if faltando:
            print(f"  - não cobertos nesta rodada: {', '.join(faltando)}")

    print("\n## Próximos passos\n")
    print("1. Escrever os roteiros dos criativos em vídeo → `references/roteiros-reels.md`")
    print("2. Mandar as células de estático/carrossel para a skill "
          "`anuncios-estaticos-carrossel`")
    print("3. Gravar em lote com hook stacking → `references/producao-e-edicao.md`")
    print("4. Nomear cada arquivo com o código da célula (a leitura de métrica depende disso)")
    print("5. Ler resultado e repor o que morrer → `references/metricas-e-escala.md`\n")


def exportar_csv(linhas, caminho):
    with open(caminho, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)
    print(f"CSV salvo em {caminho}")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--n", type=int, default=12, help="quantidade de criativos (default: 12)")
    p.add_argument("--fase", choices=list(FASES), help="restringe a uma fase")
    p.add_argument("--kit-inicial", action="store_true",
                   help="os 8 criativos de partida para quem não tem nada rodando")
    p.add_argument("--objecoes", help="rótulos reais das 3 objeções, separados por vírgula")
    p.add_argument("--rodou", help="códigos de células já rodadas, separados por vírgula "
                                   "(serão evitadas)")
    p.add_argument("--csv", metavar="SAIDA.csv", help="exporta o plano em CSV")
    p.add_argument("--semente", type=int, help="semente para reproduzir o mesmo plano")
    args = p.parse_args()

    if args.n < 1:
        print("erro: --n precisa ser ≥ 1", file=sys.stderr)
        return 1

    if args.kit_inicial:
        plano = list(KIT_INICIAL)
        print("\n> Kit inicial: 8 criativos que cobrem o essencial antes de saber o que "
              "funciona.\n> Rode todos, colete dado e só depois multiplique os vencedores.")
    else:
        ja = [c.strip() for c in (args.rodou or "").split(",") if c.strip()]
        plano = gerar(args.n, args.fase, ja, args.semente)
        if ja:
            print(f"\n> Evitando {len(ja)} célula(s) já rodada(s).")

    objecoes = {}
    if args.objecoes:
        rotulos = [o.strip() for o in args.objecoes.split(",") if o.strip()]
        for i, rotulo in enumerate(rotulos[:3], 1):
            objecoes[f"objecao{i}"] = f'objeção {i}: "{rotulo}"'

    linhas = detalhar(plano, objecoes)
    imprimir(linhas, plano)

    if args.csv:
        exportar_csv(linhas, args.csv)
    return 0


if __name__ == "__main__":
    # não estourar traceback quando a saída é cortada por `head`/`less`
    try:
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except (AttributeError, ValueError):
        pass
    sys.exit(main())
