# -*- coding: utf-8 -*-
"""
Confere o projeto do Power BI antes de abrir o arquivo.

Uso:
    python conferir.py "<pasta que contem o .pbip>"

Cada checagem abaixo nasceu de um erro que ja aconteceu neste trabalho ou no TC3.
Nao inventa regra: so testa o que ja custou uma rodada de ida e volta.
"""
import glob, io, json, os, re, sys

# Altura minima de um cartao, em px, para a fonte nao cortar o numero.
# Calibrado no que de fato renderizou: 15D em 46px e 17D em 52px passam,
# 11D em 34px corta. A conta que separa os dois casos e 2*fonte + 14.
def altura_minima(fonte):
    return 2 * fonte + 14
SCHEMA_OK = "visualContainer/2.12.0"


def ler(caminho):
    return json.load(io.open(caminho, encoding="utf-8"))


def campo(f):
    if "Measure" in f:
        return "_Medidas", f["Measure"]["Property"]
    if "Column" in f:
        return f["Column"]["Expression"]["SourceRef"]["Entity"], f["Column"]["Property"]
    return None, None


def literal(d, *caminho):
    """Puxa o valor de um Literal aninhado sem explodir quando falta um nivel.
    No PBIR quase todo objeto e uma lista de um elemento, entao desembrulha a cada passo."""
    for k in caminho:
        if isinstance(d, list):
            if not d:
                return None
            d = d[0]
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    if isinstance(d, list) and d:
        d = d[0]
    if isinstance(d, dict):
        return d.get("expr", {}).get("Literal", {}).get("Value")
    return None


