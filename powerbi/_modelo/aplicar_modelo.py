# -*- coding: utf-8 -*-
"""
Escreve o modelo semantico (TMDL) do dashboard TC4 dentro do .pbip.

Uso, com o Power BI FECHADO:
    python aplicar_modelo.py "C:\\...\\tech_challenge_4\\powerbi"

Idempotente: rodar duas vezes deixa o mesmo resultado.
Nao toca em nada dentro de .Report: visuais sao outra etapa.
"""
import os, sys, uuid, shutil

NS = uuid.UUID("6f1a0c2e-7b3d-4e58-9a11-2c4b8d0e5f33")
def tag(nome): return str(uuid.uuid5(NS, nome))

T = "\t"

# ---------------------------------------------------------------- colunas
# (nome, tipo tmdl, tipo M, formatString, summarizeBy)
TABELAS = {
 "dCategoria": [
   ("sk_categoria",      "int64",  "Int64.Type", "0",     "none"),
   ("caminho_categoria", "string", "type text",  None,    "none"),
   ("nivel_1",           "string", "type text",  None,    "none"),
   ("nivel_2",           "string", "type text",  None,    "none"),
   ("nivel_3",           "string", "type text",  None,    "none"),
   ("nivel_4",           "string", "type text",  None,    "none"),
   ("nivel_5",           "string", "type text",  None,    "none"),
   ("nivel_6",           "string", "type text",  None,    "none"),
   ("nivel_7",           "string", "type text",  None,    "none"),
   ("categoria_folha",   "string", "type text",  None,    "none"),
   ("profundidade",      "int64",  "Int64.Type", "0",     "none"),
 ],
 "fProdutos": [
   ("product_id",              "string", "type text",   None,      "none"),
   ("product_name",            "string", "type text",   None,      "none"),
   ("discounted_price_rupia",  "double", "type number", "#,0.00",  "none"),
   ("actual_price_rupia",      "double", "type number", "#,0.00",  "none"),
   ("discount_percentage",     "double", "type number", "0.0%",    "none"),
   ("rating",                  "double", "type number", "0.00",    "none"),
   ("rating_count",            "int64",  "Int64.Type",  "#,0",     "none"),
   ("img_link",                "string", "type text",   None,      "none"),
   ("product_link",            "string", "type text",   None,      "none"),
   ("sk_categoria",            "int64",  "Int64.Type",  "0",       "none"),
   ("desconto_absoluto_rupia", "double", "type number", "#,0.00",  "none"),
   ("receita_potencial_rupia", "double", "type number", "#,0",     "none"),
   ("percepcao",               "string", "type text",   None,      "none"),
 ],
 "fAvaliacoes": [
   ("sk_avaliacao", "int64",  "Int64.Type", "0", "none"),
   ("review_id",    "string", "type text",  None, "none"),
   ("product_id",   "string", "type text",  None, "none"),
   ("user_id",      "string", "type text",  None, "none"),
   ("posicao",      "int64",  "Int64.Type", "0", "none"),
 ],
 "dTermosAvaliacao": [
   ("product_id",  "string", "type text",  None,   "none"),
   ("termo",       "string", "type text",  None,   "none"),
   ("ocorrencias", "int64",  "Int64.Type", "#,0",  "sum"),
   ("percepcao",   "string", "type text",  None,   "none"),
 ],
 "dTermoComparado": [
   ("sk_termo",     "int64",  "Int64.Type",  "0",      "none"),
   ("termo",        "string", "type text",   None,     "none"),
   ("pct_abaixo",   "double", "type number", "0.0",    "none"),
   ("pct_acima",    "double", "type number", "0.0",    "none"),
   ("produtos",     "int64",  "Int64.Type",  "#,0",    "none"),
   ("diferenca_pp", "double", "type number", "+0.0;-0.0;0", "none"),
   ("lado",         "string", "type text",   None,     "none"),
   ("peso",         "double", "type number", "0.0",    "none"),
   ("destaque",      "string", "type text",  None,     "none"),
   ("destaque_lado", "string", "type text",  None,     "none"),
 ],
 "dRecomendacao": [
   ("ordem",           "int64",  "Int64.Type", "0", "none"),
   ("decisao",         "string", "type text",  None, "none"),
   ("por_que",         "string", "type text",  None, "none"),
   ("indicador",       "string", "type text",  None, "none"),
   ("valor_indicador", "string", "type text",  None, "none"),
   ("onde_ver",        "string", "type text",  None, "none"),
 ],
 "dFonte": [
   ("ordem",   "int64",  "Int64.Type", "0", "none"),
   ("secao",   "string", "type text",  None, "none"),
   ("item",    "string", "type text",  None, "none"),
   ("detalhe", "string", "type text",  None, "none"),
 ],
 "dMoeda": [
   ("sk_moeda",        "int64",  "Int64.Type",  "0",       "none"),
   ("moeda",           "string", "type text",   None,      "none"),
   ("simbolo",         "string", "type text",   None,      "none"),
   ("taxa_por_rupia",  "double", "type number", "0.0000",  "none"),
   ("data_referencia", "string", "type text",   None,      "none"),
 ],
}

