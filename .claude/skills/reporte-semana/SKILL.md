---
name: reporte-semana
description: Monta a one-page gerencial da semana — consolida tudo que foi feito (entregas, resultados, andamento, riscos/incidentes, foco da próxima semana) a partir do caderno e gera um PDF com a identidade visual da casa. Junto do PDF, monta SEMPRE o e-mail de encaminhamento pro gestor (assunto + corpo curto) com o PDF em anexo. No fim, encadeia a planejar-semana pra já montar o calendário concreto da próxima semana (que a reporte-dia depois consome). Voltada a GERENTE (lê pouco, quer resultado). Por padrão roda na sexta, última hora, pegando a semana que fecha. Irmã da reporte-dia. Transversal.
---

> DESTINO: todo arquivo de registro (demandas/, diario/, conhecimento/, gerencial/) é criado na RAIZ DO CADERNO (o repositório do caderno adicionado à sessão), NUNCA no repo de trabalho. Se o caderno não estiver na sessão, pare e peça para adicioná-lo. Ver CLAUDE.md > "Onde cada coisa mora".

# Skill: reporte-semana (one-page gerencial → PDF)

## Papel
Consolidar a semana num **único PDF de uma página** para reportar à gerência. Público = gestor que **lê pouco e não quer enrolação**: quer **o que foi feito** e **qual o resultado**. Toda linha é resultado para a área, não log de atividade. É **interativa** (confirma o destaque e o foco) e **tem memória** (lê o resumo da semana anterior para a continuidade).

## Argumento (opcional)
- `/reporte-semana` → usa a semana corrente (a que está fechando).
- `/reporte-semana AAAA-MM-DD` → força essa data como referência (a semana que contém esse dia).

## Cadência padrão
**Sexta, última hora** — fecha a semana com tudo fresco. (A skill é manual; se quiser agendar, é via tarefa do sistema, não daqui.)

## Datas
Trabalho é **segunda a sexta**. A partir da data de referência (D):
- **Semana = segunda a sexta** que contém D. Resolva `SEG` (segunda) e `SEX` (sexta).
- **Rótulo humano:** `Semana DD–DD <mês> AAAA` (ex.: `Semana 22–26 jun 2026`).
- **ID da semana (pasta):** ISO week da segunda — `date -d <SEG> +%G-W%V` (ex.: `2026-W26`).
- **Semana anterior** = `gerencial/semana/<ID-1>/resumo.md` (referência da continuidade, se existir).

## Fontes (sempre na RAIZ DO CADERNO)
Leia o intervalo SEG..SEX:
- `gerencial/dia/<dia>.md` — as dailies da semana, já **pré-digeridas**: principal matéria-prima.
- `diario/<dia>.md` — entradas do diário (demandas FECHADAS, incidentes, reuniões).
- `demandas/*/DEM_*/` — **fechadas na semana** (têm `fechamento.md` ou `documentacao.md`) vs **em andamento** (sem); `entrega.md`/`contexto.md` dizem o resultado.
- `gerencial/reunioes/<dia>-*/` — reuniões da semana (conte para o KPI).
- `demandas/INC_incidentes/DEM_INC-*/` — incidentes com Status ≠ ESTABILIZADO → seção Riscos.
- `gerencial/semana/<ID-1>/resumo.md` — o "Foco da próxima semana" que você prometeu na semana passada (para o veredito de continuidade).

## Conteúdo (as 5 seções fixas da one-page)
1. **Hero (1 frase):** o destaque da semana — a entrega de maior impacto, em linguagem de negócio. **Pergunte/confirme** qual é o destaque se houver dúvida.
2. **KPIs (4 números):** entregas fechadas · em andamento · reuniões · incidentes abertos.
3. **Entregue — resultado para a área:** 3–6 linhas. Cada uma: `[área] + o que mudou para ela` (negócio), com o resultado em **negrito** e o detalhe em cinza. NÃO descreva tarefa técnica ("mexi no arquivo X"); descreva o ganho ("área deixa de montar planilha manual").
4. **Em andamento — previsão de fechamento:** 0–4 linhas: status curto + quando fecha.
5. **Riscos e incidentes:** os `DEM_INC-*` abertos + impedimentos relevantes. Omita a seção se não houver.
6. **Foco da próxima semana:** 3–4 bullets, olhar pra frente. Vira a referência de continuidade da próxima semanal.

