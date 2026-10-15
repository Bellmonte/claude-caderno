---
name: legibilidade-ia
description: Aplica (ou audita) a camada de legibilidade para IA generativa sobre um modelo semântico Power BI já pronto, para que Copilot, Q&A e agentes conversacionais leiam o modelo e escolham os campos certos sem inventar. Bloco de instruções no model.tmdl, nomes de negócio, descrições em contrato, ocultação de coluna técnica, display folders, nomes de tabela legíveis. Frente PBI, etapa de maturação. Use em BI novo ou remodelado que vai alimentar IA. NÃO use para fix trivial, para modelo que nenhuma IA consome, nem para corrigir modelagem/DAX (isso é modelagem-dados / medidas-dax).
---

# Skill: legibilidade-ia (PBI, modelo semântico legível para IA)

Opera plano-primeiro: VARRE o modelo, APONTA as lacunas de legibilidade num plano, você aprova, e SÓ ENTÃO escreve.
Referência canônica: `conhecimento/padroes/PADRAO_LEGIBILIDADE_IA.md`. CONSULTE antes de agir. Esta skill executa; o arquivo manda.

## 0. Gate de relevância (ANTES de tudo)
A skill AGE quando: um `.pbip` / modelo semântico já tem modelagem, medidas e visuais prontos, e o dashboard vai alimentar (ou a casa quer deixar pronto para) Copilot / Q&A / agente conversacional. Etapa de MATURAÇÃO, roda depois do desenvolvimento e da validação, nunca antes.
A skill PASSA A VEZ quando:
- a modelagem está errada/incompleta (grão, relação, tabela faltando) → `modelagem-dados`. Legibilidade em cima de modelo torto só documenta o torto.
- falta medida ou a medida está errada → `medidas-dax`.
- é fix trivial, doc de texto, ou modelo que nenhuma IA vai consumir → não roda.
TRABALHO CONJUNTO: quando a descrição de medida exige mexer no DAX ou a interna precisa ser reorganizada, aciona `medidas-dax` (esta skill cobra que a descrição exista; quem escreve o DAX e a descrição 3-partes é a medidas-dax). Quando falta nome/estrutura de tabela, aciona `modelagem-dados`.
Declare o modo (AUDITAR ou APLICAR) e confirme o gate antes de seguir.

## 1. Modo AUDITAR (diagnóstico read-only)
Roda o checklist do PADRAO (§Checklist) contra o modelo e devolve o placar: quantas das 7 dimensões a camada cobre, e a lista priorizada do que falta. Não escreve nada. É o mesmo checklist que o `auditor-pbi` usa na dimensão de legibilidade; use este modo para o próprio dev rodar antes de chamar o auditor. Saída: tabela dimensão a dimensão (coberto / parcial / ausente) + próximos passos.

## 2. Modo APLICAR (as 7 dimensões, por ordem de impacto)
Ver detalhe e exemplos no PADRAO. Resumo operacional:

1. **Bloco de instruções no `model.tmdl`** (o de maior impacto). Comentário `///` multilinha imediatamente acima de `model Model`, sem linha em branco entre eles, ASCII. Regras numeradas de negócio: domínio+granularidade; conceitos que NÃO se somam; pares de medida com escopo parecido; unidades (não somar moeda/percentual diferente); medidas que dão BLANK sem contexto; sufixos ((Entrega)/(Var.)/FC) e quando usar; regra geral de priorização. Esse bloco exige ENTENDER o domínio do dashboard: levante do modelo real e das medidas, não invente regra genérica.
2. **Nomes de medida visível** em linguagem de negócio. Interna técnica fica com `.` e oculta.
3. **Descrição de medida** no contrato 5-partes (`o que + cálculo + unidade + quando usar + quando NÃO usar`), via `///` acima da declaração. Se falta e exige DAX, delega `medidas-dax`. Não confundir DAX comentado (`//`) com descrição.
4. **Ocultação (`isHidden`)** de toda chave/código de origem/encanamento; tabelas auxiliares ocultas no nível de tabela. Só fica visível o que serve de filtro/eixo/rótulo de negócio.
5. **Descrição em coluna calculada de negócio** (flag/bucket/derivada) com o que representa e o porquê.
6. **displayFolder**: medidas visíveis em pastas de domínio; internas em dot-folder (`.Internas\...`). Ver `medidas-dax` §6.
7. **Nomes de tabela** com prefixo semântico legível (`Fact_`/`Dim_`/`Out_`). Costuma já vir certo de `modelagem-dados`; só confirma.

## 3. Gotchas de TMDL (não quebrar o load)
- Descrição é comentário `///` na linha ACIMA da declaração, nunca `description:` (quebra o parser).
- Ao editar TMDL por script ou à mão, `lineageTag` novo = GUID ALEATÓRIO (uuid), nunca sequencial montado: colide e quebra o `.pbip`. Varrer duplicados.
- Texto de objeto em ASCII (sem acento). Prosa de descrição pode ter acento; nome de objeto não.
- Se o modelo foi autorado com o Power BI Modeling MCP (annotation `MCP-PBIModeling`), preferir editar por ele; senão, editar o `.tmdl` como código com os cuidados acima.

## Saída e fluxo (plano-primeiro)
1. Confirme o gate (0) e o modo.
2. **AUDITAR:** rode o checklist, entregue o placar priorizado. Fim (a menos que o usuário peça para aplicar).
3. **APLICAR:** PROPONHA o `plano.md` com o texto integral do bloco de instruções proposto (para o usuário revisar palavra por palavra, porque é a parte que carrega julgamento de negócio), a lista de renomeações, as colunas a ocultar, as descrições a criar (ou delegar) e os folders a ajustar. **PARE para aprovação.**
4. Após aprovado, escreva respeitando os gotchas de TMDL; registre em `entrega.md` o que mudou + evidência (placar antes/depois das 7 dimensões).
5. Antes de fechar, cheque: bloco de instruções cobre os 7 tópicos; nenhuma medida visível sem descrição; nenhuma chave técnica visível; load do `.pbip` não quebrou (GUIDs únicos).
