# Padrão de formatação de DAX e M

> Como todo código DAX e M sai escrito, seja medida, coluna calculada, partição ou expressão.
> O DAX segue o DAX Formatter da SQLBI, com o espaço antes do parêntese que a casa adotou. O M segue o
> que o formatador da Microsoft para Power Query e a comunidade praticam, fixado aqui porque não existe
> guia oficial tão consolidado. Cada regra tem um identificador, e é por ele que o verificador, o hook e
> o auditor falam. O que é escrever bem (DIVIDE, derivação por base, BLANK) continua no
> [[PADRAO_DAX]]; este arquivo trata só da forma.

## 1. O princípio: formatar nunca muda resultado

Formatação mexe em espaço, quebra de linha, caixa de nome de função e nome de variável ou de passo.
Nada além disso. Trocar `/` por `DIVIDE`, derivar da medida base ou tirar um `REMOVEFILTERS` é mudança
de lógica: pertence à `medidas-dax`, passa pela esteira e nunca entra numa rodada de formatação.

| Pode numa rodada de formatação | Não pode |
|---|---|
| espaço, quebra de linha, indentação | trocar função, operador ou argumento |
| maiúscula no nome de função e palavra-chave | mexer em qualquer coisa dentro de aspas |
| renomear `VAR` ou passo de M, com todas as referências no mesmo movimento | renomear medida, coluna ou tabela |
| pôr a tabela na coluna, tirar a tabela da medida | acrescentar ou remover filtro |
| comentário | mudar a ordem de passos do M |

Texto entre aspas é intocável: uma medida-HTML devolve exatamente o que está escrito ali.

## 2. DAX

| Regra | O que diz | Conferido por |
|---|---|---|
| DAX-01 | Nome de função e palavra-chave em maiúsculas, com um espaço antes do parêntese: `CALCULATE (`, `DIVIDE (`, `BLANK ()`. Vale para `VAR`, `RETURN`, `TRUE`, `FALSE`, `IN` | verificador |
| DAX-02 | Chamada curta fica numa linha só, com espaço depois do `(` e antes do `)`: `DIVIDE ( [Margem], [Receita] )`. Curta é a que cabe na linha e não tem, dentro dela, outra chamada com mais de um argumento | verificador |
| DAX-03 | Chamada longa abre o parêntese na linha da função, põe cada argumento numa linha com 4 espaços a mais que o início da função, e fecha o parêntese sozinho numa linha, alinhado com o início da função | verificador |
| DAX-04 | **Exceção da casa:** `CALCULATE` e `CALCULATETABLE` sempre quebram, um argumento por linha, mesmo quando caberiam numa linha | verificador |
| DAX-05 | Vírgula no fim da linha, nunca no começo | verificador |
| DAX-06 | Coluna sempre com a tabela, medida nunca com a tabela: `Dim_Cliente[Nome]`, `[Receita (R$)]`. Aspas na tabela só quando o nome exige | verificador, com os nomes lidos do próprio `.pbip` |
| DAX-07 | Espaço em volta de operador: `[A] - [B]`, `v_qtd >= 10`, `&&`, `\|\|`, `&` | verificador |
| DAX-08 | `VAR` na indentação base. A expressão fica na linha do `VAR` quando é curta e desce para a linha seguinte, com 4 espaços a mais, quando é longa. `RETURN` alinhado com o `VAR`, e a expressão retornada na linha seguinte, com 4 espaços a mais | verificador |
| DAX-09 | Nome de variável em `v_snake_case`, e `_` para fragmento de texto ou HTML ([[PADRAO_DAX]] §1) | verificador |
| DAX-10 | Linha de no máximo 100 caracteres, contados depois da indentação estrutural do TMDL. Texto entre aspas não entra na conta | verificador |
| DAX-11 | Comentário de linha com `--`. Medida grande ganha banner `// ===== Seção =====` | revisão |
| DAX-12 | Indentação só com espaço dentro da expressão, nunca tabulação | verificador |
| DAX-13 | Expressão curta, sem `VAR` e que cabe em 100 caracteres, fica na linha do `=`. Qualquer outra começa na linha seguinte | verificador |

### Antes

```dax
Crescimento (%) = var atual=sum(Fact_Vendas[Receita]) var ant=calculate(sum(Fact_Vendas[Receita]),DATEADD(Dim_Calendario[Data],-1,YEAR),REMOVEFILTERS(Dim_Canal)) return if(isblank(ant),blank(),(atual-ant)/ant)
```

### Depois

```dax
Crescimento (%) =
VAR v_atual = SUM ( Fact_Vendas[Receita] )
VAR v_anterior =
    CALCULATE (
        SUM ( Fact_Vendas[Receita] ),
        DATEADD ( Dim_Calendario[Data], -1, YEAR ),
        REMOVEFILTERS ( Dim_Canal )
    )
RETURN
    IF ( ISBLANK ( v_anterior ), BLANK (), ( v_atual - v_anterior ) / v_anterior )
```

O `IF` ficou numa linha porque cabe nela e não tem, dentro dele, chamada com mais de um argumento
(`ISBLANK` tem um, `BLANK` nenhum). O `CALCULATE` quebra mesmo assim, pela DAX-04.

A lógica ficou idêntica, e é de propósito. A divisão com `/` e o `SUM` repetido no lugar de uma medida
base violam o [[PADRAO_DAX]], mas corrigir isso é trabalho da `medidas-dax` numa demanda, com
paridade conferida. Uma rodada de formatação que aproveitasse para "melhorar" a conta estaria
misturando duas mudanças num commit só.

## 3. M (Power Query)