Regra de ouro: **cabe em UMA página**. Se passar, a 1ª alavanca é **reduzir a fonte/espaçamento proporcional ao volume de entregas** (ver "Escala proporcional" na Geração do PDF), NÃO cortar resultado. Só corte detalhe (nunca resultado) se, já no modo compacto, ainda estourar. Frase curta, sem jargão, sem enrolação.

## Geração do PDF
1. Carregue `conhecimento/modelos/reporte-semanal-a4.html` — a identidade visual está TRAVADA nele (cores, tipografia Archivo, layout A4). NÃO reescreva o CSS; só preencha.
2. **Monte os blocos de linha** (HTML) e injete nos marcadores. Snippets:
   - **Entregue / Em andamento (linha com área):**
     `<div class="row"><span class="pill" style="background:#BG;color:#FG">ÁREA</span><div><b>Resultado.</b> <span class="mut">detalhe curto.</span></div></div>`
     - Entregue → `#BG`=`#E3EEF3` `#FG`=`#24566F`. Em andamento → `#BG`=`#E9ECF3` `#FG`=`#384268`. As cores das pílulas acompanham a paleta do template (acento neutro `#2F6F8F`); se trocar o template pela identidade visual da sua empresa, ajuste estes pares junto.
     - **Chamado entre parênteses:** sempre que a entrega tiver código de task ou chamado (TSK/CH), termine o detalhe com o código entre parênteses, no estilo `Previsão de vendas no painel comercial (TSK-1042)`. Ex.: `<span class="mut">detalhe curto (TSK-XXXX).</span>`. Sem código (demanda interna, trabalho sem chamado), deixa sem.
   - **Riscos (linha):** igual acima com `#BG`=`#FBEDEC` `#FG`=`#9A3935`; troque o `border-top` da 1ª linha para `#F1DCDB`.
   - **Próxima semana (bullet):** `<div class="row" style="border-top:1px solid #ECEAF2"><span class="chev" style="color:#6A539D">&rsaquo;</span><div>texto.</div></div>`
