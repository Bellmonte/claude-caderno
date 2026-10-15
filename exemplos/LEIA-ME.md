# exemplos/

Uma demanda fictícia completa, no trilho CURTO, para ver o sistema funcionando antes de usar. Os
nomes, datas e números são inventados.

| Arquivo | Quem escreve | O que mostra |
|---|---|---|
| [solicitacao.md](DEM_TSK-1042_filtro-regiao-painel-vendas/solicitacao.md) | `abrir-demanda` | o pedido como chegou, o SLA e a triagem do trilho com o sinal que acendeu |
| [contexto.md](DEM_TSK-1042_filtro-regiao-painel-vendas/contexto.md) | `analisar-especificacao` | o pedido confrontado com a realidade técnica, o plano e o GATE 1 |
| [fechamento.md](DEM_TSK-1042_filtro-regiao-painel-vendas/fechamento.md) | `fechar-demanda` | o documento para o solicitante, sem nome técnico, e o bloco interno de valor |

Na vida real a pasta fica em `demandas/TSK_tasks-sprint/`. Aqui ela fica fora de `demandas/`
para não aparecer como demanda aberta no painel. Depois do fechamento, o `fechar-demanda` também
acrescentaria uma linha em `gerencial/objetos/painel-de-vendas.md`, e o `capturar-conhecimento`
levaria para o baú o aprendizado sobre filtro em dimensão compartilhada.
