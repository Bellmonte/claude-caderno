# PADRAO_LEGIBILIDADE_IA: modelo semântico legível para IA generativa

> Camada de legibilidade que se aplica sobre um modelo semântico Power BI já pronto (modelagem correta, medidas certas, visuais montados) para que uma IA generativa que lê esse modelo escolha os campos certos e não invente. Alvos: Power BI Copilot, Q&A e agentes conversacionais próprios que consomem dado desses dashboards. Frente PBI. Skill que aplica: `legibilidade-ia`. Auditor: dimensão dentro do `auditor-pbi`.
>
> Os números e exemplos abaixo vêm da comparação entre dois modelos reais, aqui chamados pelo papel: o **modelo de referência** (um painel de vendas com a camada aplicada) e o **contra-exemplo** (um painel de produção sem a camada).

## Por que isso existe

Um modelo semântico foi desenhado para um humano que enxerga a tela, lê o título do visual, entende o contexto e escolhe o campo certo. Uma IA generativa não tem esse contexto. Ela recebe o esquema do modelo (nomes de tabela, coluna e medida, mais o que houver de descrição e sinônimo) e tem que mapear a pergunta em linguagem natural para os objetos certos. Se o modelo só oferece `calc_volume_realizado` e nenhuma descrição, a IA adivinha, e adivinhar em cima de KPI de gestão vira número errado apresentado com confiança.

A camada de legibilidade transforma o modelo num artefato autodescritivo: um "prompt de sistema" no topo do modelo, vocabulário de negócio nos nomes, um contrato de uso em cada medida, e a ocultação do encanamento técnico que só gera ruído. O ganho não aparece no Power BI Desktop; aparece na qualidade da resposta que a IA dá em cima do modelo.

Regra de altitude: esta camada NÃO conserta modelagem nem cria medida. Ela pressupõe que a estrutura já está certa (isso é `modelagem-dados` e `medidas-dax`) e deixa legível o que já existe. Se a modelagem estiver errada, arrume antes; legibilidade em cima de modelo torto só documenta o torto.

## As 7 dimensões (por ordem de impacto)

O placar medido entre os dois modelos dá a dimensão do delta:

| Dimensão | Modelo de referência (com a camada) | Contra-exemplo (sem) |
|---|---|---|
| 1. Bloco de instruções p/ Copilot no `model.tmdl` | 23 regras de negócio | nenhum |
| 2. Nomes de medida | linguagem natural | técnicos (`calc_`, `total_`) |
| 3. Descrições (`///`) em objetos | ~85 linhas | 9 (e são DAX comentado, não descrição) |
| 4. Colunas ocultas (`isHidden`) | 120 | 1 |
| 5. Descrições em coluna calculada de negócio | sim, com o porquê | não |
| 6. `displayFolder` (famílias de medida) | 108 | 42 |
| 7. Nomes de tabela | `Fact_`/`Dim_`/`Out_` legíveis | sufixos crípticos (`_s`/`_p`) |

### 1. Bloco de instruções de negócio no topo do `model.tmdl`

É a de maior impacto. Um comentário `///` de múltiplas linhas imediatamente acima da declaração `model Model`, com regras numeradas que ensinam a IA a raciocinar sobre o domínio. Funciona como um prompt de sistema embutido no modelo, que viaja junto com ele. O que cada regra tipicamente cobre (adaptado ao dashboard):

- **Domínio e granularidade.** O que o modelo cobre e qual o grão temporal nativo e o de análise (ex.: nativo diário, análise mensal/anual). Instrução de sempre informar o período na resposta.
- **Conceitos que NÃO se somam.** Os grandes recortes que a IA não pode agregar entre si (ex.: Realizado, Projetado e Carteira; os recortes de Carteira que são vistas do mesmo todo e não fatias somáveis). Diga qual medida usar para cada tipo de pergunta.
- **Medidas com escopo parecido mas diferente.** Pares que confundem (ex.: Vendas Realizadas = total; Vendas Confirmadas = só status confirmado). Diga qual é o KPI principal.
- **Unidades de medida.** O que está em unidade inteira, o que está em R$, o que está em USD, o que já é percentual formatado. Instrução dura: não somar moedas diferentes nem percentuais.
- **Medidas que retornam BLANK sem contexto.** Liste as que exigem seleção única (ex.: eficiência mensal exige um único mês; valor de frete exige uma única nota) para a IA avisar o usuário em vez de reportar vazio como zero.
- **Sufixos e o que significam.** `(Entrega)` pela data de entrega, `(Var.)` responde a seletor de tela, `FC` forecast combinado. Diga quando usar cada um e quando preferir a versão fixa/determinística.
- **Regra geral de priorização.** Um parágrafo final: para pergunta sobre performance use X, sobre projeção use Y, sobre backlog use Z; prefira medidas em pasta visível, e trate as medidas com prefixo `.` como internas de suporte.

