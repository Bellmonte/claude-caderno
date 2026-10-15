# claude-caderno

Um sistema de trabalho com Claude Code para quem vive de demanda: chamado, task de sprint,
projeto de BI, incidente. Ele conduz cada demanda do pedido até a entrega, registra sozinho o que
foi feito, guarda o que se aprendeu e mostra o que aquilo valeu. Tudo mora num repositório git que
também é um cofre Obsidian, e as ferramentas (skills, agentes e hooks) vêm junto em `.claude/`.
Trocar de máquina é clonar.

Nasceu do uso diário de um analista de dados ao longo de centenas de demandas reais, e foi
generalizado para servir a qualquer pessoa ou time.

## O problema

Com o Claude Code, construir ficou rápido. O que continua lento é o resto: entender direito o
pedido antes de começar, saber quando parar para validar, documentar na medida certa, lembrar o
que foi feito na semana para a daily e para o gestor, e não aprender a mesma lição duas vezes. Sem
um método, cada sessão começa do zero e cada demanda é documentada de um jeito.

## O que ele faz

**Conduz a demanda por uma esteira com dois portões.** A abertura passa o pedido por sete sinais
objetivos e escolhe o trilho. A análise confronta o pedido com a realidade técnica e para no
primeiro portão antes de qualquer construção. A validação no ambiente real é o segundo portão,
antes de fechar.

```
abrir-demanda → analisar-especificacao [GATE 1] → frente de desenvolvimento → auditor
             → validação [GATE 2] → fechar-demanda → capturar-conhecimento + capturar-valor → publicar
```

**Documenta na proporção do trabalho.** O trilho é escolhido na abertura, com o motivo à vista:

| Trilho | Quando | Documentos |
|---|---|---|
| DIRETO | já chegou resolvido, ou ajuste trivial | `solicitacao.md` → `fechamento.md` |
| CURTO | o padrão: até um sinal aceso na triagem | `solicitacao.md` → `contexto.md` → `fechamento.md` |
| LONGO | dois ou mais sinais: épico, greenfield, multi-frente, homologação | `solicitacao` → `contexto` → `plano` → filhas → `entrega` → `documentacao` → `valor` |
| INCIDENTE | quebra não planejada | `solicitacao` (relato) → `contexto` (causa raiz) → `fechamento` (estabilização e prevenção) |

**Registra sem ninguém lembrar.** Os hooks gravam cada escrita de arquivo num log diário, cobram a
narrativa do dia antes de a sessão terminar e põem na mesa, ao abrir, o que está aberto e o que
ficou sem registro. A daily e a semanal são derivadas desse log, e por isso saem completas mesmo
depois de dias sem ninguém rodar nada.

| Hook | Quando | O que faz |
|---|---|---|
| `log_acao.py` | a cada escrita de arquivo | grava em `diario/.log/AAAA-MM-DD.jsonl`, com etapa e demanda |
| `cobrar_diario.py` | ao encerrar a sessão | não deixa terminar com trabalho feito e diário vazio |
| `abrir_dia.py` | ao abrir a sessão | mostra demandas abertas, esperas e dias sem narrativa |
| `guarda_instrucao.py` | ao encerrar cada resposta | segura a resposta que repete um pedido já atendido |

**Aprende e mede.** Todo fechamento passa o aprendizado reaproveitável para o baú
(`conhecimento/`), acrescenta uma linha no prontuário do objeto tocado (`gerencial/objetos/`) e
registra o valor entregue. O prontuário mostra o que nenhum registro por chamado enxerga:
retrabalho, tempo de homologação, histórico de devolutiva de cada dashboard ou aplicação.

**Fala com o negócio.** O documento de fechamento é escrito para o solicitante, sem nome de objeto
técnico. O técnico fica nos arquivos internos da demanda.

## Começar

