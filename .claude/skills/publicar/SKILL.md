---
name: publicar
description: Commita e dá push do que foi feito, no repositório de código e no caderno, e gera o resumo do commit que alimenta o fechamento. Cobre o modo padrão (push direto) e o modo APP (branch e PR, com poda de galho seco). Use depois da validação, no fechamento do desenvolvimento.
---

# Skill: publicar (fechamento do desenvolvimento)

Roda **depois** da validação (GATE 2). Antes disso, não comita.

O caderno versiona as próprias ferramentas em `.claude/`, então publicar o caderno publica
skill, agente, hook e settings junto, no mesmo commit. Não há espelho a fazer em pasta nenhuma.

## Dois modos

**Modo padrão** (PBI, dados, sql, caderno): commit e push direto no branch de trabalho.

**Modo APP** (repositório da aplicação): a `main` é protegida e exige Pull Request (push direto
é bloqueado com `GH013`). Commita em branch, abre PR para a `main`. O código vai no repositório
da aplicação e o registro vai no caderno, em **commits separados**, sempre. Identifique a frente pelo
`contexto.md`.

## O escopo do commit: a sessão, e o projeto inteiro

Duas réguas, e elas são diferentes de propósito.

**No projeto Power BI, sobe a pasta do projeto inteira.** Não os arquivos que eu toquei, não os
arquivos da demanda: a pasta do `.pbip` em que a sessão trabalhou, com tudo que estiver alterado
dentro dela. Se o usuário mexeu na mão em algo que eu não sei o que é, sobe junto. Um projeto
Power BI é um artefato único, com modelo e relatório amarrados, e subir metade dele deixa o
repositório num estado que não abre igual à máquina de quem trabalhou.

**Fora dele, sobe o que a sessão produziu.** No caderno e nos demais repositórios, o critério é
autoria da sessão: registro que esta sessão escreveu entra, pasta de demanda que apareceu no
diretório vinda de outra sessão fica.

**O que roda em paralelo não é problema meu.** O usuário pode trabalhar em vários dashboards ao
mesmo tempo, em sessões diferentes. Projeto que esta sessão não tocou fica de fora do commit inteiro, sem
comentário e sem pergunta. Não existe "avisar que tem outras alterações pendentes": cada sessão
cuida do seu projeto e as outras se viram.

**A contrapartida da regra é a varredura.** Subir arquivo que eu não escrevi significa publicar
mudança que eu não conferi, então a leitura antes do commit fica mais importante, e não menos.
Continua valendo `git add` do caminho explícito (a pasta do projeto, nunca `-A`), listar o que
ficou staged, e farejar segredo e dado bruto no diff inteiro, inclusive na parte que veio da mão
do usuário. Achou algo com cara de credencial no que não foi você que escreveu, pare e pergunte
antes de subir.

## Fluxo, modo padrão

1. `git status`. Mostre os arquivos alterados e confirme antes de commitar. **Nunca
   `git add -A` cego**, e sempre fareje cara de segredo ou dado bruto.
2. Monte a mensagem no formato abaixo.
3. Commit e push.
4. Gere o **resumo do commit** (tipo, o que mudou por objeto, short-hash) e grave no
   `entrega.md` da demanda, ou anexe ao que já existir.

## Fluxo, modo APP

1. Confirme que está no repositório da aplicação e que o GATE 2 passou (validação local mais
   parecer do `auditor-app`).
2. Rode a suíte de teste do backend (por exemplo em `server/`). **Gate:** vermelho, para tudo,
   não commita, reporta o que falhou. Se o `npm test` usar um glob que não expande no Git Bash,
   rode `node --test` direto na pasta do backend.
3. `git status`, mostre, confirme. Deixe de fora o que não é da tarefa (por exemplo
   `.claude/settings.local.json`).
4. Commit do **código** com `git add` explícito. Depois `git switch -c feat/<demanda>-<slug>`,
   `git push -u origin <branch>` e abra o PR para a `main`. Sem o `gh` instalado, use a URL que
   o push imprime, ou peça ao usuário (o merge é dele). Deixe a `main` local igual à
   remota com `git branch -f main origin/main`.
5. Commit do **registro** no caderno, à parte. Nunca misture código e registro.
6. Gere o resumo (tipo, o que mudou, short-hash, branch e link do PR) e grave no `entrega.md`.
   O status fica `Em PR (aguardando aprovação)` até o merge.
7. **Pode os galhos secos** das demandas anteriores. Ver abaixo.

## Fechamento do galho (higiene de branch, modo APP)

Depois que o PR é mesclado, o galho vira galho seco e só polui a lista. O alvo é sobrar `main`,
mais o branch compartilhado do time (aqui chamado `develop`; troque pelo nome que o seu time usa),
mais no máximo o galho da demanda em curso.

1. `git fetch --prune`.
2. Atualize a main sem sair do galho atual: `git branch -f main origin/main`.
3. `git branch --merged origin/main`.
4. Para cada branch dessa lista que não seja `main`, `develop` nem o galho atual:
   `git branch -d <nome>` e `git push origin --delete <nome>`.
5. `git branch` para conferir.

Regras duras, inegociáveis: nunca apague `main` nem `develop`; nunca use `git branch -D` na
poda (só `-d`, que se recusa a apagar galho não mesclado, e essa é a rede de segurança);
nunca apague galho cujo PR não foi mesclado. A poda mexe só em branch, o working tree fica
intacto.

## Formato da mensagem

```
<tipo>: <COD> [<chamado vinculado>] <descrição curta>

<resumo em linguagem de negócio, o que mudou na ótica de quem pediu>
- <ponto 1>
- <ponto 2>
```

**Título:** conventional commits (`feat|fix|refactor|style|docs|chore|verif`), coerente com a
classificação da demanda, com o código do chamado, e curto o bastante para caber numa linha.
Sem código de chamado, use o código da demanda ou o marco do cronograma.

**Corpo:** dois a quatro bullets em linguagem de negócio, dizendo o efeito para quem pediu e
não a mecânica de código. "Slicer Grupo Economico agora exibe codigo e nome completos sem
corte" funciona; "ajustei a largura do visual no JSON" não. Frases curtas, sem floreio.
Demanda trivial pode ter corpo de uma linha.

O corpo do commit e o resumo do `entrega.md` contam a mesma história, um é a versão curta do
outro. O `fechar-demanda` consome isso depois.

Quando o commit levar junto ajuste manual do usuário que você não sabe descrever, não invente
efeito de negócio para ele nem finja que não está ali. Uma linha basta: "inclui ajustes manuais
feitos no projeto fora desta demanda".

## Publicar o caderno

Mesmo fluxo do modo padrão, na raiz do caderno. O que muda é o cuidado: liste os arquivos,
fareje segredo e dado bruto, e confirme que nada de `local/` entrou. Como `.claude/` é
versionado, skill ou hook que você mexeu nesta sessão sobe junto e chega na outra máquina no
próximo `git pull`.

## Segurança

- A trava de segredo do repositório age no commit. Bloqueou, pare e avise. Não use
  `--no-verify` sem decisão consciente do usuário.
- Não toque em GUID, connection string nem dataSource.
- Corpo do commit em ASCII, sem acento, por compatibilidade de terminal no Windows.
- Nunca adicione trailer de coautoria nem linha de geração automática.