ARQUIVO = {"dCategoria": "dCategoria.csv", "fProdutos": "fProdutos.csv",
           "fAvaliacoes": "fAvaliacoes.csv", "dTermosAvaliacao": "dTermosAvaliacao.csv",
           "dMoeda": "dMoeda.csv", "dTermoComparado": "dTermoComparado.csv",
           "dRecomendacao": "dRecomendacao.csv", "dFonte": "dFonte.csv"}

OCULTAS = {"fProdutos": {"img_link", "product_link", "sk_categoria"},
           "dCategoria": {"sk_categoria", "caminho_categoria"},
           "fAvaliacoes": {"sk_avaliacao"},
           "dMoeda": {"sk_moeda"},
           "dTermoComparado": {"sk_termo"},
           "dRecomendacao": {"ordem"}, "dFonte": {"ordem"}}

# ---------------------------------------------------------------- colunas calculadas
CALCULADAS = {
 "fProdutos": [
  ("faixa_nota", "string", "faixa_nota_ordem",
   'SWITCH(TRUE(), ISBLANK(fProdutos[rating]), "sem nota", fProdutos[rating] < 3.0, "abaixo de 3,0", '
   'fProdutos[rating] < 3.5, "3,0 a 3,4", fProdutos[rating] < 4.0, "3,5 a 3,9", '
   'fProdutos[rating] < 4.3, "4,0 a 4,2", fProdutos[rating] < 4.5, "4,3 a 4,4", "4,5 ou mais")'),
  ("faixa_nota_ordem", "int64", None,
   'SWITCH(TRUE(), ISBLANK(fProdutos[rating]), 0, fProdutos[rating] < 3.0, 1, '
   'fProdutos[rating] < 3.5, 2, fProdutos[rating] < 4.0, 3, '
   'fProdutos[rating] < 4.3, 4, fProdutos[rating] < 4.5, 5, 6)'),
  ("faixa_preco", "string", "faixa_preco_ordem",
   'SWITCH(TRUE(), fProdutos[discounted_price_rupia] < 200, "ate 200", '
   'fProdutos[discounted_price_rupia] < 500, "200 a 500", '
   'fProdutos[discounted_price_rupia] < 1000, "500 a 1.000", '
   'fProdutos[discounted_price_rupia] < 2000, "1.000 a 2.000", '
   'fProdutos[discounted_price_rupia] < 5000, "2.000 a 5.000", "acima de 5.000")'),
  ("faixa_desconto", "string", "faixa_desconto_ordem",
   'SWITCH(TRUE(), fProdutos[discount_percentage] < 0.2, "ate 20%", '
   'fProdutos[discount_percentage] < 0.4, "20 a 40%", '
   'fProdutos[discount_percentage] < 0.6, "40 a 60%", '
   'fProdutos[discount_percentage] < 0.8, "60 a 80%", "80% ou mais")'),
  ("faixa_desconto_ordem", "int64", None,
   'SWITCH(TRUE(), fProdutos[discount_percentage] < 0.2, 1, '
   'fProdutos[discount_percentage] < 0.4, 2, '
   'fProdutos[discount_percentage] < 0.6, 3, '
   'fProdutos[discount_percentage] < 0.8, 4, 5)'),
  ("faixa_engajamento", "string", "faixa_engajamento_ordem",
   'SWITCH(TRUE(), fProdutos[rating_count] <= 1106, "ate 1.100", '
   'fProdutos[rating_count] <= 4740, "1.100 a 4.700", '
   'fProdutos[rating_count] <= 16020, "4.700 a 16.000", "acima de 16.000")'),
  ("faixa_engajamento_ordem", "int64", None,
   'SWITCH(TRUE(), fProdutos[rating_count] <= 1106, 1, '
   'fProdutos[rating_count] <= 4740, 2, '
   'fProdutos[rating_count] <= 16020, 3, 4)'),
  # os dois bolsos viram coluna para a pagina de lista poder filtrar com In, que e o
  # unico esquema de filtro conferido. Os cortes sao os mesmos das medidas de bolso.
  ("bolso", "string", None,
   'SWITCH( TRUE(), '
   'fProdutos[rating_count] >= 4740 && fProdutos[rating] <= 3.9, "muito avaliado, nota baixa", '
   'fProdutos[rating] >= 4.3 && fProdutos[rating_count] < 1000, "nota alta, pouco visto", '
   '"fora dos bolsos" )'),
  # posto fixo na base inteira: e o que o PBIR permite filtrar com o esquema conferido (In).
  # nao recalcula por categoria selecionada, e o subtitulo do card diz "da base" por isso.
  ("top_avaliacoes", "string", None,
   'IF( RANKX( ALL(fProdutos), fProdutos[rating_count], , DESC ) <= 10, "sim", "nao" )'),
  ("faixa_preco_ordem", "int64", None,
   'SWITCH(TRUE(), fProdutos[discounted_price_rupia] < 200, 1, '
   'fProdutos[discounted_price_rupia] < 500, 2, '
   'fProdutos[discounted_price_rupia] < 1000, 3, '
   'fProdutos[discounted_price_rupia] < 2000, 4, '
   'fProdutos[discounted_price_rupia] < 5000, 5, 6)'),
 ],
}

