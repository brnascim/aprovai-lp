#!/usr/bin/env python3
"""Calculadora de preço, margem, CPA máximo e escada de produtos.

Uso:
    python3 precificacao.py --demo
    python3 precificacao.py --interativo
    python3 precificacao.py --ticket 497 --meta-mensal 30000 --conversao 1.5

Todos os parâmetros têm default explícito (ver --help). O resultado sai em Markdown,
pronto para colar no one-page de conceito.

Leitura estratégica dos números: ../references/precificacao-e-oferta.md
"""

import argparse
import sys

BRL = lambda v: f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def calcular(
    ticket,
    meta_mensal,
    conversao_pct,
    custo_plataforma_pct,
    custo_fixo_transacao,
    imposto_pct,
    custo_entrega,
    reembolso_pct,
    cpa_real,
):
    """Devolve o dicionário completo de métricas de uma oferta."""
    if ticket <= 0:
        raise ValueError("ticket precisa ser maior que zero")
    if not 0 < conversao_pct <= 100:
        raise ValueError("conversão precisa estar entre 0 e 100 (em %)")

    taxa_plataforma = ticket * custo_plataforma_pct / 100 + custo_fixo_transacao
    imposto = ticket * imposto_pct / 100
    perda_reembolso = ticket * reembolso_pct / 100

    margem = ticket - taxa_plataforma - imposto - custo_entrega - perda_reembolso
    margem_pct = 100 * margem / ticket

    vendas_meta = meta_mensal / ticket if ticket else 0
    lucro_meta = vendas_meta * margem

    cpa_maximo = margem * 0.5              # metade da margem para o tráfego
    cpa_breakeven = margem                  # acima disso, prejuízo
    roas_breakeven = ticket / margem if margem > 0 else float("inf")

    visitantes = vendas_meta / (conversao_pct / 100) if conversao_pct else 0
    verba_mensal = vendas_meta * cpa_maximo

    resultado = {
        "ticket": ticket,
        "taxa_plataforma": taxa_plataforma,
        "imposto": imposto,
        "custo_entrega": custo_entrega,
        "perda_reembolso": perda_reembolso,
        "margem": margem,
        "margem_pct": margem_pct,
        "meta_mensal": meta_mensal,
        "vendas_meta": vendas_meta,
        "lucro_meta": lucro_meta,
        "cpa_maximo": cpa_maximo,
        "cpa_breakeven": cpa_breakeven,
        "roas_breakeven": roas_breakeven,
        "visitantes": visitantes,
        "verba_mensal": verba_mensal,
        "conversao_pct": conversao_pct,
        "cpa_real": cpa_real,
    }
    resultado["diagnostico"] = diagnosticar(resultado)
    resultado["escada"] = escada(ticket)
    resultado["parcelas"] = parcelamento(ticket)
    return resultado


def diagnosticar(r):
    """Traduz os números em decisão. Retorna lista de (nível, texto)."""
    saida = []

    if r["margem"] <= 0:
        saida.append(("⛔", "Margem negativa: cada venda dá prejuízo. "
                            "Suba o ticket ou corte custo de entrega antes de qualquer anúncio."))
        return saida

    if r["margem_pct"] < 50:
        saida.append(("⛔", f"Margem de {r['margem_pct']:.0f}% é insuficiente para tráfego pago. "
                            f"Alvo mínimo: 70% em produto digital sem entrega humana."))
    elif r["margem_pct"] < 70:
        saida.append(("⚠️", f"Margem de {r['margem_pct']:.0f}% é apertada. Dá para vender no "
                            f"orgânico; para escalar em tráfego, suba ticket ou crie order bump."))
    else:
        saida.append(("🟢", f"Margem de {r['margem_pct']:.0f}% sustenta tráfego pago."))

    if r["cpa_real"] is not None:
        if r["cpa_real"] < r["cpa_maximo"]:
            folga = 100 * (r["cpa_maximo"] - r["cpa_real"]) / r["cpa_maximo"]
            saida.append(("🟢", f"CPA real {BRL(r['cpa_real'])} está {folga:.0f}% abaixo do "
                                f"máximo sustentável. Dá para aumentar verba gradualmente."))
        elif r["cpa_real"] < r["cpa_breakeven"]:
            saida.append(("⚠️", f"CPA real {BRL(r['cpa_real'])} passou do máximo saudável "
                                f"({BRL(r['cpa_maximo'])}) mas ainda não dá prejuízo. "
                                f"Não escale: melhore conversão, ticket ou criativo primeiro."))
        else:
            saida.append(("⛔", f"CPA real {BRL(r['cpa_real'])} ≥ margem por venda "
                                f"({BRL(r['margem'])}). Cada venda paga vem no prejuízo. "
                                f"Pare de escalar agora."))

    if r["conversao_pct"] < 1:
        visitantes = f"{r['visitantes']:,.0f}".replace(",", ".")
        saida.append(("⚠️", f"Conversão de {r['conversao_pct']}% exige {visitantes} "
                            f"visitantes/mês para a meta. Antes de comprar esse tráfego, "
                            f"ataque promessa e prova."))

    if r["vendas_meta"] > 100 and r["ticket"] < 300:
        saida.append(("⚠️", f"A meta exige {r['vendas_meta']:.0f} vendas/mês em ticket baixo. "
                            f"Considere um degrau de ticket maior — volume alto custa suporte."))

    return saida


