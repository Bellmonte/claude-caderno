# TSK-1042 | Filtro de região no Painel de Vendas

## Pedido (como chegou)
Filtrar o painel por região, valendo para todas as páginas, antes da reunião mensal do dia 15.

## Premissas a verificar
- [x] **A região existe na base.** Conferido: `Dim_Vendedor[Regiao]` já vem da origem, populada
  em 100% dos vendedores ativos. Não precisa mexer na carga.
- [x] **Filtrar por vendedor e por região não briga.** Conferido: os dois campos estão na mesma
  dimensão, então o filtro de região restringe a lista de vendedores sozinho.
- [ ] **"Todas as páginas" inclui a página de metas.** Em aberto: a página de metas lê de
  `Fact_Metas`, que se liga a vendedor pela mesma dimensão. Deve funcionar, mas confirmar na
  validação.

## Critérios de aceite
- [x] Filtro de região visível no topo das quatro páginas.
- [x] Seleção feita numa página vale nas outras (slicer sincronizado).
- [x] Totais por região batem com a consulta à origem para agosto.
- [x] Página de metas responde ao filtro.

## Solicitante / área
Coordenação comercial.

## Análise (GATE 1)

Viável sem mudança estrutural. O campo já existe na dimensão de vendedor, e o pedido se resolve
na camada de visual: um slicer de região em cada página, sincronizado pelo mesmo grupo de
sincronização. O sinal 7 acendeu porque o painel voltou da validação em julho por divergência de
total; por isso a validação desta vez confere o total por região contra a origem, e não só o
visual.

**Plano**
1. Criar o slicer de região na página Resumo, no padrão visual do painel.
2. Replicar nas outras três páginas com o mesmo `syncGroup`.
3. Conferir total por região contra a origem para agosto.
4. Validar com o solicitante antes do dia 15.

**GATE 1:** aprovado pelo usuário em 09-09-2026.

## Execução
- Slicer criado e replicado nas quatro páginas, grupo `sync_regiao`.
- Conferência de agosto: as cinco regiões batem com a origem até o centavo.
- Página de metas responde ao filtro; premissa 3 confirmada.
