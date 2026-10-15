# Hook PostToolUse não enxerga escrita feita por shell

**Sintoma.** O hook de log registra as ações do dia, mas o dia aparece vazio ou incompleto, e o
hook de cobrança pede narrativa de um diário que **já foi escrito**. Foi descoberto pelo próprio
hook, cobrando um registro que existia.

**Causa.** O `matcher` do `PostToolUse` casa por nome de ferramenta. Um matcher como
`Write|Edit|MultiEdit|NotebookEdit` cobre só as ferramentas de edição. Toda escrita que passa
pelo shell fica invisível: `cat >> arquivo`, `sed -i`, `tee`, `cp`, `mv`, redireção em geral.

Isso morde com força quando a sessão roda em modo automático, porque esse modo **instrui a
preferir o Bash** para ler e editar arquivo. Ou seja, justamente na configuração em que mais se
usa shell, o log captura menos.

## Correção, em duas frentes

**1. O log passa a observar o shell também.** Acrescente `Bash` (e `PowerShell`, se usar) ao
matcher e extraia os alvos do texto do comando. A extração precisa ser conservadora: só
caminhos com extensão conhecida, descartando `/dev/`, `/tmp/` e qualquer coisa com `$` não
resolvido, e confirmando que o arquivo existe antes de registrar. Prefira perder uma escrita a
poluir o log com falso positivo. Padrões que cobrem quase tudo:

```
>>?\s*['\"]?([^\s'\"|;&>]+)                          redirecao
\bsed\s+-i[^\s]*\s+(?:-e\s+[^\s]+\s+)*['\"]?([^\s'\"|;&]+)
\btee\s+(?:-a\s+)?['\"]?([^\s'\"|;&]+)
\b(?:cp|mv)\s+(?:-\w+\s+)*[^\s]+\s+['\"]?([^\s'\"|;&]+)
```

**2. Quem verifica não confia só no log.** A pergunta "este arquivo foi escrito hoje?" tem uma
resposta que não depende de por onde a escrita veio: o **mtime**. Um hook `Stop` que checa
presença de registro deve olhar o mtime do arquivo, e usar o log apenas para saber *quanto*
trabalho houve. Log é evidência de atividade; mtime é evidência de existência.

## Regra geral

Todo hook que decide alguma coisa a partir do log carrega a premissa de que o log é completo.
Antes de confiar nele para uma decisão, pergunte por quais caminhos o fato pode acontecer sem
passar pela ferramenta observada. Quando existir um sinal do sistema de arquivos que responda
a mesma pergunta, prefira o sinal.

## Teste que pega isso

Simule um payload de `Bash` com `cat >> diario/<hoje>.md`, rode o hook e confira que a linha
entrou no `.jsonl`. Lembre que `CLAUDE_PROJECT_DIR` precisa estar em caminho Windows
(`C:\...`), porque com caminho MSYS (`/c/...`) o Python grava em outro lugar e o teste passa
sem gravar nada onde você está olhando.

## Atualização: extração por texto precisa de confirmação por mtime

A extração conservadora resolveu a captura, mas trouxe o defeito espelhado. Quando o padrão
passou a cobrir escrita por script Python embutido (`io.open("x","w")`), o hook começou a
registrar arquivo que o comando apenas **mencionava**, porque um heredoc de teste, um exemplo
de código ou um script que se escreve a si mesmo contém a mesma string sem executar nada. O
primeiro falso positivo apareceu em menos de uma hora de uso.

A regra que ficou: **o texto do comando levanta candidato, o mtime confirma.** Antes de gravar
a linha, o hook compara `time.time()` com `os.path.getmtime()` do alvo e descarta o que não foi
tocado nos últimos 90 segundos. Custa uma chamada de sistema por candidato, não exige varrer o
repositório, e mata a classe inteira de falso positivo, inclusive a que já existia no padrão de
redirecionamento.

O que continua de fora, de propósito: escrita cujo caminho vive numa variável
(`io.open(p,'w')`), porque aí não há string literal para extrair. Prefere-se perder essa a
poluir o log, e a alternativa de varrer o caderno inteiro por mtime a cada comando não paga o
custo em disco sincronizado por serviço de nuvem. O caso está registrado em
[[log_automatico_nao_ve_escrita_por_script]].

