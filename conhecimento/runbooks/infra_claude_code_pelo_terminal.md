# Claude Code pelo terminal: roteiro do infográfico

> Guia de bolso para trocar a interface gráfica pelo terminal sem perder nada do caderno.
> O arquivo tem duas partes: o **conteúdo** de cada bloco do infográfico e, no fim, a
> **direção de arte** e o prompt pronto para gerar a peça. Relacionado:
> [[obsidian_uso_no_dia_a_dia]] · [[processo_instalar_maquina_nova]].

---

## Parte 1 · Conteúdo, bloco a bloco

O infográfico lê de cima para baixo em sete blocos. Cada um traz o título que aparece na peça,
o texto e a sugestão de ícone.

### Bloco 1 · Cabeçalho

- **Título:** Claude Code no terminal
- **Subtítulo:** o mesmo caderno, as mesmas skills e os mesmos hooks, sem a janela do app
- **Faixa de destaque:** tudo que mora em `.claude/` (skills, agentes, hooks, permissões)
  funciona igual no terminal, porque vem do repositório e não do aplicativo.

### Bloco 2 · Preparar a máquina (uma vez só)

| Passo | O que fazer | Comando |
|---|---|---|
| 1 | Instalar o CLI, se ainda não estiver no PATH | `irm https://claude.ai/install.ps1 \| iex` |
| 2 | Conferir a instalação | `claude --version` e depois `claude doctor` |
| 3 | Entrar com a conta | `claude` e seguir o login no navegador |
| 4 | Usar o **Windows Terminal**, com perfil PowerShell ou Git Bash | |
| 5 | Religar o MCP do Power BI, se ele só existir na config do app | `claude mcp add powerbi-modeling-mcp --scope user -- "<caminho da extensão>\server\powerbi-modeling-mcp.exe" --start` |
| 6 | Conferir os MCPs | `claude mcp list` (MCP declarado num `.mcp.json` do repositório vem sozinho) |
| 7 | Ligar o Chrome para o `validar-tela` | extensão Claude in Chrome instalada, depois `/chrome` dentro da sessão |

Ícone sugerido: chave inglesa.

### Bloco 3 · O dia começa assim

Uma linha do tempo horizontal com cinco paradas:

1. **Abrir o terminal na raiz do caderno.** `cd <caminho>\claude-caderno`
2. **Puxar o caderno.** `git pull --ff-only`. Se der conflito, parar e olhar.
3. **Subir a sessão.** `claude` (nova) ou `claude -c` (continua a última). O hook
   `abrir_dia.py` já mostra as demandas abertas, as que esperam terceiro e o dia sem narrativa.
4. **Daily.** `/reporte-dia` devolve o bloco pronto para o WhatsApp.
5. **Trabalho do dia.** Uma sessão por demanda, nomeada com `/rename DEM_TSK-101`, para
   achar depois no `claude -r`.

Ícone sugerido: nascer do sol.

### Bloco 4 · A esteira vira comando

O desenho é a esteira em setas, cada etapa com o comando embaixo.

| Etapa | Comando no terminal |
|---|---|
| Abrir | `/abrir-demanda` + colar o texto do chamado (print com **Alt+V**) |
| Entender | `/analisar-especificacao` (GATE 1) |
| Construir | `/modelagem-dados` · `/medidas-dax` · `/montar-visuais` · `/desenvolver-app` |
| Validar | `/validar-tela` (APP, via Chrome) · Desktop do Power BI (PBI) |
| Fechar | `/fechar-demanda` |
| Publicar | `/publicar` |
| Sexta | `/reporte-semana`, que já encadeia o `/planejar-semana` |

Fora da esteira: `/registrar-incidente`, `/ata-reuniao`, `/reconciliar-bases`.

Dica de canto: quando o trabalho envolver o repositório de código, abrir com
`claude --add-dir <caminho do repositório>` ou usar `/add-dir` no meio da sessão. Com a variável
`CADERNO_REPO_TRABALHO` apontando para ele, o `log_acao.py` registra os dois repositórios do
mesmo jeito.

### Bloco 5 · Atalhos que valem decorar

Grade de cartões, tecla grande e legenda curta.

