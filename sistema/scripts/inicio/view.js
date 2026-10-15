/* Home do caderno: o estado do trabalho numa olhada.
 *
 * Lê o vault ao vivo, então reflete o instante em que você abre, sem depender
 * de nenhuma rotina ter rodado antes.
 *
 * A tela responde três perguntas, nessa ordem: o que eu faço agora (a semana e
 * a fila), o que não depende de mim (a espera) e o que saiu daqui (as entregas
 * e o baú). A ordem importa: painel que só fala de pendência conta metade da
 * história quando a fila está curta.
 */

const src = await dv.io.load("sistema/scripts/lib.js");
const lib = new Function("dv", "app", src + "; return LIB;")(dv, app);
const DT = lib.DT;

const raiz = dv.container.createDiv({ cls: "scd" });

/* ------------------------------------------------------------------ dados */

/* teto de linhas por card: a home e um resumo, e lista longa aqui compete com a
 * grade da semana em vez de completar. O excedente vai no cabecalho, que nao
 * gasta linha. */
const TETO = 3;

const abertas = lib.demandas();
const arquivadas = lib.arquivadas();
const incidentes = abertas
  .filter((d) => d.prefixo === "INC")
  .sort((a, b) => (b.parada || 0) - (a.parada || 0));
const resto = abertas.filter((d) => d.prefixo !== "INC");
/* espera de terceiro sai da conta de "parada": o relógio corre, mas o atraso
 * não é meu, e misturar as duas coisas faz o painel cobrar o que não cabe */
const espera = resto.filter((d) => d.espera);
const curso = resto.filter((d) => !d.espera);
const paradas = curso.filter((d) => (d.parada || 0) >= lib.LIMITE_ESQUECIDA);
const mexidas = abertas.filter((d) => (d.parada === null ? 99 : d.parada) <= 7);
const semNar = lib.semNarrativa(14);
const fechadas = lib.fechadasEm(7);
const entregas = lib.fechadasDetalhe(7);
const notas = lib.notasNovas(7, TETO);
const grade = lib.marcaFeitas(await lib.semanaPlanejada());

/* ---------------------------------------------------------------- cabeçalho */

const agora = DT.now();
const h = agora.hour;
const saud = h < 12 ? "Bom dia" : h < 18 ? "Boa tarde" : "Boa noite";

const topo = raiz.createDiv({ cls: "scd-topo" });
const esq = topo.createDiv();
esq.createDiv({ cls: "scd-saud", text: saud + " 👋" });
esq.createDiv({
  cls: "scd-frase",
  text: incidentes.length
    ? "Tem incidente aberto. Instabilidade não espera."
    : "O peso do registro acompanha o tamanho do trabalho.",
});

/* o meio do cabeçalho é o placar da semana, o único número do painel que fala
 * de ENTREGA, mais os sinais de saúde que antes gastavam um tile inteiro para
 * dizer zero */
const meio = topo.createDiv({ cls: "scd-placar" });
const pl1 = meio.createDiv({ cls: "scd-placar-item" });
pl1.createSpan({ cls: "scd-num scd-num-sm" + (fechadas ? " is-ok" : ""), text: String(fechadas) });
pl1.createSpan({ cls: "scd-lab", text: "fechadas na semana" });
const pl2 = meio.createDiv({ cls: "scd-placar-item" });
pl2.createSpan({ cls: "scd-num scd-num-sm", text: String(mexidas.length) });
pl2.createSpan({ cls: "scd-lab", text: "tocadas na semana" });

const saude = meio.createDiv({ cls: "scd-saude" });
if (!incidentes.length) saude.createSpan({ cls: "scd-pill is-ok", text: "0 incidentes" });
if (!semNar.length) saude.createSpan({ cls: "scd-pill is-ok", text: "diário em dia" });
else saude.createSpan({ cls: "scd-pill is-warn", text: semNar.length + " dias sem narrativa" });
if (arquivadas.length) saude.createSpan({ cls: "scd-pill", text: arquivadas.length + " arquivadas" });

const dir = topo.createDiv({ cls: "scd-data" });
dir.createSpan({ text: agora.setLocale("pt-BR").toFormat("cccc, d 'de' LLLL 'de' yyyy") });
dir.createSpan({ text: "Semana " + agora.toFormat("kkkk-'W'WW") });

/* ------------------------------------------------------------------- tiles */

/* três tiles em vez de quatro, e nenhum deles existe para exibir zero: o que
 * está em zero virou pill lá em cima. Incidente entra na frente quando existe,
 * porque aí ele manda na tela. */
const tiles = raiz.createDiv({ cls: "scd-tiles" + (incidentes.length ? " is-quatro" : "") });

