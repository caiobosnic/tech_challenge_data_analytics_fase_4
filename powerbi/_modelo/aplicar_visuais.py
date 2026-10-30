# -*- coding: utf-8 -*-
"""
Escreve as paginas e os visuais (PBIR) do dashboard TC4.

Uso, com o Power BI FECHADO:
    python aplicar_visuais.py "<pasta que contem o .pbip>"

Esta versao monta as 6 paginas com fundo e menu, e popula SO a pagina 1.
As outras cinco ficam com fundo e menu, prontas para a proxima rodada.

Idempotente. Nao toca no .SemanticModel.
"""
import json, os, re, shutil, sys

SCHEMA_VISUAL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json"
SCHEMA_PAGE   = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
SCHEMA_PAGES  = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json"

PAGINAS = [
 ("p1_visao",      "Visão executiva",       "01_visao_executiva.svg"),
 ("p2_produtos",   "Produtos e categorias", "02_produtos_categorias.svg"),
 ("p3_precos",     "Preços e descontos",    "03_precos_descontos.svg"),
 ("p4_clientes",   "Customer insights",     "04_customer_insights.svg"),
 ("p5_recomenda",  "Recomendações",         "05_recomendacoes.svg"),
 ("p6_fontes",     "Fontes e premissas",    "06_fontes_premissas.svg"),
]
# Pagina de lista, tamanho cheio, fora do menu lateral: so se chega por botao.
EXTRA = ("p7_produtos", "Produtos em foco", "07_produtos_em_foco.svg", "07_produtos_em_foco")

# Paginas de dica: 400x300, type Tooltip, fora do menu. Cada uma paga um selo do fundo.
# (id, nome, svg, chave em coordenadas.json, [(slot, medida, tamanho)])
DICAS = [
 ("p8_dica_termo", "Dica: o termo", "08_dica_termo.svg", "08_dica_termo",
  [("d_termo", "Termo em foco", "15D"), ("d_reclama", "% nos que reclamam", "15D"),
   ("d_elogia", "% nos que elogiam", "15D"), ("d_diferenca", "Diferença em pontos", "11D"),
   ("d_produtos", "Produtos com o termo", "11D")]),
 ("p9_dica_medida", "Dica: o que mede", "09_dica_medida.svg", "09_dica_medida",
  [("d_declaradas", "Avaliações", "15D"), ("d_com_texto", "Avaliações com texto", "15D")]),
 ("p10_dica_ponderacao", "Dica: ponderação", "10_dica_ponderacao.svg", "10_dica_ponderacao",
  [("d_simples", "Nota média simples", "15D"), ("d_ponderada", "Nota média ponderada", "15D")]),
 ("p11_dica_engajamento", "Dica: a faixa", "11_dica_engajamento.svg", "11_dica_engajamento",
  [("t_titulo", "Faixa em foco", "11D"), ("d_produtos_faixa", "Produtos", "15D"),
   ("d_nota_faixa", "Nota média ponderada", "15D")]),
 ("p12_dica_cambio", "Dica: câmbio", "12_dica_cambio.svg", "12_dica_cambio",
  [("d_taxa", "Taxa selecionada", "15D"), ("d_preco", "Preço médio com desconto", "15D")]),
 ("p13_dica_texto", "Dica: a diferença", "13_dica_texto.svg", "13_dica_texto",
  [("d_declaradas2", "Avaliações", "15D"), ("d_com_texto2", "Avaliações com texto", "15D")]),
 ("p14_dica_corte", "Dica: o corte", "14_dica_corte.svg", "14_dica_corte",
  [("d_acima", "Produtos acima da base", "15D"), ("d_abaixo", "Produtos abaixo da base", "15D")]),
]
DICA = DICAS[0]

# De qual visual sai cada dica. A chave e o nome do visual; o valor, a pagina de dica.
# Todo selo dourado desenhado no fundo tem que aparecer aqui, senao e promessa sem entrega.
DICA_DE = {
 "p1_kpi_avaliacoes":        "p9_dica_medida",
 "p1_kpi_nota":              "p10_dica_ponderacao",
 "p2_g_dispersao":           "p11_dica_engajamento",
 "p3_kpi_preco_desc":        "p12_dica_cambio",
 "p4_kpi_texto":             "p13_dica_texto",
 "p4_kpi_acima":             "p14_dica_corte",
 "p4_g_termos_comparados":   "p8_dica_termo",
 "p4_g_termos_acima":        "p8_dica_termo",
 "p4_g_termos_abaixo":       "p8_dica_termo",
}