3. **Substitua os tokens:** `{{AREA}}` (ex.: "BI | IA"), `{{SEMANA}}`, `{{NOME}}`, `{{CARGO}}` (ex.: "Desenvolvedor de BI | IA"), `{{HERO}}` (aceita `<b>`), `{{N_ENTREGUE}}` `{{N_ANDAMENTO}}` `{{N_REUNIOES}}` `{{N_INCIDENTES}}`, `{{ROWS_*}}`, `{{GERADO_EM}}` (data DD-MM-AAAA, vai no rodapé "Gerado a partir do versionamento de ...").
4. **Seção vazia:** remova o bloco inteiro entre `<!--SEC:NOME-->` e `<!--/SEC:NOME-->` (ex.: sem riscos → tire o bloco RISCOS).
5. **Salve** o HTML preenchido em `gerencial/semana/<ID>/resumo.html`.
5.1 **Escala proporcional (caber em 1 página).** A fonte e o espaçamento do template são dimensionados para uma semana média (~4–6 entregues). Quanto mais linhas no total (entregue + andamento + riscos + foco), menor a fonte/espaçamento para segurar a página única. Regra de bolso: **até ~8 linhas** → tamanhos padrão do template; **~9–12 linhas** → aplique o **preset compacto** abaixo; **13+ linhas** → compacto + priorize/agrupe entregas (fundir as de menor impacto numa linha só) antes de pensar em cortar. O ajuste é feito SÓ na cópia `resumo.html` da semana, **nunca** no `conhecimento/modelos/reporte-semanal-a4.html` (a identidade default fica intacta; se quiser tornar o compacto o novo default, aí sim edite o template). Preset compacto validado (W27, 11 linhas coube em 1 página): `body{line-height:1.3}` · `h1{font-size:29px}` · `.hero{font-size:14.5px;margin:12px 0 13px}` · `.kpis{gap:9px;margin-bottom:15px}` · `.kpi{padding:9px 12px}` `.kpi .n{font-size:22px}` `.kpi .l{font-size:11px}` · `.block{margin-bottom:13px}` · `.sec{font-size:11.5px;margin:0 0 7px}` · `.row{padding:5px 0;font-size:13px}` · `.pill{font-size:10px}` · `.foot{margin-top:14px;padding-top:9px}`. É escala, não redesenho: mexe só em `font-size`, `margin`, `padding`, `line-height` e `gap`; cores, fonte (Archivo) e estrutura ficam iguais.
6. **Renderize o PDF** com o Edge headless (já existe no Windows, zero instalação). Comando VALIDADO (use exatamente estes flags):
   ```
   "/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless --disable-gpu \
     --no-first-run --user-data-dir="<DIR_TMP>/edge-profile" \
     --run-all-compositor-stages-before-draw --virtual-time-budget=6000 \
     --no-pdf-header-footer --print-to-pdf="<...>/gerencial/semana/<ID>/resumo.pdf" \
     "file:///<...>/gerencial/semana/<ID>/resumo.html"
   ```
   PEGADINHAS (todas custaram tempo no teste):
   - **NÃO** use `--headless=new` — ele retorna exit 0 mas NÃO gera o PDF. Use o `--headless` clássico.
   - `--user-data-dir` próprio é obrigatório se o Edge já estiver aberto (senão o headless não roda). Aponte-o para uma pasta TEMP (scratchpad), **NUNCA** para dentro de `gerencial/` — o Edge segura arquivos do perfil e suja o caderno. Se sobrar lixo de perfil, mate só os processos `msedge.exe` com `--headless` na linha de comando (não o Edge normal do usuário).
   - `--virtual-time-budget` dá tempo da fonte (Archivo via Google) carregar antes de imprimir.
   - **O PDF é escrito de forma ASSÍNCRONA:** o processo retorna antes do arquivo existir. Após chamar, faça um loop curto checando o arquivo (existe e > 0 bytes) antes de declarar sucesso; não cheque uma vez só.
   - Valide o resultado: assinatura `%PDF`, e `/Count 1` (uma página). Se vier `/Count 2`, o conteúdo estourou — aplique o **preset compacto** (passo 5.1) e regere; só corte detalhe (nunca resultado) se, já compacto, ainda vier `/Count 2`.
   - Caminho do Edge: se o de x86 não existir, tente `C:/Program Files/Microsoft/Edge/Application/msedge.exe`; sem Edge, avise e ofereça `anthropic-skills:pdf`.
7. **Grave o registro** `gerencial/semana/<ID>/resumo.md` — o mesmo conteúdo em markdown puro (header, hero, KPIs, as seções). É a fonte da verdade do caderno e o que a próxima semanal lê para a continuidade.

## E-mail de encaminhamento (gerar SEMPRE, junto do PDF)
Além do PDF, monte o e-mail curto que acompanha o anexo, no formato que o gestor já recebe. Salve em `gerencial/semana/<ID>/email.md` (assunto + corpo) e mostre no chat pronto pra colar no Outlook. Mesmo público e tom da one-page: gestor que lê pouco, linguagem de negócio, régua de escrita do CLAUDE.md (sem travessão, sem "não é X, é Y", sem pergunta retórica, sem palavra pomposa).

**Destinatário padrão:** o gestor direto do usuário. O anexo é o `resumo.pdf` da semana — você não anexa nada, só deixa claro no chat que o PDF vai junto.

**Assunto:** `Resumo semanal — <rótulo da semana>` (o MESMO rótulo do PDF, ex.: `Resumo semanal — Semana 06–10 jul 2026`).