if (incidentes.length) {
  lib.tile(tiles, {
    icone: "alert-triangle",
    rotulo: "Incidentes",
    valor: incidentes.length,
    sub: "mais antigo há " + lib.ditoEmDias(incidentes[0].parada),
    alerta: true,
  });
}
lib.tile(tiles, {
  icone: "folder-open",
  rotulo: "Demandas abertas",
  valor: resto.length,
  sub: mexidas.length + " tocadas nos últimos 7 dias",
});
const tEspera = lib.tile(tiles, {
  icone: "hourglass",
  rotulo: "Em espera de terceiro",
  valor: espera.length,
  sub: espera.length
    ? espera.map((d) => d.espera.quem).slice(0, 3).join(" · ")
    : "nada travado fora daqui",
});
if (espera.length) tEspera.addClass("is-espera");
lib.tile(tiles, {
  icone: "play",
  rotulo: "Em curso",
  valor: curso.length,
  sub: paradas.length
    ? paradas.length + " sem toque há mais de " + lib.LIMITE_ESQUECIDA + " dias"
    : "nenhuma esquecida",
  alerta: paradas.length > 3,
});

/* ---------------------------------------------------------------- frentes */

const frentes = lib.porFrente(abertas);
if (frentes.length) lib.faixaFrentes(raiz, frentes);

/* ----------------------------------------------------------------- semana */

/* A grade da semana já existe no plano-semana.md e nunca aparecia aqui. É ela
 * que responde "o que eu faço agora", e ocupa a largura que sobrava desde que
 * o quadro de demandas encolheu. */
if (grade && grade.dias.length) {
  const cSem = lib.card(raiz, "calendar-range", "A semana", {
    texto: grade.semana,
    destino: grade.caminho,
  });
  const dias = cSem.createDiv({ cls: "scd-dias" });
  const hojeSem = agora.setLocale("pt-BR").toFormat("ccc").slice(0, 3).toLowerCase();
  for (const d of grade.dias) {
    const ehHoje = d.dia.toLowerCase().slice(0, 3) === hojeSem;
    const cel = dias.createDiv({ cls: "scd-dia" + (ehHoje ? " is-hoje" : "") });
    const cab = cel.createDiv({ cls: "scd-dia-cab" });
    cab.createSpan({ cls: "scd-dia-sem", text: ehHoje ? d.dia + " · hoje" : d.dia });
    cab.createSpan({ cls: "scd-dia-data", text: d.data });
    for (const t of d.tarefas) {
      const cls =
        "scd-tar" + (t.feita ? " is-feita" : "") + (t.tipo === "fila" ? " is-fila" : "");
      const box = cel.createDiv({ cls });
      if (t.codigo) box.createSpan({ cls: "scd-tar-quem", text: t.frente });
      box.createSpan({ cls: "scd-tar-txt", text: lib.curto(t.tarefa, 62) });
    }
  }
}

/* ------------------------------------------------------------------ grade */

const grid = raiz.createDiv({ cls: "scd-grade is-tres" });
const colA = grid.createDiv({ cls: "scd-col" });
const colB = grid.createDiv({ cls: "scd-col" });
const colC = grid.createDiv({ cls: "scd-col" });

/* --- incidentes ---------------------------------------------------------- */

if (incidentes.length) {
  const cInc = lib.card(colA, "alert-triangle", "Incidentes em aberto");
  cInc.createDiv({ cls: "scd-vazio", text: "Incidente fecha só quando estabilizado." });
  incidentes.forEach((d) => {
    lib.linhaItem(cInc, {
      titulo: d.codigo,
      sub: lib.curto(d.assunto, 78),
      destino: d.caminho,
      faixa: "late",
      chips: [{ texto: lib.ditoEmDias(d.parada), variante: "atraso" }],
    });
  });
}

/* --- o que pegar a seguir ------------------------------------------------ */

const cFila = lib.card(
  colA,
  "target",
  "O que pegar a seguir",
  curso.length > TETO ? { texto: TETO + " de " + curso.length } : undefined
);
/* a fila só olha o que é trabalho seu: o que espera terceiro tem card próprio,
 * e listar nos dois lugares fazia o painel repetir a mesma linha duas vezes */
const fila = lib.fila(curso, TETO);
if (!fila.length) {
  lib.vazio(
    cFila,
    espera.length
      ? "Nada seu na fila. O que resta está esperando terceiro, na coluna ao lado."
      : "Nada em aberto. Ou o caderno está limpo, ou alguma demanda ficou sem solicitacao.md."
  );
} else {
  const naGrade = new Set();
  if (grade) {
    for (const d of grade.dias) for (const t of d.tarefas) if (t.codigo) naGrade.add(t.codigo);
  }
  fila.forEach(({ d, motivo }) => {
    lib.linhaItem(cFila, {
      titulo: d.codigo,
      sub: lib.curto(d.assunto, 70),
      destino: d.caminho,
      faixa: naGrade.has(d.codigo) ? "ok" : (d.parada || 0) >= lib.LIMITE_ESQUECIDA ? "warn" : null,
      chips: [
        { texto: naGrade.has(d.codigo) ? "na grade da semana" : motivo },
        { texto: lib.GAVETAS[d.prefixo] || d.prefixo, variante: "proj" },
      ],
    });
  });
}

/* --- em espera de terceiro ----------------------------------------------- */

