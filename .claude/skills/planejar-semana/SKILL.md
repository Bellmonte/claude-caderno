---
name: planejar-semana
description: Monta o calendario concreto da PROXIMA semana (seg-sex, so uma semana pra frente) distribuindo as demandas em aberto de forma equilibrada, com reserva de dias pra fila de chamados. Le o estado em aberto do caderno ao fim da semana, respeita as dependencias entre tarefas-filhas dos epicos, gira as frentes em vez de afunilar uma so, e grava a grade dia a dia que a reporte-dia consome pra ja oferecer a tarefa planejada do dia. Encadeada no fim da reporte-semana (roda junto), mas tambem serve avulsa. Transversal.
---

> DESTINO: todo arquivo de registro (demandas/, diario/, conhecimento/, gerencial/) e criado na RAIZ DO CADERNO (o repositório do caderno adicionado à sessão), NUNCA no repo de trabalho. Se o caderno nao estiver na sessao, pare e peca para adiciona-lo. Ver CLAUDE.md > "Onde cada coisa mora".

# Skill: planejar-semana (calendario concreto da proxima semana)

## Papel
Transformar o que esta em aberto no caderno num **calendario dia a dia da proxima semana**, equilibrado e realista. E o passo que falta entre o "Foco da proxima semana" que a `reporte-semana` decide (a intencao) e o "Hoje" que a `reporte-dia` monta todo dia (a execucao). A semanal diz pra onde ir; esta skill quebra isso em dias; a daily le a grade e ja parte da tarefa planejada.

**Escopo: so UMA semana pra frente.** Nao monta cronograma longo. Planeja a proxima semana util (seg-sex) e para. A cada sexta o processo se repete com o estado novo, entao o plano longo emerge semana a semana em vez de ser cravado de uma vez.

Irma da `reporte-dia` (que consome a grade) e da `reporte-semana` (que a dispara). So le o caderno e escreve em `gerencial/semana/`; nao mexe em demanda nem cria registro de demanda.

## Argumento (opcional)
- `/planejar-semana` -> planeja a semana seguinte a de hoje (a que comeca na proxima segunda).
- `/planejar-semana AAAA-MM-DD` -> trata esse dia como a semana que FECHA; planeja a seguinte. (E o modo que a reporte-semana usa ao encadear: passa a propria data de referencia.)
- `--fila=N` ou `--fila=seg,qui` -> sobrescreve a reserva de fila (default 2 dias: seg + qui).
- `--prioridade=COD` -> da peso a uma frente no rodizio (ex.: `--prioridade=APP-002` pra fechar a frente da aplicação antes). Sem isso, rodizio parelho.

## Datas
Trabalho e **segunda a sexta**. A partir da referencia:
- **Semana a planejar** = a semana util seguinte. Se a referencia e hoje, e a proxima segunda-a-sexta; se e uma data (modo encadeado), e a semana seguinte a que contem essa data.
- Resolva `SEG` (segunda alvo) e `SEX` (sexta alvo) da semana a planejar.
- **Rotulo humano:** `Semana DD-DD <mes> AAAA` (mesmo padrao da semanal).
- **ID da semana (pasta):** ISO week da segunda alvo -- `date -d <SEG> +%G-W%V` (ex.: `2026-W30`). Git Bash resolve `date -d`.
- **Semana corrente (a que fecha)** = a semana da referencia; o ID dela e `<ID-1>` em relacao a alvo.

## Fontes (sempre na RAIZ DO CADERNO)
1. **`demandas/*/DEM_*/`** -- o estado em aberto, insumo principal:
   - **Aberta vs fechada:** fechada = tem `fechamento.md` ou `documentacao.md` no topo (ou, sendo epico, todas as filhas fechadas mais a doc do epico). Sem isso, esta aberta.
   - **Estagio de cada demanda/filha** (do mais adiantado ao mais cru): `documentacao.md` (fechada) > `entrega.md` (dev pronto, so falta documentar/gate 2) > `plano.md` (passou o Gate 1, pronta pra desenvolver) > `contexto.md` (analisada) > `solicitacao.md` (crua).
   - **Epicos** (pasta com filhas `DEM_XXX.NN`): leia o estagio de CADA filha e o **mapa de dependencias** (tabela "Depende de" no `EPICO_*.md` ou no `solicitacao.md` do pai). So e agendavel a filha cujas dependencias ja fecharam OU cabem antes dela na propria semana.
2. **`gerencial/semana/<ID-1>/resumo.md`** -- o "Foco da proxima semana" que a semanal acabou de gravar. E a intencao estrategica; a grade a materializa. Quando encadeada, esse arquivo acabou de nascer nesta mesma rodada.
3. **`gerencial/semana/<ID-1>/plano-semana.md`** (se existir) -- a grade da semana que esta fechando. Serve de continuidade: o que estava planejado e nao fechou volta pra fila de candidatos da proxima.
4. **`demandas/INC_incidentes/DEM_INC-*/`** -- incidentes com Status != ESTABILIZADO. Nao viram tarefa de epico; se um incidente aberto exige trabalho seu na semana, reserve nele um espaco (conta como fila/operacao, nao como epico).