# geometria do menu, igual ao SVG: primeiro item em y=127, passo 52
MENU_X, MENU_W, MENU_H, MENU_Y0, MENU_PASSO = 12, 208, 46, 116, 52


def lit(v):
    return {"expr": {"Literal": {"Value": v}}}


def cor(hex_):
    return {"solid": {"color": lit(f"'{hex_}'")}}


def prop(d):
    return [{"properties": d}]


def medida(nome):
    return {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas"}}, "Property": nome}}


def coluna(tabela, nome):
    return {"Column": {"Expression": {"SourceRef": {"Entity": tabela}}, "Property": nome}}


def proj(campo, entidade, propriedade, rotulo, ativo=False):
    p = {"field": campo, "queryRef": f"{entidade}.{propriedade}",
         "nativeQueryRef": rotulo, "displayName": rotulo}
    if ativo:
        p["active"] = True
    return p


def dica_de_pagina(secao):
    """Liga o visual a uma pagina de dica. Conferido no g_cargo.json do TC3."""
    return {"visualTooltip": prop({
        "show": lit("true"), "type": lit("'Canvas'"), "section": lit(f"'{secao}'"),
        "showActionsInTooltips": lit("false"), "transparency": lit("0D"),
        "showTooltipFieldsOnly": lit("false")})}


SEM_MOLDURA = {"background": prop({"show": lit("false")}),
               "title": prop({"show": lit("false")}),
               "border": prop({"show": lit("false")})}


def visual_cartao(nome, pos, nome_medida, tamanho="17D", dica=None):
    return {"$schema": SCHEMA_VISUAL, "name": nome, "position": pos, "visual": {
        "visualType": "card",
        "query": {"queryState": {"Values": {"projections": [
            dict(proj(medida(nome_medida), "_Medidas", nome_medida, nome_medida), active=True)]}}},
        "objects": {
            "labels": prop({"color": cor("#1F3A5F"), "fontSize": lit(tamanho),
                            "labelDisplayUnits": lit("1D")}),
            "categoryLabels": prop({"show": lit("false")}),
        },
        "visualContainerObjects": dict(SEM_MOLDURA, **(
            dica_de_pagina(dica) if dica else
            {"visualTooltip": prop({"show": lit("false")})})),
    }}


def visual_segmentacao(nome, pos, tabela, col, rotulo):
    return {"$schema": SCHEMA_VISUAL, "name": nome, "position": pos, "visual": {
        "visualType": "slicer",
        "query": {"queryState": {"Values": {"projections": [
            proj(coluna(tabela, col), tabela, col, rotulo, ativo=True)]}}},
        "objects": {
            "data": prop({"mode": lit("'Dropdown'")}),
            "header": prop({"show": lit("false")}),
            "items": prop({"textSize": lit("10D"), "fontColor": cor("#1A1A1A")}),
            "selection": prop({"selectAllCheckboxEnabled": lit("true"),
                               "singleSelect": lit("false")}),
        },
        "visualContainerObjects": dict(SEM_MOLDURA),
        "drillFilterOtherVisuals": True,
    }}


def eixos_recessivos():
    return {
        "legend": prop({"show": lit("false")}),
        "categoryAxis": prop({"labelColor": cor("#5C5A54"), "fontSize": lit("9D"),
                              "showAxisTitle": lit("false"), "gridlineShow": lit("false")}),
        "valueAxis": prop({"labelColor": cor("#5C5A54"), "fontSize": lit("9D"),
                           "showAxisTitle": lit("false"),
                           "gridlineColor": cor("#3D3B36"), "gridlineStyle": lit("'dotted'"),
                           "gridlineThickness": lit("1D")}),
        "dataPoint": prop({"defaultColor": cor("#2E6BA8"), "showAllDataPoints": lit("false")}),
        # fora da ponta, sem pastilha: o valor fica no fundo claro do card, nao dentro da barra.
        # labelPosition e enableBackground conferidos no g_cargo.json do TC3.
        "labels": prop({"show": lit("true"), "fontSize": lit("9D"), "bold": lit("true"),
                        "color": cor("#3D3B36"),
                        "labelPosition": lit("'OutsideEnd'"),
                        "enableBackground": lit("false"),
                        "labelDensity": lit("100L"),
                        "optimizeLabelDisplay": lit("false"),
                        "labelContentLayout": lit("'SingleLine'")}),
    }


def visual_barra(nome, pos, cat_tab, cat_col, cat_rotulo, nome_medida,
                 tipo="clusteredBarChart", ordenar="Descending"):
    q = {"queryState": {
            "Category": {"projections": [proj(coluna(cat_tab, cat_col), cat_tab, cat_col,
                                              cat_rotulo, ativo=True)]},
            "Y": {"projections": [proj(medida(nome_medida), "_Medidas", nome_medida, nome_medida)]},
         }}
    if ordenar:
        # grafico de magnitude ordena pelo valor, nao pelo nome da categoria.
        # sortDefinition mora DENTRO de query: conferido no g_cargo do TC3.
        q["sortDefinition"] = {"sort": [{"field": medida(nome_medida), "direction": ordenar}],
                               "isDefaultSort": True}
    return {"$schema": SCHEMA_VISUAL, "name": nome, "position": pos, "visual": {
        "visualType": tipo,
        "query": q,
        "objects": eixos_recessivos(),
        "visualContainerObjects": dict(SEM_MOLDURA, **(
            dica_de_pagina(DICA_DE[nome]) if nome in DICA_DE else {})),
    }}


def visual_barra_duas(nome, pos, cat_tab, cat_col, cat_rotulo, medidas, cores,
                      ordenar_por=None, tipo="clusteredBarChart"):
    """Duas medidas no mesmo eixo, uma cor cada. Legenda ligada porque sao duas series.
    O seletor por medida (selector.metadata) foi conferido no g_cargo.json do TC3."""
    q = {"queryState": {
            "Category": {"projections": [proj(coluna(cat_tab, cat_col), cat_tab, cat_col,
                                              cat_rotulo, ativo=True)]},
            "Y": {"projections": [proj(medida(m), "_Medidas", m, m) for m in medidas]},
         }}
    if ordenar_por:
        q["sortDefinition"] = {"sort": [{"field": medida(ordenar_por), "direction": "Descending"}],
                               "isDefaultSort": True}
    objetos = eixos_recessivos()
    objetos["legend"] = prop({"show": lit("true"), "position": lit("'TopCenter'"),
                              "showTitle": lit("false"), "fontSize": lit("9D"),
                              "labelColor": cor("#5C5A54")})
    objetos["dataPoint"] = [{"properties": {"fill": cor(c)},
                             "selector": {"metadata": f"_Medidas.{m}"}}
                            for m, c in zip(medidas, cores)]
    # valor na ponta de cada barra. 16 termos x 2 series em 618px dao 19px por barra,
    # entao o rotulo vai menor (8D) para nao brigar com a barra de cima.
    objetos["labels"] = prop({"show": lit("true"), "fontSize": lit("8D"), "bold": lit("true"),
                              "color": cor("#3D3B36"),
                              "labelPosition": lit("'OutsideEnd'"),
                              "enableBackground": lit("false"),
                              "labelDensity": lit("100L"),
                              "optimizeLabelDisplay": lit("false"),
                              "labelContentLayout": lit("'SingleLine'")})
    return {"$schema": SCHEMA_VISUAL, "name": nome, "position": pos, "visual": {
        "visualType": tipo,
        "query": q,
        "objects": objetos,
        "visualContainerObjects": dict(SEM_MOLDURA, **(
            dica_de_pagina(DICA_DE[nome]) if nome in DICA_DE else {})),
    }}


def visual_tabela(nome, pos, campos, ordenar=None, larguras=None):
    """campos: lista de (tipo, tabela, propriedade, rotulo). tipo e 'medida' ou 'coluna'."""
    projecoes = []
    for tipo, tab, prop_, rot in campos:
        campo = medida(prop_) if tipo == "medida" else coluna(tab, prop_)
        ent = "_Medidas" if tipo == "medida" else tab
        projecoes.append(proj(campo, ent, prop_, rot))   # sem active: pegadinha da tableEx
    q = {"queryState": {"Values": {"projections": projecoes}}}
    if ordenar:
        alvo, direcao = ordenar[0], ordenar[1]
        campo = coluna(ordenar[2], alvo) if len(ordenar) > 2 else medida(alvo)
        q["sortDefinition"] = {"sort": [{"field": campo, "direction": direcao}],
                               "isDefaultSort": True}
    objetos = {
        "columnHeaders": prop({"bold": lit("true"), "fontColor": cor("#FFFFFF"),
                               "backColor": cor("#1F3A5F")}),
    }
    if larguras:
        # columnAdjustment fixedWidth + columnWidth por coluna: conferido no t_benchmark do TC3.
        # sem isso a tabela usa a largura automatica e sobra card vazio do lado.
        objetos["columnHeaders"][0]["properties"]["columnAdjustment"] = lit("'fixedWidth'")
        objetos["columnWidth"] = [{"properties": {"value": lit(f"{larg}D")},
                                   "selector": {"metadata": alvo}}
                                  for alvo, larg in larguras]
    return {"$schema": SCHEMA_VISUAL, "name": nome, "position": pos, "visual": {
        "visualType": "tableEx",
        "query": q,
        "objects": dict(objetos, **{
            "values": prop({"fontColorPrimary": cor("#3D3B36"),
                            "fontColorSecondary": cor("#3D3B36"),
                            "backColorSecondary": cor("#E7E2D9")}),
            "grid": prop({"gridVertical": lit("true"), "gridVerticalColor": cor("#3D3B36"),
                          "gridHorizontal": lit("true"), "gridHorizontalColor": cor("#3D3B36"),
                          "gridHorizontalWeight": lit("1D")}),
        }),
        "visualContainerObjects": dict(SEM_MOLDURA),
    }}


def visual_botao(nome, pos, destino, acao="PageNavigation"):
    """acao: 'PageNavigation' leva para outra pagina, 'ClearAllSlicers' limpa os filtros.
    O segundo valor foi conferido no botao_limpar.json que veio do TC3."""
    return {"$schema": SCHEMA_VISUAL, "name": nome, "position": pos, "visual": {
        "visualType": "actionButton",
        "objects": {
            "icon": prop({"shapeType": lit("'blank'")}),
            "text": prop({"show": lit("false")}),
            "fill": prop({"show": lit("false")}),
            "outline": prop({"show": lit("false")}),
        },
        "visualContainerObjects": {"visualLink": prop({
            "show": lit("true"), "type": lit(f"'{acao}'"),
            "navigationSection": lit(f"'{destino}'")})},
        "drillFilterOtherVisuals": True,
    }}


def filtro_categorico(nome, tabela, col, valores):
    return {"filters": [{
        "name": nome,
        "field": coluna(tabela, col),
        "type": "Categorical",
        "filter": {
            "Version": 2,
            "From": [{"Name": "t", "Entity": tabela, "Type": 0}],
            "Where": [{"Condition": {"In": {
                "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "t"}},
                                            "Property": col}}],
                "Values": [[{"Literal": {"Value": f"'{v}'"}}] for v in valores]}}}],
        }}]}


