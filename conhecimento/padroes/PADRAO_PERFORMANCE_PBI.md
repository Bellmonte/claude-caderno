# Padrão de performance Power BI: régua de medição e catálogo de causas

> Referência da skill `auditar-performance` e do modo 3 do `auditor-pbi`. Qualidade se avalia
> lendo o `.pbip`; performance só se avalia medindo o modelo rodando. Este arquivo diz como medir,
> quando uma melhora pode ser afirmada e onde procurar a causa de cada número.
> Scripts em `.claude/scripts/performance/`. Relatório no modelo [[auditoria-performance]].

## 1. As três grandezas

| Grandeza | Como medir | Repetições | Script |
|---|---|---|---|
| tamanho do modelo | visões de armazenamento do motor (`INFO.STORAGETABLECOLUMNS` para o dicionário, `INFO.STORAGETABLECOLUMNSEGMENTS` para dados e índices), a mesma fonte do VertiPaq Analyzer | uma leitura depois de atualização completa, conferida depois de uma segunda | `tamanho_modelo.ps1` |
| tempo de atualização | comando TMSL de atualização completa, cronometrado do envio ao retorno | uma de aquecimento descartada e cinco medidas | `medir_atualizacao.ps1` |
| tempo de página | a quente, o JSON do analisador de desempenho do Desktop; o motor a frio e a quente, as consultas do mesmo JSON repetidas com o cache limpo antes de cada execução | cinco a frio e cinco a quente por consulta | `medir_consultas.ps1` |

A repetição por script mede o tempo do motor, que é a consulta DAX, e é ali que está quase toda a
lentidão corrigível. O tempo de desenhar o visual na tela só existe no JSON do analisador, e por isso
a foto do analisador continua valendo como a medida da página inteira a quente. O relatório nunca
mistura as duas.

## 2. Três regras que valem para todas as grandezas

1. **Mesmo ambiente.** Linha de base e remedição na mesma máquina, na mesma versão do Desktop e, de
   preferência, na mesma sessão. O Desktop muda todo mês, e misturar versão com correção invalida a
   comparação. O `comparar.py` recusa versões diferentes.
2. **Mediana e faixa, nunca um número só.** Faixa é do mínimo ao máximo das execuções válidas.
3. **Critério de faixas.** Uma melhora só é afirmada quando as faixas de antes e depois não se
   sobrepõem. Se sobrepuserem, o relatório diz que não houve diferença mensurável.

A medição acontece sempre numa cópia local aberta no Desktop, **com só ela aberta**, e nunca contra o
modelo publicado no serviço. Resultado bruto e export do analisador ficam em
`local/performance/<painel>/`, fora do git.

## 3. A exceção de leitura de `local/performance/`

`local/` segue negada ao Claude. A exceção é estreita: os scripts de performance leem e escrevem em
`local/performance/`, e ao chat voltam só agregados (mediana, faixa, ranking com nome de tabela,
coluna e visual). O texto das consultas pode levar valor literal de filtro, então ele fica no
`consultas.json` local e nunca aparece na tela, no relatório ou em commit.

## 4. O procedimento de uma auditoria

1. **Preparar.** Cópia local do `.pbip`, Desktop aberto só com ela, nada pesado rodando. Registrar
   máquina, versão do Desktop e data (os scripts gravam isso sozinhos no `*_meta.json`).
2. **Medir a linha de base.** Tamanho, atualização e todas as páginas uma vez, para achar a mais lenta.
   Depois, a mais lenta e a mais usada com cinco a frio e cinco a quente.
3. **Diagnosticar.** Ranking de colunas por tamanho, ranking de visuais por tempo e o `.pbip` lido
   contra o catálogo da seção 5. Cada achado recebe impacto (quanto da medição ele explica) e esforço.
4. **Corrigir pela esteira.** Uma filha por correção ou por grupo coerente de correções, com o
   `auditor-pbi` revisando como sempre. Uma mudança por commit, com o motivo escrito.
5. **Conferir a paridade.** Antes de medir o depois, as medidas principais dão o mesmo número nos
   mesmos cortes. Correção de performance que muda número é defeito novo.
6. **Remedir** com o mesmo protocolo, na mesma sessão da linha de base quando der.
7. **Relatar** antes e depois pelo critério de faixas.

## 5. Catálogo de causas

| Causa | Tamanho | Atualização | Página | Como aparece |
|---|---|---|---|---|
| coluna calculada decimal no lugar de medida (margem por linha, razão por linha) | muito | sim | | topo do ranking de colunas, dicionário quase do tamanho da coluna |
| coluna de alta cardinalidade sem uso (ID de linha, data e hora com segundos, número de documento em texto) | muito | sim | | segunda faixa do ranking, dicionário grande |
| tabela plana com atributos de dimensão repetidos no fato | sim | sim | pouco | muitas colunas de texto com cerca de 1 MB de dicionário cada, índices da tabela grandes |
| consulta do Power Query criada por referência a outra que lê fonte grande | | muito | | atualização que dobra sem tabela nova grande; a referência reavalia a cadeia inteira |
| data e hora automáticas ligadas | pouco | pouco | | tabelas `LocalDateTable_*` no modelo |
| relação bidirecional sem necessidade | | | possível | segmentação com lista que encolhe, medida que muda conforme a página |
| DAX com FILTER sobre a tabela inteira, `COUNTROWS(FILTER(VALUES(...), CALCULATE(...)))`, iterador com transição de contexto | | | sim | consulta lenta do visual, muito tempo no motor de fórmulas |
| página com excesso de visuais e segmentações | | | sim | muitas consultas por atualização da página |
| tabela no grão de linha exibida no relatório | | | muito | uma consulta única e lenta, costuma ser a página mais lenta do painel |

## 6. Armadilhas de medição (aprendidas no ensaio, em 1 milhão de linhas)

- **Cache limpo longe da execução não é frio.** Limpar e depois abrir o analisador deixa a página
  renderizar no meio. O script limpa imediatamente antes de cada execução e confere: a mediana a frio
  tem que sair acima da quente. Consulta que não sai fica `suspeito`, e mais de 30% suspeitas invalida
  a rodada como linha de base.
- **Bloco com zero consultas** é o Desktop reaproveitando o resultado do visual. Sai da mediana.
- **A página mais lenta pode não ser a mais carregada.** Uma tabela única no grão de linha já levou
  três vezes mais que uma página com 22 visuais.
- **Coluna calculada decimal pode pesar mais que coluna de alta cardinalidade.** Medir antes de apontar.
- **Atualização por script costuma ser muito estável** (menos de 2% no ensaio). Faixa bem maior que
  isso é sinal de ruído no ambiente, e a primeira suspeita é outro Desktop aberto na máquina. Num teste
  com duas cópias abertas, a faixa foi de 26 a 35 s, e o aquecimento saiu mais rápido
  que todas as medidas.
- **Arquivo do `.pbip` editado com o Desktop aberto se perde** no próximo salvamento. Desktop fechado
  durante edição de arquivo.
- **TMDL escrito à mão com data automática ligada** não ganha as tabelas de data sozinho.

## 7. Valor

Tempo de atualização e de abertura de página é tempo de trabalho. Quando a correção reduz espera de
gente de verdade, o relatório vira a linha de base e o "depois" do `valor.md` na `capturar-valor`.
