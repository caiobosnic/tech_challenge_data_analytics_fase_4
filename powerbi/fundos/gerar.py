# -*- coding: utf-8 -*-
"""Planos de fundo do dashboard TC4. Geometria copiada do TC3, paleta do MANUAL 2.3."""
import json, os

L, A = 1920, 1080
FONTE = "Carlito, Calibri, Segoe UI, sans-serif"

AREIA, CARD, BORDA = "#E7E2D9", "#FBFAF7", "#DAD4C8"
NAVY, NAVY_CLARO, LATAO = "#1F3A5F", "#2E4E78", "#A6824C"
TINTA, TINTA_FRACA, TINTA_MENU = "#5C5A54", "#8A877E", "#C9D2DE"

BARRA = 232
CAB_H, FIL_Y, FIL_H = 104, 104, 78
SLOT_X, SLOT_Y, SLOT_L, SLOT_H, SLOT_PASSO = 260.0, 128, 290.4, 42, 304.4
KPI_Y, KPI_H, KPI_L, KPI_PASSO = 210, 104, 393.0, 413.0
GRAF_Y, GRAF_H = 334, 700
ESQ_L, DIR_X, DIR_L = 946.56, 1226.56, 665.44

ICONES = {
 "inicio":   "M3 11 L12 3 L21 11 M5 10 V20 H10 V15 H14 V20 H19 V10",
 "barras":   "M3 21 H21 M7 21 V12 M12 21 V5 M17 21 V15",
 "grade":    "M3 4 H10 V11 H3 Z M14 4 H21 V11 H14 Z M3 14 H10 V21 H3 Z M14 14 H21 V21 H14 Z",
 "etiqueta": "M20 4 H13 L3 14 L10 21 L20 11 Z M16.2 8.2 L16.3 8.3",
 "balao":    "M4 5 H20 V16 H12 L7 20 V16 H4 Z M8 10 H16 M8 13 H13",
 "lampada":  "M13 2 L5 13 H11 L10 22 L19 10 H13 Z",
 "doc":      "M6 3 H15 L19 7 V21 H6 Z M15 3 V7 H19 M9 12 H16 M9 16 H16",
}

def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def txt(x, y, s, tam=12.5, peso=400, cor=TINTA, anc="start", op=1.0):
    return (f'<text x="{x}" y="{y}" font-family="{FONTE}" font-size="{tam}" '
            f'font-weight="{peso}" fill="{cor}" text-anchor="{anc}" opacity="{op}">{esc(s)}</text>')

def ret(x, y, w, h, fill, stroke=None, rx=None):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}"'
    if rx is not None: s += f' rx="{rx}"'
    s += f' fill="{fill}"'
    if stroke: s += f' stroke="{stroke}"'
    return s + '/>'

def icone(x, y, chave, cor):
    return (f'<g transform="translate({x},{y}) scale(0.9167)" fill="none" stroke="{cor}" '
            f'stroke-width="1.96" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="{ICONES[chave]}"/></g>')

def selo(x, y, rotulo):
    """Pastilha dourada: marca drill-through ou dica de ferramenta."""
    larg = 10 + len(rotulo) * 5.6
    return (ret(x, y, round(larg, 1), 22, AREIA, LATAO, 11) +
            txt(x + 12, y + 15, rotulo, 9.5, 600, LATAO))

def barra_lateral(paginas, ativa, marca, submarca):
    p = [ret(0, 0, BARRA, A, NAVY),
         ret(24, 30, 4, 30, LATAO, rx=2),
         txt(40, 46, marca, 15, 700, "#FFFFFF"),
         txt(40, 62, submarca, 10.5, 400, TINTA_MENU, op=0.75)]
    y = 127
    for i, (rotulo, ic) in enumerate(paginas):
        if i == ativa:
            p.append(ret(12, y - 11, 208, 46, NAVY_CLARO, rx=8))
            p.append(ret(12, y, 3, 24, LATAO, rx=1.5))
            cor, peso = "#FFFFFF", 600
        else:
            cor, peso = TINTA_MENU, 400
        p.append(icone(30, y, ic, cor))
        p.append(txt(66, y + 18, rotulo, 12.5, peso, cor))
        y += 52
    return "".join(p)

def cabecalho(titulo, subtitulo, pilula=None):
    p = [ret(BARRA, 0, L - BARRA, CAB_H, CARD),
         ret(BARRA, CAB_H - 1, L - BARRA, 1, BORDA),
         txt(260, 46, titulo, 25, 700, NAVY),
         txt(260, 72, subtitulo, 13, 400, TINTA)]
    if pilula:
        p.append(ret(1688.6, 34, 203.4, 30, AREIA, BORDA, 15))
        p.append(txt(1790.3, 54, pilula, 11.5, 600, TINTA, "middle"))
    return "".join(p)