def caixa(util, z):
    x, y, w, h = util
    return {"x": round(x, 2), "y": round(y, 2), "z": z,
            "width": round(w, 2), "height": round(h, 2), "tabOrder": z}


# ---------------------------------------------------------------- pagina 1
def visuais_pagina_1(coords):
    c = coords["01_visao_executiva"]
    v = []
    for i, (cid, med) in enumerate([("kpi_produtos", "Produtos"),
                                    ("kpi_avaliacoes", "Avaliações"),
                                    ("kpi_nota", "Nota média ponderada"),
                                    ("kpi_desconto", "Desconto médio %")]):
        v.append(visual_cartao(f"p1_{cid}", caixa(c[cid]["util"], 11000 + i), med,
                               dica=DICA_DE.get(f"p1_{cid}")))

    filtros = [("f_categoria", "dCategoria", "nivel_1",   "Categoria"),
               ("f_preco",     "fProdutos",  "faixa_preco", "Faixa de preço"),
               ("f_nota",      "fProdutos",  "faixa_nota",  "Faixa de nota"),
               ("f_moeda",     "dMoeda",     "moeda",       "Moeda")]
    for i, (cid, tab, col, rot) in enumerate(filtros):
        x = 260.0 + i * 304.4
        v.append(visual_segmentacao(f"p1_{cid}", {"x": round(x, 1), "y": 128, "z": i,
                                                  "width": 290.4, "height": 42, "tabOrder": i},
                                    tab, col, rot))
    v.append(visual_botao("p1_b_limpar", caixa(c["b_limpar"]["util"], 900),
                          "p1_visao", acao="ClearAllSlicers"))

    v.append(visual_barra("p1_g_cat_produtos", caixa(c["g_cat_produtos"]["util"], 100),
                          "dCategoria", "nivel_1", "Categoria", "Produtos"))
    v.append(visual_barra("p1_g_cat_avaliacoes", caixa(c["g_cat_avaliacoes"]["util"], 101),
                          "dCategoria", "nivel_1", "Categoria", "Avaliações"))
    # a faixa de nota tem ordem propria (do pior para o melhor), entao nao ordena por valor
    v.append(visual_barra("p1_g_dist_nota", caixa(c["g_dist_nota"]["util"], 102),
                          "fProdutos", "faixa_nota", "Faixa de nota", "Produtos",
                          tipo="clusteredColumnChart", ordenar=None))
    v.append(visual_cartao("p1_kpi_bolso_ruim", caixa(c["kpi_bolso_ruim"]["util"], 103),
                           "Alto engajamento, nota abaixo da base"))
    v.append(visual_cartao("p1_kpi_bolso_bom", caixa(c["kpi_bolso_bom"]["util"], 104),
                           "Nota acima da base, pouca visibilidade"))
    v.append(visual_botao("p1_g_bolsos_ir", caixa(c["g_bolsos_ir"]["util"], 901),
                          EXTRA[0]))
    return v


