# demandas/

O trabalho. Uma pasta por demanda, agrupada por gaveta de tipo.

## As gavetas

O `<TIPO>` sai do prefixo do código, e prefixo novo cria a gaveta no mesmo padrão
`PREFIXO_descricao/`.

| Gaveta | O que guarda |
|---|---|
| `TSK_tasks-sprint/` | task de sprint ou chamado comum |
| `INC_incidentes/` | quebra ou instabilidade não planejada |
| `BI_projetos/` | épico ou projeto de BI |
| `APP_aplicacao/` | frente de aplicação |

## Como uma demanda se chama

`DEM_<COD>_<slug>/`, por exemplo `DEM_TSK-1042_filtro-regiao-painel-vendas`.

Épico tem filhas numeradas dentro da própria pasta (`DEM_BI-005/DEM_BI-005.01/`). **Quem
fecha é a filha**; o pai guarda o plano e o consolidado, e por isso não conta como demanda
aberta em lugar nenhum.

## O que diz que está aberta

Ter `solicitacao.md` e **não** ter `fechamento.md` nem `documentacao.md`. É essa regra que
alimenta o contador da tela de início, o painel e o contexto que abre a sessão, então mexer
nela muda os três.

## Os trilhos

O peso do registro acompanha o tamanho do trabalho, e quem escolhe é a triagem na abertura.

**Direto**, para o que já chega resolvido ou o ajuste trivial: `solicitacao.md` → `fechamento.md`.
**Curto**, o padrão: `solicitacao.md` → `contexto.md` → `fechamento.md`.
**Longo**, para épico, greenfield, multi-frente e homologação: acrescenta `plano.md`,
`entrega.md`, `documentacao.md` e `valor.md`.
**Incidente**, com start próprio: `solicitacao.md` → `contexto.md` (causa raiz) →
`fechamento.md`, e só fecha quando estabilizado.

A régua completa está em [[CLAUDE]]; o formato de cada documento, em `conhecimento/modelos/`; uma
demanda completa de exemplo, em `exemplos/`.

## Material bruto não entra aqui

Especificação em docx, planilha do solicitante, print e PDF ficam em `local/<demanda>/`, **fora
do git**. O que importa deles vive destilado na `solicitacao.md`, e o registro cita só o caminho.
