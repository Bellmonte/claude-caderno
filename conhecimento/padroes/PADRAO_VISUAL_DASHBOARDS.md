# Padrão Visual: referência canônica (Power BI)

> Destilado de dois dashboards-vitrine, aqui chamados pelo arquétipo: o **Painel Retrato** (tela rica, flagship do padrão HTML/DAX) e o **Painel Widescreen** (variante corporativa, tela larga).
> Os dois falam a MESMA linguagem visual. A norma de "tela rica" é o Painel Retrato.
> A skill montar-visuais aponta para cá. Decisões já fechadas estão marcadas com ✓.
> As cores são uma paleta neutra de partida (acento `#2F6F8F`). Troque os slots de marca (§2) pela identidade da sua empresa e mantenha o resto da estrutura.
> Duas técnicas sustentam este padrão: a identidade por imagem de fundo com visuais transparentes por cima, e o visual HTML alimentado por medida DAX. A arte de fundo pode ser gerada por script (ex.: Python com Pillow) a partir das coordenadas dos visuais, para a moldura casar com o layout ao pixel.

## 1. Arquitetura da tela (as 4 camadas)
Toda tela do padrão empilha, de baixo para cima:
1. **Imagem PNG de fundo** (registrada em `StaticResources/RegisteredResources`, `scaling:'Fit'`, `transparency:0`): pinta os cartões brancos arredondados das seções e a arte fixa. É o "chassi" visual.
2. **Tema JSON** (`visualStyles.*`): reaplica fundo branco, borda e raio em cada visual nativo para casar com a arte (redundância proposital: se a arte sair, o visual ainda parece cartão).
3. **Visuais nativos**: gráficos de eixo (combo coluna+linha, barras), card de KPI, tabela `tableEx`/`pivotTable`, slicers.
4. **Visuais HTML/DAX**: cartões de narrativa ricos (header, insights, tabelas estilizadas, heatmap, sparkline) via custom visual **HTML Content** (Daniel Marsh-Patrick) alimentado por medida que concatena HTML/CSS/SVG.

✓ Regra de ouro do que vai em cada motor: **gráfico de eixo e card de KPI = nativo com tema**; **cartão de narrativa / tabela estilizada / heatmap / sparkline = HTML por medida DAX**. Nada de Deneb nem Charticulator: o único custom é o HTML Content.

## 2. Paleta (slots do tema)
Uma estrutura de slots só. Se a empresa tiver mais de uma identidade (marca principal e variante), cada uma vira um tema irmão com os mesmos slots, e **as duas identidades não se misturam no mesmo BI.**

| Slot do tema | Papel | Valor neutro de partida |
|---|---|---|
| dataColors[0] | marca / barras | `#2F6F8F` |
| dataColors[1] | destaque secundário | `#B7791F` (âmbar) |
| dataColors[2] | série de apoio | `#7FA7BC` |
| dataColors[3] | linha de referência | `#A4473A` |
| good | positivo | `#2F7D57` |
| neutral | atenção | `#B7791F` |
| bad | negativo | `#B04C3E` |
| maximum | topo de escala | `#2F6F8F` |
| center | meio de escala | `#F5F7F8` |
| null | sem dado | `#9AA1A9` |
| foreground | texto | `#1B2230` |
| tableAccent | total da matriz | `#2F6F8F` |
| background | fundo de visual | `#FFFFFF` |
| outspace / page | fundo de página | `#F3F5F7` |
| borda de cartão | contorno | `#E3E6EB` |
| gridline | grade | `#EEF0F3` |

Cinzas de texto secundário: `#4B5563` (rótulo) e `#6B7280` (subtítulo); legenda e caption em `#9AA1A9`.
O acento é marca e o verde é status (`good #2F7D57`, semáforo `#1B5E20`); os papéis não se trocam. Ao portar para a identidade da empresa, troque `dataColors[0/1]`, `tableAccent`, `maximum` e o fundo do total da matriz; preserve o destaque secundário como acento.

## 3. Tipografia
- Fonte única: **Segoe UI** em tudo (nos HTML: `Segoe UI, Tahoma/Arial, sans-serif`). Callout/número grande usa `Segoe UI Bold`/`Segoe UI Semibold`.
- Escala de tamanhos (px) observada, do maior ao menor:

| Uso | Painel Retrato | Painel Widescreen |
|---|---|---|
| Display de título de tela | 39 | (via callout do tema, 36) |
| Número KPI / callout | 22 | 26 (strip) / 38 (HTML card) |
| Nome de entidade (header) | 22 | não usa |
| Valor de insight | 18 | 20 (multiRowCard) |
| Badge / KPI de header | 15 | não usa |
| Título de bloco HTML | 13 | não usa |
| Título de visual nativo | 12 | 13 a 16 |
| Rótulo / label | 10 a 11 | 10 a 12 |
| Sub-rótulo / caption | 8 a 9.5 | 10 |

- Pesos: 700 títulos e valores; 600 subtítulos/semibold; 300 a 500 no display de título grande (efeito editorial, ex.: "Visão de **clientes**" com o span em itálico 500).

## 4. Tokens de forma (raio, borda, sombra, trilho)
| Token | Painel Retrato | Painel Widescreen |
|---|---|---|
| Raio padrão de visual (tema) | 10 | 8 |
| Raio de cartão header (HTML) | 14 | não usa |
| Raio de card KPI / chip | 10 | 10 (tile), 6 (mini-card HTML) |
| Raio de badge YoY | 8 | não usa |
| Raio de célula heatmap | 7 | não usa |
| Raio de barra de progresso | 3 a 4 | não usa |
| Ícone/ponto circular | 50% | 50% |
| Borda de cartão | 1px `#E3E6EB` | 1px `#E3E6EB` |
| Sombra do card KPI | nenhuma (fundo `#FCFCFD`) | on: angle 45, distance 10, spread 1, transp 75 |

Barra de progresso (Painel Retrato): trilho `background:#E3E6EB;border-radius:4px;height:5px` + fill `background:#2F6F8F;border-radius:4px`.

## 5. O que fica no tema e o que fica no visual
- **No tema** (`visualStyles`): fundo branco, borda+raio, header do visual, título padrão e, no Painel Widescreen, estilos completos de `pivotTable`/`tableEx`/`slicer`/`barChart.defaultColor`/eixos/legenda. O Painel Retrato mantém o tema enxuto (só o `*` global) e resolve o resto no visual.json.
- **No visual.json**: cores de série por `ThemeDataColor ColorId N` (nunca hex cru em série: referencia o índice do tema), cor condicional por medida-cor, data labels, títulos/subtítulos específicos.
- ✓ Cor condicional de fonte em `tableEx` = medida-cor (devolve hex ou BLANK) + binding `fontColor` por valor de campo apontando para essa medida.

## 6. Componentes nativos (tokens aplicados)
### Card de KPI
- **Painel Retrato**: `cardVisual` multilinha "Indicadores Gerais": callout `fontSize 22`, `#1B2230`, Segoe UI Bold, alinhado à esquerda; rótulo Segoe UI `#6B7280` 10px; delta `#9AA1A9`; `tileShape:rectangleRounded` curve 10; fundo `#FCFCFD`; borda `#E3E6EB`. Cada KPI acompanha um `actionButton` `information` com tooltip textual.
- **Painel Widescreen**: `cardVisual` em grade `autoGrid` 10 col: número `fontSize 26` Segoe UI Bold cor `ColorId 2`; rótulo `#6B7280` 12px; tile `rectangleRounded` curve 10; fundo `#EAEDF1` (padrão), `#D4DAE2` (projetado), `#F5EBC4` (carteira/destaque); condicional `#FF0000` quando `< 0`; sombra on.

### Combo coluna+linha (`lineStackedColumnComboChart`)
- Coluna/volume: `ColorId 0` (marca). Linha de preço médio: `ColorId 3`, com marcador ligado. Linha de preço de referência: estilo **`dashed`**, cor da marca escurecida (`Percent:-0.3`).
- Data labels ligados: label de volume com fundo da marca `transparency 50` e texto branco, `fontSize 8`, `labelPrecision 0`.
- Legenda `showTitle:false`; título Segoe UI bold 12 `#1B2230`, subtítulo `#6B7280` 8px.
- Painel Widescreen: coluna com cor condicional por medida (`#1B5E20` verde / `#B71C1C` vermelho = semáforo de atingimento, **nunca** a marca); linha de meta `ColorId 2` com marcador.

### Barras (`barChart` / `clusteredBarChart`)
- Cor = `ColorId 0`. `valueAxis` oculto; data labels OutsideEnd, precision 0. Ordenar por valor desc.