def escada(ticket):
    """Sugere a escada de produtos coerente com o ticket informado."""
    if ticket <= 97:
        papel = "produto de ENTRADA"
        sugestao = [("Isca", 0, 47), ("Entrada (este)", ticket, ticket),
                    ("Núcleo", ticket * 5, ticket * 10), ("Alto ticket", ticket * 30, ticket * 60)]
    elif ticket <= 1997:
        papel = "produto de NÚCLEO"
        sugestao = [("Isca", 0, 47), ("Entrada", ticket * 0.1, ticket * 0.25),
                    ("Núcleo (este)", ticket, ticket), ("Alto ticket", ticket * 4, ticket * 10)]
    else:
        papel = "produto de ALTO TICKET"
        sugestao = [("Isca", 0, 47), ("Entrada", ticket * 0.02, ticket * 0.06),
                    ("Núcleo", ticket * 0.15, ticket * 0.4), ("Alto ticket (este)", ticket, ticket)]
    return {"papel": papel, "degraus": sugestao,
            "order_bump": (ticket * 0.15, ticket * 0.30)}


def parcelamento(ticket, taxa_parcelamento_pct=3.0):
    """Parcelas em 6x e 12x com o acréscimo típico da plataforma."""
    linhas = []
    for n in (6, 12):
        total = ticket * (1 + taxa_parcelamento_pct / 100)
        linhas.append((n, total / n, total))
    return linhas


def relatorio(r):
    p = print
    p("\n# Precificação\n")
    p(f"**Ticket:** {BRL(r['ticket'])} — {r['escada']['papel']}\n")

    p("## Composição por venda\n")
    p("| Item | Valor |")
    p("|------|-------|")
    p(f"| Ticket | {BRL(r['ticket'])} |")
    p(f"| (−) Plataforma/gateway | {BRL(-r['taxa_plataforma'])} |")
    p(f"| (−) Imposto | {BRL(-r['imposto'])} |")
    p(f"| (−) Custo de entrega | {BRL(-r['custo_entrega'])} |")
    p(f"| (−) Provisão de reembolso | {BRL(-r['perda_reembolso'])} |")
    p(f"| **= Margem líquida** | **{BRL(r['margem'])} ({r['margem_pct']:.0f}%)** |")

    p("\n## Meta\n")
    p("| Métrica | Valor |")
    p("|---------|-------|")
    p(f"| Meta de faturamento/mês | {BRL(r['meta_mensal'])} |")
    p(f"| Vendas necessárias/mês | {r['vendas_meta']:.0f} |")
    p(f"| Vendas/dia | {r['vendas_meta']/30:.1f} |")
    p(f"| Lucro na meta (antes do tráfego) | {BRL(r['lucro_meta'])} |")
    p(f"| Visitantes/mês a {r['conversao_pct']}% de conversão | {r['visitantes']:,.0f} |"
      .replace(",", "."))

    p("\n## Tráfego\n")
    p("| Métrica | Valor | Leitura |")
    p("|---------|-------|---------|")
    p(f"| CPA máximo sustentável | {BRL(r['cpa_maximo'])} | metade da margem |")
    p(f"| CPA de equilíbrio | {BRL(r['cpa_breakeven'])} | acima disso, prejuízo |")
    p(f"| ROAS de equilíbrio | {r['roas_breakeven']:.2f}x | mínimo para não perder dinheiro |")
    p(f"| Verba mensal no CPA máximo | {BRL(r['verba_mensal'])} | para bater a meta |")

    p("\n## Parcelamento\n")
    p("| Parcelas | Valor | Total |")
    p("|----------|-------|-------|")
    for n, valor, total in r["parcelas"]:
        p(f"| {n}× | {BRL(valor)} | {BRL(total)} |")

    p("\n## Escada de produtos sugerida\n")
    p("| Degrau | Faixa |")
    p("|--------|-------|")
    for nome, lo, hi in r["escada"]["degraus"]:
        faixa = BRL(lo) if lo == hi else f"{BRL(lo)} – {BRL(hi)}"
        p(f"| {nome} | {faixa} |")
    lo, hi = r["escada"]["order_bump"]
    p(f"\nOrder bump sugerido no checkout: {BRL(lo)} – {BRL(hi)} "
      f"(complemento óbvio, sem custo de tráfego novo).")

    p("\n## Diagnóstico\n")
    for nivel, texto in r["diagnostico"]:
        p(f"- {nivel} {texto}")
    p("")


