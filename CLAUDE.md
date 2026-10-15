# claude-caderno · assistente de trabalho

> Carregado em toda sessão aberta neste repositório. As ferramentas (skills, agentes, hooks,
> settings) vivem em `.claude/` e viajam com o `git clone`: trocar de máquina é clonar.
> A persona e a régua de escrita ficam no `~/.claude/CLAUDE.md` global, porque valem em
> todo projeto (modelo em `conhecimento/modelos/CLAUDE-global.md`). Aqui mora só o que é do trabalho.

## Onde cada coisa mora

| Pasta | O que guarda |
|---|---|
| `demandas/<TIPO>/DEM_<COD>_<slug>/` | o trabalho, uma pasta por demanda |
| `diario/` | a narrativa do dia; `diario/.log/` é o log bruto automático (fora do git) |
| `conhecimento/` | o segundo cérebro: `padroes/` (a lei) · `modelos/` (formatos) · `runbooks/` (como fazer) · `decisoes/` (por quê) · `referencias/` (apoio) |
| `gerencial/` | `dia/` · `semana/` · `objetos/` (prontuário por objeto) · `valor/` · `reunioes/` · `desempenho/` |
| `contexto/` | empresa, glossário, stack, método |
| `local/` | **material bruto recebido** (planilha, extração, print, PDF). Fora do git, e o Claude não lê |
| `espelho/` | cópia de **leitura** dos ambientes, fiel, com segredo como ele está lá. Fora do git, mas legível |
| `.claude/` | skills, agentes, hooks, settings, versionados |
| `sistema/` | a camada de leitura no Obsidian: o painel `Início` e o CSS dele. Não é registro, é interface |

**Regra dura de material local.** Extração, planilha do solicitante, export de ambiente,
credencial, PDF recebido, print, `.zip` de transporte: tudo isso vive em `local/` e só lá.
Nenhuma skill escreve dado bruto fora de `local/`. Quando uma demanda precisar de um arquivo
desses, guarde em `local/<demanda>/` e **referencie o caminho** no registro, nunca o conteúdo.

## Gavetas de demanda

O `<TIPO>` sai do prefixo do código da demanda:

| Prefixo | Gaveta | Uso |
|---|---|---|
| `TSK` | `TSK_tasks-sprint/` | task de sprint ou chamado comum |
| `INC` | `INC_incidentes/` | quebra ou instabilidade não planejada |
| `BI` | `BI_projetos/` | épico ou projeto de BI |
| `APP` | `APP_aplicacao/` | frente de aplicação |

Prefixo novo cria a gaveta `PREFIXO_descricao/` no mesmo padrão. Épico tem filhas numeradas
dentro da própria pasta: `DEM_BI-005/DEM_BI-005.01/`. Quem fecha é a filha; o pai guarda o
plano e o consolidado.

## A instrução do usuário é soberana

Quando o usuário afirma o estado de alguma coisa, isso é fato encerrado. "Já está resolvido",
"já foi corrigido", "está certo", "pode fechar": nenhuma dessas frases abre investigação. Ele
trabalha nesses ambientes o dia inteiro e enxerga o que nenhum arquivo daqui mostra.

O que se faz com uma afirmação dessas é documentar e seguir, sem pedir conferência e sem rodar
consulta para provar. Se alguma coisa lida no caminho contrariar o que ele disse, o lugar disso é
uma linha no `contexto.md`, sem parar a entrega. A régua de conferir ambiente em vez de deduzir
do caderno continua valendo, e ela vale contra o caderno. Contra ele, não.

**Peso da resposta acompanha o peso da tarefa.** Pedido simples fecha com resposta curta: o que
foi feito e onde ficou. Sem recontar o contexto que ele acabou de dar, sem listar hipóteses
descartadas, sem oferecer próximo passo que ninguém pediu.

**Pedido atendido não se repete.** Antes de qualquer tabela de passos, cada linha é cruzada com
o artefato: `ls` na pasta quando for arquivo, espelho sincronizado quando for ambiente. O hook
`guarda_instrucao.py` segura a resposta quando um caminho citado na tabela já existe, e mostra
desde quando.

## Os trilhos

O peso do registro acompanha o tamanho do trabalho. **Quem escolhe o trilho é a triagem, na
abertura**, e o veredito é sempre mostrado com o motivo.

### Triagem (roda no `abrir-demanda`)

Sete sinais, todos verificáveis na entrada:

1. o pedido se quebra em tarefas independentes (vira épico com filhas)
2. toca mais de uma frente (pbi + dados, app + sql, …)
3. tem homologação formal, com rodadas de validação do solicitante
4. depende de terceiro (outra área, fornecedor, TI) para concluir
5. mexe em estrutura: modelo semântico, origem/ETL, banco, pipeline
6. é objeto novo do zero (greenfield)
7. o objeto alvo já tem histórico de retorno de validação em `gerencial/objetos/`

