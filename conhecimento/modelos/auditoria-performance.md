# Modelo: relatório de auditoria de performance

> Formato do `auditoria-performance.md`, que mora na pasta do épico da auditoria
> (`demandas/BI_projetos/DEM_BI-NNN_performance-<painel>/`). Um arquivo por auditoria: o
> diagnóstico preenche o "antes", a remedição preenche o "depois" no mesmo arquivo.
> Régua em [[PADRAO_PERFORMANCE_PBI]]. Documento técnico, lido pelo usuário. Não sai para o
> solicitante; o que sai é o `documentacao.md` do épico, em linguagem de negócio.
> Só agregados: nenhum texto de consulta, nenhum valor de dado.

---

# Auditoria de performance | {PAINEL}

## Resumo

**Painel:** {nome} | **Cópia medida:** {caminho local do .pbip}
**Linha de base:** {DD-MM-AAAA} | **Remedição:** {DD-MM-AAAA ou pendente}
**Máquina:** {nome} | **Desktop:** {versão} | **Mesma sessão:** {sim/não}

{Uma ou duas frases de conclusão: onde estava o peso, o que foi corrigido e o que mudou de forma
mensurável. No diagnóstico, onde está o peso e qual correção vem primeiro.}

## Tabela de medição

{Saída do `comparar.py`. No diagnóstico, só as colunas do antes.}

| Grandeza | Unidade | Antes (mediana) | Antes (faixa) | Depois (mediana) | Depois (faixa) | Variação | Diferença |
|---|---|---|---|---|---|---|---|
| Tamanho do modelo | MB | | leitura única | | leitura única | | |
| Atualização completa | s | | | | | | |
| Página {nome}, a quente (analisador) | ms | | | | | | |
| Motor do bloco {n}, a frio | ms | | | | | | |
| Motor do bloco {n}, a quente | ms | | | | | | |

> O motor é a consulta DAX repetida por script. A página a quente vem do analisador e inclui o
> desenho dos visuais. As duas não se somam nem se comparam entre si.

## Onde está o peso

**Dez maiores colunas**

| # | Tabela[Coluna] | Total (MB) | Dicionário | % do modelo |
|---|---|---|---|---|

**Páginas e visuais mais lentos**

| Página | Visual | Tipo | Consultas | Frio (mediana) | Quente (mediana) |
|---|---|---|---|---|---|

## Achados priorizados

| # | Causa (catálogo) | Evidência numérica | Impacto | Esforço | Correção recomendada |
|---|---|---|---|---|---|

{Impacto é quanto da medição o achado explica, em número. Esforço em baixo, médio ou alto. A ordem é
impacto sobre esforço.}

## O que foi corrigido

| Filha | Commit | Motivo |
|---|---|---|

## Paridade

| Medida | Corte | Antes | Depois | Resultado |
|---|---|---|---|---|

## Limitações

A medição cobre o modelo numa cópia local do Desktop. Ficam de fora a capacidade do serviço, o
gateway, a concorrência de usuários e a rede até a origem dos dados. {Acrescentar o que for
específico desta auditoria: rodada com frio suspeito, página sem remedição, versão diferente aceita.}

**Rastreio:** medições brutas em `local/performance/{painel}/antes` e `/depois`, fora do git.