# ---------------------------------------------------------------- medidas
MEDIDAS = [
 ("Produtos", "DISTINCTCOUNT(fProdutos[product_id])", "#,0"),
 ("Avaliações", "SUM(fProdutos[rating_count])", "#,0"),
 ("Avaliações com texto", "COUNTROWS(fAvaliacoes)", "#,0"),
 ("Taxa selecionada", "SELECTEDVALUE(dMoeda[taxa_por_rupia], 1)", "0.0000"),
 ("Símbolo", 'SELECTEDVALUE(dMoeda[simbolo], "₹")', None),
 ("Preço com desconto", "SUM(fProdutos[discounted_price_rupia]) * [Taxa selecionada]", "#,0"),
 ("Preço cheio", "SUM(fProdutos[actual_price_rupia]) * [Taxa selecionada]", "#,0"),
 ("Preço médio com desconto", "AVERAGE(fProdutos[discounted_price_rupia]) * [Taxa selecionada]", "#,0"),
 ("Preço cheio médio", "AVERAGE(fProdutos[actual_price_rupia]) * [Taxa selecionada]", "#,0"),
 ("Economia oferecida", "[Preço cheio] - [Preço com desconto]", "#,0"),
 ("Desconto médio %", "AVERAGE(fProdutos[discount_percentage])", "0.0%"),
 ("Nota média simples", "AVERAGE(fProdutos[rating])", "0.00"),
 ("Nota média ponderada",
  "DIVIDE( SUMX(fProdutos, fProdutos[rating] * fProdutos[rating_count]), SUM(fProdutos[rating_count]), BLANK() )", "0.00"),
 ("Mediana de avaliações", "MEDIAN(fProdutos[rating_count])", "#,0"),
 ("Categorias de nível 1", "CALCULATE( DISTINCTCOUNT(dCategoria[nivel_1]), fProdutos )", "#,0"),
 ("Caminhos de categoria", "CALCULATE( DISTINCTCOUNT(dCategoria[sk_categoria]), fProdutos )", "#,0"),
 ("Produtos acima da base",
  'CALCULATE( DISTINCTCOUNT(dTermosAvaliacao[product_id]), dTermosAvaliacao[percepcao] = "acima da base" )', "#,0"),
 ("Produtos na média",
  'CALCULATE( DISTINCTCOUNT(dTermosAvaliacao[product_id]), dTermosAvaliacao[percepcao] = "na media" )', "#,0"),
 ("Produtos abaixo da base",
  'CALCULATE( DISTINCTCOUNT(dTermosAvaliacao[product_id]), dTermosAvaliacao[percepcao] = "abaixo da base" )', "#,0"),
 ("Alto engajamento, nota abaixo da base",
  "CALCULATE( [Produtos], FILTER( fProdutos, fProdutos[rating_count] >= 4740 && fProdutos[rating] <= 3.9 ) )", "#,0"),
 ("Nota acima da base, pouca visibilidade",
  "CALCULATE( [Produtos], FILTER( fProdutos, fProdutos[rating] >= 4.3 && fProdutos[rating_count] < 1000 ) )", "#,0"),
 ("Ocorrências de termo", "SUM(dTermosAvaliacao[ocorrencias])", "#,0"),
 ("Diferença em pontos", "SUM(dTermoComparado[diferenca_pp])", '+0.0" pp";-0.0" pp";0'),
 ("Peso do termo", "SUM(dTermoComparado[peso])", '0.0" pp"'),
 # as duas series do grafico comparativo da pagina 4
 ("% nos que reclamam", "AVERAGE(dTermoComparado[pct_abaixo])", '0.0"%"'),
 ("% nos que elogiam", "AVERAGE(dTermoComparado[pct_acima])", '0.0"%"'),
 # os indicadores que sustentam cada recomendacao da pagina 5
 ("Concentração nas 3 maiores",
  "DIVIDE( SUMX( TOPN(3, ALL(dCategoria[nivel_1]), [Produtos], DESC), [Produtos] ), CALCULATE([Produtos], ALL(dCategoria)) )", "0.0%"),
 ("Queda de nota no desconto alto",
  'CALCULATE([Nota média ponderada], fProdutos[faixa_desconto] = "ate 20%") - CALCULATE([Nota média ponderada], fProdutos[faixa_desconto] = "80% ou mais")', "0.00"),
 ("Diferença de ruído",
  'CALCULATE( [Diferença em pontos], ALL(dTermoComparado), dTermoComparado[termo] = "noise" )', '+0.0" pp";-0.0" pp";0'),
 ("Amplitude da nota entre faixas de preço",
  "MAXX( VALUES(fProdutos[faixa_preco]), [Nota média ponderada] ) - MINX( VALUES(fProdutos[faixa_preco]), [Nota média ponderada] )", "0.00"),
 # o que a pagina de dica mostra do termo sob o cursor
 ("Termo em foco", 'SELECTEDVALUE(dTermoComparado[termo], "vários termos")', None),
 ("Produtos com o termo", "SUM(dTermoComparado[produtos])", "#,0"),
 ("Faixa em foco", 'SELECTEDVALUE(fProdutos[faixa_engajamento], "todas as faixas")', None),
 # categoria com 1 ou 2 produtos nao sustenta nota: a medida apaga a barra em vez de
 # deixar uma amostra de 1 produto liderar o grafico de satisfacao
 ("Nota ponderada com amostra mínima",
  "IF( [Produtos] >= 10, [Nota média ponderada] )", "0.00"),
 ("Produto mais avaliado",
  "MAXX( TOPN(1, ALLSELECTED(fProdutos), fProdutos[rating_count], DESC), fProdutos[product_name] )", None),
]

