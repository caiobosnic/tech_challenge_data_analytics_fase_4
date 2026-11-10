# Tech Challenge Fase 4: dashboard de Power BI gerado por código

PosTech FIAP Data Analytics, Grupo 21. Caio Rodrigues Bosnic Barbosa, RM 372603.

Trabalho de grupo. Os três notebooks têm autores diferentes e estão creditados abaixo.
A parte que este repositório detalha é a minha: a modelagem em star schema e o painel.

**Vídeo executivo do grupo:** <https://youtu.be/ZIk8-Yih-8w>
**Repositório do grupo:** <https://github.com/GusthavoSoares/tech_challenge_data_analytics_fase_4>

---

## O que tem de diferente aqui

O painel não foi montado arrastando visual no Power BI Desktop. Ele é **escrito por
script** no formato `.pbip`, que é texto e versiona como código.

```powershell
python powerbi\fundos\gerar.py                            # 14 fundos SVG
python powerbi\_modelo\aplicar_modelo.py  "...\powerbi"   # 8 tabelas, 35 medidas
python powerbi\_modelo\aplicar_visuais.py "...\powerbi"   # 14 páginas, 121 visuais
python powerbi\_modelo\conferir.py        "...\powerbi"   # confere antes de abrir
```

Quatro scripts idempotentes. Mudou o texto de uma recomendação no notebook? Roda os
quatro e o painel inteiro acompanha, incluindo o texto desenhado no fundo.

### O conferidor

`conferir.py` é a parte de que mais gosto. Ele abre os 121 `visual.json` e o modelo TMDL
antes de o Power BI abrir, e reprova o projeto se achar qualquer uma destas:

| Checagem | O erro que ela evita |
|---|---|
| medida ou coluna referenciada que não existe no modelo | visual vazio sem explicação |
| `sortDefinition` fora de `query` | barra ordenada por nome em vez de valor |
| `active` em projeção que não é categoria | aviso em todo `tableEx` |
| cartão com altura menor que `2 × fonte + 14` | número cortado em cima e embaixo |
| visual que passa da borda da página | visual que some na margem |
| dica apontando para página que não existe ou não é `type: Tooltip` | hover sem nada |
| **selo desenhado no fundo sem a entrega correspondente** | promessa que o painel não cumpre |
| travessão em qualquer arquivo | regra de escrita do projeto |

A última linha é a que mais pegou erro. Cada selo dourado no fundo anuncia uma dica ou
uma ação; o conferidor cruza o `coordenadas.json` com os visuais gerados e reprova se o
fundo prometer algo que o visual não entrega. Eram oito selos e, numa das rodadas,
**nenhum** estava implementado.

A regra de altura de cartão saiu de medição, não de teoria: 15D em 46px e 17D em 52px
renderizam inteiro, 11D em 34px corta. Razão sozinha não separava os dois casos.

Testei o conferidor plantando defeito de propósito. Ele pega os três e sai com código 1.

### O que foi conferido antes de ser escrito

Todo construto PBIR usado aqui foi lido de um arquivo real do projeto da fase 3, nunca
escrito de memória: `sortDefinition` dentro de `query`, `columnWidth` com
`selector.metadata`, `labelPosition: OutsideEnd`, `dataPoint` por medida, ação
`ClearAllSlicers`, página de dica com `type: Tooltip`.

Duas coisas **não** estão aqui por falta de referência conferida: drill de hierarquia em
gráfico e filtro Top N. Nos 291 visuais do projeto anterior não existe nenhum dos dois, e
preferi mudar a promessa do subtítulo a inventar esquema. O card dos 10 mais avaliados usa
coluna calculada com `RANKX`, e o subtítulo diz "da base" por causa disso.

## Estrutura

```
.
├── data/amazon.csv                             base do Kaggle
├── notebooks/
│   ├── tc_4_amazon.ipynb                       extração e tratamento inicial
│   ├── tc_4_amazon_novo.ipynb                  limpeza textual e NLP
│   └── tc_4_amazon_modelagem_powerbi.ipynb     star schema, 9 tabelas
├── results/                                    as 9 tabelas que o painel lê
└── powerbi/
    ├── LEIA.md                                 como rodar e o que foi conferido
    ├── tc4_amazon.pbip                         projeto em texto
    ├── _modelo/                                os três scripts e o conferidor
    └── fundos/                                 gerador dos SVG, os 14 fundos e as prévias
```

## O painel

14 páginas: 6 de leitura, 1 de lista alcançada por botão, e 7 de dica de ferramenta.
121 visuais, 35 medidas, 10 colunas calculadas.

| Página | O que responde |
|---|---|
| Visão executiva | onde o portfólio ganha e onde perde |
| Produtos e categorias | relevância, hierarquia e engajamento |
| Preços e descontos | desconto compra avaliação? e a satisfação por categoria |
| Customer insights | o que separa quem reclama de quem elogia |
| Recomendações | seis decisões, cada uma com o número que a sustenta |
| Fontes e premissas | de onde veio cada número e o que foi assumido |
| Produtos em foco | os 112 e os 76 que as recomendações mandam investigar, nominalmente |

A página de recomendações não é tabela. Cada bloco traz a decisão, o porquê, a base do
número e um botão que leva à página onde dá para conferir. O número vem de medida do
modelo e acompanha o filtro; o texto ao redor é fixo e declarado como interpretação.

## O que a análise encontrou

| Achado | Número |
|---|---|
| Concentração do catálogo | 97,2% dos produtos em 3 categorias (1.313 de 1.351) |
| Desconto contra nota | Pearson -0,16. A nota ponderada cai de 4,16 para 4,01 da menor à maior faixa de desconto |
| Desconto contra engajamento | +0,00 |
| Tráfego desperdiçado | 112 produtos muito avaliados com nota no quartil inferior |
| Reputação parada | 76 produtos bem avaliados com menos de mil avaliações |
| O que separa reclamação de elogio | `average` +13,8 pp, `bad` +13,2 pp, `noise` +9,9 pp |
| Preço contra satisfação | a nota varia só 0,10 ponto entre as seis faixas de preço |

## Decisões de modelagem que mudaram o resultado

**A categoria é hierarquia, não lista.** Virar linha inflaria a soma de `rating_count` de
23,8 milhões para 98,9 milhões, **4,2 vezes**. O notebook calcula as duas e mostra lado a
lado.

**O corte de percepção é percentil.** Um corte fixo em 3,0 marcaria 6 produtos de 1.351
como negativos. Os percentis 25 e 75 desta base dão 3,90 e 4,30, e separam 340, 591 e 419.

**Termo exclusivo de uma faixa é nome de marca.** A primeira versão devolvia `boult` e
`sandisk`. A final compara só termo presente nas duas faixas, por frequência relativa.

**`review_id` não é chave.** 759 ids aparecem em produtos diferentes. A tabela de fato usa
chave substituta.

## Créditos

| Notebook | Autoria |
|---|---|
| `tc_4_amazon.ipynb` | grupo |
| `tc_4_amazon_novo.ipynb` | grupo |
| `tc_4_amazon_modelagem_powerbi.ipynb`, modelo e painel | Caio Bosnic |

## Grupo 21

Alexandre de Souza Amorim (372077) · Allison Lima (372648) ·
Caio Rodrigues Bosnic Barbosa (372603) · Gusthavo Lourenço Rios Soares (371911)