def filtros_padrao(v, rotulos, prefixo, coords=None, pagina=None):
    for i, (cid, tab, col, rot) in enumerate(rotulos):
        x = 260.0 + i * 304.4
        v.append(visual_segmentacao(f"{prefixo}_{cid}",
                                    {"x": round(x, 1), "y": 128, "z": i,
                                     "width": 290.4, "height": 42, "tabOrder": i},
                                    tab, col, rot))
    if coords and "b_limpar" in coords:
        v.append(visual_botao(f"{prefixo}_b_limpar", caixa(coords["b_limpar"]["util"], 900),
                              pagina, acao="ClearAllSlicers"))


FILTROS_GERAIS = [("f_categoria", "dCategoria", "nivel_1", "Categoria"),
                  ("f_preco", "fProdutos", "faixa_preco", "Faixa de preço"),
                  ("f_nota", "fProdutos", "faixa_nota", "Faixa de nota"),
                  ("f_moeda", "dMoeda", "moeda", "Moeda")]


def kpis(v, c, prefixo, itens):
    for i, (cid, med) in enumerate(itens):
        nome = f"{prefixo}_{cid}"
        v.append(visual_cartao(nome, caixa(c[cid]["util"], 11000 + i), med,
                               dica=DICA_DE.get(nome)))


