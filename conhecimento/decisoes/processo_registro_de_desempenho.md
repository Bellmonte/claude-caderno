# Decisão: registro de desempenho derivado das demandas

**Contexto:** um vídeo curto sobre carreira defendia manter uma tabela contínua do
próprio trabalho, com dez colunas (entrega, objetivo, status, prioridade, período, impacto,
evidência, feedback, competências e visibilidade), e a partir dela um painel anual. O argumento é
que fazer um bom trabalho e comunicar esse trabalho são coisas diferentes: o gestor não viu os
problemas que apareceram no caminho, e quem depende da memória chega na conversa de aumento, de
promoção ou no 1:1 sem ter o que mostrar.

## Decisão

O caderno já guardava sete das dez colunas, espalhadas pelo fechamento, pelo bloco de valor e pelo
cabeçalho de SLA de cada demanda. Manter uma planilha à parte repetiria o erro do antigo
`razao-valor.csv`, que morreu por ser alimentado em paralelo à fonte. Por isso o registro é
**derivado**: `.claude/scripts/registro_desempenho.py` varre as demandas e regrava
`gerencial/desempenho/registro-<ano>.md` e `painel-<ano>.html`. Corrigir uma linha é corrigir a
demanda e rodar de novo.

As três colunas que faltavam passaram a ser campos do bloco de valor, nos modelos de fechamento
(chamado e APP) e no `valor.md`: **Feedback**, **Visibilidade** e **Competências**. A
`capturar-valor` preenche, e a `fechar-demanda` roda o gerador no fim.

## Como cada coluna é lida

| Coluna | De onde sai |
|---|---|
| Entrega | título do fechamento ou da documentação |
| Objetivo | dor endereçada do valor, senão o problema do fechamento |
| Status | fechamento existe, `AGUARDANDO.md`, `ARQUIVADO.md` (arquivada fica fora) |
| Prioridade | origem da prioridade (urgência e estratégica são alta, rotina é média, volume é baixa), senão o risco |
| Período | data de entrega, encerramento ou data do fechamento; demanda aberta usa a abertura |
| Impacto | o que mudou (depois), senão o que muda na prática, senão a primeira linha da solução |
| Evidência | medida ou proxy do valor, senão a evidência, senão a primeira validação |
| Feedback | campo declarado; no retroativo, só sinal explícito no texto (aprovação da área, rodada de devolutiva) |
| Competências | campo declarado; no retroativo, as três mais citadas por palavra-chave |
| Visibilidade | campo declarado; no retroativo, solicitante externo ou interno mais citação no reporte semanal, na daily e em ata |

Tudo que vem do retroativo sai marcado **(inferido)**, e o que não dá para ler sai como **não
registrado**. Lacuna fica visível e não é preenchida com texto inventado, mesma régua do rollup
de valor. Aprovação de auditor não conta como feedback, porque é segunda opinião técnica e não
retorno de gente.

## Privacidade

O registro é interno e pessoal, como a camada de valor. Visibilidade é escrita por papel e área,
nunca por nome de pessoa. Para virar material de conversa com o gestor ou de currículo, passa
antes por higienização: sai nome de pessoa, nome de sistema interno e número que só faz sentido
dentro da empresa, e fica o resultado dito em linguagem de negócio.