const cEsp = lib.card(colB, "hourglass", "Em espera de terceiro", {
  texto: espera.length > TETO ? TETO + " de " + espera.length : "não é atraso meu",
});
if (!espera.length) {
  lib.vazio(cEsp, "Nada travado fora daqui. Marque com um AGUARDANDO.md quando estiver.");
} else {
  espera.slice(0, TETO).forEach((d) => {
    /* espera longa deixa de ser espera e vira cobrança a fazer: o âmbar é o
     * lembrete de que alguém precisa ser puxado */
    const velha = (d.espera.dias || 0) > 30;
    lib.linhaItem(cEsp, {
      titulo: d.codigo,
      sub: lib.curto(d.espera.nota || d.assunto, 62),
      destino: d.caminho,
      faixa: velha ? "warn" : "ev",
      chips: [
        {
          texto: d.espera.quem + (d.espera.dias === null ? "" : " · " + lib.ditoEmDias(d.espera.dias)),
          variante: velha ? "atraso" : "ev",
        },
      ],
    });
  });
}

/* --- as mais esquecidas -------------------------------------------------- */

/* só aparece quando existe esquecimento de verdade. Com a fila curta, este card
 * repetia exatamente as linhas do "pegar a seguir". */
if (paradas.length) {
  const cEsq = lib.card(colB, "clock", "As mais esquecidas");
  cEsq.createDiv({
    cls: "scd-vazio",
    text:
      paradas.length +
      " sem toque há mais de " +
      lib.LIMITE_ESQUECIDA +
      " dias, e sem ninguém para esperar:",
  });
  const vistas = {};
  paradas
    .sort((a, b) => (b.parada || 0) - (a.parada || 0))
    .filter((d) => (vistas[d.prefixo] ? false : (vistas[d.prefixo] = true)))
    .slice(0, TETO)
    .forEach((d) => {
      lib.linhaItem(cEsq, {
        titulo: d.codigo,
        sub: lib.curto(d.assunto, 58),
        destino: d.caminho,
        faixa: "warn",
        chips: [{ texto: lib.ditoEmDias(d.parada), variante: "atraso" }],
      });
    });
}

/* --- últimos dias -------------------------------------------------------- */

const cDia = lib.card(colC, "calendar-days", "Últimos dias narrados", {
  texto: "diário",
  destino: "diario",
});
const dias = lib.diarios(TETO);
if (!dias.length) {
  lib.vazio(cDia, "Nenhum dia narrado ainda. A narrativa é o que atravessa as máquinas.");
} else {
  dias.forEach((d) => {
    const idade = Math.round(DT.now().diff(DT.fromISO(d.dia), "days").days);
    lib.linhaItem(cDia, {
      titulo: DT.fromISO(d.dia).setLocale("pt-BR").toFormat("dd/LL"),
      sub: lib.curto(d.titulo, 58),
      destino: d.caminho,
      chips: [{ texto: idade <= 0 ? "hoje" : idade + "d atrás" }],
    });
  });
}

/* --- sem narrativa ------------------------------------------------------- */

if (semNar.length) {
  const cSem = lib.card(colC, "book-x", "Dias sem narrativa");
  cSem.createDiv({
    cls: "scd-vazio",
    text: "Teve escrita de arquivo e ninguém contou o dia.",
  });
  semNar.forEach((d) => {
    lib.linhaItem(cSem, {
      titulo: DT.fromISO(d).setLocale("pt-BR").toFormat("cccc, dd/LL"),
      chips: [{ texto: d, variante: "atraso" }],
    });
  });
}

/* ----------------------------------------------------------------- rodapé */

const rodape = raiz.createDiv({ cls: "scd-rodape" });

const cEnt = lib.card(rodape, "check-check", "Saiu nos últimos 7 dias", {
  texto: fechadas + (fechadas === 1 ? " fechamento" : " fechamentos"),
});
if (!entregas.length) {
  lib.vazio(cEnt, "Nenhum fechamento na semana. Ou a semana foi de análise, ou faltou fechar.");
} else {
  /* o card das entregas e o mais largo do rodape: cabe uma matriz 3x3 sem
   * competir com nada, e uma semana inteira costuma caber nela */
  const lista = cEnt.createDiv({ cls: "scd-ents" });
  entregas.slice(0, TETO * 3).forEach((e) => {
    const b = lista.createDiv({ cls: "scd-ent" });
    b.createSpan({ cls: "scd-ent-cod", text: e.codigo });
    b.createSpan({ text: lib.curto(e.assunto, 34) });
    b.onclick = () => lib.abrir(e.caminho);
  });
}

const cBau = lib.card(rodape, "library", "O baú cresceu", {
  texto: "baú",
  destino: "conhecimento/INDICE.md",
});
if (!notas.length) {
  lib.vazio(cBau, "Nenhuma nota nova na semana. Entrega sem aprendizado registrado é entrega que não volta.");
} else {
  notas.forEach((n) => {
    lib.linhaItem(cBau, {
      titulo: "",
      sub: lib.curto(n.titulo, 62),
      destino: n.caminho,
      chips: [{ texto: n.gaveta }],
    });
  });
}