Formato (TMDL): cada linha do bloco começa com `///`, sem linha em branco entre o bloco e o `model Model`. Texto sem acento (ASCII), como o resto dos objetos. O `///` acima da declaração é a descrição que o TMDL entende; a propriedade `description:` escrita à mão quebra o load.

### 2. Nomes de medida em linguagem natural

A IA mapeia a pergunta do usuário direto no nome da medida. Nome que já é frase de negócio (`Meta de Vendas`, `Vendas Confirmadas`, `Carteira em Aberto`) elimina uma camada de tradução e de erro. Nome técnico (`total_meta_entregas`, `calc_volume_realizado`, `calc_dias_disponiveis`) força a IA a adivinhar o significado a partir do token, e ela erra.

Regra: toda medida VISÍVEL tem nome de negócio, legível, que um gerente reconheceria. As medidas internas de suporte ficam com prefixo `.` e ocultas (ali o nome técnico tudo bem, ninguém lê). Ver `medidas-dax` para a convenção de internas.

### 3. Descrições (`///`) em objetos, num contrato fixo

Descrição de medida segue sempre o mesmo template de 5 partes, na ordem: **o que é + como é calculada + unidade/formato + quando usar + quando NÃO usar**. O "quando não usar" é a parte que mais impede a IA de escolher a medida errada, e a que quase ninguém escreve.

Exemplo do modelo de referência:

```
/// Volume total de vendas previsto na ultima versao da meta comercial,
/// calculado como a soma de QTD_Meta filtrada pela versao maxima disponivel;
/// formato numerico inteiro (unidades). Use para comparar a meta de vendas
/// vigente com o realizado; nao use quando quiser analisar versoes historicas
/// da meta.
measure 'Meta de Vendas' = ...
```

Cuidado com o falso positivo: DAX antigo comentado com `//` no corpo da medida NÃO é descrição e NÃO ajuda a IA (é nota de desenvolvedor e não viaja no esquema). Descrição de verdade é o `///` na linha acima da declaração. O contra-exemplo "tem" 9 linhas de `///`, mas na prática são restos de DAX; conta como zero para a IA.

Este contrato de descrição de medida é o mesmo da skill `medidas-dax` (§6, "descrição em 3 partes"). A skill `legibilidade-ia` não reescreve DAX; ela cobra que a descrição exista e delega à `medidas-dax` quando falta.

### 4. Disciplina de `isHidden` nas colunas técnicas

Toda chave, código de origem e coluna de encanamento (`COD_EMPRESA`, `COD_CLIENTE`, `COD_PRODUTO`, `ID_PEDIDO`, `DT_PEDIDO`, ids de merge) fica `isHidden`. Some do que a IA enxerga. O ganho é duplo: enxuga o esquema (a IA não gasta contexto com dezenas de chaves numéricas) e evita que ela tente usar uma chave como dimensão ou somá-la. No modelo de referência são 120 colunas ocultas contra 1 no contra-exemplo.

Regra prática: se a coluna só serve para relacionamento ou para uma medida calcular por trás, ela é oculta. Só fica visível o que um humano ou uma IA usaria como filtro, eixo ou rótulo de negócio. Tabelas auxiliares inteiras (`Out_*` de suporte, parâmetros, segmentações) levam `isHidden` no nível da tabela.

### 5. Descrições em coluna calculada de negócio, com o porquê

Coluna calculada que carrega intenção (uma flag, um IsPast, um bucket) ganha `///` explicando o que representa e, quando cabe, por que existe daquele jeito. Exemplo do modelo de referência:

```
/// Indica se o mes/ano e anterior ao mes corrente. Coluna calculada usada
/// pelas medidas FC para substituir FORMAT+VALUE em contexto de linha, evita
/// conversao de string a cada iteracao.
column IsPast = ...
```

Isso dá à IA o "porquê" além do "o quê", e ainda documenta a decisão técnica para o próximo dev.

### 6. `displayFolder` organizando as medidas em famílias