| Regra | O que diz | Conferido por |
|---|---|---|
| M-01 | `let` na coluna zero da expressão, cada passo com 4 espaços, `in` alinhado com o `let` e o passo final na linha seguinte, com 4 espaços | verificador |
| M-02 | Um passo por linha, com nome que diz o que ele faz, sem espaço e sem acento, dispensando o `#"..."`: `TiposAjustados`, `ComCabecalho`, `SemDuplicadas`, `Renomeadas`. Nome padrão da interface (`#"Tipo Alterado"`, `#"Personalização Adicionada1"`, `#"Consultas Mescladas2"`) é violação | verificador |
| M-03 | Chamada longa quebra como no DAX: parêntese aberto na linha da função, um argumento por linha com 4 espaços a mais, e o parêntese de fechamento alinhado com o início do passo | verificador |
| M-04 | Lista ou registro que passe de 100 caracteres, ou com mais de três itens compostos (item que é ele mesmo lista, registro ou chamada), fica com um item por linha. Chave de abertura e de fechamento seguem a regra do parêntese. Itens simples que cabem na linha ficam juntos | verificador |
| M-05 | Espaço em volta de `=` dentro de registro e em volta de operador: `[Delimiter = ","]`, `Pasta & "vendas.csv"` | verificador |
| M-06 | `each` curto fica na linha. Lógica longa vira função com parâmetro nomeado, `(linha) => ...`, quebrada em linhas | verificador (comprimento), revisão (nome do parâmetro) |
| M-07 | Comentário `//` **acima** do passo, dizendo por que ele existe quando isso não é óbvio. Nada de comentário no fim da linha | verificador |
| M-08 | Vírgula no fim da linha, linha de no máximo 100 caracteres, indentação só com espaço | verificador |
| M-09 | Mudança de tipo com a cultura declarada quando a fonte usa separador decimal diferente do pt-BR | revisão |

Continua valendo o molde da `modelagem-dados`: origem, tipagem com nome técnico e renomeação para
o nome de negócio por último.

### Antes

```m
let
    Fonte = Csv.Document(File.Contents(Pasta & "vendas.csv"),[Delimiter=",", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Cabeçalhos Promovidos" = Table.PromoteHeaders(Fonte, [PromoteAllScalars=true]),
    #"Tipo Alterado" = Table.TransformColumnTypes(#"Cabeçalhos Promovidos",{{"id", Int64.Type}, {"data", type date}, {"cliente", type text}, {"valor", type number}}, "en-US")
in
    #"Tipo Alterado"
```

### Depois

```m
let
    Fonte = Csv.Document(
        File.Contents(Pasta & "vendas.csv"),
        [Delimiter = ",", Columns = 6, Encoding = 65001, QuoteStyle = QuoteStyle.None]
    ),
    ComCabecalho = Table.PromoteHeaders(Fonte, [PromoteAllScalars = true]),
    // a fonte usa ponto como separador decimal
    TiposAjustados = Table.TransformColumnTypes(
        ComCabecalho,
        {
            {"id", Int64.Type},
            {"data", type date},
            {"cliente", type text},
            {"valor", type number}
        },
        "en-US"
    )
in
    TiposAjustados
```

O registro do `Csv.Document` tem quatro campos simples e cabe na linha, então fica junto. A lista de
tipos quebra porque tem quatro itens compostos, cada um uma lista, e é nela que alguém vai mexer.
A cultura `"en-US"` já estava no antes: formatar não acrescenta argumento.

Renomear passo muda a referência dos passos seguintes. A troca é feita no mesmo movimento, em todas
as referências, e a paridade é conferida do mesmo jeito, mesmo que renomear passo não mude dado.

## 4. O detalhe do TMDL

No `.pbip`, o código mora dentro do TMDL, e o TMDL tem a própria indentação estrutural, com
tabulação. A expressão de uma medida ou de uma partição começa algumas tabulações para dentro, e a
formatação do código vem depois disso, com espaço.

- O verificador desconta o prefixo de tabulação comum a todas as linhas da expressão antes de medir
  indentação e comprimento. As regras DAX-12 e M-08 valem só para o que vem depois desse prefixo.
- `///` acima de medida é descrição, não código, e fica fora do verificador.
- Edição de arquivo do `.pbip` só com o Desktop fechado, porque o próximo salvamento do Desktop
  sobrescreve o que foi escrito por fora. Na gravação por script, mantenha a codificação e a quebra
  de linha CRLF que o arquivo já tem: trocar BOM ou final de linha gera diff no arquivo inteiro e
  pode derrubar o load.

## 5. Como isto é garantido

| Camada | O que faz |
|---|---|
| `.claude/scripts/lint_formatacao.py` | Lê `.tmdl`, `.dax`, `.pq` e `.m`, aponta cada violação com arquivo, objeto, linha e regra. Roda sem rede. Com `--relatorio`, devolve o total por regra e os objetos piores de um painel inteiro |
| hook `valida_formatacao.py` | A cada escrita (Write, Edit, ou script via Bash e PowerShell), confere **só os objetos que mudaram em relação ao `HEAD`** do git do painel e devolve as violações com código 2. Legado que ninguém tocou não trava a edição |
| `PreToolUse` nas operações de medida e partição do `powerbi-modeling-mcp` | Confere a expressão antes de ela ir para o modelo aberto, que nenhum hook de arquivo enxerga |
| `auditor-pbi`, modo 2 | Consome o `--relatorio` na auditoria completa |
| rodada de formatação (demanda própria) | Reformata um painel inteiro, objeto por objeto, e só entrega com o verificador limpo e a paridade conferida |

Formatadores na web (DAX Formatter, formatadores de M online) enviam o código a um serviço de
terceiro, e código de painel corporativo não sai da máquina. Um formatador que rode localmente só entra
depois de confirmado que roda sem rede, e mesmo assim a régua continua sendo o verificador.