### Tabela (`tableEx` / `pivotTable`)
- `tableEx` (Painel Retrato, "Pedidos recentes"): header Segoe UI 12 bold `#1B2230`; borda `#E3E6EB`; **cor condicional de fonte** por medida-cor `.Margem vs Meta Cor` → verde `#2E6F3A` / vermelho `#9F3D27`.
- `pivotTable` (Painel Widescreen): estilo todo no tema. Header de coluna Semibold 10 `#6B7280` com fundo `#FAFBFC`; valores 11 `#4B5563`; **total geral em texto branco sobre `#2F6F8F`**; grid vertical `#E3E6EB` / horizontal `#F1F3F6`; zebra `tableEx` `#FFFFFF`/`#F9FAFC`.

## 7. Componentes HTML/DAX (a alma do Painel Retrato)
Medidas em `...SemanticModel/definition/tables/Medidas.tmdl`, renderizadas pelo visual **HTML Content**. Sobre a autoria dessas medidas (VAR `_` para fragmentos de HTML, `CONCATENATEX` com ordenação, cultura `en-US` para coordenada SVG), ver [PADRAO_DAX](PADRAO_DAX.md) §7.

**Reset comum** de todo container HTML: `font-family:Segoe UI,Tahoma,sans-serif; box-sizing:border-box; background:#FFFFFF; overflow:hidden` + texto base `color:#1B2230`. Estado vazio: `<div style='padding:16px;color:#9AA1A9;font-size:12px'>Selecione um cliente.</div>`.

### Header da entidade: `Cabecalho Cliente (HTML)`
Cartão `border:1px solid #E3E6EB; border-radius:14px; padding:12px 16px`.
- Badge de ranking: `width:44px;height:44px;border-radius:10px;background:#2F6F8F;color:#FFFFFF;font-size:15px;font-weight:700` exibindo `#N`.
- Nome: `font-size:22px;font-weight:700;line-height:1.1` (ellipsis).
- Metadados: `font-size:11px;color:#9AA1A9`, no formato "N produtos · N regiões · início-fim · N pedidos".
- KPIs de header (Ranking Geral / Share): rótulo `9px;letter-spacing:.5px;color:#9AA1A9`, valor `15px;font-weight:700`, complemento `/ total` em `11px;color:#9AA1A9;font-weight:400`.
- Chips de REGIÃO: texto simples `11px;#1B2230`. Chips de CATEGORIA: pílula `border:1px solid #E3E6EB;padding:2px 9px;border-radius:10px;font-size:10px;color:#6B7280`. Rótulo "REGIÃO:"/"CATEGORIA:" em `#9AA1A9;9px;letter-spacing:.5px`.

### Painel INSIGHTS: `Insights Cliente (HTML)`
`padding:10px 16px`. Título "INSIGHTS" `13px;font-weight:700;letter-spacing:.5px` + ícone "i". Blocos separados por `border-top:1px solid #F1F3F6;padding-top:6px;margin-top:6px`. Tokens: label `8.5px;letter-spacing:.5px;color:#9AA1A9`; valor `18px;#1B2230;line-height:1.1`; sub `8.5px;#9AA1A9`.
- Mix por categoria: barra `height:7px;background:#E3E6EB;border-radius:3px`, fill `#2F6F8F` na principal e `#C9D3DA` nas demais.

### Tabela de produtos: `Produtos Vendidos (HTML)`
`padding:10px 14px`. `<th>` `color:#9AA1A9;font-size:8.5px;letter-spacing:.5px;font-weight:600`; linha `border-top:1px solid #F1F3F6`; nome do produto `12px;font-weight:700;#1B2230`. Coluna "Participação" = mini-barra `flex;height:5px` (trilho `#E3E6EB`, fill `#2F6F8F`) + `%` em `10px;#6B7280`.

### Heatmap Cliente x Produto: `Heatmap Cliente Produto (HTML)`
Rampa da cor de marca por intensidade (SWITCH sobre ratio): `#DCE8EE → #B3CCD8 → #7FA7BC → #4E86A3 → #2F6F8F`; texto `#1F3A4A` (claro) ou `#FFFFFF` (ratio ≥ 0.55). Célula `min-width:64px;padding:2px 8px;border-radius:7px;font-size:10.5px;font-weight:600`. Legenda `background:linear-gradient(90deg,#DCE8EE,#2F6F8F)`.