**Nenhum sinal aceso: CURTO. Um sinal: CURTO, com a ressalva dita em voz alta. Dois ou mais:
LONGO.** Quebra ou instabilidade não planejada não passa por aqui: é INCIDENTE. O veredito é uma
proposta. Diga qual trilho e quais sinais acenderam, e siga; se o usuário discordar, troca.

### Trilho DIRETO (a demanda que já chega resolvida, ou o ajuste trivial)

Quando a demanda chega com o trabalho já feito, ou quando o pedido é um ajuste trivial e
reversível (largura de coluna, texto de título, cor, ordem de campo), a triagem não roda. A
demanda nasce e fecha na mesma sessão, com `solicitacao.md` e `fechamento.md`. O `contexto.md`
entra só quando há mecanismo que valha guardar. Sem GATE 1, auditor, conferência em ambiente,
mockup ou captura de conhecimento. Na dúvida entre DIRETO e CURTO, vale o DIRETO: promover
depois custa barato.

### Trilho CURTO (o padrão, e o caso mais frequente)

`solicitacao.md` → `contexto.md` (análise e plano na mesma folha) → `fechamento.md` (o que foi
feito, como, validação, cabeçalho de SLA e o bloco de valor).

### Trilho LONGO (épico, greenfield, multi-frente, homologação)

`solicitacao.md` → `contexto.md` → `plano.md` → filhas, cada uma no trilho curto →
`entrega.md` (com o parecer do auditor da frente) → `documentacao.md` → `valor.md`.

### Trilho INCIDENTE (start próprio)

`solicitacao.md` (o relato como chegou) → `contexto.md` (causa raiz) → `fechamento.md`
(estabilização e o que evita a reincidência). Fecha só quando **estabilizado**, e o aprendizado
vai obrigatoriamente para o baú.

## A esteira

1. `abrir-demanda` cria a pasta, grava o SLA e **decide o trilho**.
2. `analisar-especificacao` confronta o pedido com a realidade técnica. **[GATE 1]**
3. Desenvolvimento, só nas frentes do escopo (ver "Frentes" abaixo).
4. O auditor da frente dá a segunda opinião.
5. Validação no ambiente real. **[GATE 2]** Na frente APP, `validar-tela` percorre no navegador
   o fluxo alterado e deixa a evidência no `entrega.md`.
6. `fechar-demanda` escreve o fechamento e encadeia `capturar-conhecimento` e `capturar-valor`.
7. `publicar` commita, dá push e fecha o galho.

Fluxo curto, sem GATE 1: `reconciliar-bases`, `ata-reuniao`, `registrar-incidente`. O trilho
DIRETO vai de `abrir-demanda` direto para `fechar-demanda` e `publicar`.

## Frentes

O núcleo (esteira, registro, gestão) serve a qualquer stack. As frentes são pacotes opcionais:
quem não trabalha com elas apaga as pastas listadas, e o resto continua funcionando.

| Frente | Skills | Agente | Padrões |
|---|---|---|---|
| Power BI | `modelagem-dados` · `medidas-dax` · `montar-visuais` · `legibilidade-ia` · `auditar-performance` | `auditor-pbi` | `PADRAO_DAX` · `PADRAO_FORMATACAO` · `PADRAO_LEGIBILIDADE_IA` · `PADRAO_PERFORMANCE_PBI` · `PADRAO_VISUAL_DASHBOARDS` |
| Aplicação (APP) | `desenvolver-app` · `validar-tela` | `auditor-app` | `PADRAO_APP` · `PADRAO_PROMPT_AGENTE` |

Frente nova (SQL, automação, engenharia de dados) segue o mesmo desenho: uma skill por etapa de
construção, um auditor somente leitura e um padrão em `conhecimento/padroes/`. A matriz de
roteamento fica em [[ROTEAMENTO_FRENTES]].

## Registro orgânico (o que acontece sem ninguém acionar)

Hooks em `.claude/hooks/`, ligados no `.claude/settings.json`:

- **`log_acao.py`** (PostToolUse) grava toda escrita de arquivo em `diario/.log/AAAA-MM-DD.jsonl`.
  É determinístico: acontece mesmo que a sessão morra no meio. Cobre o caderno e, se a variável
  `CADERNO_REPO_TRABALHO` apontar para ele, o repositório de código onde o trabalho acontece.
  Cada linha carrega `etapa` da esteira e `demanda`. Escrita em `fechamento.md` ou
  `documentacao.md` lê do próprio documento a data em que o trabalho terminou e grava
  `entrega_declarada`, marcando `retroativo` quando ela não é a de hoje. Cada trilho nomeia essa
  data do seu jeito: `Entrega` no chamado, `Encerramento` no incidente e `Data` na frente APP.
- **`cobrar_diario.py`** (Stop) não deixa a sessão terminar com trabalho feito e diário vazio.
  Cobra uma vez por sessão.
- **`abrir_dia.py`** (SessionStart) põe na mesa o que está aberto e que dia ficou sem narrativa.
- **`guarda_instrucao.py`** (Stop) segura a resposta que repete um pedido já atendido.

