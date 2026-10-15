# Modelo: prontuário do objeto

> Chamado é evento, objeto é o que dura. Este arquivo acumula a vida inteira de um objeto
> (dashboard, agente, pipeline, view) atravessando todos os chamados que passaram por ele.
> Mora em `gerencial/objetos/<objeto>.md` e **cresce uma linha por fechamento**, escrito pela
> skill `fechar-demanda`. É daqui que sai retrabalho, tempo de homologação e histórico de
> devolutiva, que nenhum registro por chamado enxerga.
>
> A régua de honestidade: **separe o que está registrado do que é relato**. Um indicador que
> só existe por memória vale menos, e precisa dizer isso. O formato nasceu de um estudo de
> metadados de um painel com muitas rodadas de homologação, feito a partir do histórico do
> repositório e do relato do desenvolvedor.

---

# Metadados de desenvolvimento: {NOME DO OBJETO}

**Fonte:** {de onde vieram os dados: histórico do repositório, log do caderno, relato}
**Gerado em:** {DD-MM-AAAA}

## Visão geral

| Métrica | Valor |
|---|---|
| Data de criação | {DD-MM-AAAA} |
| Última atualização | {DD-MM-AAAA} |
| Tempo total de desenvolvimento | {~N meses (N dias)} |
| Total de atualizações | {N} |
| Chamados envolvidos | {N (lista de códigos)} |
| Atualizações de criação / modificação | {N / N} |

## Indicador de retrabalho

| Métrica | Valor |
|---|---|
| Chamados com retorno de validação | {N de N} |
| Total de retornos | {N ocorrências} |
| Atualizações vinculadas a ciclos de retorno | {N de N} |
| Ciclo formal de homologação | {período, N devoluções em N entregas} |
| Intervalo médio entre devoluções | {~N dias} |

**Taxa de retrabalho: {N}%** ({N} retornos em {N} entregas)

## Ciclos de retorno de validação

| Ciclo | Chamado | Commits | Retorno? | Fonte da informação |
|---|---|---|---|---|
| {n} | {código} | {hashes curtos} | {Sim/Não} | {registrado no histórico · relato} |

## Pontos de atenção

- {Leitura honesta do que os números dizem, incluindo o que muda de interpretação.}
- {Quanto do indicador existe só por relato, e qual seria o número sem ele.}
- {O que o tempo de ciclo revela sobre processo, e não sobre o objeto.}

## Linha do tempo

| Data | Chamado | Commit | Resumo | Ciclo | Retorno? | Tipo |
|---|---|---|---|---|---|---|
| {DD-MM-AAAA} | {código} | {hash} | {o que mudou} | {n ou —} | {Sim/Não} | {Novo · Modificação · Ciclo de homologação} |

> Linhas de ciclo de retorno são destacadas. Distinga sempre o que foi classificado por relato
> do que está explícito no histórico registrado.

---

## Como manter

1. A skill `fechar-demanda` acrescenta a linha da entrega na Linha do tempo, sempre que a
   demanda nomear um objeto.
2. Se a entrega foi **retorno de validação** (o solicitante devolveu), marque na hora. Esse é
   o dado que mais se perde e o que mais vale depois.
3. Os blocos de visão geral e retrabalho são recalculados a partir da linha do tempo, nunca
   mantidos à mão em paralelo.
4. O documento executivo em PDF ou HTML é **derivado** deste arquivo, usando
   [prontuario-objeto.html](prontuario-objeto.html) como identidade visual. Esse HTML é um
   exemplar já preenchido com dados fictícios: copie a estrutura e troque os dados. Nunca é a
   fonte.