def visuais_pagina_2(coords):
    c = coords["02_produtos_categorias"]; v = menu("p2_produtos")
    filtros_padrao(v, FILTROS_GERAIS, "p2", c, "p2_produtos")
    kpis(v, c, "p2", [("kpi_cat1", "Categorias de nível 1"),
                      ("kpi_caminhos", "Caminhos de categoria"),
                      ("kpi_mediana_aval", "Mediana de avaliações"),
                      ("kpi_top_produto", "Produto mais avaliado")])
    v.append(visual_barra("p2_g_hierarquia", caixa(c["g_hierarquia"]["util"], 100),
                          "dCategoria", "nivel_2", "Categoria nível 2", "Produtos"))
    v.append(visual_barra("p2_g_dispersao", caixa(c["g_dispersao"]["util"], 101),
                          "fProdutos", "faixa_engajamento", "Faixa de engajamento",
                          "Nota média ponderada", tipo="clusteredColumnChart", ordenar=None))
    top = visual_tabela("p2_g_top10", caixa(c["g_top10"]["util"], 102), [
        ("coluna", "fProdutos", "product_name", "Produto"),
        ("medida", None, "Avaliações", "Avaliações"),
        ("medida", None, "Nota média ponderada", "Nota"),
        ("medida", None, "Preço com desconto", "Preço"),
    ], ordenar=("Avaliações", "Descending"),
       larguras=[("fProdutos.product_name", 280), ("_Medidas.Avaliações", 118),
                 ("_Medidas.Nota média ponderada", 100),
                 ("_Medidas.Preço com desconto", 135)])
    # o subtitulo prometia 10 e a tabela rolava a base inteira. agora entrega 10.
    top["filterConfig"] = filtro_categorico("top10", "fProdutos", "top_avaliacoes", ["sim"])
    v.append(top)
    return v


def visuais_pagina_3(coords):
    c = coords["03_precos_descontos"]; v = menu("p3_precos")
    filtros_padrao(v, [("f_categoria", "dCategoria", "nivel_1", "Categoria"),
                       ("f_preco", "fProdutos", "faixa_preco", "Faixa de preço"),
                       ("f_desconto", "fProdutos", "faixa_desconto", "Faixa de desconto"),
                       ("f_moeda", "dMoeda", "moeda", "Moeda")], "p3", c, "p3_precos")
    kpis(v, c, "p3", [("kpi_preco_desc", "Preço médio com desconto"),
                      ("kpi_preco_cheio", "Preço cheio médio"),
                      ("kpi_desconto_med", "Desconto médio %"),
                      ("kpi_economia", "Economia oferecida")])
    v.append(visual_barra("p3_g_desc_nota", caixa(c["g_desc_nota"]["util"], 100),
                          "fProdutos", "faixa_desconto", "Faixa de desconto",
                          "Nota média ponderada", tipo="clusteredColumnChart", ordenar=None))
    v.append(visual_barra("p3_g_desc_cat", caixa(c["g_desc_cat"]["util"], 101),
                          "dCategoria", "nivel_1", "Categoria", "Desconto médio %"))
    # pergunta 4 do enunciado: quais categorias tem maior ou menor satisfacao.
    # Era a unica das 8 sem nenhum visual.
    v.append(visual_barra("p3_g_nota_cat", caixa(c["g_nota_cat"]["util"], 103),
                          "dCategoria", "nivel_1", "Categoria",
                          "Nota ponderada com amostra mínima"))
    v.append(visual_barra("p3_g_faixa_preco", caixa(c["g_faixa_preco"]["util"], 102),
                          "fProdutos", "faixa_preco", "Faixa de preço",
                          "Nota média ponderada", tipo="clusteredColumnChart", ordenar=None))
    return v


