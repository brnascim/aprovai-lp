#!/usr/bin/env python3
"""Audita a copy de um anúncio antes de publicar.

Checa: promessa de renda/garantia, atributo pessoal, escassez suspeita, limites de
caracteres, CTA ausente, aberturas fracas e excesso de texto na arte.

Uso:
    python3 validar_copy.py anuncio.json
    python3 validar_copy.py --demo
    python3 validar_copy.py --template > anuncio.json
    python3 validar_copy.py --texto "Ganhe R$ 10 mil por mês trabalhando de casa"

Saída: lista de achados por severidade. Código de saída 1 se houver BLOQUEIO.
Isto não substitui a leitura de ../references/politicas-meta.md.
"""

import argparse
import json
import re
import sys
from pathlib import Path

LIMITES = {
    "texto_primario_1a_linha": 125,   # antes do "ver mais" no feed
    "headline": 40,
    "descricao": 30,
    "texto_arte_principal": 8,        # em palavras
    "slide": 20,                      # em palavras
}

# (regex, severidade, mensagem, sugestão)
REGRAS = [
    # --- promessa de renda / garantia de resultado ---
    (r"\b(ganhe|fature|lucre|receba|embolse)\b[^.!?]{0,40}\br?\$\s*[\d.,]+",
     "BLOQUEIO", "Promessa de renda com valor",
     "Tire o número da promessa. Fale do processo: 'o método que uso para...'"),
    (r"\b(renda|lucro|retorno|ganho)s?\s+(garantid|cert|assegurad)\w*",
     "BLOQUEIO", "Renda/lucro garantido",
     "Substitua por 'resultado depende de aplicação' e descreva o método"),
    (r"\bresultado\s+garantid\w+", "BLOQUEIO", "Resultado garantido",
     "Troque por garantia de reembolso com prazo e condição escritas"),
    (r"\b(100%\s*(de\s*)?(garantid|aprovaç|sucesso)\w*|infal[íi]vel|sem\s+risco\s+nenhum)",
     "BLOQUEIO", "Absolutismo ('100%', 'infalível')",
     "Nenhum método é infalível. Descreva o que o produto faz e a garantia real"),
    (r"\b(aprovaç[ãa]o|emagrecimento|cura)\s+garantid\w+", "BLOQUEIO",
     "Garantia em nicho sensível",
     "Nicho regulado: remova a garantia de resultado (ver nichos-sensiveis.md)"),
    (r"\b(cura|curar)\s+(a|o|sua|seu)\s+\w+", "ALERTA", "Promessa de cura",
     "Promessa de cura é vedada fora de contexto médico regulamentado"),

    # --- atributo pessoal ---
    (r"\bvoc[êe]\s+(est[áa]|é|tem|sofre|vive)\s+(endividad|acima\s+do\s+peso|gord|obes|"
     r"deprimid|ansios|desempregad|falid|sozinh|solteir|doente|viciad)\w*",
     "BLOQUEIO", "Atributo pessoal (afirma algo sobre a pessoa)",
     "Troque 'você está X' por 'para quem quer Y' ou descreva a situação, não a pessoa"),
    (r"\b(cansad[oa]\s+de\s+(ser|estar|ter))\b", "ALERTA",
     "Possível atributo pessoal ('cansado de ser/estar...')",
     "Reformule para a situação: 'quando [situação acontece]...'"),
    (r"\bvoc[êe]\s+(que\s+)?(é|est[áa])\s+(gord|magr|vel|jovem|negr|branc|pobre|rico)\w*",
     "BLOQUEIO", "Atributo pessoal protegido",
     "Remova. Segmente por interesse e objetivo, nunca por característica pessoal"),

    # --- escassez / urgência suspeita ---
    (r"\b[úu]ltim(as|os)\s+\d+\s+(vagas|unidades|c[óo]pias)", "ALERTA",
     "Escassez numérica",
     "Só use se as vagas forem realmente limitadas e verificáveis"),
    (r"\b(s[óo]\s+hoje|acaba\s+(hoje|em\s+\d+\s*(h|min))|[úu]ltimas?\s+horas?)",
     "ALERTA", "Urgência com prazo",
     "O prazo precisa ser verdadeiro: se comprar amanhã, a condição tem que ser outra"),
    (r"\bde\s+r?\$\s*[\d.,]+\s+por\s+r?\$\s*[\d.,]+", "ALERTA",
     "Preço 'de/por' (ancoragem)",
     "Só é legítimo se o preço cheio já foi praticado de verdade"),

    # --- exagero e estética de golpe ---
    (r"\b(segredo|m[ée]todo\s+secreto)\b[^.!?]{0,40}\b(banco|governo|ningu[ée]m\s+te\s+conta)",
     "ALERTA", "Narrativa conspiratória",
     "Padrão associado a golpe: alta rejeição, CPM caro"),
    (r"\b(sem\s+esfor[çc]o|sem\s+fazer\s+nada|dinheiro\s+f[áa]cil|f[óo]rmula\s+m[áa]gica|"
     r"do\s+zero\s+ao\s+milh[ãa]o)", "ALERTA", "Promessa de facilidade irreal",
     "Descreva o esforço real. Facilidade irreal gera reembolso e reprovação"),
    (r"\b(ú|u)nica\s+chance\b", "ALERTA", "Exagero de exclusividade",
     "Use apenas se for verdade literal"),

    # --- forma ---
    (r"^(voc[êe]\s+sabia|aten[çc][ãa]o!|ol[áa],?\s+tudo\s+bem|imagine\s+poder)",
     "MELHORIA", "Abertura fraca",
     "A 1ª linha é headline. Comece com público + situação, número ou frase literal dele"),
    (r"[A-ZÀ-Ú]{15,}", "MELHORIA", "Trecho em CAIXA ALTA",
     "Caixa alta em bloco reduz leitura e cheira a spam"),
    (r"(curt[ea]|salv[ae]|comente|compartilhe)[^.!?]{0,30}(e|,)\s*(curt|salv|coment|compartilh)",
     "MELHORIA", "Mais de uma ação pedida",
     "Peça UMA ação. Múltiplos pedidos diluem e reduzem todos"),
]

EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]"
)

TEMPLATE = {
    "nome": "Criativo 1 - dor nomeada",
    "tipo": "estatico",
    "nivel_consciencia": 2,
    "texto_arte_principal": "4 dias fechando folha é opcional",
    "texto_arte_apoio": "Para escritório de contabilidade com até 5 pessoas",
    "texto_primario": "",
    "headline": "",
    "descricao": "",
    "cta": "Saiba mais",
    "slides": [],
    "prova_declarada": []
}

DEMO = {
    "nome": "Criativo demo - com problemas de propósito",
    "tipo": "estatico",
    "nivel_consciencia": 2,
    "texto_arte_principal": "GANHE R$ 10 MIL POR MÊS TRABALHANDO DE CASA SEM ESFORÇO",
    "texto_arte_apoio": "Últimas 3 vagas!",
    "texto_primario": "Você sabia que você está endividado e pode mudar isso? "
                      "Resultado garantido em 30 dias. De R$ 5.000 por R$ 297. "
                      "Curte, salva e compartilha esse post!",
    "headline": "O método secreto que os bancos não querem que você saiba",
    "descricao": "Aproveite agora essa oportunidade única do mercado",
    "cta": "",
    "slides": [],
    "prova_declarada": []
}


def achar(texto, campo, achados):
    if not texto:
        return
    baixo = texto.lower()
    for padrao, sev, titulo, sugestao in REGRAS:
        m = re.search(padrao, baixo, re.IGNORECASE | re.MULTILINE)
        if m:
            achados.append({
                "severidade": sev, "campo": campo, "titulo": titulo,
                "trecho": texto[max(0, m.start() - 10):m.end() + 10].strip(),
                "sugestao": sugestao,
            })


def contar_palavras(texto):
    return len([p for p in re.split(r"\s+", texto.strip()) if p])


