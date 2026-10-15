# Obsidian no dia a dia do caderno

> Guia de uso para quem nunca abriu a ferramenta. A configuração e o racional de por que ela
> entrou estão em [[obsidian_cofre_sobre_o_caderno]]; aqui é só como operar.

## A ideia em uma frase

O Obsidian não guarda nada. Ele lê a pasta do caderno direto do disco, arquivo `.md` por
arquivo `.md`, e mostra as ligações entre eles. Fechar o Obsidian não muda nada no caderno, e
qualquer editor continua abrindo os mesmos arquivos. É uma lente, e o que ela acrescenta é a
navegação por ligação, que editor de texto nenhum dá.

Com o tempo o caderno passa de centenas de notas e de wikilinks espalhados por elas. É esse
tecido que a ferramenta desenha.

## A tela

Três áreas, e você mexe pouco nelas.

À **esquerda** fica a barra lateral com o explorador de arquivos (a árvore de pastas), a busca
e os marcadores. No **meio** fica a nota aberta. À **direita** ficam os painéis de contexto, e
são eles que valem o preço: links inversos, links de saída e o grafo local.

Se a lateral direita não aparecer, o botão de abrir fica no canto superior direito. Vale deixar
ela sempre aberta.

## A interface está em português, e a internet não

Toda documentação e todo tutorial de Obsidian que você achar usam os nomes em inglês, então
procurar por "backlinks" na paleta de comandos não devolve nada. Esta tabela é a ponte:

| No seu Obsidian | Como o mundo chama |
|---|---|
| Links inversos | backlinks |
| Links de saída | outgoing links |
| **Marcadores** | bookmarks |
| Alternador rápido | quick switcher |
| Paleta de comandos | command palette |
| Visualização em gráfico · Gráfico local | graph view · local graph |
| Explorador de arquivos | file explorer |
| Arquivos excluídos | excluded files |
| Notas diárias · Modelos | daily notes · templates |
| Modo de origem · Visualização de leitura | source mode · reading view |
| Dividir para a direita | split right |
| Abrir visualização vinculada | open linked view |

A regra prática ao usar a paleta (`Ctrl+P`): digite o termo em **português** e uma palavra só,
ou melhor ainda, um pedaço curto dela. A paleta casa por trecho em qualquer posição, então
"marca" acha os de marcador e "gráf" acha os do grafo.

Quando o comando não aparecer, não insista na paleta: o **botão direito** no arquivo, na aba ou
na pasta abre um menu que mostra o nome traduzido de verdade. É mais rápido que adivinhar o
termo, e serve para descobrir como sua versão chama cada coisa.

## Os cinco atalhos que resolvem 90%

| Atalho | O que faz |
|---|---|
| `Ctrl+O` | abre qualquer nota digitando parte do nome. É o mais usado de todos |
| `Ctrl+Shift+F` | busca em todo o caderno, com operadores (abaixo) |
| `Ctrl+P` | paleta de comandos: digite o que quer fazer e ele acha |
| `Ctrl+E` | alterna entre Modo de origem (markdown cru) e Visualização de leitura |
| `Ctrl+clique` | abre o link num painel novo ao lado, sem perder o de onde veio |

O `Ctrl+O` merece destaque porque muda o jeito de trabalhar. Em vez de caçar na árvore de
pastas, você digita `roteamento` e cai no `ROTEAMENTO_FRENTES`. Com centenas de notas, procurar
pela árvore deixa de fazer sentido rápido.

Um detalhe que economiza tempo: segurar `Ctrl` e passar o mouse sobre um link mostra a nota
inteira num balão, sem sair de onde você está.

## Buscar de verdade

A busca aceita operadores, e é aí que ela passa a valer mais que o `Ctrl+F` do editor.

- `path:conhecimento` restringe a uma pasta. Combine com o resto: `path:runbooks folding`
- `file:PADRAO` procura no nome do arquivo, não no conteúdo
- `"coluna calculada"` entre aspas casa a frase exata
- `-teste` exclui quem contém a palavra
- `tag:#pbi` procura por tag, se você usar

Elas se combinam. `path:demandas TSK-10` lista as demandas daquela faixa de código sem você
lembrar em que gaveta cada uma caiu.

## Os painéis que fazem a diferença

**Links inversos** é a razão de tudo. Com uma nota aberta, o painel mostra todas as outras
notas que apontam para ela. Abra uma decisão do baú e você vê quais runbooks e quais demandas
dependem daquela decisão. Essa pergunta, "quem depende disto", a busca por texto nunca
respondeu direito, porque exigia que você lembrasse o nome exato para procurar.

**Links de saída** é o inverso: para onde esta nota aponta. Serve para conferir se uma nota
nova ficou órfã no meio do caderno.

**Grafo local** desenha só a vizinhança da nota aberta, um ou dois saltos ao redor. É bem mais
útil no dia a dia que o grafo geral, e é o que vale deixar fixo na lateral.

## O grafo, e por que filtrar

Uma nota antes de começar: o texto aqui diz grafo, que é o nome técnico, mas a interface em
português traduziu como **gráfico**. É a mesma coisa, e é por "gráf" que você acha na paleta.

