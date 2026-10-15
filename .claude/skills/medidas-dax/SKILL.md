---
name: medidas-dax
description: Cria, corrige e organiza/documenta medidas DAX de um dashboard Power BI, seguindo o padrão da casa (autoria, BLANK/zero, derivação por base, time intelligence, internas, format, display folders, descrição e sinônimos). Use em demandas que tocam medidas/cálculo/KPI/forecast. Frente PBI. NÃO use para demandas que só mexem em M/origem ou só em visual.
---

# Skill: medidas-dax (PBI — autoria + organização de medidas)

Opera plano-primeiro: PROPÕE o que será criado/alterado/organizado, você aprova, e SÓ ENTÃO escreve.
Referência canônica do padrão: `conhecimento/padroes/PADRAO_DAX.md` — CONSULTE antes de escrever. Esta skill resume; o arquivo manda.

## 0. Gate de relevância (ANTES de tudo)
Olhe tipo/frente/escopo da demanda (contexto.md, plano.md). A skill AGE quando:
- cria medida nova, corrige medida existente, ou reorganiza/redocumenta medidas (descrição, folder, sinônimos, sufixo de unidade, ocultar internas);
- o arquivo tocado é `*/Medidas*.tmdl` ou `cultures/*.tmdl`, ou a tarefa fala em medida/cálculo/KPI/%/forecast/aderência.
A skill PASSA A VEZ quando:
- é exclusivamente M/origem/tipagem de coluna → `modelagem-dados`;
- é exclusivamente visual.json/layout → `montar-visuais`.
TRABALHO CONJUNTO (chame a outra skill junto) quando a medida depende de coluna/relação nova (ex.: precisa de `IsPast`, `Mes.Semana`, ou de relação inativa para role-playing) → aciona `modelagem-dados`.
Declare qual caso identificou antes de seguir.

## 1. Autoria — regras (resumo; detalhe no PADRAO_DAX.md)
- VAR/RETURN só com reuso, ramificação ou captura de contexto. One-liner trivial em uma linha.
- VAR naming: `v_snake_case` (lógica) · `_` (string/HTML). Sem PascalCase.
- `DIVIDE()` para medida no denominador; `/` só para constante.
- BLANK/zero (regra de ouro): default BLANK · `DIVIDE(,,0)` zera % · `+0` materializa · `COALESCE` protege iterador · `BLANK()` esconde.
- Formatação DAX Formatter (funções MAIÚSCULAS, args de CALCULATE em linhas próprias, banners em medidas grandes).

## 2. Composição (coração)
- Núcleo de medidas-base; derive via `CALCULATE([base], <modificador>)`. NUNCA copie a base.
- Variantes (PY/YTD/Entrega/FC/Var.) são wrappers — ver famílias no PADRAO_DAX.md §3.
- ANTI-PADRÃO proibido: cópia literal da base (`.legado_*_copia`).

## 3. Time intelligence
- Dim_Calendario marcada como tabela de data. PY = `DATEADD(-1,YEAR)`; YTD = `DATESYTD`; forecast pela coluna `IsPast` (NÃO FORMAT(TODAY())).

## 4. Internas (`.`) e UI
- Cálculo pesado/reusado e flags de CF/UI vão para `.internas` hidden; a visível só orquestra. Subtipos `.ux/.valida/.aut/.legado/.total/.resumo`.
- Texto: `SELECTEDVALUE(...,"fallback")`, `CONCATENATEX(... , ordenacao)`, fallback de seleção múltipla; cultura pt-BR/en-US conforme §7 do PADRAO.

## 5. Format + unidade
- Format string por grandeza (PADRAO §8). % padrão = 1 casa (`0.0%`); 2 casas só caso específico.
- Unidade sinalizada em 3 lugares: sufixo no nome `( )` + folder + format/descrição.

## 6. Documentação e organização (Lado A)
- Descrição em 3 partes: `[def + cálculo + formato] · Use para X · Não use quando Y`. É o mesmo contrato que a camada de legibilidade pra IA cobra; a maturação completa do modelo pra IA (bloco de instruções no `model.tmdl`, ocultar coluna técnica, nomes de negócio) é a skill `legibilidade-ia` (ver `conhecimento/padroes/PADRAO_LEGIBILIDADE_IA.md`).
- Display folders NUMERADOS (`00 Internas`, `01 ...`), subpastas com `\`, dot-folders fixos `.Internas` e `.Texto`. Nomes de domínio adaptados ao dashboard.
- Sinônimos/cultura (`cultures/pt-BR.tmdl`): só em flagship, fase final — não obrigatório.
- Nomes ASCII (sem acento) nos objetos.

## Saída e fluxo (plano-primeiro)
1. Confirme o gate (0) e o caso (criar / corrigir / organizar).
2. PROPONHA o `plano.md`: medidas a criar/alterar (com a base de que derivam), modificadores CALCULATE, format string, folder de destino, descrição 3-partes, e o que é interna vs visível. **PARE para aprovação.**
3. Após aprovado, escreva o DAX seguindo o PADRAO_DAX.md; registre em `entrega.md` o que foi feito + evidência (ex.: medida testada num recorte concreto).
4. Antes de fechar, cheque anti-padrões (cópia de base, FORMAT(TODAY()) em forecast, medida sem descrição no estágio de maturação, folders inconsistentes) e reporte.
5. Guardrail de load (o erro só aparece no Desktop): a MESMA medida não pode ter dois `displayName` diferentes no mesmo visual ("queryRef só pode ter um displayName") — se ela já é o valor do eixo, o hover já a mostra, não repita no bloco de Tooltips. Descrição `///` é padrão e NÃO quebra; comentário `//` em JSON quebra.