def validar(anuncio):
    achados = []
    campos_texto = ["texto_arte_principal", "texto_arte_apoio", "texto_primario",
                    "headline", "descricao"]

    for campo in campos_texto:
        achar(anuncio.get(campo, ""), campo, achados)

    for i, slide in enumerate(anuncio.get("slides") or [], 1):
        texto = slide if isinstance(slide, str) else slide.get("texto", "")
        achar(texto, f"slide {i}", achados)
        if contar_palavras(texto) > LIMITES["slide"]:
            achados.append({
                "severidade": "MELHORIA", "campo": f"slide {i}",
                "titulo": f"Slide com {contar_palavras(texto)} palavras "
                          f"(limite {LIMITES['slide']})",
                "trecho": texto[:60], "sugestao": "Uma ideia por slide. Quebre em dois"})

    # limites de caracteres
    for campo, limite in (("headline", LIMITES["headline"]),
                          ("descricao", LIMITES["descricao"])):
        valor = anuncio.get(campo, "") or ""
        if len(valor) > limite:
            achados.append({
                "severidade": "MELHORIA", "campo": campo,
                "titulo": f"{len(valor)} caracteres (corta em ~{limite})",
                "trecho": valor, "sugestao": f"Reduza para até {limite} caracteres"})

    principal = anuncio.get("texto_arte_principal", "") or ""
    if contar_palavras(principal) > LIMITES["texto_arte_principal"]:
        achados.append({
            "severidade": "MELHORIA", "campo": "texto_arte_principal",
            "titulo": f"{contar_palavras(principal)} palavras na arte "
                      f"(limite {LIMITES['texto_arte_principal']})",
            "trecho": principal,
            "sugestao": "Texto grande na arte não é lido no feed. Corte para o essencial"})

    primario = anuncio.get("texto_primario", "") or ""
    if primario:
        primeira = primario.split("\n")[0]
        if len(primeira) > LIMITES["texto_primario_1a_linha"]:
            achados.append({
                "severidade": "MELHORIA", "campo": "texto_primario",
                "titulo": f"1ª linha com {len(primeira)} caracteres "
                          f"(some no 'ver mais' após ~{LIMITES['texto_primario_1a_linha']})",
                "trecho": primeira[:70] + "...",
                "sugestao": "Coloque o gancho inteiro nos primeiros 125 caracteres"})
        if len(EMOJI.findall(primario)) > 4:
            achados.append({
                "severidade": "MELHORIA", "campo": "texto_primario",
                "titulo": f"{len(EMOJI.findall(primario))} emojis",
                "trecho": "", "sugestao": "Até 3–4 emojis. Excesso parece spam"})

    if not (anuncio.get("cta") or "").strip():
        achados.append({
            "severidade": "ALERTA", "campo": "cta", "titulo": "CTA ausente",
            "trecho": "", "sugestao": "Defina o botão nativo compatível com o destino"})

    # prova sem lastro
    texto_todo = " ".join(str(anuncio.get(c, "") or "") for c in campos_texto)
    # "+3.000 alunos", "mais de 50 clientes", "12 mil pessoas", "aumento de 30%"
    # — mas não "escritório com até 5 pessoas", que não é alegação de prova
    tem_numero_prova = re.search(
        r"(?:(?:\+|mais\s+de|j[áa])\s*\d[\d.,]*|\b\d{2,}[\d.,]*\s*(?:mil\s+)?)"
        r"\s*(?:alunos|clientes|pessoas|casos|empresas|vendas)\b"
        r"|\b\d+(?:[.,]\d+)?\s*%",
        texto_todo, re.IGNORECASE)
    if tem_numero_prova and not anuncio.get("prova_declarada"):
        achados.append({
            "severidade": "ALERTA", "campo": "prova",
            "titulo": "Número de prova sem lastro declarado",
            "trecho": tem_numero_prova.group(0),
            "sugestao": "Preencha 'prova_declarada' com a fonte, ou marque [PROVA: falta]"})

    ordem = {"BLOQUEIO": 0, "ALERTA": 1, "MELHORIA": 2}
    achados.sort(key=lambda a: ordem[a["severidade"]])
    return achados


def imprimir(anuncio, achados):
    icone = {"BLOQUEIO": "⛔", "ALERTA": "⚠️ ", "MELHORIA": "💡"}
    print(f"\n# Auditoria — {anuncio.get('nome', 'anúncio')}\n")

    if not achados:
        print("✅ Nenhum problema encontrado pelas regras automáticas.\n"
              "   Faça mesmo assim a checagem manual de politicas-meta.md "
              "(prova real, coerência com o destino).\n")
        return 0

    contagem = {s: sum(1 for a in achados if a["severidade"] == s)
                for s in ("BLOQUEIO", "ALERTA", "MELHORIA")}
    print(f"{contagem['BLOQUEIO']} bloqueio(s) · {contagem['ALERTA']} alerta(s) · "
          f"{contagem['MELHORIA']} melhoria(s)\n")

    for a in achados:
        print(f"{icone[a['severidade']]} **{a['titulo']}** — campo `{a['campo']}`")
        if a["trecho"]:
            print(f"   trecho: \"{a['trecho']}\"")
        print(f"   → {a['sugestao']}\n")

    if contagem["BLOQUEIO"]:
        print("⛔ Não publique com bloqueio pendente: reprova no Meta e/ou "
              "configura publicidade enganosa (CDC art. 37).\n")
        return 1
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("arquivo", nargs="?", help="JSON do anúncio")
    p.add_argument("--demo", action="store_true", help="roda um anúncio problemático de exemplo")
    p.add_argument("--template", action="store_true", help="imprime o JSON em branco")
    p.add_argument("--texto", help="audita um texto solto")
    args = p.parse_args()

    if args.template:
        print(json.dumps(TEMPLATE, indent=2, ensure_ascii=False))
        return 0

    if args.texto:
        anuncio = {"nome": "texto avulso", "texto_primario": args.texto, "cta": "-"}
    elif args.demo:
        anuncio = DEMO
    elif args.arquivo:
        caminho = Path(args.arquivo)
        if not caminho.exists():
            print(f"erro: arquivo não encontrado: {caminho}", file=sys.stderr)
            return 1
        try:
            anuncio = json.loads(caminho.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"erro: JSON inválido: {e}", file=sys.stderr)
            return 1
    else:
        p.print_help()
        return 0

    if isinstance(anuncio, list):
        codigo = 0
        for item in anuncio:
            codigo = max(codigo, imprimir(item, validar(item)))
        return codigo

    return imprimir(anuncio, validar(anuncio))


if __name__ == "__main__":
    sys.exit(main())