**Pré-requisitos:** [Claude Code](https://code.claude.com), Git e Python 3 no PATH (os hooks são
scripts Python). Opcional: [Obsidian](https://obsidian.md) com o plugin Dataview, para o painel.

**1. Crie o seu repositório a partir deste.** Use o botão **Use this template** no GitHub, ou clone
e aponte para um repositório seu, de preferência privado, porque é ali que o seu trabalho vai
morar:

```bash
git clone https://github.com/Bellmonte/claude-caderno.git meu-caderno
```

**2. Ligue a trava de segredo.** O `core.hooksPath` é configuração local e não vem no clone:

```bash
git config core.hooksPath .githooks
```

**3. Copie a persona global.** Edite `conhecimento/modelos/CLAUDE-global.md` com o seu nome e o seu
jeito de trabalhar, e copie para `~/.claude/CLAUDE.md`. Ela vale em todo projeto; o `CLAUDE.md`
da raiz vale só aqui.

**4. Conte ao caderno onde você está.** Preencha `contexto/empresa.md`, `stack.md`, `metodo.md` e
`glossario.md`. Pode ser aos poucos: o caderno usa o que estiver lá.

**5. (Opcional) Aponte o repositório de código.** Se o trabalho acontece em outro repositório
(dashboards, aplicação), defina a variável `CADERNO_REPO_TRABALHO` com o caminho dele, e o log
passa a cobrir os dois.

**6. Abra a primeira demanda.** Na raiz do caderno:

```bash
claude
```

e peça `/abrir-demanda` colando o texto do chamado. O resto da esteira segue dali. Um exemplo de
demanda completa, do pedido ao fechamento, está em [`exemplos/`](exemplos/).

O passo a passo para uma segunda máquina está em
[`conhecimento/runbooks/processo_instalar_maquina_nova.md`](conhecimento/runbooks/processo_instalar_maquina_nova.md),
e o guia de uso pelo terminal em
[`conhecimento/runbooks/infra_claude_code_pelo_terminal.md`](conhecimento/runbooks/infra_claude_code_pelo_terminal.md).

## Skills

**Núcleo**, para qualquer stack:

| Skill | Para |
|---|---|
| `abrir-demanda` | criar a pasta, gravar o SLA e decidir o trilho |
| `analisar-especificacao` | confrontar o pedido com a realidade técnica (GATE 1) |
| `fechar-demanda` | fechamento no peso do trilho, prontuário do objeto, captura de conhecimento e valor |
| `capturar-conhecimento` | destilar o aprendizado para o baú |
| `capturar-valor` | registrar o valor entregue e atualizar o consolidado |
| `publicar` | commit e push revisados, com a lista de arquivos antes |
| `registrar-incidente` | transformar uma quebra em registro rastreável e aprendizado |
| `reconciliar-bases` | isolar as linhas que fazem duas bases não baterem |
| `ata-reuniao` | ata a partir de transcrição, com o conhecimento extraído |
| `gerar-mockup-validacao` | mockup HTML para validar uma solução visual ou estrutural |
| `reporte-dia` | a daily, derivada do log e do diário |
| `reporte-semana` | a one-page da semana em PDF, com o e-mail para o gestor |
| `planejar-semana` | o calendário da próxima semana, equilibrando as frentes |

**Frentes opcionais.** Quem não trabalha com elas apaga as pastas, e o núcleo segue igual:

| Frente | Skills | Auditor |
|---|---|---|
| Power BI | `modelagem-dados` · `medidas-dax` · `montar-visuais` · `legibilidade-ia` · `auditar-performance` | `auditor-pbi` |
| Aplicação | `desenvolver-app` · `validar-tela` | `auditor-app` |

Para tirar a frente Power BI, apague as cinco skills, o `auditor-pbi`, os padrões dela em
`conhecimento/padroes/` e os hooks `valida_pbir.py` e `valida_formatacao.py` do
`.claude/settings.json`. Frente nova (SQL, automação, engenharia de dados) segue o mesmo desenho:
uma skill por etapa, um auditor somente leitura e um padrão.

## Estrutura

```
.claude/          skills, agentes, hooks, scripts e settings, versionados
CLAUDE.md         as regras do sistema: trilhos, esteira, convenções, segurança
demandas/         o trabalho, uma pasta por demanda, agrupada por gaveta de tipo
diario/           a narrativa do dia; .log/ é o registro bruto automático, fora do git
conhecimento/     o segundo cérebro
  padroes/          a lei: SLA, DAX, visual, aplicação, prompt de agente
  modelos/          os formatos: fechamento, prontuário, reporte, template de demanda
  runbooks/         como fazer
  decisoes/         por que foi assim
  referencias/      apoio
gerencial/        dia/ · semana/ · objetos/ · valor/ · reunioes/ · desempenho/
contexto/         empresa, glossário, stack, método
local/            material bruto recebido. Fora do git, e o Claude não lê
espelho/          cópia de leitura dos ambientes. Fora do git
sistema/          o painel do Obsidian
exemplos/         uma demanda completa, para ver o sistema funcionando
```

## Obsidian

O caderno é um cofre válido: basta abrir a pasta no Obsidian. A configuração vem versionada em
`.obsidian/`, junto com um plugin próprio de navegação. O painel `Início` usa o Dataview com
JavaScript Queries ligado. Nenhuma skill depende do Obsidian.

## Segurança

Segredo, chave e dado bruto nunca entram em arquivo versionado. Extração, planilha recebida,
export de ambiente e credencial vivem em `local/`, que o `.gitignore` cobre e que o Claude é
proibido de ler. A trava em `.githooks/pre-commit` barra commit com cara de segredo. Detalhe em
[SECURITY.md](SECURITY.md) e no [CLAUDE.md](CLAUDE.md).

## Projetos relacionados

O [claude-worklog](https://github.com/natanaeloliver/claude-worklog) parte da mesma ideia por
outro ângulo. Ele resolve a mecânica de sessão para um time: injeta o contexto da demanda ativa,
trabalha com vários repositórios e várias janelas e se recupera de queda de terminal. O
claude-caderno resolve o método: como conduzir, documentar, aprender e prestar contas. Os dois
convivem bem.

## Licença

[MIT](LICENSE)