MEDIDAS_MULTILINHA = []

# ---------------------------------------------------------------- relacionamentos
RELACOES = [
 ("dCategoria", "sk_categoria", "fProdutos", "sk_categoria"),
 ("fProdutos", "product_id", "fAvaliacoes", "product_id"),
 ("fProdutos", "product_id", "dTermosAvaliacao", "product_id"),
]


def consulta_m(tabela, pasta):
    cols = TABELAS[tabela]
    tipos = ", ".join(f'{{"{n}", {tm}}}' for n, _, tm, _, _ in cols)
    return (f'let\n'
            f'    Origem = Csv.Document(File.Contents("{pasta}{ARQUIVO[tabela]}"), '
            f'[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n'
            f'    Cabecalho = Table.PromoteHeaders(Origem, [PromoteAllScalars=true]),\n'
            f'    Tipado = Table.TransformColumnTypes(Cabecalho, {{{tipos}}}, "en-US")\n'
            f'in\n'
            f'    Tipado')


def bloco_m(texto, niveis):
    p = T * niveis
    return "\n".join(p + l for l in texto.split("\n"))


def tmdl_tabela(tabela, pasta):
    L = [f"table {tabela}", f"{T}lineageTag: {tag('t:'+tabela)}", ""]
    for nome, dt, _, fmt, sb in TABELAS[tabela]:
        L.append(f"{T}column {nome}")
        if nome in OCULTAS.get(tabela, set()):
            L.append(f"{T*2}isHidden")
        L.append(f"{T*2}dataType: {dt}")
        if fmt:
            L.append(f"{T*2}formatString: {fmt}")
        L.append(f"{T*2}lineageTag: {tag(f'c:{tabela}.{nome}')}")
        L.append(f"{T*2}summarizeBy: {sb}")
        L.append(f"{T*2}sourceColumn: {nome}")
        L.append("")
        L.append(f"{T*2}annotation SummarizationSetBy = Automatic")
        L.append("")
    for nome, dt, ordena, dax in CALCULADAS.get(tabela, []):
        L.append(f"{T}column {nome} = {dax}")
        L.append(f"{T*2}dataType: {dt}")
        if nome.endswith("_ordem"):
            L.append(f"{T*2}isHidden")
        L.append(f"{T*2}lineageTag: {tag(f'cc:{tabela}.{nome}')}")
        L.append(f"{T*2}summarizeBy: none")
        if ordena:
            L.append(f"{T*2}sortByColumn: {ordena}")
        L.append("")
        L.append(f"{T*2}annotation SummarizationSetBy = Automatic")
        L.append("")
    L.append(f"{T}partition {tabela} = m")
    L.append(f"{T*2}mode: import")
    L.append(f"{T*2}source =")
    L.append(bloco_m(consulta_m(tabela, pasta), 4))
    L.append("")
    L.append(f"{T}annotation PBI_ResultType = Table")
    L.append("")
    return "\n".join(L)