def filtros(rotulos, coords, limpar=True):
    p = [ret(BARRA, FIL_Y, L - BARRA, FIL_H, AREIA)]
    for i, r in enumerate(rotulos):
        x = SLOT_X + i * SLOT_PASSO
        p.append(txt(x + 2, 122, r.upper(), 9.5, 700, TINTA_FRACA))
        p.append(ret(round(x, 1), SLOT_Y, SLOT_L, SLOT_H, CARD, BORDA, 8))
    if limpar:
        p.append(ret(1782, SLOT_Y, 110, SLOT_H, AREIA, LATAO, 8))
        p.append(txt(1837, 154, "Limpar filtros", 11.5, 600, LATAO, "middle"))
        coords["b_limpar"] = {"tipo": "botao", "card": [1782, SLOT_Y, 110, SLOT_H],
                              "util": [1782, SLOT_Y, 110, SLOT_H]}
    return "".join(p)

def kpis(itens, coords):
    p = []
    for i, it in enumerate(itens):
        x = KPI_X = round(SLOT_X + i * KPI_PASSO, 1)
        p.append(ret(x, KPI_Y, KPI_L, KPI_H, CARD, BORDA, 10))
        p.append(txt(x + 56, 244, it["nome"], 12.5, 600, TINTA))
        p.append(txt(x + 22, 300, it["base"], 10.5, 400, TINTA_FRACA))
        if it.get("selo"):
            p.append(selo(x + 293, 224, it["selo"]))
        coords[it["id"]] = {"tipo": "kpi", "card": [x, KPI_Y, KPI_L, KPI_H],
                            "util": [x + 20, KPI_Y + 36, KPI_L - 40, 52],
                            "selo": it.get("selo")}
    return "".join(p)

def card(x, y, w, h, titulo, sub, coords, cid, selo_txt=None):
    p = [ret(round(x, 2), y, round(w, 2), h, CARD, BORDA, 10),
         txt(round(x + 20, 2), y + 32, titulo, 15, 600, NAVY),
         txt(round(x + 20, 2), y + 50, sub, 11.5, 400, TINTA_FRACA)]
    if selo_txt:
        larg = 10 + len(selo_txt) * 5.6
        p.append(selo(round(x + w - larg - 14, 1), y + 14, selo_txt))
    coords[cid] = {"tipo": "grafico", "card": [round(x, 2), y, round(w, 2), h],
                   "util": [round(x + 16, 2), y + 66, round(w - 32, 2), h - 82],
                   "selo": selo_txt}
    return "".join(p)

def card_duplo(x, y, w, h, titulo, sub, metades, coords, cid, selo_txt=None):
    """Um card com dois numeros lado a lado. O rotulo de cada um vem do fundo."""
    p = [ret(round(x, 2), y, round(w, 2), h, CARD, BORDA, 10),
         txt(round(x + 20, 2), y + 32, titulo, 15, 600, NAVY),
         txt(round(x + 20, 2), y + 50, sub, 11.5, 400, TINTA_FRACA)]
    if selo_txt:
        larg = 10 + len(selo_txt) * 5.6
        sx = round(x + w - larg - 14, 1)
        p.append(selo(sx, y + 14, selo_txt))
        coords[cid + "_ir"] = {"tipo": "botao", "card": [sx, y + 14, round(larg, 1), 22],
                               "util": [sx, y + 14, round(larg, 1), 22]}
    meia = (w - 48) / 2
    p.append(ret(round(x + w / 2, 1), y + 84, 1, h - 120, BORDA))
    for i, m in enumerate(metades):
        mx = x + 16 + i * (meia + 16)
        centro = round(mx + meia / 2, 1)
        p.append(txt(centro, y + 110, m["rotulo"], 12.5, 600, TINTA, "middle"))
        for k, linha in enumerate(m["base"]):
            p.append(txt(centro, y + h - 54 + k * 16, linha, 10.5, 400, TINTA_FRACA, "middle"))
        coords[m["id"]] = {"tipo": "kpi", "card": [round(mx, 2), y + 84, round(meia, 2), h - 120],
                           "util": [round(mx, 2), y + 124, round(meia, 2), 58]}
    coords[cid] = {"tipo": "moldura", "card": [round(x, 2), y, round(w, 2), h],
                   "selo": selo_txt}
    return "".join(p)


# ---------------------------------------------------------------- texto corrido
# O fundo nao desenha dado que filtra. Desenha texto autoral: decisao, premissa, limite.
# Esse texto vem do CSV, entao a tela e o modelo nunca divergem.
ESTREITOS = set("iíjltfrI.,:;'\"!|()[]- ")
LARGOS = set("mwMW@%")
ALERTAS = []

def largura(s, tam):
    """Largura aproximada em px. Calibri/Carlito: estreito 0,30, largo 0,84, resto 0,52."""
    return sum(0.30 if c in ESTREITOS else 0.84 if c in LARGOS else 0.52 for c in s) * tam