def visuais_pagina_4(coords):
    c = coords["04_customer_insights"]; v = menu("p4_clientes")
    filtros_padrao(v, [("f_categoria", "dCategoria", "nivel_1", "Categoria"),
                       ("f_lado", "fProdutos", "percepcao", "Percepção"),
                       ("f_nota", "fProdutos", "faixa_nota", "Faixa de nota"),
                       ("f_moeda", "dMoeda", "moeda", "Moeda")], "p4", c, "p4_clientes")
    kpis(v, c, "p4", [("kpi_texto", "Avaliações com texto"),
                      ("kpi_acima", "Produtos acima da base"),
                      ("kpi_media", "Produtos na média"),
                      ("kpi_abaixo", "Produtos abaixo da base")])
    # era tabela estreita num card de 914px. virou barra de duas series, que preenche o card
    # e mostra a comparacao em vez de pedir que o leitor compare numeros na mao.
    comp = visual_barra_duas("p4_g_termos_comparados",
                             caixa(c["g_termos_comparados"]["util"], 100),
                             "dTermoComparado", "termo", "Termo",
                             ["% nos que reclamam", "% nos que elogiam"],
                             ["#2E6BA8", "#C08A3E"],
                             ordenar_por="Diferença em pontos")
    comp["filterConfig"] = filtro_categorico("destaque", "dTermoComparado", "destaque", ["sim"])
    v.append(comp)
    for nome, cid, lado, z in [("p4_g_termos_acima", "g_termos_acima", "elogio", 101),
                               ("p4_g_termos_abaixo", "g_termos_abaixo", "reclamação", 102)]:
        g = visual_barra(nome, caixa(c[cid]["util"], z),
                         "dTermoComparado", "termo", "Termo", "Peso do termo")
        # dois filtros: o lado e o recorte dos 15. o subtitulo promete 15, entao entrega 15.
        g["filterConfig"] = {"filters": (
            filtro_categorico(f"lado_{z}", "dTermoComparado", "lado", [lado])["filters"] +
            filtro_categorico(f"top15_{z}", "dTermoComparado", "destaque_lado", ["sim"])["filters"])}
        v.append(g)
    return v


def visuais_pagina_produtos(coords):
    """Os 112 e os 76 que as recomendacoes 3 e 4 mandam investigar, nominalmente."""
    c = coords[EXTRA[3]]
    v = menu("")
    v.append(visual_botao("p7_b_voltar", caixa(c["b_voltar"]["util"], 900), "p1_visao"))
    for cid, valor, z in [("t_bolso_ruim", "muito avaliado, nota baixa", 100),
                          ("t_bolso_bom", "nota alta, pouco visto", 101)]:
        t = visual_tabela(f"p7_{cid}", caixa(c[cid]["util"], z), [
            ("coluna", "fProdutos", "product_name", "Produto"),
            ("medida", None, "Avaliações", "Avaliações"),
            ("medida", None, "Nota média ponderada", "Nota"),
            ("medida", None, "Preço com desconto", "Preço"),
        ], ordenar=("Avaliações", "Descending"),
           larguras=[("fProdutos.product_name", 380), ("_Medidas.Avaliações", 120),
                     ("_Medidas.Nota média ponderada", 100),
                     ("_Medidas.Preço com desconto", 130)])
        t["filterConfig"] = filtro_categorico(f"bolso_{z}", "fProdutos", "bolso", [valor])
        v.append(t)
    return v


def visuais_pagina_dica(coords, chave, slots):
    """Cartoes num fundo de 400x300. O que estiver sob o cursor filtra todos eles."""
    c = coords[chave]
    return [visual_cartao(slot, caixa(c[slot]["util"], i + 1), med, tamanho=tam)
            for i, (slot, med, tam) in enumerate(slots)]


