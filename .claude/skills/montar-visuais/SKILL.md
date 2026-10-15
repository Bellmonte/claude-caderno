---
name: montar-visuais
description: Monta e ajusta os visuais de um dashboard Power BI editando o PBIP como código (page.json, visual.json, pages.json) a partir de um print/mockup + spec. Decide nativo vs HTML/SVG, define o layout e a arquitetura de filtro da página. Use em demandas de montagem/ajuste visual. Frente PBI. NÃO use para demandas que só mexem em M/origem.
---

# Skill: montar-visuais (PBI — visuais como código)

Princípio central: NÃO se monta visual arrastando no Desktop. Edita-se o PBIP como código (texto/JSON/TMDL), versionável e replicável.
Opera plano-primeiro: PROPÕE o layout/arquitetura, você aprova, e SÓ ENTÃO escreve os arquivos.

## 0. Gate de relevância (ANTES de tudo)
AGE quando a demanda toca `page.json`, `visual.json`, `pages.json`, layout, posicionamento, formatação visual, ou montagem de página/dashboard.
PASSA A VEZ quando é exclusivamente M/origem → `modelagem-dados`.
TRABALHO CONJUNTO:
- Visual HTML/SVG custom → precisa de uma medida-HTML: esta skill é dona do layout e ESPECIFICA a medida; a autoria DAX segue `conhecimento/padroes/PADRAO_DAX.md` (aciona `medidas-dax`). Ver seção 4.
- Medida analítica nova/alterada que o visual consome → normalmente já foi feita na etapa `medidas-dax` anterior; se faltar, aciona `medidas-dax`.
Declare o caso identificado antes de seguir.

## 1. Insumos
- **Print/mockup** = referência de PIXEL (paleta, espaçamento, tipografia, layout). Não exige Figma.
- **Spec** = referência de CÁLCULO (KPIs, fórmulas dos campos).
O print vira o alvo visual; a spec vira o alvo de dados.

## 2. Método (4 passos — o coração)
1. **Molde primeiro.** Antes de criar, leia uma página/visual PRONTA do próprio projeto e use como molde (formato do page.json, como um visual HTML se amarra a uma medida, estrutura de combo/slicer). Copiar o que já funciona elimina ~80% do risco.
2. **Quebrar a spec em componentes** e, para cada um, decidir nativo vs HTML/SVG (seção 3).
3. **Reaproveitar medidas existentes**, criar só as novas. Medidas analíticas geralmente já vieram da etapa `medidas-dax`; a exceção são as medidas-HTML (seção 4), que só nascem aqui.
4. **Montar**: `page.json` (dimensão, fundo, interações de filtro) + um `visual.json` por visual + registrar no `pages.json`.

## 3. Régua: nativo vs HTML/SVG
Use NATIVO quando:
- o PBI já faz bem (barras+linha, slicer), OU
- precisa de interação real (clicar para filtrar a página).
Use HTML/SVG (medida que devolve string, renderizada pelo visual custom "HTML Content") quando:
- o layout do print não existe como visual nativo, OU
- precisa de controle de pixel: badges, mini-barras, heatmap, cards ricos, tabela com cor condicional fina.

## 3b. Consulta nas decisões (gate granular — específico desta skill)
No visual, boa parte é decisão de critério/gosto, e não há preview ao vivo (a conferência só vem no Desktop). Por isso NÃO decida sozinho e siga: sempre que houver mais de um caminho razoável, PARE e pergunte antes de escrever. Casos típicos de parada:
- nativo vs HTML/SVG num componente em que os dois cabem;
- interpretação de ambiguidade do print (espaçamento, hierarquia, qual KPI é o principal);
- escolha de molde quando há mais de um candidato no projeto;
- qualquer desvio do print que você for tentado a "melhorar" por conta própria.
Objetivo: reduzir retorno negativo na validação local. Uma pergunta rápida agora custa menos que refazer no Desktop. (Este gate granular é próprio de montar-visuais; nas skills de DAX/M, o plano-primeiro basta porque a decisão é mais verificável.)

## 4. Medidas-HTML (a fronteira com medidas-dax)
- O "visual HTML" não tem inteligência: renderiza a string que uma medida DAX devolve. Programa-se a tela em CSS/SVG dentro do DAX.
- Esta skill é DONA do layout e ESPECIFICA a medida-HTML (o que desenhar, com quais dados, em que paleta). A escrita da medida segue o PADRAO_DAX.md (CONCATENATEX com ordenação, cultura "en-US" para coordenadas SVG e "pt-BR" para texto exibido, fragmentos `_` para string/HTML).
- **Restrição que dita a arquitetura:** HTML Content é SÓ LEITURA — não captura clique. Logo, a seleção fica SEMPRE num slicer nativo, e os visuais HTML só reagem ao filtro. Desenhe a página a partir disso.

## 5. Puxar a identidade do print
- Extraia do print a paleta (ex.: acento #2F6F8F, destaque #B7791F), o ritmo de espaçamento e os tamanhos de fonte; replique no CSS-dentro-do-DAX.
- "Deixar igual a outro visual" = copiar cores/estilo/marcadores, porque ambos são descritos em texto.

## 6. Verificação (sem preview ao vivo)
- Valide o JSON/TMDL (parseável, estrutura coerente com o molde).
- Siga padrões já comprovados do projeto.
- A conferência final é VOCÊ abrindo no PBI Desktop — encaixa no gate de validação humana da esteira. Gotchas de modelagem (ex.: dependência circular de sortByColumn) aparecem aqui, na ida e volta.

### 6.1 Guardrail de sintaxe do PBIP (DURO — erro recorrente que quebra o load)
Erro de schema só aparece ao abrir o Desktop (sem preview), então cada deslize é retrabalho. Antes de fechar:
- **ZERO comentário em JSON.** `visual.json`/`page.json`/`pages.json` e qualquer `*.json` NÃO aceitam `//` nem `/* */` — quebra o parse e o relatório não abre. Nunca escreva comentário em JSON.
- **Parse não basta — valide o SCHEMA.** JSON válido ainda derruba o load se inventar propriedade que o objeto não aceita. Nunca chute chave: copie de um molde REAL do próprio repo. Casos que já quebraram: `show` dentro de `visualHeaderTooltip` (não aceita `show`); mesma medida com dois `displayName` diferentes no mesmo visual ("queryRef só pode ter um displayName") — se a medida já é o valor do eixo, o hover já a mostra, não repita no bloco de Tooltips.
- **Rode `ConvertFrom-Json` em todo `*.json` tocado** e confira displayName único por medida antes de declarar pronto.
- **`///` em TMDL são DESCRIÇÕES válidas, não comentário** — são padrão da casa (`medidas-dax` exige descrição na medida) e NÃO quebram o load. Não confundir com o comentário que quebra, e não sair removendo descrição válida achando que é o problema.

## Saída e fluxo (plano-primeiro)
1. Confirme o gate (0) e os insumos (print + spec).
2. PROPONHA o `plano.md`: lista de componentes do print, decisão nativo/HTML por componente, qual molde existente será usado, medidas reaproveitadas vs medidas-HTML a criar, e a arquitetura de filtro (slicer nativo + reações). **PARE para aprovação.**
3. Após aprovado: leia o molde, escreva os `visual.json`/`page.json`, registre no `pages.json`, e (se houver HTML) escreva as medidas-HTML no padrão DAX. Registre em `entrega.md` o que foi feito.
4. Antes de fechar: valide os JSON/TMDL e liste o que precisa de conferência no Desktop (não afirme "funcionando" sem o aval do Desktop).