def linhas(s, tam, larg, maximo, onde):
    """Quebra por palavra. Se passar do orcamento de linhas, grita em vez de cortar calado."""
    saida, atual = [], ""
    for palavra in str(s).split():
        teste = (atual + " " + palavra).strip()
        if atual and largura(teste, tam) > larg:
            saida.append(atual); atual = palavra
        else:
            atual = teste
    if atual:
        saida.append(atual)
    if len(saida) > maximo:
        ALERTAS.append(f"{onde}: {len(saida)} linhas, cabem {maximo}")
    return saida


def bloco_recomendacao(x, y, w, h, n, rec, coords):
    """Decisao, por que, indicador vivo e o botao para conferir. Nada de tabela."""
    PW = 236.0
    px = round(x + w - PW - 24, 2)
    tx = round(x + 24, 2)
    tw = px - tx - 24
    p = [ret(round(x, 2), y, round(w, 2), h, CARD, BORDA, 10),
         f'<circle cx="{round(x+39,2)}" cy="{y+33}" r="15" fill="{NAVY}"/>',
         txt(round(x + 39, 2), y + 38, n, 13, 700, "#FFFFFF", "middle"),
         txt(round(x + 66, 2), y + 38, rec["decisao"], 15, 600, NAVY),
         ret(tx, y + 60, round(w - 48, 2), 1, BORDA),
         txt(tx, y + 86, "POR QUÊ", 9.5, 700, TINTA_FRACA)]
    for i, l in enumerate(linhas(rec["por_que"], 11.5, tw, 5, f"rec {n} por_que")):
        p.append(txt(tx, y + 106 + i * 16, l, 11.5, 400, TINTA))
    p.append(txt(tx, y + 206, "BASE DO NÚMERO", 9.5, 700, TINTA_FRACA))
    for i, l in enumerate(linhas(rec["valor_indicador"], 10.5, tw, 3, f"rec {n} valor")):
        p.append(txt(tx, y + 224 + i * 14, l, 10.5, 400, TINTA_FRACA))

    p.append(ret(px, y + 74, PW, 140, AREIA, rx=8))
    p.append(ret(px, y + 86, 3, 116, LATAO, rx=1.5))
    for i, l in enumerate(linhas(rec["indicador"], 10.5, PW - 40, 3, f"rec {n} indicador")):
        p.append(txt(round(px + PW / 2, 2), y + 172 + i * 13.5, l, 10.5, 400, TINTA, "middle"))
    coords[f"r{n}_valor"] = {"tipo": "kpi", "card": [px, y + 74, PW, 140],
                             "util": [round(px + 14, 2), y + 78, round(PW - 28, 2), 76]}

    p.append(ret(px, y + 228, PW, 30, AREIA, LATAO, 8))
    p.append(txt(round(px + PW / 2, 2), y + 248, "conferir em " + rec["onde_ver"],
                 10.5, 600, LATAO, "middle"))
    coords[f"r{n}_ir"] = {"tipo": "botao", "card": [px, y + 228, PW, 30],
                          "util": [px, y + 228, PW, 30], "destino": rec["onde_ver"]}
    return "".join(p)


def bloco_fonte(x, y, w, h, titulo, sub, itens):
    """Premissa e limite sao texto autoral, nao medida. Entao viram texto, nao tabela.
    O espaco que sobra vira respiro entre os itens, para o card nao ficar oco embaixo."""
    p = [ret(round(x, 2), y, round(w, 2), h, CARD, BORDA, 10),
         txt(round(x + 24, 2), y + 34, titulo, 16, 600, NAVY),
         txt(round(x + 24, 2), y + 54, sub, 11.5, 400, TINTA_FRACA),
         ret(round(x + 24, 2), y + 70, round(w - 48, 2), 1, BORDA)]
    quebras = [linhas(it["detalhe"], 12, w - 86, 4, f"{titulo} / {it['item']}") for it in itens]
    alto = sum(22 + len(q) * 17 for q in quebras)
    folga = (y + h - 24) - (y + 102) - alto
    respiro = max(16, min(80, folga / max(len(itens) - 1, 1))) if len(itens) > 1 else 16
    yy = y + 102
    for it, q in zip(itens, quebras):
        p.append(ret(round(x + 24, 2), yy - 12, 3, 15, LATAO, rx=1.5))
        p.append(txt(round(x + 38, 2), yy, it["item"], 13.5, 600, NAVY))
        yy += 22
        for l in q:
            p.append(txt(round(x + 38, 2), yy, l, 12, 400, TINTA))
            yy += 17
        yy += respiro
    if yy - respiro > y + h - 16:
        ALERTAS.append(f"{titulo}: estourou o card em {round(yy - respiro - (y + h - 16))}px")
    return "".join(p)


