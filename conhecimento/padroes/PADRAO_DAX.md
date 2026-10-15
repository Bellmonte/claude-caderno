# Padrão DAX — referência canônica (Power BI)

> Destilado de três dashboards reais em estágios diferentes de maturidade: um cru, um com documentação
> leve e um flagship. Os três são estágios do MESMO padrão; a norma é o estágio flagship.
> A skill medidas-dax aponta para cá. Decisões já fechadas estão marcadas com ✓.

## 1. Escrita da medida
- VAR/RETURN quando há (a) reuso de subexpressão, (b) ramificação IF/SWITCH, ou (c) captura de contexto antes de mudá-lo. One-liner trivial fica em uma linha.
- ✓ Nomenclatura de VAR: `v_snake_case` para lógica de negócio; `_` (underscore) para fragmentos de string/HTML. PascalCase puro está APOSENTADO.
- Divisão: `DIVIDE()` sempre que o denominador é medida/coluna; `/` só para constante literal (ex.: /1000, /100).
- Formatação: regras numeradas, exemplo de antes e depois e como é garantida em [[PADRAO_FORMATACAO]] (estilo DAX Formatter, espaço antes do parêntese, CALCULATE sempre quebrado).

## 2. BLANK / zero (regra de ouro — 4 casos)
- Default: deixe **BLANK** (visual esconde a linha) — é o desejado na maioria.
- `DIVIDE(num, den, 0)`: zera o resultado quando um % de KPI deve ler 0% em vez de vazio.
- `+ 0`: materializa o zero (continuidade de eixo, texto comparativo, conditional formatting que falha com BLANK).
- `COALESCE(..., 0)`: protege iterador (dentro de SUMX) onde BLANK quebraria a soma.
- `BLANK()` explícito: suprime valor sem sentido (ex.: % quando saldo <= 0).

## 3. Composição e reuso (coração do padrão)
- Núcleo pequeno de medidas-base; dezenas de derivadas por cima.
- NUNCA reescrever a lógica base: derive sempre via `CALCULATE([base], <modificador>)`.
- Variantes role-playing / segmentação / forecast são WRAPPERS, não cópias.
- Famílias de derivação típicas: PY = `DATEADD(-1,YEAR)`; YTD = `DATESYTD`; (Entrega) = `USERELATIONSHIP`; FC = base_realizada(IsPast=TRUE)+base_planejada(IsPast=FALSE); (Var.) = `IF(SELECTEDVALUE(Out_Segmentacao)=1, fixo, FC)`.
- ANTI-PADRÃO: cópia literal da base (`.legado_*_copia`).

## 4. Time intelligence
- 100% dependente da Dim_Calendario marcada como tabela de data.
- PY/LY: `DATEADD(Dim_Calendario[Data], -1, YEAR)` — não usar SAMEPERIODLASTYEAR.
- YTD: `CALCULATE([base], DATESYTD(Dim_Calendario[Data]))` (padrão preferido sobre TOTALYTD).
- WTD: construído à mão (coluna Mes.Semana + FILTER).
- Forecast: usar coluna booleana `IsPast` do calendário — NÃO `FORMAT(TODAY(),"yyyymm")` em contexto de linha (legado a migrar).

## 5. CALCULATE — modificadores por convenção
- `REMOVEFILTERS(dim)`: denominador de share/total; ignorar Ano por design (acumulado histórico).
- `ALLEXCEPT(Dim_Calendario,[Ano])`: participação mês-sobre-ano.
- `ALLSELECTED(dim[col])`: % dentro da seleção do visual.
- `KEEPFILTERS(...)`: interseção em vez de sobrescrita.
- `USERELATIONSHIP(...)`: role-playing (vira display folder "(Entrega)"/"(Faturamento)").
- `TREATAS(SUMMARIZE(...), fato[col])`: relação virtual / alinhamento de grão sem relação física.

## 6. Medidas internas (prefixo `.` = oculta)
Subtipos por sub-prefixo; a medida VISÍVEL só orquestra, o cálculo pesado/reusado vai para interna:
- `.base/denominador` (ex.: `.Volume Total (t)`)
- `.ux_*` texto/rótulo de UI
- `.valida_*` flag 1/2 para formatação condicional
- `.aut_*` variantes de escopo de autorização
- `.legado_*` deprecado, oculto para referência
- `.total_*`/`.resumo`/`.rodape_*` intermediários e textos de cabeçalho/rodapé
Regra: intermediário reusado por >1 medida visível, ou que serve só a CF/UI, vira `.interna` hidden.

## 7. Texto / UI
- Seleção única: `SELECTEDVALUE(dim[col], "fallback")` ou guarda `HASONEVALUE`.
- Listas/HTML: `CONCATENATEX(tabela, "<linha>", "", coluna_ordenacao, ASC/DESC)` — sempre com ordenação explícita.
- Seleção múltipla/vazio: texto-fallback num IF no RETURN ("Selecione um cliente.").
- Cultura no FORMAT: `"pt-BR"` para milhar/percentual exibido; `"en-US"` para coordenadas SVG (decimal com ponto).

## 8. Format string por grandeza
| Grandeza | formatString |
|---|---|
| Volume/qtd inteiro (t, un) | `#,0` |
| Volume com decimal / (kt) | `#,0.00` / `#,0.0` |
| ✓ Percentual (padrão) | `0.0%;-0.0%;0.0%` (1 casa) |
| Percentual (caso específico) | 2 casas só quando justificado |
| USD | `\$#,0;(\$#,0);\$#,0` + PBI_FormatHint currencyCulture |
| Câmbio R$/USD | `\$#,0.0000;...` |
| Margem (ratio cru) | `0.0000` (entra em cálculo de preço) |
| Data | `dd/mm/yyyy` |

## 9. Unidade coexistente — sinalizada em 3 lugares (não confiar em um só)
1. Sufixo no NOME entre parênteses: `(t)`, `(kt)`, `(USD/t)`, `(USD)`, `(%)`, `(R$)`. Barreira principal.
2. Display folder por domínio.
3. format string + descrição (que termina com "; formato …").
Outros sufixos: `(Entrega)`, `(Var.)`, `(FC)`, `(texto)`, `(bruto)`.

## 10. Descrição (3 partes)
`[definição + como é calculado + formato] · Use para X · Não use quando Y`.
Ex.: "Percentual de margem = Margem Líquida / Receita Líquida, só p/ pedidos com lista de preço (%). Use para rentabilidade; não use em pedidos sem lista, retorna em branco."

## 11. Display folders
- ✓ Padrão NUMERADO: `00 Internas`, `01 Volume`, `02 ...` — força a ordem.
- Subpastas com `\` (ex.: `Margem & Preco\Dolar & Cambio`, `.Internas\Legado`).
- ✓ Dot-folders fixos, reaplicados em todo BI: `.Internas` e `.Texto`.
- Nomes de domínio adaptados por dashboard (compras tem "Frete e Precos"; vendas tem "Margem & Preco").
- Uma medida pertence a só uma pasta. Não criar pasta vazia.

## 12. Sinônimos / cultura (fase final, só flagship)
- `cultures/pt-BR.tmdl`: `description:` (lista Q&A "termo1; termo2; …") + `caption:` (nome amigável).
- Não obrigatório em todo BI — é polimento de dashboard-vitrine.

## 13. Nomenclatura ASCII
Sem acento/cedilha/til em NOMES de objeto (Negociacao, Preco). Descrições/textos de UI podem ter acento.