**Corpo (nesta ordem):**
1. Saudação pela hora do dia: `Bom dia,` (até 12h) · `Boa tarde,` (12–18h) · `Boa noite,` (após 18h). Como roda sexta última hora, o padrão é `Boa tarde,`.
2. Linha: `Segue resumo da semana.`
3. Linha-resumo com o intervalo numérico e o número: `Semana de DD/MM a DD/MM: N entregas fechadas em X áreas.` (X = quantas áreas distintas aparecem no Entregue). Quando a semana é um épico só, adapte pro enquadramento do épico sem forçar o "X áreas" (ex.: `Semana de 06/07 a 10/07: épico de Monitoramento das Cargas entregue (24 tarefas).`).
4. 3 a 5 bullets (`•`), cada um 1 frase, nesta lógica:
   - **Destaque:** o hero reescrito em conversa, começando por `Destaque foi ...`.
   - **Outras entregas:** 1–2 bullets fundindo as demais entregas de maior impacto (`Também saíram ...`). Funda por área/tema, não liste tarefa por tarefa.
   - **Incidente/risco:** só se houve incidente na semana (`O incidente ... foi revertido e estabilizado.`). Sem incidente, omite o bullet.
   - **Próxima semana:** 1 bullet olhando pra frente (`Próxima semana segue em ...`), espelhando o foco que você gravou no `resumo.md`.
5. Linha: `Fico à disposição para qualquer esclarecimento.`
6. Fecho: `Atenciosamente,` (a assinatura é automática do Outlook; NÃO a escreva).

Regra de ouro do e-mail: é um bilhete de acompanhamento, não a one-page repetida. Curto, 3–5 bullets; o PDF carrega o detalhe. Enviar é ação do usuário (a skill só entrega o texto pronto).

## Encadeamento: plano da próxima semana (rodar SEMPRE ao final)
Depois de gravar o `resumo.md` (que carrega o "Foco da próxima semana"), **chame a skill `planejar-semana`** passando a data de referência desta semanal (`/planejar-semana <SEX ou D>`). Ela lê as demandas em aberto e o foco que você acabou de gravar, e monta o calendário concreto da próxima semana em `gerencial/semana/<ID+1>/plano-semana.md`. É esse plano que a `reporte-dia` consome pra já oferecer a tarefa planejada de cada dia. Use os defaults (reserva de fila seg+qui, rodízio parelho) salvo se o usuário pedir outra coisa; mostre a grade no chat junto do PDF e do e-mail. A semanal continua sendo um comando só: o report do gestor e o plano da sua semana saem juntos.

## Fluxo (4 fases)
1. **Ler** — resolva SEG..SEX e o ID; leia as fontes; leia o resumo anterior se existir.
2. **Consolidar (interativa)** — agrupe por área, escreva os resultados em linguagem de negócio. **Confirme o destaque (hero)** e **pergunte o foco da próxima semana**. Se houve resumo anterior, dê um veredito curto de continuidade (o que prometi pra essa semana saiu?).
3. **Renderizar** — preencher template → HTML → PDF (passos acima) e montar o `email.md` (seção "E-mail de encaminhamento").
4. **Entregar** — grave e informe os caminhos do `resumo.pdf` E do `email.md`; mostre no chat o e-mail pronto pra colar (assunto + corpo), lembrando de anexar o PDF. O próprio corpo do e-mail já serve de resumo curto pra WhatsApp, se quiser adiantar. **Por fim, dispare a `planejar-semana`** (seção "Encadeamento") e mostre a grade da próxima semana.

## Boas práticas
- Resultado, não atividade. Negrito no ganho; cinza no detalhe. Gerente lê o negrito primeiro.
- Uma página, sempre. Cortar é editorial — priorize as entregas de maior impacto.
- Linguagem de negócio. A régua e a tabela de tradução do jargão estão no modelo [[fechamento-chamado]], seção "Linguagem: este documento sai para a área", e valem igual aqui. Sem jargão técnico, sem siglas não explicadas.
- A prosa (hero e detalhes) segue a régua de escrita do CLAUDE.md: natural e fluida, sem travessão, sem "não é X, é Y", sem pergunta retórica, sem palavra pomposa. As linhas de área/resultado podem ser curtas (é layout escaneável), mas escritas como alguém falaria.
- Só lê o caderno e escreve em `gerencial/semana/` — não mexe em demandas nem cria registro de demanda.
- A identidade visual vive no `conhecimento/modelos/reporte-semanal-a4.html`, que vem com uma paleta neutra. Para usar a marca da sua empresa, edite o template (e os pares de cor das pílulas acima), não a lógica da skill.