def bloco_caminho(x, y, w, h, titulo, sub, etapas):
    """O caminho do dado e um fluxo, entao desenha como fluxo e nao como lista."""
    p = [ret(round(x, 2), y, round(w, 2), h, CARD, BORDA, 10),
         txt(round(x + 24, 2), y + 34, titulo, 16, 600, NAVY),
         txt(round(x + 24, 2), y + 54, sub, 11.5, 400, TINTA_FRACA),
         ret(round(x + 24, 2), y + 70, round(w - 48, 2), 1, BORDA)]
    ex, ew = round(x + 40, 2), round(w - 80, 2)
    quebras = [linhas(e["detalhe"], 11, ew - 76, 2, f"{titulo} / {e['item']}") for e in etapas]
    alturas = [max(66, 40 + len(q) * 15) for q in quebras]
    folga = (y + h - 26) - (y + 98) - sum(alturas)
    passo = max(14, min(34, folga / max(len(etapas) - 1, 1)))
    yy = y + 98
    for k, (e, q, alt) in enumerate(zip(etapas, quebras, alturas)):
        p.append(ret(ex, yy, ew, alt, AREIA, rx=8))
        p.append(ret(ex, round(yy + 14, 2), 3, round(alt - 28, 2), LATAO, rx=1.5))
        p.append(f'<circle cx="{round(ex+40,2)}" cy="{round(yy+alt/2,2)}" r="15" fill="{NAVY}"/>')
        p.append(txt(round(ex + 40, 2), round(yy + alt / 2 + 5, 2),
                     e["item"].split(".")[0].strip(), 13, 700, "#FFFFFF", "middle"))
        rotulo = e["item"].split(".", 1)[-1].strip()
        p.append(txt(round(ex + 70, 2), yy + 26, rotulo, 13, 600, NAVY))
        for n, l in enumerate(q):
            p.append(txt(round(ex + 70, 2), yy + 44 + n * 15, l, 11, 400, TINTA))
        if k < len(etapas) - 1:
            cx = round(ex + 40, 2)
            p.append(f'<path d="M{cx} {round(yy+alt+3,2)} V{round(yy+alt+passo-7,2)}" '
                     f'stroke="{LATAO}" stroke-width="2" fill="none"/>')
            p.append(f'<path d="M{cx-4} {round(yy+alt+passo-11,2)} L{cx} {round(yy+alt+passo-5,2)} '
                     f'L{cx+4} {round(yy+alt+passo-11,2)}" stroke="{LATAO}" stroke-width="2" '
                     f'fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
        yy += alt + passo
    if yy - passo > y + h - 16:
        ALERTAS.append(f"{titulo}: estourou o card em {round(yy - passo - (y + h - 16))}px")
    return "".join(p)


def rodape(fonte):
    return txt(260, 1062, fonte, 10.5, 400, TINTA_FRACA)

def montar(partes):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{L}" height="{A}" '
            f'viewBox="0 0 {L} {A}">{ret(0,0,L,A,AREIA)}{"".join(partes)}</svg>')


# ============================================================ as 6 telas
MENU = [("Visão executiva",       "barras"),
        ("Produtos e categorias", "grade"),
        ("Preços e descontos",    "etiqueta"),
        ("Customer insights",     "balao"),
        ("Recomendações",         "lampada"),
        ("Fontes e premissas",    "doc")]

MARCA, SUBMARCA = "Amazon", "Portfólio e cliente"
FONTE_RODAPE = ("Fonte: Amazon Sales Dataset (Kaggle) · 1.351 produtos, 10.598 avaliações com texto · "
                "valores em rupia indiana, convertidos pela segmentação de moeda")

def achar_resultados():
    base = os.path.dirname(os.path.abspath(__file__))
    for rel in ("../../results", "../saida_real", "../results", "results"):
        caminho = os.path.normpath(os.path.join(base, rel))
        if os.path.isfile(os.path.join(caminho, "dRecomendacao.csv")):
            return caminho
    raise SystemExit("nao achei dRecomendacao.csv. Rode o notebook primeiro.")