| Tecla | O que faz |
|---|---|
| **Esc** | interrompe o Claude no meio, sem perder a conversa |
| **Esc Esc** | volta a uma mensagem anterior e desfaz as edições de arquivo feitas depois dela |
| **Shift+Tab** | alterna o modo: normal → aceita edições → plano |
| **@** | cita um arquivo (`@demandas/TSK_tasks-sprint/...`) com autocompletar |
| **/** | lista comandos e skills |
| **!** | roda um comando de shell direto, sem passar pelo Claude (`!git status`) |
| **Alt+V** | cola imagem (print de tela, erro do Desktop) |
| **Ctrl+J** ou **\\ + Enter** | quebra linha sem enviar |
| **Seta ↑** | repete o que foi digitado antes |
| **Ctrl+R** | busca no histórico de mensagens |
| **Ctrl+O** | mostra o detalhe do que o Claude executou |
| **Ctrl+T** | mostra a lista de tarefas da sessão |
| **Ctrl+B** | manda um comando demorado para segundo plano |
| **Ctrl+G** | abre o texto no editor externo, bom para colar chamado grande |
| **Ctrl+C** duas vezes | sai da sessão |

### Bloco 6 · Comandos de sessão

Duas colunas: fora da sessão e dentro dela.

**Na linha de comando**

| Comando | Para que serve |
|---|---|
| `claude` | sessão nova na pasta atual |
| `claude -c` | continua a última conversa desta pasta |
| `claude -r` | escolhe uma conversa antiga para retomar |
| `claude -p "pergunta"` | resposta avulsa, sem abrir sessão |
| `claude --model opus` | escolhe o modelo já na entrada |
| `claude update` | atualiza o CLI |

**Dentro da sessão**

| Comando | Para que serve |
|---|---|
| `/clear` | zera a conversa ao trocar de demanda |
| `/compact` | resume a conversa quando ela fica longa, mantendo o fio |
| `/context` | mostra quanto da janela de contexto já foi usado |
| `/usage` | consumo e limites do plano |
| `/model` | troca o modelo |
| `/resume` · `/rename` | retoma e nomeia sessões |
| `/rewind` | mesmo efeito do Esc Esc |
| `/mcp` | estado dos servidores MCP conectados |
| `/permissions` · `/hooks` | confere as regras que vêm do `settings.json` |
| `/memory` | abre o CLAUDE.md e a memória |
| `/export` | salva a conversa em arquivo |
| `/terminal-setup` | ajusta o Shift+Enter no terminal |
| `/statusline` | põe modelo, pasta e galho no rodapé |
| `/doctor` | diagnóstico quando algo não sobe |

### Bloco 7 · Cuidados

Faixa em tom de alerta, seis itens curtos.

1. **O painel do app não existe aqui.** Sem Browser pane, sem aba de diff, sem painel de
   artifacts. Diff se vê com `!git diff`, tela da aplicação se valida no Chrome real com
   `/chrome`, que era a regra para popup de qualquer jeito.
2. **O modo de permissão aparece no rodapé.** Conferir antes de pedir algo grande. Plano
   para pensar, normal para mexer em ambiente, aceitar edições só dentro do caderno. Nunca
   `--dangerously-skip-permissions`.
3. **O Esc Esc desfaz arquivo e deixa o ambiente como está.** Escrita em ferramenta externa,
   publicação, commit e push ficam feitos. Por isso mudança em ambiente continua passando pelo
   humano.
4. **Os hooks seguem ligados.** O `cobrar_diario.py` vai segurar o fim da sessão se o diário
   estiver vazio, igual ao app. O `guarda_instrucao.py` e o `valida_pbir.py` também.
5. **`local/` continua fechada** e segredo não sai em resposta. A regra vem do repositório,
   então vale no terminal sem configurar nada.
6. **Uma sessão por demanda.** Trocar de assunto no meio mistura contexto e o log. Nova
   demanda, `/clear` ou terminal novo.

### Rodapé

"Mudou algo no fluxo? A fonte é este arquivo no caderno."
Data da versão: <DD-MM-AAAA>.

---

## Parte 2 · Direção de arte

- **Formato:** vertical, 1080 × 3000 px, pensado para abrir no celular e imprimir em A4
  dividido em duas páginas.
- **Leitura:** um bloco por faixa, com respiro entre eles; o bloco 5 (atalhos) é o maior e
  o mais visual, porque é o que se consulta de verdade.
- **Paleta:** fundo escuro de terminal (#0F1115), texto claro (#E6E6E6), destaque em verde
  de prompt (#3FB950) para comandos, âmbar (#D29922) só no bloco de cuidados.
- **Tipografia:** comandos e teclas em monoespaçada (JetBrains Mono ou Cascadia Code), texto
  corrido em sans (Inter). Tecla desenhada como capa de teclado, com borda e sombra leve.
- **Ícones:** traço fino, uma cor, um por bloco.
- **Nada de** foto, mascote ou gradiente chamativo. A peça precisa parecer ferramenta.

## Parte 3 · Prompt pronto para gerar

Cole na ferramenta de geração junto com a Parte 1 inteira:

> Monte um infográfico vertical (1080 × 3000 px), em português do Brasil com acentuação
> correta, chamado "Claude Code no terminal". Use exatamente o conteúdo dos sete blocos abaixo,
> na ordem, sem inventar comando nem atalho. Estilo de terminal: fundo #0F1115, texto #E6E6E6,
> comandos em verde #3FB950 e fonte monoespaçada, bloco de cuidados em âmbar #D29922. Teclas
> desenhadas como capas de teclado. O bloco de atalhos é o destaque visual, em grade de
> cartões. O bloco da esteira vira uma sequência de setas com o comando sob cada etapa. Ícones
> de traço fino, uma cor. Sem fotos, sem mascote. Entregue em HTML autocontido pronto para
> exportar em PNG e PDF.
