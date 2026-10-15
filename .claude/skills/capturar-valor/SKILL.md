---
name: capturar-valor
description: No fechamento de uma demanda, completa o registro INTERNO de valor (valor.md), passa pelo auditor-valor e auto-incrementa o consolidado (rollup derivado + portfolio-valor.md). Roda o mais autonoma possivel, com interacao minima. Transversal. NUNCA compartilha com cliente.
---

> DESTINO: todo arquivo de registro e criado na RAIZ DO CADERNO, NUNCA no repo de trabalho. Ver CLAUDE.md > "Onde cada coisa mora".
> PRIVACIDADE (dura): o registro de valor e INTERNO e pessoal. NUNCA entra no documentacao.md nem em qualquer entrega compartilhada com o cliente/solicitante. Serve à conversa de crescimento de quem fez a entrega, e por isso fica só no caderno.

# Skill: capturar-valor (fechamento - camada de valor)

## Papel
Fechar o delta de valor da demanda de forma honesta e comparavel, e alimentar o portfolio que se auto-incrementa. Irma da capturar-conhecimento: uma cuida do aprendizado (bau), esta cuida do impacto (portfolio).

## Principio de operacao: autonoma, interacao minima
Rode sozinha a partir do que ja esta nos arquivos da demanda. NAO abra um formulario nem faca rodada de perguntas. So pergunte se um campo essencial (dimensao, baseline ou medida) nao der para inferir e mudar a leitura do valor. Se der para inferir com uma ressalva, infira e rebaixe a confianca, nao pergunte.

## Entradas (leia, nao peca)
- `demandas/<TIPO>/DEM-XXX/valor.md` - se ja existe o bloco de baseline semeado no GATE 1 (pela analisar-especificacao), complete o resto. Se nao existe, crie do `_TEMPLATE-DEM/valor.md` reconstruindo o baseline do contexto.md/diario e marcando confianca rebaixada por ser retroativo.
- `demandas/<TIPO>/DEM-XXX/contexto.md` (dor, solicitante, origem), `entrega.md` (o que foi feito, evidencia), resumo do commit e `documentacao.md` (SLA, esforco, objeto). Reaproveite; nao repita.

## Fluxo
1. Complete o `valor.md`: preencha o "depois", a medida ou proxy, a evidencia (linkando, nao copiando), esforco (do cabecalho de SLA), horizonte, confianca e o contra-argumento obrigatorio.
   Preencha tambem as tres linhas do registro de carreira: **Feedback** (quem comentou e o que;
   aprovacao de auditor nao conta, e sem retorno escreva "nenhum recebido"), **Visibilidade**
   (quem ficou sabendo) e **Competencias** (o que precisou usar ou desenvolver). Sao lidas pelo
   `registro_desempenho.py`, e o que ficar em branco ali sai como inferido.
2. Classifique com honestidade: dimensao primaria (uma das sete: tempo, confiabilidade, decisao, risco-dependencia, adocao, capacidade, custo), origem da prioridade (estrategica/rotina/urgencia/volume). Valor pode ser baixo ou negativo; registre assim.
3. Chame o agente **auditor-valor** (2a opiniao adversarial). Aplique o parecer: rebaixe confianca, troque medida inflada por proxy honesto, marque vaidade. So segue o que passou pelo advogado.
4. NAO mantenha contagem a mao em lugar nenhum. O consolidado e DERIVADO: rode
   `python .claude/scripts/rollup_valor.py --md`, que varre os blocos de valor das demandas e
   regrava `gerencial/valor/rollup.md` com as distribuicoes e as lacunas. O antigo
   `razao-valor.csv` morreu duas vezes justamente por ser mantido em paralelo a fonte.
   Na sequencia rode `python .claude/scripts/registro_desempenho.py --md`, que regrava o
   registro e o painel anual de desempenho em `gerencial/desempenho/`.
5. Atualize `gerencial/valor/portfolio-valor.md` (crie na primeira entrega de destaque) so na NARRATIVA: se a entrega for de
   destaque, um paragrafo curto. Numero nenhum entra ali a mao; quem guarda numero e o rollup.
6. Em `gerencial/valor/indicadores-gerais.md`, quando existir, mexa apenas na ponte com o perfil: se a
   entrega lastreia uma competencia, reforce a linha correspondente. As distribuicoes saem do
   rollup e nao sao copiadas para ca. Nunca higienize o registro interno, so acumule.
7. Mostre o que foi adicionado e PARE para confirmacao.

## Anti-vaidade (regra dura)
Metrica de atividade NUNCA e valor: numero de dashboards, de commits, de linhas. Valor e tempo devolvido, decisao habilitada, risco tirado da mesa, dado em que se passou a confiar. Sem baseline, o campo diz "sem baseline medido" e a confianca cai. Proxy sempre marcado como proxy, com a conta explicita.

## Regra
Brevidade. O valor.md e curto e honesto. O numero aqui vai ser lido por um gestor cetico e, no limite, numa entrevista: numero que nao sobrevive a uma pergunta e pior que numero nenhum.
