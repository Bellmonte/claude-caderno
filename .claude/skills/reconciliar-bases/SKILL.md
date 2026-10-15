---
name: reconciliar-bases
description: Reconcilia duas bases/extrações que deveriam apresentar o mesmo número e isola as linhas divergentes. Investigação técnica, start próprio (não passa pelo analisar-especificacao). Use para área x área, sistema x sistema (ex.: BI x ERP) ou qualquer caso "deveria bater e não bate". Transversal.
---

> DESTINO: todo arquivo de registro (demandas/, diario/, conhecimento/, gerencial/) é criado na RAIZ DO CADERNO (o repositório do caderno adicionado à sessão), NUNCA no repo de trabalho. Se o caderno não estiver na sessão, pare e peça para adicioná-lo. Ver CLAUDE.md > "Onde cada coisa mora".

# Skill: reconciliar-bases (investigação técnica — start próprio)

Compara duas bases que, em tese, representam o mesmo número, e ISOLA onde está a diferença.
Start próprio: NÃO passa pelo analisar-especificacao. Você cria a solicitação e chama esta skill direto. Ainda assim é uma demanda formal: mora em `demandas/<TIPO>/DEM-XXX/` e gera registro.

## FRONTEIRA — o teto desta skill (leia primeiro)
Função técnica: ENCONTRAR e APRESENTAR a divergência. NÃO classificar causa.
- A skill isola as linhas/registros divergentes (quais, quanto, qual chave) e os apresenta com clareza.
- A skill NÃO taxa nada de "erro" nem de "divergência de negócio". Não decompõe a diferença por causa.
- A explicação do PORQUÊ (ex.: produção para estoque, devolução desdobrada, deslocamento de turno) cabe ao analista de negócio / stakeholder da área — não à skill, não ao time técnico.
Entregue o "onde está a diferença", pare ali.

## Entrada — a solicitação já vem preenchida
Leia `demandas/<TIPO>/DEM-XXX/solicitacao.md`. Ela deve conter (gabarito do que uma solicitação de reconciliação precisa ter):
1. **O que cada base representa** — fonte A e fonte B, o que cada uma mede e por qual lente.
2. **O número que deveria bater** — a métrica a reconciliar, e a unidade.
3. **De-para de campos + chave de junção** — equivalências (ex.: `nr_nota` <-> `numero_nota`, `qtd` <-> `producao`) e qual(is) campo(s) formam a chave.
4. **Período e grão da comparação** — recorte temporal e em que grão somar (produto, nota, dia, mês...).
5. **Os dois arquivos/extrações** — referenciados na própria pasta da demanda.
Se algo estiver faltando, ambíguo, ou se você interpretar um ponto de forma diferente da descrita, PERGUNTE antes de seguir. Não assuma.

## Checagens fixas (pegadinhas silenciosas — SEMPRE aplicar)
- **Vírgula decimal:** CSV brasileiro ("1.234,56") parseia errado e gera divergência fantasma. Trate o separador decimal/milhar explicitamente antes de comparar.
- **Agregação no grão acordado:** some no grão definido (ex.: por produto/período) ANTES de comparar; não compare linha a linha se o grão é agregado, senão o de-para de chave engana.
- **Tipos e chave:** normalize tipos da chave dos dois lados (texto vs número, zeros à esquerda, espaços).

## Fluxo
1. Leia a solicitação e os dois arquivos. Confirme o de-para, a chave, o grão e o período. Questione inconsistências.
2. Prepare os dados de forma defensiva (checagens fixas acima): parse de decimal, tipagem, agregação no grão.
3. Cruze A x B pela chave. Calcule a diferença total. Isole os registros onde A != B (e os que existem só de um lado).
4. Produza o LAUDO (curto, em `demandas/<TIPO>/DEM-XXX/entrega.md`):
   - diferença total (valor e %),
   - tabela das linhas divergentes: chave, valor A, valor B, delta,
   - registros presentes só em A ou só em B,
   - SEM classificar causa — apenas apresentar para a área analisar.
5. Deixe claro que a explicação das divergências cabe à área de negócio.

## Natureza
É investigação, não conserto. A skill não altera nenhuma das bases. Não conclui "erro" — conclui "estas são as linhas onde diverge".