Por causa disso, **a daily e a semanal são derivadas**. Elas leem o log bruto mais o diário e
saem completas mesmo depois de uma semana sem ninguém acionar nada.

**A régua de leitura do log:** ele registra quando o arquivo foi escrito, e isso responde o que
foi tocado no dia. Para afirmar o que foi **entregue**, vale o campo de entrega do fechamento,
que o log carimba como `entrega_declarada`. Linha com `retroativo` nunca entra na contagem de
entregas do dia.

## Documentação proporcional

O trilho curto fecha em um documento só, e o rastro fino sai de graça do log. A documentação
pesada fica onde ela paga: épico, incidente e entrega com homologação. Formato de cada documento
em `conhecimento/modelos/`; a régua de SLA, complexidade e risco em
`conhecimento/padroes/PADRAO_SLA.md`.

**O fechamento fala com o negócio.** O `fechamento.md` e o `documentacao.md` são os únicos
arquivos da pasta que saem para o solicitante, e o leitor é analista de negócio. Nome de objeto
técnico não entra ali (arquivo, medida, pipeline, notebook, id de dataset). O técnico mora no
`contexto.md`, no `plano.md` e no `entrega.md`, e o que sobrar vira uma linha de rastreio no
rodapé. Tabela de tradução no modelo [[fechamento-chamado]].

## Prontuário do objeto

Chamado é evento; **objeto é o que dura**. Todo fechamento que toca um objeto nomeado (um
dashboard, um agente, um pipeline) acrescenta uma linha em `gerencial/objetos/<objeto>.md`. É
dali que saem retrabalho, tempo de homologação e histórico de devolutiva, que nenhum registro por
chamado consegue enxergar. Formato em `conhecimento/modelos/prontuario-objeto.md`.

## Os dois marcadores de estado

| Arquivo | O que significa | Efeito |
|---|---|---|
| `ARQUIVADO.md` | parada por decisão | sai da contagem de abertas; vale para a pasta e todas as filhas |
| `AGUARDANDO.md` | travada em terceiro | continua aberta, sai da conta de esquecidas e ganha card próprio |

O `AGUARDANDO.md` leva frontmatter com `quem`, `desde` (`AAAA-MM-DD`) e `nota`. Passando de 30
dias, a espera acende em âmbar. Remover o arquivo devolve a demanda ao estado anterior. Marcador
não conta como toque na demanda.

## Convenções

- Saída de documento é markdown salvo no lugar certo do repositório.
- Data em texto: `DD-MM-AAAA`. Data em nome de arquivo e ID: `AAAA-MM-DD`.
- Nome de objeto técnico sem acento. Texto de documento **com** acento.
- Commit em ASCII, título em conventional commits e corpo curto em linguagem de negócio.
- Vínculo entre notas por wikilink `[[nome-da-nota]]`. O caderno é um cofre Obsidian válido.
- Brevidade é o padrão. Curto e consultável vence completo e abandonado.

## Segurança (inegociável)

A régua é sobre o que **sai**: arquivo versionado, push, documento, resposta, mensagem de commit.
Dentro da máquina, ler o que existe é condição para trabalhar. Fora dela, segredo nunca passa.

**Nunca sai daqui:**

- Segredo, chave, token, senha ou connection string. Placeholder: `<TOKEN>`.
- Sugestão gerada para o ambiente (fluxo, notebook, pipeline) com valor lido; sai com placeholder.
- Dado corporativo bruto. Dado pessoal de terceiro é sensível (LGPD): anonimizar antes de registrar.
- Commit sem listar os arquivos staged e sinalizar o que tiver cara de segredo ou dado bruto.
  Nunca `git add -A` cego. A trava em `.githooks/pre-commit` é a rede, não a regra.
- O escopo do commit é a **sessão**. Arquivo que a sessão não escreveu só sobe depois de lido o
  diff. Régua completa na skill `publicar`.

**Pode ler:** `espelho/` sai fiel do ambiente, com segredo, para permitir apontar credencial
hardcoded. É local, fora do git e regenerável. Ao citar algo de lá, mascare sempre
(`Client-Token: <SECRET>`). `local/` é negada por permissão; racional em
[[processo_espelho_separado_do_material_bruto]]. A exceção é `local/performance/`, lida e escrita
pelos scripts de `.claude/scripts/performance/`, que devolvem ao chat só agregados.

## O caderno é a fonte, e ele se lê antes de concluir

- Com remoto configurado, a sessão abre com `git pull --ff-only`. Conflito quer dizer trabalho
  não commitado nesta máquina: parar e mostrar, nunca resolver por cima.
- Nenhuma afirmação sobre uma demanda sai antes de ler o registro dela (`entrega.md`, lista
  mestra de passos, prompt de abertura).
- **Decisão escrita no caderno vale.** Artefato que contraria decisão registrada é defeito, e
  isso se diz com a data e o trecho.
- `local/` e `espelho/` podem estar velhos ou ausentes. Estado de ambiente não se deduz de
  arquivo ausente: peça a saída.
- Caderno e ambiente divergindo, diga qual dos dois está velho e por quê.
