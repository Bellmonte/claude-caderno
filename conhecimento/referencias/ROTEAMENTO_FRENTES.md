# Matriz de roteamento de frentes: referência

> Mapa de consistência multi-frente: dado um caso de uso, qual frente ou skill AGE e quando CEDE a
> vez. Usada pelo `analisar-especificacao` (Passo 4) para rotear, e incrementada pelo
> `capturar-conhecimento` quando uma demanda traz uma decisão de roteamento NOVA. Sem novidade, não
> se escreve aqui. Ela orienta e não esgota: sem match, roteie pelo melhor julgamento e adapte ao
> feedback.
>
> As linhas abaixo são o ponto de partida que o caderno traz. Cada linha nova que entrar aqui deve
> citar a demanda de origem no fim da célula ("Origem: DEM_<COD>"), para a regra nunca ficar sem
> o caso que a justificou.

## Frentes
`pbi` · `dados` · `sql` · `app` · `automacao`

## Casos de uso → frente/skill

### Frente PBI (motor maduro)
| Caso de uso | Age | Cede a vez quando |
|---|---|---|
| Estrutura/M/origem do modelo, relacionamento, calendário | `modelagem-dados` | é só medida → `medidas-dax`; só visual → `montar-visuais` |
| Medida/cálculo/KPI/%/forecast | `medidas-dax` (régua em [[PADRAO_DAX]]) | é só M → `modelagem-dados`; só visual → `montar-visuais` |
| Layout/visual/página do report | `montar-visuais` | é só M/medida → as outras do PBI |
| Pedido que fala em FILTRO ("adicionar X como opção no filtro", "a opção Y não aparece no slicer") | Antes de abrir o `visual.json`, olhe de ONDE o slicer se alimenta. Se a dimensão for tabela fixa dentro do modelo ou se o membro novo depender de uma consulta de origem que ainda não existe, é `modelagem-dados`: o slicer já projeta a coluna certa e passa a mostrar a opção sozinho assim que o membro existir. Confirme com `SUMMARIZECOLUMNS` na dimensão antes de decidir | o membro JÁ existe na dimensão e o problema é seleção padrão, ordenação, tamanho ou item oculto no visual → `montar-visuais`. Se o membro vem de FORA do modelo (view, procedure ou tabela auxiliar do ERP que o M só lê), a frente inteira cede para o motor **sql**: nenhum `.pbip` é tocado e a opção aparece sozinha no refresh. Quando o membro ausente é um **ano**, confira o corte do calendário gerado em M (`[Ano] <= Date.Year(LocalNow())` esconde o ano seguinte), os outros calendários do modelo e filtro de ano travado em página |
| Pedido de **tamanho** num visual HTML renderizado por medida ("aumenta a altura desse gráfico") | `medidas-dax`: o tamanho do desenho mora no CSS **dentro da medida**, e não na `position` do visual. Mexer em `position`, `page.json` e imagem de fundo é o caminho errado e se anula (aumentar visual e página juntos deixa o gráfico proporcionalmente menor). Use px absoluto no container e `overflow-y:auto` | o visual é **nativo** → `montar-visuais` mexendo em `position`; o pedido é reposicionar ou reordenar → `montar-visuais` |
| Pedido que chega com o recorte de banco pronto ("antes do painel, adicionar a coluna na tabela e na rotina de carga") | Antes de aceitar o recorte, percorra a corrente de trás para frente: tabela → rotina de carga (nos DOIS ramos, histórico e incremental) → consulta de origem do modelo → coluna no modelo → projeção no visual. O recorte é hipótese do solicitante sobre o estado. Parando no último elo, nenhuma frente de banco entra e é só `montar-visuais`, com `medidas-dax` só se a prova de grão pedir medida própria | a corrente para na tabela ou na rotina → motor **sql**; para na consulta de origem ou na tipagem em M → `modelagem-dados` |
| "Incluir mais um produto/item/rubrica" numa grade de matriz | Soa `montar-visuais` e quase nunca é. Olhe a projeção de `Columns`: vindo o item de uma TABELA-PONTE com uma medida só no valor, o visual não é tocado e todas as matrizes da página ganham a coluna sozinhas. O trabalho é `modelagem-dados` (origem e coluna) mais `medidas-dax` (medida do item, linha na ponte e o `SWITCH` que traduz a ordem); `montar-visuais` entra só no acabamento de largura | a projeção lista UMA MEDIDA POR ITEM → a grade é montada no visual e `montar-visuais` volta a ser o motor, editando todos os visuais que exibem a grade |
| Incluir código/ID nas tabelas detalhadas "para exportar e cruzar" | `montar-visuais`: o código entra como projeção da MESMA tabela do nome, com `displayName` legível (é ele que vira cabeçalho da exportação); nada muda no modelo. Antes de projetar, faça a prova de grão por consulta (nome com dois códigos divide linha) | o código não está no modelo mas existe na origem → `modelagem-dados` antes; a origem não tem código → não invente chave, registre pendência e ceda ao motor **sql**/**dados** |
| Renomear título/rótulo de um painel | depende de ONDE o texto mora | título nativo do visual (`visual.json`) → `montar-visuais`; rótulo renderizado dentro de uma medida HTML → `medidas-dax`. Localize o texto por grep no `.SemanticModel` além do `.Report` antes de rotear |
| Regra de KPI que muda só numa página, quando a medida do visual é COMPARTILHADA com outras páginas | `medidas-dax` do começo ao fim: cria a medida DERIVADA (`CALCULATE([base], KEEPFILTERS(...))`) e aponta o cartão daquela página para ela. Alterar a medida base é o erro: varra quem consome antes e teste por segmento, porque a aba irmã pode ficar em branco | a página é a única consumidora → altera a base, sem derivada; o pedido é redesenho do cartão → `montar-visuais` |
| Uma categoria deve parar de contar num indicador ("esse tipo não entra nas estatísticas") | `medidas-dax`, e a pergunta que decide é se a regra é do DOMÍNIO ou de uma página. Sendo do domínio, altera a MEDIDA-BASE com `KEEPFILTERS`, depois de varrer os consumidores e provar antes e depois por consulta em cada um. Em base de planilha, recorte por conteúdo (`CONTAINSSTRING`) em vez de lista, porque a mesma categoria convive em várias grafias | a regra vale só numa página → derivada, como na linha acima; o registro precisa sumir da TELA → entra `montar-visuais`; a categoria nasce errada na origem → `modelagem-dados` |
| "Incluir um card novo" ou mexer num card | Veja se o card é visual nativo ou HTML renderizado dentro de uma medida. Sendo HTML, é `medidas-dax` do começo ao fim e **não toca no relatório** | a coluna de cards é nativa (`cardVisual`) → `montar-visuais` |
| Deixar o modelo legível para IA (Copilot, Q&A, agente que lê o modelo e escolhe o campo certo) | `legibilidade-ia`, etapa de MATURAÇÃO depois do dev e da validação. Régua em [[PADRAO_LEGIBILIDADE_IA]] | a modelagem está errada → `modelagem-dados`; falta ou erra medida → `medidas-dax`. Não roda em fix trivial nem em modelo que nenhuma IA consome |
| Valor em branco ou errado cuja causa está (em parte) na CARGA da origem | a frente `pbi` faz a SUA parte no modelo e CEDE a parte de origem ao motor **dados**, lendo o espelho do ambiente ([[processo_espelho_separado_do_material_bruto]]); registra a dependência e não finge resolver na origem | a causa é toda no modelo (hardcode, dado já chega certo) → resolve inteiro no PBI |
| Entidade que parece "parada" (o realizado zera a partir de certo mês) mas a operação garante que nunca parou | antes de modelar, procure a coluna NORMALIZADA que a origem já entrega: o time de dados costuma já ter resolvido e o modelo só não passou a usar. Confirmado, é `modelagem-dados` (repontar relacionamento) e a `legibilidade-ia` entra na MESMA entrega, porque escrever a regra é metade do conserto | a origem NÃO tem coluna normalizada e a separação exige rateio → não invente de-para no painel: consolide no grupo, registre a limitação e ceda a decisão ao negócio |
| Painel de monitoramento que "não mostra" um objeto | Olhe ONDE o conteúdo é montado antes de abrir o `.pbip`: se a fato lê uma tabela populada por extração, o conserto é no parser da extração (motor `dados`) e o report só reflete. Confirme a premissa no modelo real: pode ser filtro de visual escondendo de propósito | o objeto está capturado e o que falha é exibição → `montar-visuais` ou `medidas-dax` |
| Dashboard lento para abrir ou para filtrar | `auditar-performance`, com régua em [[PADRAO_PERFORMANCE_PBI]]: mede primeiro e liga o número à causa no `.pbip` | a lentidão é do refresh agendado de OUTRO modelo → entregue o diagnóstico com dado real (histórico de atualização por tipo de disparo) e ceda o ajuste de janela ao dono da orquestração |
| "O painel A puxa de outra fonte, faça puxar da fonte do painel B" (dois BIs divergindo no mesmo indicador) | `modelagem-dados`, e o primeiro movimento é comparar as duas consultas de origem lado a lado antes de acreditar que a fonte difere. Divida o valor errado pelo certo: múltiplo inteiro limpo é fan-out de JOIN dentro da consulta nativa | as consultas leem objetos realmente distintos → decisão de qual é a oficial sobe ao negócio; a fonte é a mesma e o que difere é o cálculo → `medidas-dax` |

### Frente APP (aplicação: front, back, API e agentes de IA)
| Caso de uso | Age | Cede a vez quando |
|---|---|---|
| Front (HTML/CSS/JS), back (Node/Express), API/rota | `desenvolver-app` (régua em [[PADRAO_APP]]) | — |
| Agente novo, persona, registro do agente, handler no roteador | `desenvolver-app` (+ [[PADRAO_PROMPT_AGENTE]]) | — |
| Indicador "ao vivo" na aplicação (rota + store + card) | `desenvolver-app` | a CRIAÇÃO da view de origem é do motor **sql** (o app só consome) |
| Bug ou divergência de resultado num indicador ou agente | `desenvolver-app` | a causa está na view ou procedure de origem → motor **sql** (registra dependência) |
| Distribuição de relatório ou fluxo conversado por ferramenta de automação | `desenvolver-app` faz só o proxy e o registro do agente | a lógica do fluxo em si → motor **automacao** |
| Novo canal de ingresso para um agente (ex.: mensageria) | `desenvolver-app` (rota própria + segredo + allowlist + render no servidor) | o microsserviço de transporte é IRMÃO e BURRO: toda IA e toda chave ficam na aplicação; trocar de provedor mexe só nele |

### Fronteiras duras do APP
- O app PARA no Node/JS/front/API. View, procedure e PL/SQL de origem → **sql**.
- Fluxo de automação (nós e lógica) → **automacao**; no app, a ferramenta de automação é só proxy.
- Demanda que atravessa a fronteira: a frente que age executa a sua parte e REGISTRA a dependência
  da outra ponta, sem fingir resolver sozinha.

### Investigações com start próprio (não passam pelo desenvolvimento normal)
| Caso de uso | Age |
|---|---|
| Conferir e isolar divergência genérica entre bases (CSV, origem, sistema x BI) | `reconciliar-bases` |
| Transcrição de reunião → ata (e destila demandas do alinhamento) | `ata-reuniao` → `abrir-demanda` |
| Quebra ou instabilidade não planejada que afetou o ambiente ou as demandas (carga falhou, base explodiu, alteração de origem derrubou a camada de dados) | `registrar-incidente` (namespace `DEM_INC-NNN`; entrada variada, de e-mail a print, log ou relato; fecha só quando ESTABILIZADO) |

### Chassi transversal (apoio de gate, sem ser frente)
| Caso de uso | Age | Cede a vez quando |
|---|---|---|
| Validar visualmente uma solução ou desenho num gate (arquitetura, modelo de dados, contrato, fluxo, antes e depois, KPIs de diagnóstico) | `gerar-mockup-validacao`: mockup HTML autocontido do entregável, com dados reais do diagnóstico; chamado pela `analisar-especificacao` (GATE 1) ou por qualquer frente no GATE 2. Identidade em [[PADRAO_VISUAL_REPORTE]] | é fix trivial, doc de texto puro sem estrutura, ou dashboard PBI cujo próprio Desktop já é a validação |

### Frente DADOS (plataforma de dados, notebooks e pipelines; motor sem skill, execução manual ou assistida)
| Caso de uso | Age | Cede a vez quando |
|---|---|---|
| Extração ou notebook da camada de dados | motor `dados` (manual) | vira modelo, medida ou visual → frentes `pbi`; é view ou procedure do banco → `sql` |
| Segredo hardcoded em notebook ou pipeline | motor `dados`: mover para o cofre de chaves da plataforma | rotação de senha já vazada é higiene à parte → `registrar-incidente` |
| Testar ou homologar notebook que grava no lake de produção | motor `dados`: isolar em namespace paralelo (`_v2`), nunca apontar escrita de dev para caminho vivo | — |
| Ajustar notebook, pipeline ou trigger existente | motor `dados`: LER o espelho em `espelho/<ambiente>/` (reexportar antes pela rotina somente leitura), propor o ajuste como ARQUIVO em `proposto/` dentro da demanda, com instrução de import. O usuário importa e publica na mão. Régua em [[processo_espelho_separado_do_material_bruto]] | tocar main ou produção é gate humano; o Claude nunca escreve no ambiente vivo |
| Pedido que fala em DASHBOARD mas é sobre QUANDO ele atualiza ("atualiza tarde", "queria que atualizasse junto com o X") | motor `dados`: nada de modelo, medida ou visual é tocado. É orquestração, e o método é levantar todo objeto que o painel consome (fato, camada final e dimensão) antes de mover qualquer coisa, porque antecipar só o refresh deixa o painel rápido e errado | o painel atualiza no horário certo e o problema é o NÚMERO → `pbi` (ou incidente, se quebrou) |

Ainda sem skill própria: execução e revisão manuais, sem auditor de dados. Nasce skill quando o
padrão se repetir.

### Motor SQL (banco de origem e ERP; sem skill própria, execução manual ou assistida)
| Caso de uso | Age | Cede a vez quando |
|---|---|---|
| Pedido que chega como ajuste de painel ("falta uma opção no filtro", "esse número soma o que não devia") mas a regra mora numa view ou procedure do ERP | motor `sql`: ler o objeto, achar o critério na **consulta irmã** da mesma família, alterar e registrar no cabeçalho do objeto. Nenhum `.pbip` é tocado | a regra está no modelo → volta às frentes `pbi`; a alteração é de carga do lake → motor `dados` |

**Antes de recompilar:** objeto de origem é compartilhado. Levante os consumidores por grep no nome
da tabela, separe quem filtra a coluna alterada de quem não filtra, e meça a migração com uma
consulta sobre a tabela como ela está hoje. Procedure que apaga e reinsere janela reclassifica o
histórico inteiro no primeiro refresh. A execução no banco é sempre do usuário; o Claude entrega o
arquivo.

**`automacao`** (ferramenta de fluxos, integrações) ainda não tem skill própria. Se houver um
servidor MCP da ferramenta, use-o para catálogo de nós e validação de fluxo antes de subir, sempre
em modo de leitura e proposta. A régua de fronteira não muda: o fluxo em si é `automacao`, e na
aplicação a ferramenta é só proxy.
