---
name: registrar-incidente
description: Registra um incidente operacional — uma quebra/instabilidade não-planejada que afetou o ambiente ou as demandas (carga que falhou, base que explodiu, dashboard fora, alteração de origem que derrubou o lakehouse). Start próprio (não passa pelo analisar-especificacao). A entrada pode ser variada (e-mail exportado, print, log, relato verbal, mensagem). Use quando algo QUEBROU e precisa virar registro rastreável + aprendizado, não desenvolvimento. Transversal.
---

> DESTINO: todo arquivo de registro (demandas/, diario/, conhecimento/, gerencial/) é criado na RAIZ DO CADERNO (o repositório do caderno adicionado à sessão), NUNCA no repo de trabalho. Se o caderno não estiver na sessão, pare e peça para adicioná-lo. Ver CLAUDE.md > "Onde cada coisa mora".

# Skill: registrar-incidente (reação a quebra — start próprio)

Transforma um incidente operacional em registro formal rastreável e em aprendizado para o baú.
Start próprio: NÃO passa pelo analisar-especificacao. É uma demanda formal de fluxo curto, mora em `demandas/INC_incidentes/DEM_INC-NNN/`.

## Quando é incidente (e quando NÃO é)
- **É incidente:** algo quebrou/instabilizou sem ter sido planejado — carga que falhou, base que explodiu de porte, objeto de origem alterado que derrubou outras áreas, dashboard que parou de atualizar, ambiente comprometido. Reativo, não-planejado, geralmente com terceiros envolvidos na correção.
- **NÃO é incidente:** trabalho planejado (vai pra esteira de desenvolvimento via `analisar-especificacao`); "deveria bater e não bate" entre bases (vai pra `reconciliar-bases`); dúvida/pedido de informação.
- Na régua das primitivas: incidente VIRA REGISTRO (versiona no caderno), não fica só no chat. O diário pega a linha do dia; a DEM_INC guarda o loop aberto (status) e o impacto rastreável.

## Nomenclatura da pasta
`DEM_INC-NNN` — sequencial curto. Conte só as pastas `DEM_INC-*` existentes e use o próximo número. Prefixo `DEM_` sempre, subgrupo `INC`.

## Entrada — variada
O material bruto pode chegar em qualquer forma: **e-mail exportado (.eml)**, print, trecho de log, mensagem, ou relato verbal do usuário. Transcreva o que importa para o `solicitacao.md`, SEM interpretar ainda.
- **E-mail .eml grande:** leia só o necessário (cabeçalho From/To/CC/Subject/Date + corpo `text/plain`); não despeje HTML/anexos base64 no registro.
- **Segurança (DURO):** nada de segredo/token/connection string nem dado corporativo bruto no registro. Anonimize dado pessoal de terceiros (LGPD). Nomes de objeto sem acento (ASCII).
- Se faltar algo essencial (o que quebrou, o impacto, o encaminhamento), PERGUNTE antes de seguir.

## Campos automáticos (capturados AGORA)
- **Data de detecção = hoje.** OBTENHA A DATA REAL DO SISTEMA (ex.: `date +%d-%m-%Y`, no formato DD-MM-AAAA do campo). Nunca assuma.
- **Sprint** (bucket temporal, mesma regra das outras): dia <= 15 -> SPRINT_1; senão SPRINT_2. Label `SPRINT_<1|2> - <MMM>/<AA>`.

## Saída 1 — solicitacao.md (o relato bruto)
`demandas/INC_incidentes/DEM_INC-NNN/solicitacao.md`:
```
# INC-NNN | <título curto do incidente>

**Tipo:** Incidente operacional
**Data de detecção:** <DD-MM-AAAA>
**Sprint:** <SPRINT_X - MMM/AA>
**Forma de entrada:** <e-mail exportado | print | log | relato | mensagem>
**Status:** ABERTO

## Relato (bruto)
<o material transcrito e organizado — SEM diagnóstico ainda>
```

## Saída 2 — contexto.md (o diagnóstico)
`demandas/INC_incidentes/DEM_INC-NNN/contexto.md` — o que dá rastreabilidade e vira matéria do baú. Seções:
- **Detecção** — quando e como notou (a carga falhou, o e-mail, o alerta).
- **Impacto** — o que parou, quem foi afetado, e o custo concreto (ex.: "perdi a manhã nas demandas", "dashboards X/Y sem atualizar", "pipeline 1h38 e falhou"). Números quando houver.
- **Causa raiz** — a mudança/evento que originou. Distinga pontual x estrutural.
- **Acordo/contexto violado** (se houver) — o que estava combinado e foi contrariado.
- **Encaminhamento** — ação corretiva pedida + **responsável** (muitas vezes terceiro: TI/DBA). É o loop que mantém o incidente ABERTO.
- **Comunicação** — a quem foi reportado (destinatários, data/hora, prioridade), se houve.

## Status / ciclo de vida
O incidente NÃO fecha quando você registra — fecha quando o **ambiente estabiliza**. Estados:
- `ABERTO` — registrado, correção pendente (em geral com terceiro).
- `ACOMPANHANDO` — correção em andamento; atualize o contexto.md conforme evolui.
- `ESTABILIZADO` — ambiente normalizado/confirmado; só então fechar.
Atualize o campo `Status` no solicitacao.md e registre a virada no diário do dia.

## Fluxo
1. Identifique a forma de entrada e transcreva o relato bruto -> `solicitacao.md` (Status ABERTO).
2. Diagnostique -> `contexto.md` (detecção, impacto, causa raiz, acordo violado, encaminhamento, comunicação).
3. Registre uma linha no diário do dia (`diario/AAAA-MM-DD.md`): `## Incidente | <objeto/título>` com impacto e encaminhamento. (Se o usuário já tem entrada do dia, acrescente; não duplique.)
4. **Capture conhecimento** se houver lição reaproveitável: o incidente quase sempre vira uma **decisão** no baú (não runbook) — "por que não se faz X" / "qual o limite do ambiente". Chame `capturar-conhecimento` ou registre a decisão + linha no INDICE. Avalie linha nova na matriz de roteamento só se for novidade.
5. Mantenha o status até **ESTABILIZADO**. Ao normalizar, feche e anote no diário.

> O `contexto.md` é interno e é onde o diagnóstico técnico mora, com nome de objeto à vontade. O
> `fechamento.md`, escrito depois pela `fechar-demanda`, sai para a área e segue a régua de
> linguagem de negócio do modelo [[fechamento-chamado]].

## Natureza
É reação e registro, não desenvolvimento. A skill não conserta o ambiente (a correção costuma ser de terceiros) — ela garante que a quebra vire rastro + aprendizado e que o loop aberto não se perca.