### Sparkline: `Analise Mensal Produto (HTML)` (mistura div + SVG)
Barras em `div` (`background:#2F6F8F;border-radius:3px 3px 0 0`) + SVG de linha `<polyline fill='none' stroke='#B7791F' stroke-width='2' vector-effect='non-scaling-stroke'/>` e pontos `width:7px;height:7px;border-radius:50%;background:#B7791F;border:1.5px solid #FFFFFF`. A linha usa o destaque secundário do tema.

### Rankings (`Ranking Clientes`, `Ranking Produtos por Mes`, `Top Clientes`)
Gramática única: título CAIXA ALTA `13px;font-weight:700`; posição `#9AA1A9;12px` no formato "00"; nome `font-weight:600;#1B2230`; barra de volume relativo (trilho `#E3E6EB`, fill `#2F6F8F`); valores à direita.

### Card HTML do Painel Widescreen: `Cards Prazo Entrega (HTML)`
Único HTML do painel widescreen: 3 mini-cards empilhados. Wrapper `display:flex;flex-direction:column;gap:8px`; card `background:#F7F9FA;border-radius:6px;padding:12px;text-align:center`; rótulo `17px;#4B5563`; número `38px;font-weight:600;#1B2230`; sub `14px;#6B7280`.

## 8. Tokens semânticos (reaproveitáveis)
| Sinal | Texto | Fundo |
|---|---|---|
| Positivo / YoY alta | `#2E6F3A` | `#E8F1E5` |
| Negativo / YoY baixa | `#9F3D27` | `#F4E0DA` |
| Semáforo de atingimento OK | `#1B5E20` | sem fundo |
| Semáforo de atingimento abaixo | `#B71C1C` | sem fundo |
| Condicional negativo (KPI) | `#FF0000` | sem fundo |

Setas: `▴` alta / `▾` baixa. Badge YoY: `padding:1px 6px;border-radius:8px;font-size:9.5px;font-weight:600`. Ícone de ajuda "i": círculo `12px;border:1px solid #C9D3DA;border-radius:50%;color:#9AA1A9;font-size:9px;font-weight:700`.

## 9. Layout / canvas / grid
| | Painel Retrato | Painel Widescreen |
|---|---|---|
| Canvas | 1280 × 1600 (retrato) | 2900 × 1300 (widescreen) |
| displayOption | ActualSize | FitToPage |
| Páginas | 2 (Geral, Produtos) | 1 (Geral) |
| Margem lateral | 20px | header 120px no topo + coluna de filtros x=20 w=300 |
| Faixa full-width | 1240px | conteúdo a partir de x=340 |

- **Agrupamento**: uso intenso de `parentGroupName`. Cada gráfico é colado ao seu `actionButton` de info e slicer num grupo. No Painel Widescreen, a faixa de KPIs e o painel de filtros são grupos (`groupMode: ScaleMode`, coordenada do filho relativa ao grupo).
- **Delimitação de seção**: imagem PNG de fundo + borda de cartão do tema. **Não há shapes de moldura**; os únicos `shape` são linhas divisórias finas entre slicers do painel lateral (Painel Widescreen).
- Slicers e cards com `visualHeader`/título ocultos; gráficos com título+subtítulo visíveis.

## 10. Regras para reproduzir sem confundir identidades
1. Comece pela imagem de fundo (arte) + registre o PNG; ligue `background image scaling:Fit`, transparência 0.
2. Duplique o tema JSON de um painel pronto e troque só os slots de marca (§2). Mantenha Segoe UI e a estrutura de `visualStyles`.
3. Gráfico de eixo e KPI = nativo, cor por `ColorId` (nunca hex cru na série). Cartão de narrativa = HTML por medida.
4. Reuse os tokens de forma (§4) e semânticos (§8): são a "cola" que faz telas diferentes parecerem a mesma casa.
5. Acento é marca, verde é status. Se a marca da empresa for verde, o status positivo muda de família (ex.: azul ou cinza escuro), e os papéis nunca se trocam no mesmo painel.

## 11. Arquivos-fonte (onde achar o molde num `.pbip`)
- **Tema**: `<Painel>.Report/StaticResources/RegisteredResources/<tema>.json`.
- **Medidas HTML**: `<Painel>.SemanticModel/definition/tables/Medidas.tmdl`.
- **Páginas e visuais**: `<Painel>.Report/definition/pages/`.
- Registre aqui os painéis-vitrine do seu repositório de dashboards, um por arquétipo, para servir de molde à `montar-visuais`.