Abra o grafo geral e ele vai decepcionar. Só uma fração pequena das notas é alvo de algum link,
e as demandas quase não se citam entre si, então o desenho vira uma nuvem de pontos soltos em
volta de um miolo pequeno. A ferramenta está certa; esse é o formato do caderno, porque demanda é
registro de evento e não conversa com as outras.

Onde ele rende é filtrado. No painel do grafo tem um campo de busca, e digitando
`path:conhecimento` aparece o segundo cérebro desenhado: runbook puxando decisão, decisão
puxando padrão, e as notas mais citadas no meio ligando quase tudo. As campeãs costumam ser
as decisões de processo e os runbooks que resolvem problema recorrente.

Nas opções do grafo há uma chave para mostrar links não resolvidos. Ligada, aparecem também os
nós fantasma, que são wikilinks escritos apontando para nota que ninguém escreveu ainda. Isso é
informação útil: um alvo citado quatro vezes que não existe é um runbook faltando. A
tentação de criar nota vazia só para calar o grafo é o erro clássico, porque troca um sinal útil
por silêncio.

## Wikilink, que é como o caderno se costura

Escrevendo `[[` no meio de qualquer nota, o Obsidian abre uma lista com todas as notas do
caderno e você escolhe. O resultado fica `[[nome-da-nota]]`, e vira link clicável.

Duas coisas que o caderno já resolveu por você e vale saber que existem. A primeira é que o
link é gravado por caminho completo, e não pelo nome curto, porque dezenas de notas se chamam
`contexto`, `plano` ou `entrega`; com nome curto o link ficaria ambíguo e apontaria para a nota
errada. A segunda é que renomear uma nota conserta sozinho todos os links que apontavam para
ela, então você pode renomear sem medo pela própria ferramenta.

Renomear **por fora** do Obsidian é outra história, e aí vale a regra abaixo.

## Os dois usos que pagam a conta aqui

**Ler o baú.** Comece sempre pelo `conhecimento/INDICE.md`, que é a porta de entrada com uma
linha por nota. De lá você entra numa decisão ou runbook e passa a navegar por ligação, com os
links inversos dizendo quem depende do quê. É a leitura que a busca por texto não permitia, porque
exigia saber o nome antes de procurar.

**Vasculhar o diário.** As notas de `diario/` são datadas e não se citam entre si, então nem
grafo nem link inverso ajudam ali. O que resolve é a busca com escopo. `path:diario` mais um termo
responde "quando foi que eu mexi nisso", e é isso que o diário nunca soube responder sozinho.
Alguns recortes que funcionam bem:

- `path:diario TSK-101` traz todos os dias que tocaram aquela demanda, na ordem
- `path:diario "retorno de validação"` acha os episódios de devolutiva
- `path:diario <sigla de uma unidade ou sistema>` reconstrói uma investigação que atravessou
  vários dias

Para abrir um dia específico, `Ctrl+O` e a data já basta: digitando `2026-08` ele lista o mês
inteiro. No explorador de arquivos a pasta também se ordena sozinha, porque o nome é a data em
formato que ordena.

Vale fixar `conhecimento/INDICE.md` como marcador, para ele virar o ponto de partida de toda
sessão de leitura. Botão direito na aba do arquivo e escolha **Marcador...**; pela paleta é
`Ctrl+P` e `marca`. O painel deles é o ícone de marcador de página na barra da esquerda.

## O que não fazer

O caderno é lido por skills, e elas dependem dos caminhos e da estrutura. Então:

Não renomeie nem mova pasta de demanda para "ficar melhor no grafo". As skills leem
`demandas/<TIPO>/DEM_<COD>_<slug>/` e quebram se aquilo mudar de lugar.

Não migre a captura para template do Obsidian. Quem escreve no caderno são as skills, que fazem
isso melhor e com a régua certa. O Obsidian entra depois, para ler.

Não instale plugin de comunidade além do Dataview, que a Home exige. Os painéis nativos já
respondem o resto, e o consolidado de valor o `rollup_valor.py` já faz, versionado e sem depender
de ninguém ter plugin instalado.

Não aceite o Obsidian Sync. Quem sincroniza este caderno é o git, e os dois disputando o mesmo
arquivo dá conflito.

## Roteiro dos primeiros quinze minutos

1. Abra `conhecimento/referencias/ROTEAMENTO_FRENTES.md`, que é a nota mais conectada do
   caderno, e navegue pelos wikilinks dela com `Ctrl+clique`, abrindo ao lado.
2. Abra uma decisão qualquer em `conhecimento/decisoes/` e leia o painel de links inversos. Veja
   quem depende dela.
3. Filtre o grafo por `path:conhecimento` e olhe o desenho do baú.
4. Ligue os links não resolvidos no grafo e veja quais notas o caderno cita mas nunca escreveu.
   Cada uma é um candidato a runbook.

Se depois disso nada tiver dito algo que a busca do editor já não dizia, tudo bem largar.
Nenhuma skill depende do Obsidian estar instalado.
