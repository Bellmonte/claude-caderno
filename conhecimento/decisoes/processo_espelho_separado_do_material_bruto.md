# Espelho de ambiente é pasta própria, e não um canto de `local/`

**Problema.** O espelho dos ambientes morava em `local/espelho-ambiente/`, e o runbook prometia
que o Claude leria dali para propor ajuste. Só que o `.claude/settings.json` nega
`Read(local/**)`, então **o desenho nunca pôde funcionar**: quem deveria ler o espelho estava
proibido de abrir a pasta. A contradição só apareceu quando o espelho de um segundo ambiente
nasceu no mesmo lugar e o primeiro `cat` foi barrado.

## Decisão

Espelho sai de `local/` e vira `espelho/` na raiz, com uma pasta por ambiente (por exemplo
`automacao/`, `banco/`, `notebooks/`). Fora do git, como antes, mas **legível**.

As duas pastas parecem iguais e são opostas, e é isso que justifica regra diferente:

| | `local/` | `espelho/` |
|---|---|---|
| O que guarda | material bruto recebido: planilha do solicitante, extração, print, PDF | cópia de leitura do ambiente, exportada por script |
| Segredo | como veio, sem tratamento | como está no ambiente; redigir é opção do exportador, para cópia que sai da máquina |
| Claude lê? | **não**, e a regra de permissão garante | **sim**, é o propósito |
| Regenerável | não, é o original | sim, em minutos |

Manter as duas sob a mesma regra obrigava a escolher entre bloquear o que é sensível e
habilitar o que é de trabalho. Separando, cada uma fica com a regra que merece: `local/`
segue negada, `espelho/` fica aberta.

## A escrita continua sendo por arquivo

Separar leitura não afrouxa escrita. O ajuste proposto vai para `proposto/` **dentro da
demanda** que o gerou, versionado junto do contexto que o explica, e quem importa no ambiente
continua sendo o humano. Nenhum script escreve, publica, ativa ou executa.

O `proposto/` mora na demanda e não numa pasta global de propostas porque um arquivo de fluxo
sem a demanda ao lado não diz por que existe, e é o porquê que se perde primeiro.

## A régua é sobre sair, e não sobre ver

O espelho sai **fiel**, com segredo como está no ambiente, e a redação fica como opção do
exportador para quando a cópia precisar sair da máquina.

Redigir por padrão estaria errado por dois motivos. O prático: um ambiente local controlado
onde o operador não pode nem ler o que existe trava o trabalho e obriga a rotacionar
credencial por nada. O de fundo, mais importante: **espelho redigido esconde exatamente o
problema que se quer achar**. Credencial digitada direto num fluxo é achado de auditoria; com
o valor trocado por marcador, ela some do radar.

O que protege é fechar a saída, e a saída já está fechada em três camadas: a pasta fora do
git, a trava em `.githooks/pre-commit` que barra segredo literal no staged, e a régua do
`CLAUDE.md` que proíbe citar valor em resposta, documento ou commit, mascarando sempre
(`Client-Token: <SECRET>`). Segurança que depende de o operador não ver nada impede o trabalho
e não impede o vazamento.

Onde a responsabilidade fica: **quem decide o que entra na máquina é o usuário; o que não pode
sair dela é regra do sistema.**

## O que uma exportação real ensina sobre redação

Quem escrever um exportador com opção de redigir vai esbarrar nas mesmas três armadilhas.

**Redator que olha só o nome da chave não cobre par `{name, value}`.** Muitas ferramentas de
automação gravam header, query e campo de formulário assim: a chave é literalmente `value`, e
o nome sensível está no **irmão**. Um header `Client-Token` passa inteiro. O conserto é
correlacionar: ao encontrar um objeto com `name` e `value`, decidir pelo `name`.

**Vocabulário de segredo envelhece com o ambiente.** Sempre sobra uma chave que não estava na
lista (um `appkey`, por exemplo). A régua prática: **audite o resultado da exportação**, sem
confiar só no redator. Contar quantos `<SECRET>` foram plantados e varrer o que sobrou com
cara de credencial (JWT, `sk-`, hex longo) leva segundos.

**Nem todo hex longo é segredo.** Identificador de conversa ou de registro não dá acesso;
credencial dá. Redigir identificador tornaria o espelho inútil para entender o fluxo.

Como montar e repovoar o espelho está em `espelho/LEIA-ME.md`.