def tmdl_medidas():
    L = ["table _Medidas", f"{T}lineageTag: {tag('t:_Medidas')}", ""]
    for nome, dax, fmt in MEDIDAS:
        L.append(f"{T}measure '{nome}' = {dax}")
        if fmt:
            L.append(f"{T*2}formatString: {fmt}")
        L.append(f"{T*2}lineageTag: {tag('m:'+nome)}")
        L.append("")
    for nome, dax, fmt in MEDIDAS_MULTILINHA:
        L.append(f"{T}measure '{nome}' = ```")
        L.append(bloco_m(dax, 3))
        L.append(f"{T*2}```")
        if fmt:
            L.append(f"{T*2}formatString: {fmt}")
        L.append(f"{T*2}lineageTag: {tag('m:'+nome)}")
        L.append("")
    L.append(f"{T}column Coluna")
    L.append(f"{T*2}isHidden")
    L.append(f"{T*2}dataType: string")
    L.append(f"{T*2}lineageTag: {tag('c:_Medidas.Coluna')}")
    L.append(f"{T*2}summarizeBy: none")
    L.append(f"{T*2}sourceColumn: Coluna")
    L.append("")
    L.append(f"{T*2}annotation SummarizationSetBy = Automatic")
    L.append("")
    L.append(f"{T}partition _Medidas = m")
    L.append(f"{T*2}mode: import")
    L.append(f"{T*2}source =")
    L.append(bloco_m('let\n    Origem = #table({"Coluna"}, {})\nin\n    Origem', 4))
    L.append("")
    L.append(f"{T}annotation PBI_ResultType = Table")
    L.append("")
    return "\n".join(L)


