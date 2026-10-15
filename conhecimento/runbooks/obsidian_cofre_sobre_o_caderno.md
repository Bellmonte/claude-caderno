# Obsidian como camada de leitura sobre o caderno

> O caderno já é um cofre válido: notas em markdown costuradas por wikilink. O Obsidian entra
> só para **ler e navegar**. A captura continua nas skills, que são melhores
> nisso, e nenhuma delas depende do Obsidian estar instalado.

## Abrir

"Open folder as vault" apontando para a raiz do repositório, seja qual for o caminho na
máquina. Na primeira abertura, recuse o convite do Obsidian Sync e desligue o que for envio de
uso. Quem sincroniza aqui é o git.

A configuração do cofre é versionada em `.obsidian/app.json`, pela mesma lógica do `.claude/`:
tema, formato de link e exclusões são iguais em toda máquina, então o cofre abre pronto. O que
fica fora do git é só o estado da janela e o cache, que mudariam a cada clique.

## Configuração que importa (Settings)

A tabela abaixo é o que o `app.json` já grava. Vale para conferir, ou para reconstruir a mão
se algum dia o arquivo se perder.

**Files and links**

| Opção | Valor | Por quê |
|---|---|---|
| New link format | **Absolute path in vault** | vários nomes de nota se repetem no cofre, e os campeões são `contexto`, `plano`, `entrega`, `valor` (um por demanda) e `SKILL` (um por skill). Com caminho curto, todo link novo para esses nomes fica ambíguo |
| Automatically update internal links | **ligado** | renomear nota conserta quem aponta para ela |
| Default location for new notes | uma pasta escolhida, **nunca a raiz** | senão nota nova cai solta no topo do repositório |
| Detect all file extensions | ligado | deixa enxergar `.html` e `.py` do caderno |
| Excluded files | `local`, `.claude`, `.git` | ver a seção de segurança |
| Use [[Wikilinks]] | ligado | é o formato que o caderno já usa |

**Appearance e plugins.** O único plugin da comunidade é o Dataview, com JavaScript Queries
ligado, porque a Home (`sistema/dashboards/inicio.md`) depende dele; o racional está em
[[processo_home_obsidian_sobre_o_caderno]]. O plugin próprio `caderno-nav` vem versionado em
`.obsidian/plugins/`. Fora isso, os painéis nativos (backlinks, grafo local e busca) bastam, e
o rollup de valor resolve sem plugin nenhum. O acento do tema vem de `.obsidian/appearance.json`,
na mesma cor da paleta de [[PADRAO_VISUAL_REPORTE]].

## Três plugins nativos que precisam ficar desligados

Vêm ligados de fábrica e conflitam com decisões que o caderno já tomou.

**Daily Notes** é o mais perigoso, e o motivo não é óbvio. Ele cria a nota do dia em branco ao
primeiro clique, e se estiver apontado para `diario/` com formato de data, cria exatamente
`diario/AAAA-MM-DD.md`. Só que o `cobrar_diario.py` decide se o dia foi narrado olhando
existência e mtime do arquivo, **sem checar conteúdo**. Um arquivo vazio criado por clique
engana o hook: ele para de cobrar a narrativa de um dia que ninguém escreveu, e a falha é
silenciosa. Mesmo desligado, dá para abrir o dia com `Ctrl+O` e a data.

**Templates** existe para captura, e a captura aqui é das skills, que aplicam a régua certa.
Template no Obsidian faria nota nascer fora da esteira e no formato errado.

**Sync** é o serviço pago de sincronização. Quem sincroniza este caderno é o git, e os dois
disputando o mesmo arquivo dá conflito.

Ficam ligados os que fazem o trabalho de leitura: backlinks, links de saída, grafo, busca
global, alternador rápido, explorador, pré-visualização, sumário e favoritos. Canvas também,
que serve para rascunhar arquitetura; o cuidado com ele é o mesmo de qualquer nota nova, e a
opção de pasta padrão já impede que caia na raiz.

## Segurança: o Obsidian ignora o .gitignore

Isso pesa. A pasta `local/` costuma ter centenas de arquivos e é justamente onde moram
extração, planilha de solicitante, export de ambiente e material sensível. O git a ignora, o
Obsidian **não**: sem configuração, ela entra na busca e no grafo como qualquer nota.

Em `Settings → Files and links → Excluded files`, acrescente `local`. Isso tira a pasta da
busca, do grafo e das sugestões de link. Vale lembrar que a exclusão reduz a presença mas não é
uma parede: o arquivo continua abrível por caminho direto. Para o que exige parede, o lugar
continua sendo fora do cofre.

Acrescente também `.claude` e `.git`, que são ferramenta e encanamento, e não leitura.

## O grafo útil aqui é o do baú, não o do caderno inteiro

O grafo global vai parecer decepcionante, e a razão é estrutural: só uma fração pequena das
notas é alvo de algum wikilink. As demandas quase não se linkam entre si, então o grafo global vira uma
nuvem de pontos soltos em volta de um miolo pequeno.

Onde ele rende é filtrado. No painel do grafo, use `path:conhecimento` e o desenho que aparece
é o do segundo cérebro: runbook puxando decisão, decisão puxando padrão, e a matriz de
roteamento no meio ligando quase tudo.

O **grafo local** (o de uma nota só, com um ou dois saltos) é mais útil no dia a dia que o
global, e é ele que vale deixar aberto na lateral.

## As três coisas para olhar nos primeiros dez minutos

1. Abra uma decisão do baú e olhe o painel **Backlinks** no rodapé. É a pergunta "quem depende
   disto", que o caderno nunca conseguiu responder por busca de texto.
2. Abra `conhecimento/referencias/ROTEAMENTO_FRENTES.md` e navegue pelos wikilinks dela. É a
   nota mais conectada do cofre.
3. Filtre o grafo por `path:conhecimento` e veja o baú desenhado.

Se em dez minutos nada disso te disser algo que a busca do editor já não dizia, o Obsidian não
está pagando o custo, e tudo bem: nada no caderno depende dele.

## Os alvos órfãos

São wikilinks escritos apontando para nota que não existe. Aparecem no grafo como nó fantasma.
Dividem-se em dois tipos, e o tratamento é diferente:

- **Ponteiro para pasta de demanda** (um wikilink com o nome de uma pasta `DEM_<COD>`). O
  Obsidian não resolve pasta, só nota. O conserto é apontar para o documento certo dentro dela,
  com link markdown relativo, e não com wikilink.
- **Nota que nunca foi escrita** (um runbook citado em três ou quatro lugares que ninguém
  escreveu). Cada uma é um pedaço de conhecimento que foi citado mas nunca capturado. **Não crie nota vazia para calar o grafo.** Um órfão citado quatro
  vezes é sinal de runbook que está faltando, e essa é a informação mais útil que o grafo dá.

Ver o que está órfão é fácil pela própria ferramenta: o painel do grafo tem a opção de mostrar
links não resolvidos.

## O que o Obsidian não muda

A captura continua nas skills. Não migre nada para template do Obsidian, não crie fluxo de
escrita por lá e não renomeie arquivo para "ficar melhor no grafo": as skills leem esses
caminhos e a estrutura é lida por elas. O Obsidian lê o que o caderno já escreve, e só.
