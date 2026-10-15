# O painel do caderno é efeito do hook, não comando que se aciona

**Problema.** O caderno sabia responder "o que está pendente, o que eu fazia ontem, como está a
semana", mas a resposta vivia espalhada e sempre datada. As dailies em `gerencial/dia/` e os
planos em `gerencial/semana/` são fotos de um momento, e a foto envelhece: num dia qualquer a
daily mais recente tinha mais de duas semanas e o último plano cobria uma semana já passada. Marcar essas
notas como atalho leva mais rápido a documentos velhos, o que não resolve nada.

Ao mesmo tempo, o `abrir_dia.py` **já calculava** o estado real a cada abertura de sessão, e
jogava fora: injetava como contexto da conversa e desaparecia. Nenhuma outra ferramenta via
aquilo, e nem o próprio usuário fora do chat.

## Decisão

O painel é **efeito colateral do hook que já roda**, não script que alguém aciona. O
`abrir_dia.py` passou a gravar `PAINEL.md` na raiz com a mesma leitura que já fazia.

O que pesou foi a aderência à regra do caderno, mais que a economia de código: registro que depende de
alguém lembrar de acionar é registro que não acontece. Foi exatamente isso que motivou os
hooks. Um script de painel rodado à mão teria o mesmo defeito das dailies que envelheceram.

**O que entra:** incidentes em aberto primeiro (é o que mais dói ficar invisível), a grade da
semana corrente quando existe, os últimos dias narrados com o título que cada um deu ao dia,
os dias com trabalho e sem narrativa, e as demandas sem fechamento agrupadas por gaveta e
ordenadas pelo tempo sem receber toque.

**Idade por mtime, não por data escrita no documento.** O mesmo raciocínio de
[[hook_posttooluse_nao_ve_escrita_por_shell]]: o sistema de arquivos responde independente de
por onde veio a escrita, e ninguém precisa manter o dado atualizado à mão.

## O desenho é horizontal de propósito

Painel que rola é painel que ninguém lê. A primeira versão empilhava 45 demandas em lista e
gastava 104 linhas, o que obriga a rolar justamente quando a pergunta é "como estão as coisas
numa olhada". A correção foi trocar lista por **tabela**, que ocupa a largura em vez da altura,
e mandar o detalhe longo para um bloco `<details>` recolhido.

Três cuidados que só aparecem quando se monta tabela por script:

**Pipe em célula quebra a tabela.** O título de um dia do diário tem a forma
`DEM_X | assunto | STATUS`, e sem escapar isso vira coluna a mais e a tabela inteira desalinha,
sem erro nenhum. Toda célula passa por uma função que escapa e trunca.

**Recorte precisa de diversidade, não só de ordenação.** Ordenar as esquecidas por tempo parado
e cortar as 8 primeiras devolveu 8 filhas do mesmo épico, todas com a mesma idade: a seção
dizia que havia buracos, mas não onde. Com teto de duas por frente, as mesmas 8 linhas passam
a cobrir quatro frentes.

**Título do documento vale mais que nome de pasta.** O slug da pasta some nas tarefas filhas de
épico (`DEM_APP-002.01` não tem descrição no nome), e ali a única fonte do assunto é o `# ` de
dentro do `solicitacao.md`.

**Detalhe recolhido pede callout do Obsidian, não `<details>` de HTML.** Dentro de bloco HTML o
Markdown não é processado, então a tabela sai como texto corrido com barra vertical no meio, e
o efeito piora com a quebra de linha estrita ligada, que cola tudo numa linha só. A forma que
funciona é o callout nativo, `> [!abstract]- Título`, com cada linha da tabela prefixada por
`> `; o hífen depois do tipo é o que faz nascer fechado. Isso amarra o painel ao Obsidian, o
que aqui é aceitável justamente porque ele não versiona e existe para ser lido lá.

## Fica fora do git, e isso importa

O painel é retrato de um instante numa máquina, como o log bruto em `diario/.log/`. Versionar
geraria conflito entre máquinas e ruído de commit a cada sessão, para um arquivo que se
regenera sozinho em segundos. O que atravessa máquinas continua sendo o registro destilado.

Repare que isso o distingue do `gerencial/valor/rollup.md`, que também é derivado mas **é**
versionado. A diferença é a fonte: o rollup deriva de conteúdo estável (os blocos de valor
dentro das demandas fechadas) e muda pouco; o painel deriva de estado momentâneo e muda toda
sessão. Derivado não decide sozinho se versiona; quem decide é a volatilidade da fonte.

## O que isso exige de quem escrever painel parecido

O hook não pode quebrar a sessão. A geração do arquivo fica em `try/except` mudo: se falhar,
a sessão abre normalmente e só o painel não sai. Vale para todo efeito colateral pendurado em
hook, porque o trabalho do usuário nunca pode depender do enfeite.