def ler_csv(pasta, nome):
    import csv
    with open(os.path.join(pasta, nome), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

RESULTADOS = achar_resultados()
RECOMENDACOES = sorted(ler_csv(RESULTADOS, "dRecomendacao.csv"), key=lambda r: int(r["ordem"]))
FONTES = sorted(ler_csv(RESULTADOS, "dFonte.csv"), key=lambda r: int(r["ordem"]))
print(f"lendo texto autoral de {RESULTADOS}: "
      f"{len(RECOMENDACOES)} recomendações, {len(FONTES)} itens de fonte\n")

coords = {}
paginas = {}

# ---------------------------------------------------------------- 1
c = {}
paginas["01_visao_executiva"] = montar([
 barra_lateral(MENU, 0, MARCA, SUBMARCA),
 cabecalho("Visão executiva",
           "Onde o portfólio ganha e onde perde, em uma tela",
           "base: 1.351 produtos em 9 categorias"),
 filtros(["Categoria", "Faixa de preço", "Faixa de nota", "Moeda"], c),
 kpis([{"id":"kpi_produtos","nome":"Produtos no portfólio","base":"após consolidar IDs repetidos"},
       {"id":"kpi_avaliacoes","nome":"Avaliações declaradas","base":"rating_count somado","selo":"dica: o que mede"},
       {"id":"kpi_nota","nome":"Nota média ponderada","base":"ponderada por nº de avaliações","selo":"dica: ponderação"},
       {"id":"kpi_desconto","nome":"Desconto médio","base":"média simples do percentual"}], c),
 card(260, GRAF_Y, ESQ_L, 340,
      "O portfólio é de eletrônicos, não um catálogo diverso",
      "nº de produtos por categoria de nível 1", c, "g_cat_produtos"),
 card(260, 694, ESQ_L, 340,
      "E a atenção do cliente segue a mesma concentração",
      "nº de avaliações por categoria de nível 1, escala própria", c, "g_cat_avaliacoes"),
 card(DIR_X, GRAF_Y, DIR_L, 340,
      "Onde a nota se concentra",
      "produtos por faixa de nota, de 2,0 a 5,0", c, "g_dist_nota"),
 card_duplo(DIR_X, 694, DIR_L, 340,
      "Dois bolsos de oportunidade",
      "produtos que já têm tráfego, e produtos que mereciam ter", [
        {"id": "kpi_bolso_ruim", "rotulo": "Muito avaliado, nota baixa",
         "base": ["avaliações acima da mediana", "e nota no quartil inferior"]},
        {"id": "kpi_bolso_bom", "rotulo": "Nota alta, pouco visto",
         "base": ["nota no quartil superior", "e menos de mil avaliações"]},
      ], c, "g_bolsos", "ver os produtos"),
 rodape(FONTE_RODAPE)])
coords["01_visao_executiva"] = c

# ---------------------------------------------------------------- 2
c = {}
paginas["02_produtos_categorias"] = montar([
 barra_lateral(MENU, 1, MARCA, SUBMARCA),
 cabecalho("Produtos e categorias",
           "Quem sustenta o portfólio e quem só ocupa espaço",
           "base: 211 caminhos, até 7 níveis"),
 filtros(["Categoria", "Faixa de preço", "Faixa de nota", "Moeda"], c),
 kpis([{"id":"kpi_cat1","nome":"Categorias de nível 1","base":"3 delas concentram 97%"},
       {"id":"kpi_caminhos","nome":"Caminhos distintos","base":"hierarquia completa"},
       {"id":"kpi_mediana_aval","nome":"Mediana de avaliações","base":"por produto"},
       {"id":"kpi_top_produto","nome":"Produto mais avaliado","base":"maior rating_count"}], c),
 card(260, GRAF_Y, ESQ_L, GRAF_H,
      "Hierarquia de categorias",
      "nível 2, dentro do nível 1 que você escolher no filtro de categoria", c,
      "g_hierarquia"),
 card(DIR_X, GRAF_Y, DIR_L, 340,
      "Nota por faixa de engajamento",
      "nota média ponderada em cada faixa de nº de avaliações", c, "g_dispersao", "dica: produto"),
 card(DIR_X, 694, DIR_L, 340,
      "Os 10 mais avaliados da base",
      "posto fixo por nº de avaliações: o filtro de categoria mostra quais destes 10 são dela", c, "g_top10"),
 rodape(FONTE_RODAPE)])
coords["02_produtos_categorias"] = c

# ---------------------------------------------------------------- 3
c = {}
paginas["03_precos_descontos"] = montar([
 barra_lateral(MENU, 2, MARCA, SUBMARCA),
 cabecalho("Preços e estratégia comercial",
           "Desconto compra avaliação? E a que preço",
           "valores na moeda selecionada"),
 filtros(["Categoria", "Faixa de preço", "Faixa de desconto", "Moeda"], c),
 kpis([{"id":"kpi_preco_desc","nome":"Preço médio com desconto","base":"na moeda selecionada","selo":"dica: câmbio"},
       {"id":"kpi_preco_cheio","nome":"Preço cheio médio","base":"na moeda selecionada"},
       {"id":"kpi_desconto_med","nome":"Desconto médio","base":"percentual, sem conversão"},
       {"id":"kpi_economia","nome":"Economia oferecida","base":"preço cheio menos o com desconto"}], c),
 card(260, GRAF_Y, ESQ_L, 340,
      "Desconto e nota caminham juntos?",
      "nota média ponderada em cada faixa de desconto: Pearson -0,16, Spearman -0,15", c, "g_desc_nota"),
 card(260, 694, ESQ_L, 340,
      "Satisfação por categoria",
      "nota ponderada por categoria de nível 1, só as que têm 10 produtos ou mais", c, "g_nota_cat"),
 card(DIR_X, GRAF_Y, DIR_L, 340,
      "Desconto médio por categoria",
      "nível 1, ordenado do maior para o menor", c, "g_desc_cat"),
 card(DIR_X, 694, DIR_L, 340,
      "Faixa de preço e satisfação",
      "nota média ponderada por faixa de preço", c, "g_faixa_preco"),
 rodape(FONTE_RODAPE)])
coords["03_precos_descontos"] = c

# ---------------------------------------------------------------- 4
c = {}
paginas["04_customer_insights"] = montar([
 barra_lateral(MENU, 3, MARCA, SUBMARCA),
 cabecalho("Customer insights",
           "O que o cliente escreve, e não só a nota que ele dá",
           "base: 10.598 avaliações com texto"),
 filtros(["Categoria", "Percepção", "Faixa de nota", "Moeda"], c),
 kpis([{"id":"kpi_texto","nome":"Avaliações com texto","base":"o arquivo traz bem menos que as declaradas","selo":"dica: a diferença"},
       {"id":"kpi_acima","nome":"Produtos acima da base","base":"nota ≥ p75","selo":"dica: o corte"},
       {"id":"kpi_media","nome":"Produtos na média","base":"entre p25 e p75"},
       {"id":"kpi_abaixo","nome":"Produtos abaixo da base","base":"nota ≤ p25"}], c),
 card(260, GRAF_Y, ESQ_L, GRAF_H,
      "O que separa quem reclama de quem elogia",
      "os 8 termos de cada lado com maior diferença. Comparação da base inteira: não acompanha os filtros", c,
      "g_termos_comparados", "dica: o termo"),
 card(DIR_X, GRAF_Y, DIR_L, 340,
      "Elogio: o que mais aparece",
      "os 15 de maior peso acima da base. Calculado na base inteira: não acompanha os filtros", c, "g_termos_acima"),
 card(DIR_X, 694, DIR_L, 340,
      "Reclamação: o que mais aparece",
      "os 15 de maior peso abaixo da base. Calculado na base inteira: não acompanha os filtros", c, "g_termos_abaixo"),
 rodape(FONTE_RODAPE)])
coords["04_customer_insights"] = c

# ---------------------------------------------------------------- 5
# Seis blocos de leitura. A decisao e o "por que" sao texto autoral, entao ficam no fundo.
# O indicador e medida, entao fica num visual de cartao em cima do painel bege.
c = {}
BLOCO_L = (1632.0 - 20) / 2
BLOCO_A = (884 - 40) / 3
_blocos = []
for k, rec in enumerate(RECOMENDACOES):
    bx = 260 + (k % 2) * (BLOCO_L + 20)
    by = int(150 + (k // 2) * (BLOCO_A + 20))
    _blocos.append(bloco_recomendacao(bx, by, BLOCO_L, int(BLOCO_A), rec["ordem"], rec, c))
paginas["05_recomendacoes"] = montar([
 barra_lateral(MENU, 4, MARCA, SUBMARCA),
 cabecalho("Recomendações",
           "Seis decisões: o que fazer, por quê, e o número que sustenta",
           "leitura de cima para baixo"),
 *_blocos,
 rodape("Decisão e justificativa são interpretação nossa sobre a análise. "
        "O número de cada bloco é medida do modelo e acompanha o filtro."),
])
coords["05_recomendacoes"] = c

# ---------------------------------------------------------------- 6
# Premissa e limite nao sao medida: sao texto declarado. Viram texto lido do dFonte.csv,
# entao a tela e a tabela do modelo nunca divergem. Altura de cada card segue o conteudo:
# o de 3 itens fica menor que o de 4, em vez de todos iguais com buraco embaixo.
c = {}
def _itens(secao):
    return [f for f in FONTES if f["secao"] == secao]
paginas["06_fontes_premissas"] = montar([
 barra_lateral(MENU, 5, MARCA, SUBMARCA),
 cabecalho("Fontes e premissas",
           "De onde veio cada número e o que foi assumido",
           " · ".join(f"{sum(1 for f in FONTES if f['secao'] == sec)} {rot}"
                      for sec, rot in [("Premissas", "premissas"), ("Limites", "limites"),
                                       ("Tratamentos", "tratamentos")])),
 bloco_fonte(260, 150, 806.0, 394, "As premissas declaradas",
             "sem elas, três números desta análise não se sustentam", _itens("Premissas")),
 bloco_fonte(260, 564, 806.0, 470, "O que a base não mede",
             "limites que precisam ser ditos antes da conclusão", _itens("Limites")),
 bloco_caminho(1086.0, 150, 806.0, 470, "O caminho do dado",
               "da linha baixada no Kaggle até a tabela do modelo", _itens("Caminho")),
 bloco_fonte(1086.0, 640, 806.0, 394, "Tratamentos aplicados",
             "consolidação de IDs, hierarquia e extração de termos", _itens("Tratamentos")),
 rodape(FONTE_RODAPE)])
coords["06_fontes_premissas"] = c

def dica_texto(pid, titulo, texto, a, b, rodape, coords, titulo_medida=None):
    """Dica de 400x300: o que o indicador significa em cima, dois numeros vivos embaixo.
    Molde conferido no page.json de 297783e59b0c2b2b3906 do TC3."""
    c = {}
    p = [ret(0, 0, 400, 300, CARD), ret(0, 0, 400, 5, NAVY)]
    if titulo_medida:
        c["t_titulo"] = {"tipo": "kpi", "card": [16, 18, 368, 44], "util": [16, 18, 368, 44]}
        p.append(ret(16, 18, 368, 44, AREIA, rx=6))
        y0 = 70
    else:
        p.append(txt(20, 36, titulo, 14, 600, NAVY))
        y0 = 58
    p.append(ret(20, y0, 360, 1, BORDA))
    for i, l in enumerate(linhas(texto, 11, 356, 5, f"{pid} texto")):
        p.append(txt(20, y0 + 22 + i * 15, l, 11, 400, TINTA))
    for i, (rotulo, cor_rotulo, cid) in enumerate([a, b]):
        x = 18 + i * 188
        p.append(txt(x + 2, 164, rotulo, 9, 700, cor_rotulo))
        p.append(ret(x, 172, 176, 46, AREIA, rx=6))
        c[cid] = {"tipo": "kpi", "card": [x, 172, 176, 46], "util": [x, 172, 176, 46]}
    p.append(ret(20, 240, 360, 1, BORDA))
    for i, l in enumerate(linhas(rodape, 10, 356, 3, f"{pid} rodape")):
        p.append(txt(20, 262 + i * 13, l, 10, 400, TINTA_FRACA))
    paginas[pid] = (f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" '
                    f'viewBox="0 0 400 300">{"".join(p)}</svg>')
    coords[pid] = c


# ---------------------------------------------------------------- 7, os produtos em foco
# As recomendacoes 3 e 4 mandam investigar 112 e 76 produtos. O painel contava quantos
# e nunca dizia quais. Esta tela diz. Fica fora do menu lateral: so chega por botao.
c = {}
paginas["07_produtos_em_foco"] = montar([
 barra_lateral(MENU, -1, MARCA, SUBMARCA),
 cabecalho("Produtos em foco",
           "Os dois bolsos da visão executiva, produto a produto",
           "volta pelo botão"),
 ret(1688.6, 34, 203.4, 30, AREIA, LATAO, 15),
 txt(1790.3, 54, "voltar para a visão", 11.5, 600, LATAO, "middle"),
 card(260, 150, 806.0, 884,
      "Muito avaliado, nota baixa",
      "nº de avaliações acima da mediana da base e nota no quartil inferior", c,
      "t_bolso_ruim"),
 card(1086.0, 150, 806.0, 884,
      "Nota alta, pouco visto",
      "nota no quartil superior e menos de mil avaliações", c,
      "t_bolso_bom"),
 rodape("Os dois cortes vêm da distribuição desta base, não de número redondo. "
        "Mediana de avaliações: 4.740. Quartis de nota: 3,90 e 4,30.")])
c["b_voltar"] = {"tipo": "botao", "card": [1688.6, 34, 203.4, 30],
                 "util": [1688.6, 34, 203.4, 30]}
coords["07_produtos_em_foco"] = c

# ---------------------------------------------------------------- 8, a dica do termo
# Pagina de dica de ferramenta: 400x300, type Tooltip.
# Formato conferido no page.json de 297783e59b0c2b2b3906 do TC3.
DICA_L, DICA_A = 400, 344
c = {}
def _fatia(x, y, w, rotulo, cor_rotulo, cid, altura=46):
    c[cid] = {"tipo": "kpi", "card": [x, y, w, altura], "util": [x, y, w, altura]}
    return (txt(x + 2, y - 10, rotulo, 9, 700, cor_rotulo) +
            ret(x, y, w, altura, AREIA, rx=6))

_dica = [ret(0, 0, DICA_L, DICA_A, CARD),
         ret(0, 0, DICA_L, 5, NAVY),
         _fatia(18, 38, 364, "TERMO", TINTA_FRACA, "d_termo"),
         ret(20, 100, 360, 1, BORDA),
         _fatia(18, 128, 176, "EM QUEM RECLAMA", "#2E6BA8", "d_reclama"),
         _fatia(206, 128, 176, "EM QUEM ELOGIA", "#C08A3E", "d_elogia"),
         ret(20, 190, 360, 1, BORDA),
         txt(20, 228, "diferença", 11.5, 400, TINTA),
         _fatia(214, 206, 168, "", TINTA_FRACA, "d_diferenca", 44),
         txt(20, 288, "produtos com o termo", 11.5, 400, TINTA),
         _fatia(214, 266, 168, "", TINTA_FRACA, "d_produtos", 44),
         txt(20, 332, "% dos produtos de cada faixa em que o termo aparece",
             8.5, 400, TINTA_FRACA)]
paginas["08_dica_termo"] = (
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{DICA_L}" height="{DICA_A}" '
    f'viewBox="0 0 {DICA_L} {DICA_A}">{"".join(_dica)}</svg>')
coords["08_dica_termo"] = c

# ---------------------------------------------------------------- 8 a 13, as dicas dos selos
# Cada selo dourado desenhado no fundo e uma promessa. Estas seis pagam as seis que faltavam.
AZUL, OURO = "#2E6BA8", "#A6824C"
dica_texto("09_dica_medida", "O que rating_count mede",
  "É quanta gente avaliou o produto, não quanto ele vendeu. A base não traz volume de "
  "venda, então toda leitura de receita a partir daqui é inferência, não medição.",
  ("AVALIAÇÕES DECLARADAS", AZUL, "d_declaradas"), ("COM TEXTO NO ARQUIVO", OURO, "d_com_texto"),
  "a diferença entre as duas está explicada em Fontes e premissas", coords)

dica_texto("10_dica_ponderacao", "Por que a nota é ponderada",
  "A média simples trata um produto com 3 avaliações igual a um com 400 mil. A ponderada "
  "pesa cada nota pelo número de avaliações que existe atrás dela.",
  ("MÉDIA SIMPLES", AZUL, "d_simples"), ("MÉDIA PONDERADA", OURO, "d_ponderada"),
  "a distância entre as duas mostra o peso dos produtos muito avaliados", coords)

dica_texto("11_dica_engajamento", None,
  "Faixa definida pelos quartis de rating_count desta base, não por corte redondo. "
  "A nota é ponderada dentro da faixa.",
  ("PRODUTOS NA FAIXA", AZUL, "d_produtos_faixa"), ("NOTA PONDERADA", OURO, "d_nota_faixa"),
  "passe por outra barra para comparar as faixas", coords, titulo_medida=True)

dica_texto("12_dica_cambio", "A conversão é premissa, não cotação",
  "A base só traz rupia indiana e não traz câmbio. A taxa é fixa, declarada na tabela "
  "dMoeda, e serve para ordem de grandeza. Não serve para fechar operação.",
  ("TAXA POR RUPIA", AZUL, "d_taxa"), ("PREÇO MÉDIO", OURO, "d_preco"),
  "a data e a fonte da taxa estão em Fontes e premissas", coords)

dica_texto("13_dica_texto", "São duas contagens diferentes",
  "rating_count é o total que a Amazon declara no produto. O arquivo traz só uma linha de "
  "texto por avaliação extraída, que é muito menos. A análise de termos usa a segunda.",
  ("DECLARADAS", AZUL, "d_declaradas2"), ("COM TEXTO", OURO, "d_com_texto2"),
  "nenhuma conclusão de texto vale para as 23,8 milhões declaradas", coords)

dica_texto("14_dica_corte", "De onde vem o corte da percepção",
  "Percentis 25 e 75 do rating desta base: abaixo é nota <= 3,90 e acima é nota >= 4,30. "
  "Um corte fixo em 3,0 marcaria só 6 produtos de 1.351, porque a nota é comprimida.",
  ("ACIMA DA BASE", AZUL, "d_acima"), ("ABAIXO DA BASE", OURO, "d_abaixo"),
  "o corte é da base inteira: o filtro de categoria muda a contagem, não o corte", coords)

# ---------------------------------------------------------------- gravar
saida = os.path.dirname(os.path.abspath(__file__))
atuais = {n + ".svg" for n in paginas}
for velho_svg in sorted(set(os.listdir(saida)) - atuais):
    if velho_svg.endswith(".svg"):
        os.remove(os.path.join(saida, velho_svg))
        print(f"removido (nao existe mais): {velho_svg}")
# a pasta de previa segue a mesma lista: PNG de pagina que nao existe mais sai junto,
# senao sobra nome da numeracao antiga do lado do novo
_previa = os.path.join(saida, "previa")
if os.path.isdir(_previa):
    _validos = {n + ".png" for n in paginas} | {"todas_as_dicas.png"}
    for velho_png in sorted(set(os.listdir(_previa)) - _validos):
        if velho_png.endswith(".png"):
            os.remove(os.path.join(_previa, velho_png))
            print(f"removido da previa (nao existe mais): {velho_png}")
for nome, svg in paginas.items():
    with open(os.path.join(saida, nome + ".svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"{nome + '.svg':<34} {len(svg):>7,} bytes")
with open(os.path.join(saida, "coordenadas.json"), "w", encoding="utf-8") as f:
    json.dump(coords, f, ensure_ascii=False, indent=2)
print(f"\ncoordenadas.json: {sum(len(v) for v in coords.values())} áreas em {len(coords)} páginas")
if ALERTAS:
    print("\nTEXTO QUE NAO CABE:")
    for a in ALERTAS:
        print("  -", a)
else:
    print("texto: todo bloco cabe no card")