def main():
    if len(sys.argv) < 2:
        print('uso: python conferir.py "<pasta que contem o .pbip>"')
        sys.exit(1)
    raiz = os.path.abspath(sys.argv[1])
    rep = next((os.path.join(raiz, d) for d in os.listdir(raiz) if d.endswith(".Report")), None)
    sem = next((os.path.join(raiz, d) for d in os.listdir(raiz) if d.endswith(".SemanticModel")), None)
    if not rep or not sem:
        print(f"ERRO: nao achei .Report e .SemanticModel em {raiz}")
        sys.exit(1)
    R, S = os.path.join(rep, "definition"), os.path.join(sem, "definition")

    medidas = set(re.findall(r"measure '([^']+)'",
                             io.open(f"{S}/tables/_Medidas.tmdl", encoding="utf-8").read()))
    colunas = {}
    for t in glob.glob(f"{S}/tables/*.tmdl"):
        txt = io.open(t, encoding="utf-8").read()
        tab = re.search(r"^table (\S+)", txt, re.M).group(1)
        colunas[tab] = set(re.findall(r"^\tcolumn ([^\s=]+)", txt, re.M))

    paginas = {os.path.basename(os.path.dirname(a)): ler(a)
               for a in glob.glob(f"{R}/pages/*/page.json")}
    ordem = ler(f"{R}/pages/pages.json")["pageOrder"]
    coords = ler(os.path.join(raiz, "fundos", "coordenadas.json"))

    erros, n_vis, com_dica = [], 0, set()

    for arq in sorted(glob.glob(f"{R}/pages/*/visuals/*/visual.json")):
        n_vis += 1
        d = ler(arq)
        v, nome, tipo = d["visual"], d["name"], d["visual"]["visualType"]
        pag = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(arq))))

        if SCHEMA_OK not in d["$schema"]:
            erros.append(f"{nome}: schema diferente de {SCHEMA_OK}")
        if "sortDefinition" in v:
            erros.append(f"{nome}: sortDefinition fora de query")
        if "tooltipText" in json.dumps(d):
            erros.append(f"{nome}: tooltipText nao existe no schema 2.12.0")
        if tipo == "actionButton" and "query" in v:
            erros.append(f"{nome}: actionButton nao leva query")

        for papel, bloco in v.get("query", {}).get("queryState", {}).items():
            for pr in bloco.get("projections", []):
                ent, prop = campo(pr["field"])
                alvo = medidas if ent == "_Medidas" else colunas.get(ent, set())
                if prop not in alvo:
                    erros.append(f"{nome}: {ent}.{prop} nao existe no modelo")
                if pr.get("active") and not (
                        papel == "Category" or (tipo in ("card", "slicer") and papel == "Values")):
                    erros.append(f"{nome}: active em {papel} de {tipo}")

        for flt in d.get("filterConfig", {}).get("filters", []):
            ent, prop = campo(flt["field"])
            if prop not in colunas.get(ent, set()):
                erros.append(f"{nome}: filtro em {ent}.{prop}, que nao existe")

        for sel in v.get("objects", {}).get("columnWidth", []) + \
                   v.get("objects", {}).get("dataPoint", []):
            m = sel.get("selector", {}).get("metadata")
            if m:
                ent, _, prop = m.partition(".")
                alvo = medidas if ent == "_Medidas" else colunas.get(ent, set())
                if prop not in alvo:
                    erros.append(f"{nome}: selector aponta para {m}, que nao existe")

        if tipo == "card":
            f = literal(v, "objects", "labels", "properties", "fontSize")
            if f:
                alto = d["position"]["height"]
                minimo = altura_minima(float(f.rstrip("D")))
                if alto < minimo:
                    erros.append(f"{nome}: {f} em {alto}px, precisa de {minimo:g}, o valor corta")

        pg = paginas.get(pag, {})
        pos = d["position"]
        if pg and (pos["x"] + pos["width"] > pg["width"] + 0.5 or
                   pos["y"] + pos["height"] > pg["height"] + 0.5):
            erros.append(f'{nome}: passa da borda de {pag} ({pg["width"]}x{pg["height"]})')

        if literal(v, "visualContainerObjects", "visualTooltip", "properties", "type") == "'Canvas'":
            secao = literal(v, "visualContainerObjects", "visualTooltip",
                            "properties", "section").strip("'")
            com_dica.add(nome)
            if secao not in paginas:
                erros.append(f"{nome}: dica aponta para pagina inexistente {secao}")
            elif paginas[secao].get("type") != "Tooltip":
                erros.append(f"{nome}: dica aponta para {secao}, que nao e type Tooltip")

    for pid in paginas:
        if pid not in ordem:
            erros.append(f"pages.json: {pid} fora do pageOrder")

    # todo selo dourado desenhado no fundo e uma promessa: ou existe a dica, ou tira o selo
    prefixo = {"01_visao_executiva": "p1", "02_produtos_categorias": "p2",
               "03_precos_descontos": "p3", "04_customer_insights": "p4",
               "07_produtos_em_foco": "p7"}
    nomes = {ler(a)["name"] for a in glob.glob(f"{R}/pages/*/visuals/*/visual.json")}
    n_selos = 0
    for pag, areas in coords.items():
        for cid, a in areas.items():
            selo = a.get("selo")
            if not selo:
                continue
            n_selos += 1
            alvo = f"{prefixo.get(pag, '?')}_{cid}"
            if selo.startswith("dica"):
                if alvo not in com_dica:
                    erros.append(f'{alvo}: o fundo promete "{selo}" e o visual nao tem dica')
            # selo que nao e dica anuncia uma acao: tem que existir botao em cima dele
            elif f"{alvo}_ir" not in nomes:
                erros.append(f'{alvo}: o fundo promete "{selo}" e nao existe botao {alvo}_ir')

    for arq in glob.glob(f"{R}/**/*.json", recursive=True) + \
               glob.glob(f"{S}/**/*.tmdl", recursive=True):
        if "—" in io.open(arq, encoding="utf-8").read():
            erros.append(f"{os.path.basename(arq)}: travessao")

    print(f"{n_vis} visuais em {len(paginas)} paginas "
          f"({sum(1 for p in paginas.values() if p.get('type') == 'Tooltip')} de dica)")
    print(f"{len(medidas)} medidas, {sum(len(c) for c in colunas.values())} colunas, "
          f"{n_selos} selos no fundo, {len(com_dica)} visuais com dica")
    print()
    if erros:
        for e in erros:
            print("  X", e)
        sys.exit(1)
    print("  nenhum problema")


if __name__ == "__main__":
    main()