## Regras de distribuicao (o motor)
1. **Uma tarefa substancial por dia focado.** Tarefa leve (documentar uma filha ja validada, fechar um epico curto) pode juntar duas num dia. Tarefa pesada (investigacao/coleta profunda, construcao de varios dias) ocupa o slot inteiro e, se nao couber, segue na semana seguinte (nao se espreme).
2. **Reserva de fila de chamados.** Default **2 dias por semana, segunda e quinta** (abre a semana na fila e da um respiro no meio). Esses dias recebem "Fila de chamados". Sobram 3 dias de epico. A reserva e sobrescrita por `--fila`. Uma demanda com data de inicio marcada dentro da semana (ex.: uma task de sprint que arranca na segunda) vive nesse espaco de fila, nao toma dia de epico.
3. **Dependencia manda.** Nunca agende uma filha antes das dependencias dela. Se a dependencia fecha nesta mesma semana, a filha pode vir depois dela, no mesmo intervalo.
4. **Rodizio, nao afunilamento.** Gire as frentes abertas pra todas andarem; evite a mesma frente em dias seguidos se houver outra frente pronta pra avancar. Excecao: com `--prioridade`, a frente escolhida ganha mais slots.
5. **Fechar rapido o que esta quase pronto.** Filhas em `entrega.md` (so falta gate 2 / documentar) e epicos a um passo do fim entram cedo na semana -- tiram uma frente da mesa e liberam foco.
6. **Gate e trabalho seu, marcado.** Validacao no PBI Desktop, decisao que depende de gestor ou de governanca externa entram como item **seu** (tipo `gate`), nao como dev. Deixe explicito de quem e a bola.
7. **So entra o que e startavel.** Filha com dependencia nao satisfeita nem agendavel na semana nao entra na grade; vai pra secao "Fora da grade" com o motivo (dependencia, comeca em data futura, aguardando governanca).

## Saida (o artefato que a daily le)
Grave em **`gerencial/semana/<ID>/plano-semana.md`** (o `<ID>` da semana ALVO; crie a pasta se nao existir -- a semanal daquela semana depois escreve `resumo.*` na mesma pasta, sem colisao de nome).

Estrutura:
```
# Plano da semana <ID> -- <Rotulo humano>

Gerado em DD-MM-AAAA a partir das demandas em aberto ao fim da semana <ID-1>.
Reserva de fila: <dias> (default seg + qui). Frente prioritaria: <COD ou "rodizio parelho">.

## Grade
| Dia | Data  | Frente   | Tarefa                                   | Tipo  |
|-----|-------|----------|------------------------------------------|-------|
| Seg | DD/MM | Chamados | Fila de chamados                         | fila  |
| Ter | DD/MM | APP-002  | .06 Modelo de dados                      | epico |
| Qua | DD/MM | BI-001   | .02 Mapa dashboard -> base -> origem     | epico |
| Qui | DD/MM | Chamados | Fila de chamados                         | fila  |
| Sex | DD/MM | BI-002   | Voce valida .06/.07 no Desktop           | gate  |

## Fora da grade esta semana
- <FRENTE>.<NN> <titulo> -- <motivo: dependencia X aberta / comeca em DD/MM / aguardando governanca>
```
Tipo e um de: `fila`, `epico`, `gate`. A coluna Tarefa nomeia a filha pelo numero e titulo curto (o mesmo do mapa do epico), pra daily casar direto.

## Fluxo (3 fases)
1. **Ler** -- resolva SEG/SEX/ID da semana alvo; escaneie as demandas em aberto, com estagio e dependencias das filhas; leia o foco da semanal (`<ID-1>/resumo.md`) e o plano da semana que fecha (`<ID-1>/plano-semana.md`) pra continuidade.
2. **Montar a grade** -- aplique as regras acima. Se rodando avulsa e sem argumentos, confirme **so duas coisas** em uma pergunta enxuta: a reserva de fila (default seg+qui) e se ha frente prioritaria. Encadeada pela semanal, use os defaults sem travar o fluxo e mostre a grade pronta pra ajuste.
3. **Salvar e mostrar** -- grave `plano-semana.md` e mostre a grade no chat. Deixe claro que a `reporte-dia` vai puxar dela o candidato de "Hoje" automaticamente.

## Boas praticas
- So uma semana pra frente. Nao invente cronograma de meses; a repeticao semanal constroi o longo prazo.
- Equilibrio antes de velocidade: melhor toda frente andar um passo do que uma fechar e as outras pararem. `--prioridade` e a valvula pra quando voce quiser o contrario.
- Realidade escorrega. A grade e um ponto de partida pra daily, nao um contrato; a daily sempre confirma.
- Prosa do cabecalho e dos motivos segue a regua de escrita do CLAUDE.md: natural, sem travessao, sem "nao e X, e Y", sem pergunta retorica, sem palavra pomposa. A grade e tabela escaneavel, frase curta.
- So le o caderno e escreve em `gerencial/semana/<ID>/plano-semana.md`; nao toca demanda nem cria registro de demanda.