DESTINO = {"Visão executiva": "p1_visao", "Produtos e categorias": "p2_produtos",
           "Preços e descontos": "p3_precos", "Customer insights": "p4_clientes",
           "Recomendações": "p5_recomenda", "Fontes e premissas": "p6_fontes"}

# medida que sustenta cada recomendacao, na ordem do dRecomendacao.csv
INDICADOR = {"1": "Concentração nas 3 maiores",
             "2": "Queda de nota no desconto alto",
             "3": "Alto engajamento, nota abaixo da base",
             "4": "Nota acima da base, pouca visibilidade",
             "5": "Diferença de ruído",
             "6": "Amplitude da nota entre faixas de preço"}


def visuais_pagina_5(coords):
    """Sem tabela. Cada bloco e texto no fundo mais um numero vivo e um botao de ir conferir.
    A decisao e o 'por que' sao interpretacao nossa, entao sao texto. O numero e medida."""
    c = coords["05_recomendacoes"]; v = menu("p5_recomenda")
    for n, med in INDICADOR.items():
        v.append(visual_cartao(f"p5_r{n}_valor", caixa(c[f"r{n}_valor"]["util"], 100 + int(n)),
                               med, tamanho="24D"))
        destino = DESTINO[c[f"r{n}_ir"]["destino"]]
        v.append(visual_botao(f"p5_r{n}_ir", caixa(c[f"r{n}_ir"]["util"], 200 + int(n)), destino))
    return v


def visuais_pagina_6(coords):
    """Premissa, limite e caminho do dado sao texto declarado, nao medida.
    Ficam desenhados no fundo a partir do dFonte.csv, entao a pagina so leva o menu."""
    return menu("p6_fontes")


def menu(pagina_atual):
    v = []
    for i, (pid, _, _) in enumerate(PAGINAS):
        if pid == pagina_atual:
            continue
        y = MENU_Y0 + i * MENU_PASSO
        v.append(visual_botao(f"menu_{i}",
                              {"x": MENU_X, "y": y, "z": 20000 + i,
                               "width": MENU_W, "height": MENU_H, "tabOrder": 20000 + i},
                              pid))
    return v


