---
name: fechar-demanda
description: Fecha uma demanda validada. Escreve o documento de fechamento no peso do trilho (curto, longo ou incidente), atualiza o prontuário do objeto e encadeia a captura de conhecimento e de valor. Transversal a todas as frentes.
---

# Skill: fechar-demanda (última etapa da esteira)

Uma skill para todo fechamento. O que muda entre um caso e outro é o **peso**, e o peso vem do
trilho decidido lá na abertura, não de julgamento novo aqui.

## Antes de escrever: leia o log

O log bruto do dia (`diario/.log/AAAA-MM-DD.jsonl`) registrou toda escrita de arquivo desta
demanda, com hora. Use-o para o início real, a entrega e o esforço, **antes de perguntar
qualquer data**. Perguntar o que o log já sabe é desperdício.

```bash
grep '"demanda": "DEM_XXX' diario/.log/*.jsonl
```

## Entradas (leia dos arquivos, não peça prints)

- `solicitacao.md` (SLA, trilho, objeto alvo) · `contexto.md` (problema, escopo, aceite, ripple)
- `entrega.md`, quando existir (trilho longo, com o parecer do auditor)
- o resumo do commit, quando já houver
- `gerencial/objetos/<objeto>.md`, se o objeto já tem prontuário

Reaproveite o que a esteira já decidiu. Tipo, frente, objeto e solicitante já estão escritos:
não reclassifique.

## Onde escreve, por trilho

| Trilho | Arquivo | Modelo |
|---|---|---|
| **CURTO** | `fechamento.md` (único) | [[fechamento-chamado]] ou [[fechamento-app]] |
| **LONGO** | `documentacao.md`, com `entrega.md` já escrito | mesmos modelos, e o valor vai no `valor.md` separado |
| **INCIDENTE** | `fechamento.md` | seção própria, abaixo |

No trilho curto, **o bloco de valor entra no próprio fechamento** e não existe `valor.md`
separado. O bloco é interno e nunca vai para documento compartilhado com o solicitante.

Escolha entre os dois modelos pela origem: chamado com SLA usa [[fechamento-chamado]];
alinhamento de gestão ou item de cronograma da frente APP usa [[fechamento-app]], que fala
para público de negócio.

## Fechamento de incidente

Incidente não fecha quando o conserto entra. Fecha quando **estabiliza**. O documento tem:

- **O que quebrou** e o que o usuário sentiu.
- **Causa raiz**, não o sintoma.
- **O que foi feito para estabilizar**, com a data.
- **Janela de observação**: quanto tempo acompanhou depois, e o que confirmou a estabilidade.
- **O que evita a reincidência**, e se isso já foi feito ou virou demanda nova.

O aprendizado de incidente vai **obrigatoriamente** para o baú. Incidente sem runbook ou
decisão é incidente que vai voltar.

Incidente é o documento que mais circula fora da TI, então a régua de linguagem abaixo pega com
força aqui. "O que quebrou" é o que a pessoa deixou de conseguir fazer, não o objeto que falhou.
Nome de tabela, de pipeline e de caminho no lake ficam no `contexto.md`, que é onde o diagnóstico
mora.

## Prontuário do objeto (o passo que não existia)

Se a demanda tem `Objeto alvo` preenchido, acrescente a linha desta entrega em
`gerencial/objetos/<objeto>.md`, no formato [[prontuario-objeto]]. Crie o arquivo se for a
primeira vez.

Marque com honestidade se **esta entrega foi retorno de validação**, ou seja, se o solicitante
devolveu algo entregue antes. Esse é o dado que mais se perde e o que mais vale depois, porque
é dele que sai a taxa de retrabalho do objeto. Distinga sempre o que está registrado do que é
relato de memória.

Depois de acrescentar a linha, recalcule os blocos de visão geral e retrabalho a partir da
linha do tempo. Nunca mantenha os dois em paralelo à mão.

## Fluxo

1. Leia o log e os arquivos da demanda. Identifique o trilho.
2. Calcule SLA, esforço, complexidade e risco por [[PADRAO_SLA]].
3. Escreva o documento no modelo do trilho. **Mostre e pare para confirmação.**
4. Depois do OK:
   a. salve no arquivo certo;
   b. atualize `gerencial/objetos/<objeto>.md`;
   c. acione `capturar-conhecimento` se houver algo reaproveitável;
   d. acione `capturar-valor` se o trilho for longo (no curto, o bloco de valor já ficou no
      próprio fechamento);
   e. registre no `diario/AAAA-MM-DD.md` que a demanda fechou;
   f. rode `python .claude/scripts/registro_desempenho.py --md`, que regrava o registro anual
      de desempenho em `gerencial/desempenho/` com a entrega nova. Nada ali é escrito à mão.

## Regras de escrita

Direto e corporativo, frases curtas, sem floreio. Nunca invente: faltou, escreve `N/A`. Sempre
separe "o que foi feito" de "como foi feito". Sempre registre validação. Faltando informação
crítica, feche com **Pendente confirmar:** e as dúvidas.

### O fechamento fala com o negócio (vale para TODA frente)

O `fechamento.md` e o `documentacao.md` são os únicos arquivos da pasta que saem para o
solicitante e para a área. O leitor é analista de negócio. Todo o resto da pasta
(`contexto.md`, `plano.md`, `entrega.md`) é onde o técnico mora, e o usuário lê aqueles.

Isso **não é regra da frente APP**. Vale igual em PBI, dados, sql e automação. O que muda é só
qual jargão você precisa traduzir.

Nada de nome de objeto técnico no corpo. Se o detalhe técnico for mesmo necessário, ele vira uma
linha de rastreio no rodapé:

```
**Rastreio:** detalhamento técnico em `entrega.md`, na pasta da demanda.
```

No trilho CURTO não existe `entrega.md`, então o rastreio aponta para o `contexto.md`.

| Não escreva | Escreva |
|---|---|
| `.pbip`, TMDL, JSON, modelo semântico, estado do Desktop | o painel, a tela, a base do painel |
| nome de medida, nome de tabela, nome de coluna | o indicador, a informação, o campo que a pessoa vê |
| nome de pipeline, de bloco, de atividade, de notebook, de parâmetro | a rotina geral de cargas, a fila compartilhada, o agendamento |
| id de dataset, GUID, workspace id | o nome do painel |
| gold, silver, bronze, serverless, lakehouse | o repositório de dados da empresa |
| view, procedure, query, `SELECT` | a consulta ao sistema, a origem do dado |
| wikilink para padrão interno (`[[PADRAO_DAX]]` e afins) | nada; isso fica nos arquivos internos |

"Como foi feito" também vira negócio: de onde vem o número, a que filtro ele responde, o que
garante que bate com a fonte oficial, o que muda na prática para quem usa.

Antes de salvar, releia o documento no lugar do solicitante. Se uma frase só faz sentido para
quem conhece o ambiente por dentro, reescreva ou mande para o rastreio.

## Regra dura

O peso do documento acompanha o trilho. Chamado de rotina não ganha dossiê, e épico não ganha
bilhete. Se você está escrevendo três parágrafos sobre um ajuste de rótulo, o trilho está
errado, e vale dizer isso em vez de escrever.
