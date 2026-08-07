#!/usr/bin/env python3
"""Pontua e ranqueia ideias de produto digital pela matriz de 6 critérios.

Uso:
    python3 score_ideias.py ideias.json          # ranqueia um arquivo
    python3 score_ideias.py --demo               # exemplo preenchido
    python3 score_ideias.py --template > i.json  # gera o arquivo em branco
    python3 score_ideias.py ideias.json --csv ranking.csv

Formato do JSON: lista de objetos com "ideia" e as 6 notas de 0 a 5.
Critérios e régua de pontuação: ../references/matriz-de-decisao.md
"""

import argparse
import csv
import json
import sys
from pathlib import Path

# critério -> (peso, rótulo curto)
CRITERIOS = {
    "dor": (3, "Dor"),
    "poder_de_compra": (3, "Poder de compra"),
    "capacidade_de_entrega": (2, "Capacidade de entrega"),
    "alcancabilidade": (2, "Alcançabilidade"),
    "diferenciacao": (1, "Diferenciação"),
    "velocidade": (1, "Velocidade"),
}

NOTA_MAXIMA = sum(peso * 5 for peso, _ in CRITERIOS.values())  # 60

FAIXAS = [
    (48, "🟢 Ataque agora"),
    (38, "🟡 Boa — valide o critério mais fraco"),
    (28, "🟠 Reescreva (estreite público ou troque formato)"),
    (0, "🔴 Descarte"),
]

TEMPLATE = [
    {
        "ideia": "[Público específico] consegue [resultado] em [prazo] sem [dor]",
        "lente": "sub-nicho | vizinho | gargalo | formato | entrada | recorrencia | ferramenta | servico",
        "dor": 0,
        "poder_de_compra": 0,
        "capacidade_de_entrega": 0,
        "alcancabilidade": 0,
        "diferenciacao": 0,
        "velocidade": 0,
    }
]

DEMO = [
    {
        "ideia": "Nutricionista clínico recém-formado lota a agenda em 60 dias sem depender de indicação",
        "lente": "sub-nicho",
        "dor": 5, "poder_de_compra": 4, "capacidade_de_entrega": 5,
        "alcancabilidade": 4, "diferenciacao": 4, "velocidade": 3,
    },
    {
        "ideia": "Confeiteira de bolo caseiro precifica sem trabalhar de graça, em 1 semana",
        "lente": "gargalo",
        "dor": 5, "poder_de_compra": 2, "capacidade_de_entrega": 4,
        "alcancabilidade": 5, "diferenciacao": 3, "velocidade": 5,
    },
    {
        "ideia": "Escritório de contabilidade fecha a folha em metade do tempo com planilha + 5 vídeos",
        "lente": "ferramenta",
        "dor": 4, "poder_de_compra": 5, "capacidade_de_entrega": 4,
        "alcancabilidade": 4, "diferenciacao": 3, "velocidade": 5,
    },
    {
        "ideia": "Curso de marketing digital para empreendedores",
        "lente": "sub-nicho",
        "dor": 2, "poder_de_compra": 3, "capacidade_de_entrega": 3,
        "alcancabilidade": 2, "diferenciacao": 1, "velocidade": 2,
    },
    {
        "ideia": "Mentoria de investimentos com carteira recomendada",
        "lente": "vizinho",
        "dor": 4, "poder_de_compra": 5, "capacidade_de_entrega": 0,
        "alcancabilidade": 3, "diferenciacao": 2, "velocidade": 3,
    },
]


def avaliar(item, indice):
    """Calcula nota ponderada, eliminação e critério mais fraco de uma ideia."""
    faltando = [c for c in CRITERIOS if c not in item]
    if faltando:
        raise ValueError(
            f"ideia #{indice} ({item.get('ideia', 'sem título')!r}): "
            f"faltam os critérios {', '.join(faltando)}"
        )

    notas = {}
    for criterio in CRITERIOS:
        valor = item[criterio]
        if not isinstance(valor, (int, float)) or not 0 <= valor <= 5:
            raise ValueError(
                f"ideia #{indice}: '{criterio}' deve ser um número de 0 a 5 (recebido {valor!r})"
            )
        notas[criterio] = float(valor)

    total = sum(notas[c] * peso for c, (peso, _) in CRITERIOS.items())
    zerados = [CRITERIOS[c][1] for c in CRITERIOS if notas[c] == 0]

    # critério mais fraco = maior perda ponderada; desempata pelo maior peso
    perdas = {c: (5 - notas[c]) * CRITERIOS[c][0] for c in CRITERIOS}
    mais_fraco = max(perdas, key=lambda c: (perdas[c], CRITERIOS[c][0]))

    if zerados:
        faixa = "⛔ ELIMINADA (nota 0 em " + ", ".join(zerados) + ")"
    else:
        faixa = next(rotulo for corte, rotulo in FAIXAS if total >= corte)

    return {
        "ideia": item.get("ideia", f"ideia #{indice}"),
        "lente": item.get("lente", "-"),
        "total": total,
        "pct": round(100 * total / NOTA_MAXIMA),
        "eliminada": bool(zerados),
        "faixa": faixa,
        "mais_fraco": CRITERIOS[mais_fraco][1],
        "nota_mais_fraco": notas[mais_fraco],
        "notas": notas,
    }