def main():
    if len(sys.argv) < 2:
        print('uso: python aplicar_visuais.py "<pasta que contem o .pbip>"')
        sys.exit(1)
    raiz = os.path.abspath(sys.argv[1])
    rep = [d for d in os.listdir(raiz) if d.endswith(".Report")]
    if not rep:
        print(f"ERRO: nenhuma pasta .Report em {raiz}")
        sys.exit(1)
    rep = os.path.join(raiz, rep[0])
    definicao = os.path.join(rep, "definition")
    pastas_pag = os.path.join(definicao, "pages")
    registrados = os.path.join(rep, "StaticResources", "RegisteredResources")
    fundos = os.path.join(raiz, "fundos")
    coords = json.load(open(os.path.join(fundos, "coordenadas.json"), encoding="utf-8"))

    # 1. copiar os SVG para RegisteredResources
    os.makedirs(registrados, exist_ok=True)
    usados = [p[2] for p in PAGINAS] + [EXTRA[2]] + [d[2] for d in DICAS]
    for orfao in sorted(set(os.listdir(registrados)) - set(usados)):
        if orfao.endswith(".svg"):
            os.remove(os.path.join(registrados, orfao))
    for svg in usados:
        shutil.copy2(os.path.join(fundos, svg), os.path.join(registrados, svg))

    # 2. registrar no report.json
    rj = os.path.join(definicao, "report.json")
    r = json.load(open(rj, encoding="utf-8"))
    pacotes = [p for p in r.get("resourcePackages", []) if p.get("name") != "RegisteredResources"]
    pacotes.append({"name": "RegisteredResources", "type": "RegisteredResources",
                    "items": [{"name": svg, "path": svg, "type": "Image"}
                              for svg in [p[2] for p in PAGINAS] + [EXTRA[2]] + [d[2] for d in DICAS]]})
    r["resourcePackages"] = pacotes
    json.dump(r, open(rj, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # 3. apagar paginas antigas e escrever as 6
    if os.path.isdir(pastas_pag):
        for d in os.listdir(pastas_pag):
            p = os.path.join(pastas_pag, d)
            if os.path.isdir(p):
                shutil.rmtree(p)
    os.makedirs(pastas_pag, exist_ok=True)

    total = 0
    for pid, nome, svg in PAGINAS:
        pd_ = os.path.join(pastas_pag, pid)
        os.makedirs(os.path.join(pd_, "visuals"), exist_ok=True)
        json.dump({"$schema": SCHEMA_PAGE, "name": pid, "displayName": nome,
                   "displayOption": "FitToPage", "height": 1080, "width": 1920,
                   "objects": {"background": prop({
                       "image": {"image": {
                           "name": lit(f"'{svg}'"),
                           "url": {"expr": {"ResourcePackageItem": {
                               "PackageName": "RegisteredResources", "PackageType": 1,
                               "ItemName": svg}}},
                           "scaling": lit("'Normal'")}},
                       "transparency": lit("0D")})}},
                  open(os.path.join(pd_, "page.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)

        if pid == "p1_visao":
            vis = menu(pid) + visuais_pagina_1(coords)
        else:
            vis = {"p2_produtos": visuais_pagina_2, "p3_precos": visuais_pagina_3,
                   "p4_clientes": visuais_pagina_4, "p5_recomenda": visuais_pagina_5,
                   "p6_fontes": visuais_pagina_6}[pid](coords)
        for v in vis:
            vd = os.path.join(pd_, "visuals", v["name"])
            os.makedirs(vd, exist_ok=True)
            json.dump(v, open(os.path.join(vd, "visual.json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=2)
        total += len(vis)
        print(f"  {nome:<24} {len(vis):>3} visuais   fundo: {svg}")

    # a pagina de lista: tamanho cheio como as outras, mas fora do menu lateral
    pid, nome, svg, _ = EXTRA
    pd_ = os.path.join(pastas_pag, pid)
    os.makedirs(os.path.join(pd_, "visuals"), exist_ok=True)
    json.dump({"$schema": SCHEMA_PAGE, "name": pid, "displayName": nome,
               "displayOption": "FitToPage", "height": 1080, "width": 1920,
               "objects": {"background": prop({
                   "image": {"image": {
                       "name": lit(f"'{svg}'"),
                       "url": {"expr": {"ResourcePackageItem": {
                           "PackageName": "RegisteredResources", "PackageType": 1,
                           "ItemName": svg}}},
                       "scaling": lit("'Normal'")}},
                   "transparency": lit("0D")})}},
              open(os.path.join(pd_, "page.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    vis = visuais_pagina_produtos(coords)
    for v in vis:
        vd = os.path.join(pd_, "visuals", v["name"])
        os.makedirs(vd, exist_ok=True)
        json.dump(v, open(os.path.join(vd, "visual.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
    total += len(vis)
    print(f"  {nome:<24} {len(vis):>3} visuais   fundo: {svg}  (fora do menu)")

    # as paginas de dica: 400x300 e type Tooltip, como o TC3 faz
    for pid, nome, svg, chave, slots in DICAS:
      pd_ = os.path.join(pastas_pag, pid)
      os.makedirs(os.path.join(pd_, "visuals"), exist_ok=True)
      cab = open(os.path.join(fundos, svg), encoding="utf-8").read(300)
      larg = int(re.search(r'width="(\d+)"', cab).group(1))
      alt = int(re.search(r'height="(\d+)"', cab).group(1))
      json.dump({"$schema": SCHEMA_PAGE, "name": pid, "displayName": nome,
               "displayOption": "ActualSize", "height": alt, "width": larg,
               "objects": {"background": prop({
                   "image": {"image": {
                       "name": lit(f"'{svg}'"),
                       "url": {"expr": {"ResourcePackageItem": {
                           "PackageName": "RegisteredResources", "PackageType": 1,
                           "ItemName": svg}}},
                       "scaling": lit("'Normal'")}},
                   "transparency": lit("0D")})},
               "type": "Tooltip"},
              open(os.path.join(pd_, "page.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
      vis = visuais_pagina_dica(coords, chave, slots)
      for v in vis:
        vd = os.path.join(pd_, "visuals", v["name"])
        os.makedirs(vd, exist_ok=True)
        json.dump(v, open(os.path.join(vd, "visual.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
      total += len(vis)
      print(f"  {nome:<24} {len(vis):>3} visuais   fundo: {svg}  ({larg}x{alt}, dica)")

    json.dump({"$schema": SCHEMA_PAGES,
               "pageOrder": [p[0] for p in PAGINAS] + [EXTRA[0]] + [d[0] for d in DICAS],
               "activePageName": PAGINAS[0][0]},
              open(os.path.join(pastas_pag, "pages.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    print(f"\n{len(PAGINAS)+1+len(DICAS)} paginas, {total} visuais, {len(PAGINAS)+1+len(DICAS)} fundos registrados")


if __name__ == "__main__":
    main()