def perguntar(texto, default, tipo=float):
    entrada = input(f"{texto} [{default}]: ").strip().replace(",", ".")
    if not entrada:
        return default
    try:
        return tipo(entrada)
    except ValueError:
        print(f"  valor inválido, usando {default}")
        return default


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ticket", type=float, default=497, help="preço à vista (default: 497)")
    p.add_argument("--meta-mensal", type=float, default=30000,
                   help="faturamento-alvo por mês (default: 30000)")
    p.add_argument("--conversao", type=float, default=1.5,
                   help="conversão da página em %% (default: 1.5)")
    p.add_argument("--custo-plataforma", type=float, default=9.9,
                   help="taxa da plataforma em %% (default: 9.9)")
    p.add_argument("--custo-fixo-transacao", type=float, default=0,
                   help="taxa fixa por transação em R$ (default: 0)")
    p.add_argument("--imposto", type=float, default=6.0,
                   help="imposto em %% (default: 6.0 — Simples, faixa inicial)")
    p.add_argument("--custo-entrega", type=float, default=12,
                   help="custo por aluno: hospedagem, suporte, material (default: 12)")
    p.add_argument("--reembolso", type=float, default=8.0,
                   help="taxa de reembolso esperada em %% (default: 8.0)")
    p.add_argument("--cpa-real", type=float, default=None,
                   help="CPA que você mede hoje (opcional; ativa o diagnóstico de escala)")
    p.add_argument("--demo", action="store_true", help="roda um caso de exemplo completo")
    p.add_argument("--interativo", action="store_true", help="pergunta cada valor")
    args = p.parse_args()

    if args.demo:
        r = calcular(ticket=497, meta_mensal=30000, conversao_pct=1.5,
                     custo_plataforma_pct=9.9, custo_fixo_transacao=0, imposto_pct=6,
                     custo_entrega=12, reembolso_pct=8, cpa_real=180)
        relatorio(r)
        return 0

    if args.interativo:
        print("\nEnter aceita o valor entre colchetes.\n")
        ticket = perguntar("Preço à vista (R$)", 497.0)
        meta = perguntar("Meta de faturamento por mês (R$)", 30000.0)
        conv = perguntar("Conversão da página (%)", 1.5)
        plat = perguntar("Taxa da plataforma (%)", 9.9)
        fixo = perguntar("Taxa fixa por transação (R$)", 0.0)
        imp = perguntar("Imposto (%)", 6.0)
        entrega = perguntar("Custo de entrega por aluno (R$)", 12.0)
        reemb = perguntar("Reembolso esperado (%)", 8.0)
        cpa_txt = input("CPA que você mede hoje (R$, Enter para pular): ").strip().replace(",", ".")
        cpa = float(cpa_txt) if cpa_txt else None
    else:
        ticket, meta, conv = args.ticket, args.meta_mensal, args.conversao
        plat, fixo, imp = args.custo_plataforma, args.custo_fixo_transacao, args.imposto
        entrega, reemb, cpa = args.custo_entrega, args.reembolso, args.cpa_real

    try:
        r = calcular(ticket, meta, conv, plat, fixo, imp, entrega, reemb, cpa)
    except ValueError as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1

    relatorio(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