def tmdl_relacoes():
    L = []
    for de_t, de_c, para_t, para_c in RELACOES:
        nome = tag(f"r:{de_t}.{de_c}>{para_t}.{para_c}")
        L.append(f"relationship {nome}")
        L.append(f"{T}fromColumn: {para_t}.{para_c}")
        L.append(f"{T}toColumn: {de_t}.{de_c}")
        L.append("")
    return "\n".join(L)


def main():
    if len(sys.argv) < 2:
        print('uso: python aplicar_modelo.py "<pasta que contem o .pbip>"')
        sys.exit(1)
    raiz = os.path.abspath(sys.argv[1])
    modelo = None
    for d in os.listdir(raiz):
        if d.endswith(".SemanticModel"):
            modelo = os.path.join(raiz, d)
    if not modelo:
        print(f"ERRO: nenhuma pasta .SemanticModel em {raiz}")
        sys.exit(1)

    definicao = os.path.join(modelo, "definition")
    tabelas = os.path.join(definicao, "tables")
    os.makedirs(tabelas, exist_ok=True)

    # a pasta dos CSV fica dois niveis acima: ../results
    dados = os.path.abspath(os.path.join(raiz, "..", "results")) + os.sep

    escritos = []
    for t in TABELAS:
        p = os.path.join(tabelas, f"{t}.tmdl")
        open(p, "w", encoding="utf-8").write(tmdl_tabela(t, dados.replace("\\", "\\\\")))
        escritos.append(p)
    p = os.path.join(tabelas, "_Medidas.tmdl")
    open(p, "w", encoding="utf-8").write(tmdl_medidas())
    escritos.append(p)

    p = os.path.join(definicao, "relationships.tmdl")
    open(p, "w", encoding="utf-8").write(tmdl_relacoes())
    escritos.append(p)

    # model.tmdl precisa referenciar tudo
    mp = os.path.join(definicao, "model.tmdl")
    m = open(mp, encoding="utf-8").read()
    refs = ["ref table " + t for t in list(TABELAS) + ["_Medidas"]]
    m = "\n".join(l for l in m.split("\n") if not l.startswith("ref table "))
    m = m.rstrip("\n") + "\n"
    m += "\n" + "\n".join(refs) + "\n"
    open(mp, "w", encoding="utf-8").write(m)
    escritos.append(mp)

    print(f"pasta dos CSV: {dados}")
    for p in escritos:
        print(f"  {os.path.relpath(p, raiz)}  ({os.path.getsize(p):,} bytes)")
    print(f"\n{len(TABELAS)} tabelas, {len(MEDIDAS)+len(MEDIDAS_MULTILINHA)} medidas, "
          f"{len(RELACOES)} relacionamentos, "
          f"{sum(len(v) for v in CALCULADAS.values())} colunas calculadas")


if __name__ == "__main__":
    main()
