### 📌 [TSK-1042] — MELHORIA: FILTRO DE REGIÃO NO PAINEL DE VENDAS | Baixa — Baixo — No prazo

**ID:** TSK-1042 [CH-2210] | **Solicitante:** Coordenação comercial | **Marcadores:** PBI · COMERCIAL
**Objeto afetado:** Painel de Vendas | **Ambiente:** produção

**Sprint:** SPRINT_1 - SET/26 | **Criação:** 08-09-2026 10:12 | **No caderno desde:** 09-09-2026
**Início previsto:** 09-09-2026 | **Início real:** 09-09-2026 | **Prazo:** 15-09-2026 | **Entrega:** 11-09-2026
**SLA:** no prazo · 2 dias úteis de folga | **Esforço:** 2 dias úteis
**Complexidade:** Baixa | **Risco:** Baixo · alteração só de tela, sem mudança na base

**Problema:** o painel só permitia filtrar por vendedor, e cada gerente regional precisava ver só a própria região na reunião mensal.
**Impacto:** os gerentes montavam a visão da região à mão, somando vendedor por vendedor.
**Causa:** o painel nunca teve filtro de região, embora a informação já existisse na base.

**Solução (o que foi feito):**
* Filtro de região no topo das quatro páginas do painel.
* A região escolhida numa página continua valendo ao navegar para as outras.

**Como foi feito:**
* Aproveitada a informação de região que a base já trazia, sem mexer na carga.
* Filtro replicado e sincronizado entre as páginas.

**Validação:**
* Total de agosto por região conferido contra o sistema de origem → as cinco regiões batem.
* Página de metas testada com o filtro → responde corretamente.
* Coordenação comercial validou em 11-09-2026 → aprovado.

**Status:** Entregue
**Obs.:** o filtro de vendedor passa a mostrar só os vendedores da região escolhida.

**Rastreio:** detalhe técnico no `contexto.md` desta demanda.

---
ℹ️ **Como ler este cabeçalho**
**Complexidade** = ambientes envolvidos + porte da alteração · Baixa · Média · Alta
**Risco** = Complexidade × tempo até o prazo × validação
**SLA** = entrega contra o prazo da sprint, em dias úteis.

---
<!-- INTERNO: não compartilhar. Só no trilho curto; no longo isto vira valor.md. -->
🔒 **Valor (interno)**
**Dor endereçada:** montagem manual da visão por região | **Beneficiário:** gerentes regionais
**Dimensão:** tempo · decisão
**Origem da prioridade:** rotina
**Antes:** cerca de 30 minutos por gerente antes de cada reunião mensal (relato do solicitante, sem medição) → **Depois:** visão pronta no painel (proxy)
**Confiança:** média | **Contra-argumento:** o ganho de tempo é relatado, não medido
**Feedback:** coordenação comercial elogiou na validação, 11-09-2026 | **Visibilidade:** área comercial, reunião mensal
**Competências:** modelagem de filtro em dimensão compartilhada, validação contra a origem