Medidas agrupadas em pastas temáticas dão à IA (e ao humano) o mapa mental de quais medidas convivem e reforçam a regra de priorização do bloco de instruções. As internas vão para dot-folders (`.Internas\...`), que ficam no fim e sinalizam "suporte, não use direto". Esquema do modelo de referência: pastas de domínio visíveis (`Realizado`, `Meta`, `Forecast (FC)`, `Carteira`, `Carteira\Vencimento`, `Operacional`, `Margem & Preco`, `Por Entrega (Entrega)`, `Variaveis (Var.)`) e `.Internas\{UI,Validacao,Autorizacao,Legado,Atualizacao}`. Ver `medidas-dax` §6 para a convenção de numeração de folder.

### 7. Nomes de tabela legíveis com prefixo semântico

`Fact_`, `Dim_`, `Out_` (fato, dimensão, auxiliar) dizem a natureza da tabela no próprio nome. A IA trata `Out_*` como não analítica e sabe onde procurar fato e dimensão. Sufixos crípticos (`_s`, `_p`) não carregam essa informação. Observação honesta: isto se sobrepõe ao padrão de modelagem da casa e muitas vezes já vem certo de `modelagem-dados`; a camada só confirma.

## O que NÃO conta como melhoria da camada

- **Esquema linguístico de Q&A (sinônimos, `cultures/pt-BR.tmdl`).** Existe nos dois modelos e é gerado automaticamente pelo Power BI. Só conta como trabalho deliberado se houver sinônimo curado à mão (peso alto, termo de negócio que a autogeração não acharia). Não cobrar sinônimo como item obrigatório; é refino de flagship, fase final, opcional.
- **Prefixo `.` em medida interna.** Os dois modelos já usam. É convenção de `medidas-dax` e não desta camada. Aqui ele só importa porque a interna tem que ficar oculta e fora do caminho da IA.

## Checklist de auditoria (o que o `auditor-pbi` verifica)

Rodar contra o `.pbip` do dashboard. Cada item aponta, não conserta.

1. **Bloco de instruções.** `model.tmdl` tem o comentário `///` de instruções de negócio acima do `model Model`? Cobre domínio, conceitos que não somam, unidades, medidas-BLANK, sufixos e priorização?
2. **Nomes de medida.** Toda medida visível tem nome de negócio? Alguma medida técnica (`calc_`, `total_`, snake_case) está visível?
3. **Descrição de medida.** Toda medida visível tem `///` no contrato de 5 partes? Alguma só tem DAX comentado no lugar da descrição (falso positivo)?
4. **Ocultação.** Chaves e códigos de origem estão `isHidden`? Tabelas auxiliares estão ocultas no nível de tabela? Sobrou coluna técnica visível?
5. **Coluna calculada de negócio.** Flags/buckets/derivadas com intenção têm `///`?
6. **displayFolder.** Medidas visíveis estão em pastas de domínio; internas em dot-folder?
7. **Nomes de tabela.** Prefixo semântico legível (`Fact_`/`Dim_`/`Out_` ou equivalente da casa)?

Veredito: quantos dos 7 a camada cobre, e a lista priorizada do que falta (o bloco de instruções primeiro, sempre).

## Onde isso entra na esteira

Camada de MATURAÇÃO, roda depois que modelagem + medidas + visuais estão prontos e validados, tanto em BI novo (greenfield) quanto em remodelagem ou migração (ex.: ao reconstruir o modelo sobre uma origem nova). Sequência: `modelagem-dados` / `medidas-dax` / `montar-visuais` -> **`legibilidade-ia`** (aplica a camada) -> `auditor-pbi` (segunda opinião, com a dimensão de legibilidade) -> validação no Desktop. Não roda em fix trivial nem em dashboard que nenhuma IA vai consumir; serve aos que alimentam Copilot, Q&A ou agente próprio, ou que a casa quer deixar prontos para isso.

## Gotchas de TMDL que esta camada toca

- Descrição é `///` na linha acima da declaração; `description:` escrito à mão quebra o load.
- Ao editar TMDL por script, todo `lineageTag` novo é um GUID aleatório (uuid). Sequencial montado colide e quebra o `.pbip`.

## Relacionados

- `PADRAO_DAX.md` e skill `medidas-dax`: contrato de descrição de medida, internas, folders, sinônimos.
- skill `modelagem-dados`: estrutura, nomenclatura de tabela, star schema.
- skill `legibilidade-ia`: o executor que aplica esta camada, plano-primeiro.