def ranquear(ideias):
    avaliadas = [avaliar(item, i + 1) for i, item in enumerate(ideias)]
    # eliminadas sempre no fim; entre iguais, maior nota primeiro
    avaliadas.sort(key=lambda r: (r["eliminada"], -r["total"]))
    return avaliadas


def imprimir(resultados):
    print(f"\n# Ranking de ideias  ({len(resultados)} avaliadas · nota máxima {NOTA_MAXIMA:.0f})\n")
    print("| # | Ideia | Nota | % | Situação | Critério mais fraco |")
    print("|---|-------|------|---|----------|---------------------|")
    for pos, r in enumerate(resultados, 1):
        marca = "—" if r["eliminada"] else str(pos)
        ideia = r["ideia"] if len(r["ideia"]) <= 62 else r["ideia"][:59] + "..."
        print(
            f"| {marca} | {ideia} | {r['total']:.0f} | {r['pct']}% | {r['faixa']} "
            f"| {r['mais_fraco']} ({r['nota_mais_fraco']:.0f}/5) |"
        )

    finalistas = [r for r in resultados if not r["eliminada"]][:3]
    if not finalistas:
        print("\n⛔ Nenhuma ideia sobreviveu. Volte às lentes de geração "
              "(references/geracao-de-ideias.md) e gere um lote novo.\n")
        return

    print("\n## Finalistas e o que testar\n")
    for pos, r in enumerate(finalistas, 1):
        print(f"**{pos}. {r['ideia']}**  \n"
              f"Nota {r['total']:.0f}/{NOTA_MAXIMA:.0f} · lente: {r['lente']}  \n"
              f"Ponto fraco: **{r['mais_fraco']}** ({r['nota_mais_fraco']:.0f}/5) → "
              f"o teste de validação precisa atacar isso "
              f"(references/validacao-rapida.md)\n")

    if len(finalistas) >= 2 and abs(finalistas[0]["total"] - finalistas[1]["total"]) <= 3:
        v0, v1 = finalistas[0]["notas"]["velocidade"], finalistas[1]["notas"]["velocidade"]
        vencedor = finalistas[0] if v0 >= v1 else finalistas[1]
        print(f"⚖️  Empate técnico (≤3 pontos). Desempate por velocidade até a 1ª venda: "
              f"**{vencedor['ideia']}**\n")


def exportar_csv(resultados, caminho):
    colunas = ["posicao", "ideia", "lente", "total", "pct", "situacao", "criterio_mais_fraco"]
    colunas += list(CRITERIOS)
    with open(caminho, "w", newline="", encoding="utf-8") as fh:
        escritor = csv.writer(fh)
        escritor.writerow(colunas)
        for pos, r in enumerate(resultados, 1):
            escritor.writerow(
                ["" if r["eliminada"] else pos, r["ideia"], r["lente"], f"{r['total']:.0f}",
                 r["pct"], r["faixa"], r["mais_fraco"]]
                + [f"{r['notas'][c]:.0f}" for c in CRITERIOS]
            )
    print(f"CSV salvo em {caminho}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("arquivo", nargs="?", help="JSON com a lista de ideias")
    p.add_argument("--demo", action="store_true", help="roda com ideias de exemplo")
    p.add_argument("--template", action="store_true", help="imprime um JSON em branco")
    p.add_argument("--csv", metavar="SAIDA.csv", help="também exporta o ranking em CSV")
    args = p.parse_args()

    if args.template:
        print(json.dumps(TEMPLATE, indent=2, ensure_ascii=False))
        return 0

    if args.demo:
        ideias = DEMO
    elif args.arquivo:
        caminho = Path(args.arquivo)
        if not caminho.exists():
            print(f"erro: arquivo não encontrado: {caminho}", file=sys.stderr)
            return 1
        try:
            ideias = json.loads(caminho.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"erro: JSON inválido em {caminho}: {e}", file=sys.stderr)
            return 1
    else:
        p.print_help()
        return 0

    if not isinstance(ideias, list) or not ideias:
        print("erro: o JSON deve ser uma lista não vazia de ideias", file=sys.stderr)
        return 1

    try:
        resultados = ranquear(ideias)
    except ValueError as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1

    imprimir(resultados)
    if args.csv:
        exportar_csv(resultados, args.csv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
