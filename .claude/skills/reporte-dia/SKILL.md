---
name: reporte-dia
description: Monta a daily (retrospectiva do que foi planejado, o que foi feito, incidentes em aberto, impedimentos e o plano de hoje) derivando do log automático e do diário, e salva em gerencial/dia/ para a retrospectiva seguinte. Devolve um bloco pronto para colar no WhatsApp. Use antes da daily. Transversal.
---

# Skill: reporte-dia (a daily)

## Papel

Montar a daily do dia, abrindo com a retrospectiva do que foi planejado e fechando com o plano
de hoje. Salva em `gerencial/dia/<D>.md`, e é esse arquivo que alimenta a retrospectiva da
próxima.

**Ela é derivada, não reconstruída.** A fonte primária é o log automático
(`diario/.log/*.jsonl`), que registrou toda escrita de arquivo com hora e demanda, aconteça o
que acontecer com a sessão. Pergunte apenas o que o log **não** pode saber: se algo concluiu de
verdade, o que foi conversa e não virou arquivo, e o que vem hoje.

## Argumento

- `/reporte-dia` usa a data de hoje.
- `/reporte-dia AAAA-MM-DD` força essa data como hoje (D).

## Janela

Trabalho é de segunda a sexta. **L** = a daily mais recente salva em `gerencial/dia/`. A janela
é `(L, D]`, e ela cobre o intervalo inteiro, fim de semana incluído. É isso que traz o que foi
feito em casa e chegou por push. Sem daily anterior, siga sem retrospectiva.

## Fontes, nesta ordem

1. **`diario/.log/<data>.jsonl`** para toda data da janela. Diz o que foi tocado, quando e de
   qual demanda. É a espinha, e não depende de ninguém ter lembrado de nada.
2. **`diario/<data>.md`** para toda data da janela. A narrativa, quando existe.
3. `gerencial/dia/<L>.md`, de onde sai o que tinha sido planejado.
4. `gerencial/semana/<ID>/plano-semana.md` (ID = `date -d <D> +%G-W%V`), de onde sai o
   candidato de hoje.
5. `demandas/INC_incidentes/DEM_INC-*/`, para os incidentes que ainda não estabilizaram.
6. `gerencial/reunioes/<data>-*/`, para alinhamento no intervalo.

Um comando resolve a leitura do log:

```bash
cat diario/.log/*.jsonl | python -c "import sys,json,collections; d=collections.defaultdict(set); [d[j.get('demanda') or j['area']].add(j['arquivo']) for j in map(json.loads,sys.stdin)]; [print(k, len(v)) for k,v in sorted(d.items())]"
```

## Fluxo

**1. Ler.** Resolva D, L e a janela. Leia o log e o diário do intervalo. Monte, do log, a lista
de demandas tocadas com contagem de alterações.

**2. Classificar sozinho o que der.** Demanda com `fechamento.md` ou `documentacao.md` escrito
na janela está **finalizada**. Demanda tocada sem isso está **em andamento**. Isso sai do log,
sem perguntar.

**3. Retrospectiva.** Compare a seção "Hoje" da daily anterior com o que o log mostra. Resuma
num veredito de uma linha ("fechei tudo que planejei", ou "planejei 3, fechei 2, o resto
seguiu"). Item planejado sem nenhum rastro no log é a única coisa que vira pergunta: pode ter
sido trabalho de conversa, reunião ou análise que não gerou arquivo.

**Não pergunte mais "trabalhou em algo fora do plano".** O log responde isso. Só confirme o
que ele mostrou.

**4. Hoje, incidentes e impedimentos.** Ofereça a tarefa planejada da semana como candidato
principal, junto das demandas em andamento. Liste os `DEM_INC-*` com status diferente de
`ESTABILIZADO`, que são lembrete recorrente até fechar. Pergunte impedimentos, e omita a seção
se não houver.

**5. Montar e salvar** em `gerencial/dia/<D>.md`, com o mesmo conteúdo do bloco entregue.

## Formato do item

Resumo de no máximo 50 caracteres:

```
• ÁREA | RESUMO ATÉ 50 CARACTERES | CHAMADO
```

ÁREA é o setor (por exemplo "Indústria / Controle de Produção"); em reunião, a área temática.
CHAMADO é o código da task ou do chamado (por exemplo `TSK-1042` ou `CH-2210`); em reunião,
"Alinhamento DD/MM".

## Saída (WhatsApp)

Bloco de código, negrito com asterisco, ordem fixa. Omita seção vazia, menos a retrospectiva,
que sempre aparece. "Hoje" é a última e usa bullets livres.

```
*Daily — DD/MM* 📋

🔄 *Planejado p/ ontem — fiz?*
• Fechei tudo que planejei ✅
• ➕ [extra] ...

✅ *Finalizado*
• ÁREA | RESUMO | CHAMADO

🗓️ *Reunião*
• ÁREA | RESUMO | CHAMADO

🚧 *Iniciado / em andamento*
• ÁREA | RESUMO | CHAMADO

🔴 *Incidente em aberto*
• INC-NNN | RESUMO | aguardando <quem>

⛔ *Impedimentos*
• ...

🎯 *Hoje*
• ...
```

## Boas práticas

- O log é a verdade sobre **o que foi tocado**. Só o humano sabe **o que ficou pronto**.
  Pergunte a segunda coisa, nunca a primeira.
- Salvar a daily é o que faz a retrospectiva funcionar. Nunca pule esse passo.
- Só lê o caderno e escreve em `gerencial/dia/`. Não mexe em demanda.
- Nada no intervalo, nem log nem diário: pare, avise e pergunte se foi feriado ou folga. Não
  invente movimentação.
