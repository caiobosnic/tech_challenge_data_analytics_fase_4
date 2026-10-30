# Scripts do dashboard

Rodar **com o Power BI fechado**, nesta ordem, da raiz do `tech_challenge_4`:

```powershell
python powerbi\fundos\gerar.py
python powerbi\_modelo\aplicar_modelo.py  "$PWD\powerbi"
python powerbi\_modelo\aplicar_visuais.py "$PWD\powerbi"
python powerbi\_modelo\conferir.py        "$PWD\powerbi"
```

Os quatro são idempotentes. `gerar.py` só precisa rodar quando o texto autoral
(`dRecomendacao.csv`, `dFonte.csv`) ou a geometria mudarem.

| Script | O que faz |
|---|---|
| `fundos\gerar.py` | escreve os 13 SVG de fundo e o `coordenadas.json`. Lê `dRecomendacao.csv` e `dFonte.csv` para desenhar o texto das páginas 5 e 6 |
| `_modelo\aplicar_modelo.py` | escreve o modelo semântico em TMDL: 8 tabelas de dados mais `_Medidas`, 34 medidas, 3 relacionamentos de direção única, 9 colunas calculadas |
| `_modelo\aplicar_visuais.py` | escreve 13 páginas e 110 visuais, copia os SVG para `RegisteredResources` e registra o pacote no `report.json` |
| `_modelo\conferir.py` | confere o resultado antes de abrir o arquivo. Sai com código 1 se achar problema |

O caminho dos CSV é calculado a partir da pasta do `.pbip` (`..\results`), então mover o
projeto só exige rodar de novo.

## O que o projeto tem hoje

| | |
|---|---|
| Páginas de leitura | 6 (Visão executiva, Produtos e categorias, Preços e descontos, Customer insights, Recomendações, Fontes e premissas) |
| Páginas de dica | 7, todas 400 de largura, `type: Tooltip` |
| Visuais | 110: 42 cartões, 40 botões, 16 segmentações, 11 gráficos, 1 tabela |
| Medidas | 34 |
| Colunas calculadas | 9 (as faixas e as suas colunas de ordenação, mais `top_avaliacoes`) |

As tabelas: `fProdutos` (1.351), `dCategoria` (211), `fAvaliacoes` (10.598),
`dTermosAvaliacao` (114.500), `dTermoComparado` (840), `dMoeda` (3),
`dRecomendacao` (6), `dFonte` (15).

## O que foi conferido em arquivo real do TC3, não escrito de memória

| Construto | Onde confere |
|---|---|
| `sortDefinition` vive **dentro de `query`** | `g_cargo` |
| `active: true` só no eixo de categoria, nunca na medida | `g_cargo` |
| `active` ausente em toda projeção de `tableEx` | `t_benchmark` |
| `filterConfig` no nível do visual, com `From`/`Where`/`In` | `g_cargo` |
| botão sem consulta, ação em `visualContainerObjects.visualLink` | `menu_0` |
| fundo da página em `objects.background` com `ResourcePackageItem` | `page.json` do Início |
| `labelPosition: 'OutsideEnd'` e `enableBackground` no rótulo | `g_cargo` |
| `columnWidth` por coluna com `selector.metadata`, mais `columnAdjustment: fixedWidth` | `t_benchmark` |
| `dataPoint` com uma cor por medida, via `selector.metadata` | `g_cargo` |
| ação `'ClearAllSlicers'` no botão | `botao_limpar.json` |
| página de dica: `type: "Tooltip"`, `displayOption: "ActualSize"`, 400x300 | `page.json` de `297783e59b0c2b2b3906` |
| `visualTooltip` com `type: 'Canvas'` e `section` apontando para ela | `g_cargo` |

A pasta `referencia\` tem os 291 `visual.json` do TC3 achatados. Antes de escrever
qualquer construto novo, procurar ali primeiro.

## O que foi tentado e não funciona

**`tooltipText`** não existe no schema `visualContainer/2.12.0`. O Power BI aceita com
aviso de propriedade adicional em cada visual. Removido.

**DAX em várias linhas** no TMDL precisa de bloco com três crases. Uma quebra fora de
lugar impede o arquivo de abrir. Toda medida aqui é de uma linha só.

**`Table.TransformColumnTypes` sem o terceiro argumento `"en-US"`** faz o pt-BR ler
`3305.42` como `330542`. Todas as consultas M passam a cultura.

## O que não existe por falta de referência

**Drill de hierarquia** em gráfico. Precisa de `Category` com várias projeções e
`active` só na primeira. Nenhum dos 291 arquivos do TC3 tem isso: lá, todo visual com
vários campos é `tableEx`. Enquanto não houver molde, a hierarquia de categoria é
navegada pela segmentação de nível 1, e o subtítulo do gráfico diz isso.

**Filtro Top N** no PBIR. Também sem referência. O card dos 10 mais avaliados usa a
coluna calculada `top_avaliacoes`, que é posto fixo na base inteira com `RANKX`. O
subtítulo diz "da base" por causa disso: filtrar uma categoria mostra quais dos 10 são
dela, não refaz o top 10 dentro dela.

Para destravar os dois, basta montar o visual à mão no Desktop, salvar, e copiar o
`visual.json` dele para `referencia\`.

## As regras que o `conferir.py` aplica

Cada uma nasceu de um erro que já aconteceu, não de teoria:

| Checagem | O erro que ela evita |
|---|---|
| schema `2.12.0` em todo visual | arquivo que não abre |
| `sortDefinition` dentro de `query` | barra ordenada por nome em vez de valor |
| `active` só na categoria | aviso em todo `tableEx` |
| nada de `tooltipText` | 30 linhas de aviso ao abrir |
| botão sem query | aviso no botão |
| toda medida e coluna referenciada existe no modelo | visual vazio sem explicação |
| todo `selector.metadata` aponta para alvo real | largura de coluna e cor que não aplicam |
| altura do cartão ≥ 2 × fonte + 14 | número cortado em cima e embaixo |
| visual dentro da borda da página | visual que some na margem |
| dica aponta para página que existe e é `type: Tooltip` | hover sem nada |
| toda página está no `pageOrder` | página que não aparece |
| **todo selo dourado do fundo tem a dica correspondente** | promessa desenhada e não entregue |
| zero travessão em qualquer arquivo | regra do projeto |

A conta `2 × fonte + 14` saiu dos casos reais: 15D em 46px e 17D em 52px renderizam,
11D em 34px corta. Razão sozinha não separava os dois.
