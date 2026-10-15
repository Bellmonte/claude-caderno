/* Biblioteca compartilhada dos painéis do caderno.
 *
 * Carregada por `new Function` a partir de dv.io.load, e não por import: código
 * dentro do plugin exige reiniciar o Obsidian a cada alteração, e aqui basta
 * salvar e reabrir a nota. Por causa disso o arquivo NÃO pode ter top-level
 * await; onde precisar de assincronia, use .then().
 *
 * Termina exportando o objeto literal LIB.
 */

const DT = dv.luxon.DateTime;

/* o plugin da sidebar expõe o setIcon, que não está no escopo do dataviewjs */
const NAV = app.plugins.plugins["caderno-nav"];

/* uma demanda sem toque há mais tempo que isso conta como esquecida */
const LIMITE_ESQUECIDA = 21;

/* prefixo do código -> nome da frente. Mesma lista do hook abrir_dia.py;
 * prefixo novo que não estiver aqui aparece pelo próprio prefixo. */
const GAVETAS = {
  TSK: "Tasks de sprint",
  INC: "Incidentes",
  BI: "Projetos de BI",
  APP: "Aplicação",
};

/* ---------------------------------------------------------------- utilidades */

function hoje() {
  return DT.now().startOf("day");
}

function diasDesde(ms) {
  if (!ms) return null;
  return Math.floor((Date.now() - ms) / 86400000);
}

function ditoEmDias(n) {
  if (n === null || n === undefined) return "-";
  if (n === 0) return "hoje";
  if (n === 1) return "1 dia";
  return n + " dias";
}

function curto(texto, limite) {
  if (!texto) return "-";
  const t = String(texto).replace(/\s+/g, " ").trim();
  if (t.length <= limite) return t;
  const corte = t.slice(0, limite).replace(/\s+\S*$/, "");
  return (corte || t.slice(0, limite)).replace(/[ ,;:-]+$/, "") + "…";
}

/* Abrir arquivo NUNCA dentro da sidebar: pega o leaf mais recente da área
 * principal, senão a nota nasce na barra lateral e some ao trocar de view. */
async function abrir(caminho) {
  const f = app.vault.getAbstractFileByPath(caminho);
  if (!f) return aviso("Não achei: " + caminho);
  const ws = app.workspace;
  const leaf = ws.getMostRecentLeaf(ws.rootSplit) || ws.getLeaf("tab");
  await leaf.openFile(f);
}

/* new Notice nem sempre está no escopo do dataviewjs */
function aviso(msg) {
  try {
    new Notice(msg);
  } catch (e) {
    console.warn("[caderno]", msg);
  }
}

/* ------------------------------------------------------------------ desenho */

function ico(pai, nome, cls) {
  const s = pai.createSpan({ cls: cls || "scd-ico" });
  if (NAV && NAV.setIcon) NAV.setIcon(s, nome);
  return s;
}

function card(pai, icone, titulo, opcoes) {
  const o = opcoes || {};
  const box = pai.createDiv({ cls: "scd-card" });
  const cab = box.createDiv({ cls: "scd-card-cab" });
  ico(cab, icone, "scd-ico scd-ico-ac");
  cab.createSpan({ cls: "scd-card-tit", text: titulo });
  if (o.texto) {
    const b = cab.createDiv({ cls: "scd-verto" });
    b.createSpan({ text: o.texto });
    ico(b, "chevron-right");
    if (o.destino) b.onclick = () => abrir(o.destino);
  }
  return box.createDiv({ cls: "scd-card-corpo" });
}

function tile(pai, d) {
  const t = pai.createDiv({ cls: "scd-tile" + (d.alerta ? " is-alerta" : "") });
  const cab = t.createDiv({ cls: "scd-tile-cab" });
  ico(cab, d.icone, "scd-ico scd-ico-sm");
  cab.createSpan({ cls: "scd-lab", text: d.rotulo });
  t.createDiv({ cls: "scd-num", text: String(d.valor) });
  /* o subtítulo é onde mora a inteligência: "8 há mais de 21 dias" diz mais
   * que o número sozinho, que só informa quando já se sabe o contexto */
  t.createDiv({ cls: "scd-tile-sub", text: d.sub || "" });
  if (d.destino) {
    t.addClass("is-click");
    t.onclick = () => abrir(d.destino);
  }
  return t;
}

function chip(pai, texto, variante) {
  return pai.createSpan({
    cls: "scd-chip" + (variante ? " is-" + variante : ""),
    text: texto,
  });
}

/* Card vazio nunca fica mudo: a frase diz o que aquilo significa. */
function vazio(pai, texto) {
  return pai.createDiv({ cls: "scd-vazio", text: texto });
}

/* Uma linha por item, com codigo e assunto lado a lado. Empilhar em duas
 * linhas dobrava a altura do painel sem acrescentar informacao: o assunto e
 * complemento do codigo, nao outro dado. */
function linhaItem(pai, d) {
  const l = pai.createDiv({ cls: "scd-lin" + (d.faixa ? " f-" + d.faixa : "") });
  const esq = l.createDiv({ cls: "scd-lin-esq" });
  const tit = esq.createDiv({ cls: "scd-lin-tit" });
  /* item sem codigo (nota do bau, por exemplo) nao ganha separador orfao */
  if (d.titulo) {
    const cod = tit.createSpan({ cls: "scd-lin-cod", text: d.titulo });
    if (d.destino) {
      cod.addClass("is-link");
      cod.onclick = () => abrir(d.destino);
    }
  }
  if (d.sub) {
    if (d.titulo) tit.createSpan({ cls: "scd-lin-sep", text: "|" });
    const sub = tit.createSpan({ cls: "scd-lin-sub", text: d.sub });
    if (d.destino && !d.titulo) {
      sub.addClass("is-link");
      sub.onclick = () => abrir(d.destino);
    }
  }
  const meta = l.createDiv({ cls: "scd-lin-meta" });
  (d.chips || []).forEach((c) => chip(meta, c.texto, c.variante));
  return l;
}

/* Faixa horizontal com uma celula por frente, acima dos cards. Ocupa a largura
 * que sobrava e responde "onde esta o peso" antes de abrir qualquer card.
 *
 * Clicar numa frente LISTA as demandas dela logo abaixo. A primeira versao
 * abria a mais parada, e isso confunde: quem clica num numero espera ver os
 * itens que ele conta, nao pular para um deles. */
function faixaFrentes(pai, frentes) {
  const caixa = pai.createDiv();
  const f = caixa.createDiv({ cls: "scd-frentes" });
  const painel = caixa.createDiv({ cls: "scd-frente-lista" });
  painel.style.display = "none";

  const maior = Math.max.apply(null, frentes.map((x) => x.total));
  let aberta = null;

  frentes.forEach((fr) => {
    const c = f.createDiv({ cls: "scd-frente" });
    c.createDiv({ cls: "scd-lab", text: fr.rotulo });
    const n = c.createDiv({ cls: "scd-frente-n" });
    n.createSpan({ cls: "scd-num scd-num-sm", text: String(fr.total) });
    n.createSpan({
      cls: "scd-frente-sem" + (fr.recentes ? " is-ok" : ""),
      text: fr.recentes ? "+" + fr.recentes + " na semana" : "parada",
    });
    const b = c.createDiv({ cls: "scd-barra" });
    const i = b.createEl("i");
    i.style.width = Math.round((fr.total / maior) * 100) + "%";
    if (!fr.recentes) i.addClass("is-late");

    c.onclick = () => {
      /* clicar na que ja esta aberta fecha, para o painel nao virar entulho */
      if (aberta === fr.prefixo) {
        painel.style.display = "none";
        aberta = null;
        f.findAll(".scd-frente").forEach((x) => x.removeClass("is-sel"));
        return;
      }
      aberta = fr.prefixo;
      f.findAll(".scd-frente").forEach((x) => x.removeClass("is-sel"));
      c.addClass("is-sel");
      painel.style.display = "";
      painel.empty();

      const cab = painel.createDiv({ cls: "scd-frente-lista-cab" });
      cab.createSpan({ cls: "scd-card-tit", text: fr.rotulo });
      cab.createSpan({ cls: "scd-lab", text: fr.total + " em aberto" });
      const fechar = cab.createDiv({ cls: "scd-verto" });
      fechar.createSpan({ text: "fechar" });
      fechar.onclick = (ev) => {
        ev.stopPropagation();
        c.click();
      };

      fr.itens.forEach((d) => {
        linhaItem(painel, {
          titulo: d.codigo,
          sub: curto(d.assunto, 86),
          destino: d.caminho,
          faixa: (d.parada || 0) >= LIMITE_ESQUECIDA ? "warn" : null,
          chips: [{
            texto: ditoEmDias(d.parada),
            variante: (d.parada || 0) >= LIMITE_ESQUECIDA ? "atraso" : null,
          }],
        });
      });
    };
  });
  return caixa;
}

/* Demanda fechada nos ultimos N dias: a pasta ganhou fechamento.md ou
 * documentacao.md e o arquivo foi tocado dentro da janela. E o unico numero do
 * painel que fala de entrega, e nao de pendencia. */
function fechadasEm(dias) {
  const janela = (dias || 7) * 86400000;
  const agora = Date.now();
  const vistos = {};
  let n = 0;
  for (const f of app.vault.getFiles()) {
    if (!f.path.startsWith("demandas/")) continue;
    if (f.name !== "fechamento.md" && f.name !== "documentacao.md") continue;
    const pasta = f.parent ? f.parent.path : "";
    if (vistos[pasta]) continue;
    if (f.stat && agora - f.stat.mtime <= janela) {
      vistos[pasta] = true;
      n++;
    }
  }
  return n;
}

/* ------------------------------------------------------------------- dados */

/* Uma demanda é uma PASTA DEM_*, e o Dataview indexa arquivos, não pastas.
 * Por isso a varredura é sobre app.vault.getFiles(), agrupando por pasta.
 * Regra igual à do hook abrir_dia.py, para os dois números nunca divergirem:
 * épico não conta (quem fecha são as filhas) e fechamento.md ou documentacao.md
 * significam fechada. */
function varrerDemandas() {
  const porPasta = {};
  const comMarcador = new Set();
  const espera = {};
  const fechadas = [];
  for (const f of app.vault.getFiles()) {
    if (!f.path.startsWith("demandas/")) continue;
    const pasta = f.parent ? f.parent.path : "";
    /* o marcador pode estar na pasta da demanda ou na do epico acima dela */
    if (f.name === "ARQUIVADO.md") comMarcador.add(pasta);
    /* espera de terceiro: o frontmatter do AGUARDANDO.md diz quem trava */
    if (f.name === "AGUARDANDO.md") espera[pasta] = f;
    if (f.name === "fechamento.md" || f.name === "documentacao.md") {
      fechadas.push({ pasta, mtime: f.stat ? f.stat.mtime : 0 });
    }
    const nome = pasta.split("/").pop() || "";
    if (!nome.startsWith("DEM_")) continue;
    if (!porPasta[pasta]) porPasta[pasta] = { nome, arquivos: {}, mtime: 0 };
    porPasta[pasta].arquivos[f.name] = true;
    /* marcador nao e trabalho na demanda: contar o mtime dele faria arquivar
     * ou marcar espera zerar o contador de parada */
    const marcador = f.name === "ARQUIVADO.md" || f.name === "AGUARDANDO.md";
    if (!marcador && f.stat && f.stat.mtime > porPasta[pasta].mtime) {
      porPasta[pasta].mtime = f.stat.mtime;
    }
  }

  /* ARQUIVADO.md na propria pasta ou em qualquer pasta acima tira a demanda da
   * cobranca, sem fechar nem apagar. Apagar o marcador devolve tudo ao painel. */
  const estaArquivada = (p) => {
    let atual = p;
    while (atual && atual.startsWith("demandas")) {
      if (comMarcador.has(atual)) return true;
      const corte = atual.lastIndexOf("/");
      if (corte < 0) break;
      atual = atual.slice(0, corte);
    }
    return false;
  };

  const caminhos = Object.keys(porPasta);
  const abertas = [];
  const arquivadas = [];
  for (const p of caminhos) {
    const d = porPasta[p];
    /* épico: existe outra pasta DEM_ dentro desta */
    const temFilha = caminhos.some((o) => o !== p && o.startsWith(p + "/"));
    if (temFilha) continue;
    if (d.arquivos["fechamento.md"] || d.arquivos["documentacao.md"]) continue;
    if (!d.arquivos["solicitacao.md"]) continue;
    if (estaArquivada(p)) {
      arquivadas.push(d.nome);
      continue;
    }

    const partes = d.nome.split("_");
    const codigo = partes.length > 1 ? partes[1] : d.nome;
    abertas.push({
      nome: d.nome,
      codigo,
      prefixo: codigo.split("-")[0],
      caminho: p + "/solicitacao.md",
      parada: diasDesde(d.mtime),
      assunto: assuntoDe(p + "/solicitacao.md", partes.slice(2).join("_")),
      espera: leEspera(espera[p]),
    });
  }
  return { abertas, arquivadas, fechadas };
}

/* O AGUARDANDO.md marca demanda que depende de terceiro para andar. Sem ele,
 * "parada ha 35 dias" acusa esquecimento onde existe espera, e o painel cobra
 * do usuário o atraso de outra pessoa. O frontmatter carrega quem trava e
 * desde quando; o corpo do arquivo fica livre para o contexto. */
function leEspera(arquivo) {
  if (!arquivo) return null;
  const cache = app.metadataCache.getFileCache(arquivo);
  const fm = (cache && cache.frontmatter) || {};
  const desde = fm.desde ? String(fm.desde).slice(0, 10) : null;
  let dias = null;
  if (desde) {
    const d = DT.fromISO(desde);
    if (d.isValid) dias = Math.max(0, Math.round(DT.now().diff(d, "days").days));
  }
  return {
    quem: fm.quem || "terceiro",
    desde,
    dias,
    nota: fm.nota || "",
    caminho: arquivo.path,
  };
}

function demandas() {
  return varrerDemandas().abertas;
}

/* Demandas fora da cobranca por marcador. O painel diz quantas sao, para o
 * arquivamento nunca virar sumico silencioso. */
function arquivadas() {
  return varrerDemandas().arquivadas;
}

/* O nome da pasta não descreve tarefa filha de épico (DEM_APP-002.01 é só o
 * código), então o assunto sai do primeiro heading do documento. Usa o cache de
 * metadados, que já está em memória, em vez de ler o arquivo do disco. */
function assuntoDe(caminho, reserva) {
  const f = app.vault.getAbstractFileByPath(caminho);
  if (f) {
    const cache = app.metadataCache.getFileCache(f);
    const h = cache && cache.headings && cache.headings[0];
    if (h && h.heading) {
      let t = h.heading.trim();
      if (t.includes("|")) t = t.split("|").slice(1).join("|").trim();
      const tr = t.indexOf("—");
      if (t.startsWith("DEM_") && tr > -1) t = t.slice(tr + 1).trim();
      if (t) return t;
    }
  }
  return (reserva || "").replace(/-/g, " ");
}

/* O que pegar agora, derivado do estado. Incidente primeiro, porque
 * instabilidade não espera; depois o mais parado, com teto de um por frente
 * para a fila girar em vez de afunilar sempre na mesma. */
/* Demandas que dependem de terceiro, da mais antiga para a mais nova. */
function emEspera() {
  return varrerDemandas()
    .abertas.filter((d) => d.espera)
    .sort((a, b) => (b.espera.dias || 0) - (a.espera.dias || 0));
}

/* As que sao trabalho seu agora: nem esperando terceiro, nem incidente. */
function emCurso() {
  return varrerDemandas().abertas.filter((d) => !d.espera && d.prefixo !== "INC");
}

/* Fechadas na janela, com codigo e assunto, para o painel falar do que SAIU e
 * nao so do que falta. Uma pasta conta uma vez. */
function fechadasDetalhe(dias) {
  const janela = (dias || 7) * 86400000;
  const agora = Date.now();
  const vistas = {};
  const saida = [];
  for (const f of varrerDemandas().fechadas.sort((a, b) => b.mtime - a.mtime)) {
    if (vistas[f.pasta]) continue;
    if (agora - f.mtime > janela) continue;
    vistas[f.pasta] = true;
    const nome = f.pasta.split("/").pop() || "";
    const partes = nome.split("_");
    saida.push({
      nome,
      codigo: partes.length > 1 ? partes[1] : nome,
      assunto: assuntoDe(f.pasta + "/solicitacao.md", partes.slice(2).join(" ")),
      caminho: f.pasta + "/solicitacao.md",
      quando: diasDesde(f.mtime),
    });
  }
  return saida;
}

/* Notas do bau criadas ou tocadas na janela, para o painel mostrar o caderno
 * aprendendo, e nao so entregando. */
function notasNovas(dias, quantas) {
  const janela = (dias || 7) * 86400000;
  const agora = Date.now();
  return app.vault
    .getMarkdownFiles()
    .filter((f) => f.path.startsWith("conhecimento/") && f.name !== "INDICE.md")
    .filter((f) => f.stat && agora - f.stat.mtime <= janela)
    .sort((a, b) => b.stat.mtime - a.stat.mtime)
    .slice(0, quantas || 5)
    .map((f) => ({
      titulo: tituloDe(f),
      gaveta: f.path.split("/")[1] || "",
      caminho: f.path,
    }));
}

function tituloDe(arquivo) {
  const cache = app.metadataCache.getFileCache(arquivo);
  const h = (cache && cache.headings) || [];
  const um = h.find((x) => x.level === 1);
  const bruto = um ? um.heading : arquivo.basename.replace(/[_-]/g, " ");
  /* os titulos do bau vem como "Runbook - Assunto"; o prefixo ja e o chip */
  return bruto.replace(/^(Runbook|Decis[aã]o|Modelo|Refer[eê]ncia|Padr[aã]o)\s*[—-]\s*/i, "");
}

/* A grade da semana vive em gerencial/semana/AAAA-Www/plano-semana.md, escrita
 * pela skill planejar-semana. O painel so LE: a fonte continua sendo o plano.
 * Assincrona porque precisa do conteudo do arquivo, nao so do cache. */
async function semanaPlanejada() {
  const semana = DT.now().toFormat("kkkk-'W'WW");
  const caminho = "gerencial/semana/" + semana + "/plano-semana.md";
  if (!app.vault.getAbstractFileByPath(caminho)) return null;
  let texto = "";
  try {
    texto = await dv.io.load(caminho);
  } catch (e) {
    return null;
  }

  const ordem = ["Seg", "Ter", "Qua", "Qui", "Sex"];
  const dias = ordem.map((d) => ({ dia: d, data: "", tarefas: [] }));
  for (const linha of texto.split(/\r?\n/)) {
    if (!linha.startsWith("|")) continue;
    const col = linha.split("|").map((c) => c.trim());
    if (col.length < 6) continue;
    const i = ordem.indexOf(col[1]);
    if (i < 0) continue;
    dias[i].data = col[2];
    dias[i].tarefas.push({ frente: col[3], tarefa: col[4], tipo: col[5] });
  }
  return { semana, caminho, dias: dias.filter((d) => d.tarefas.length) };
}

/* Uma tarefa da grade esta feita quando a demanda que ela cita ja fechou. O
 * cruzamento e pelo codigo (BI-005, TSK-101): tarefa de fila ou de gate nao
 * cita demanda, entao fica sem marca em vez de virar falso positivo. */
function marcaFeitas(grade) {
  if (!grade) return grade;
  const v = varrerDemandas();
  const aberto = new Set(v.abertas.map((d) => d.codigo));
  const fechado = new Set(
    v.fechadas.map((f) => {
      const partes = (f.pasta.split("/").pop() || "").split("_");
      return partes.length > 1 ? partes[1] : "";
    })
  );
  for (const dia of grade.dias) {
    for (const t of dia.tarefas) {
      const cod = (t.frente.match(/[A-Z]{2,5}-[\d.]+/) || [])[0];
      t.codigo = cod || null;
      t.feita = !!cod && fechado.has(cod) && !aberto.has(cod);
    }
  }
  return grade;
}

function fila(abertas, quantos) {
  const inc = abertas
    .filter((d) => d.prefixo === "INC")
    .sort((a, b) => (b.parada || 0) - (a.parada || 0));
  const resto = abertas
    .filter((d) => d.prefixo !== "INC")
    .sort((a, b) => (b.parada || 0) - (a.parada || 0));

  const saida = inc.slice(0, 2).map((d) => ({ d, motivo: "incidente aberto" }));
  const vistas = {};
  for (const d of resto) {
    if (saida.length >= (quantos || 5)) break;
    if (vistas[d.prefixo]) continue;
    vistas[d.prefixo] = true;
    saida.push({ d, motivo: "parada há " + ditoEmDias(d.parada) });
  }
  return saida;
}

function porFrente(abertas) {
  const g = {};
  for (const d of abertas) {
    if (d.prefixo === "INC") continue;
    (g[d.prefixo] = g[d.prefixo] || []).push(d);
  }
  return Object.keys(g)
    .map((p) => {
      const lista = g[p].sort((a, b) => (b.parada || 0) - (a.parada || 0));
      return {
        prefixo: p,
        rotulo: GAVETAS[p] || p,
        total: lista.length,
        velha: lista[0],
        itens: lista,
        recentes: lista.filter((d) => (d.parada === null ? 99 : d.parada) <= 7).length,
      };
    })
    .sort((a, b) => b.total - a.total);
}

function diarios(quantos) {
  const notas = app.vault
    .getMarkdownFiles()
    .filter((f) => f.path.startsWith("diario/") && /^\d{4}-\d{2}-\d{2}\.md$/.test(f.name))
    .sort((a, b) => (a.name < b.name ? 1 : -1))
    .slice(0, quantos || 6);
  return notas.map((f) => {
    const cache = app.metadataCache.getFileCache(f);
    const h = (cache && cache.headings) || [];
    const dois = h.find((x) => x.level === 2);
    return {
      dia: f.name.replace(".md", ""),
      titulo: dois ? dois.heading : "",
      caminho: f.path,
    };
  });
}

/* Dia com trabalho no log e sem narrativa. O log fica fora do git e é rastro de
 * máquina, então aqui ele pode simplesmente não existir. */
function semNarrativa(janela) {
  const falta = [];
  for (let i = 1; i <= (janela || 14); i++) {
    const d = DT.now().minus({ days: i }).toFormat("yyyy-MM-dd");
    const log = app.vault.getAbstractFileByPath("diario/.log/" + d + ".jsonl");
    const nota = app.vault.getAbstractFileByPath("diario/" + d + ".md");
    if (log && !nota) falta.push(d);
  }
  return falta;
}

/* --------------------------------------------------------------------- CSS */

/* Injetado a quente para o ciclo de edição ser salvar e reabrir, sem reiniciar.
 * O id fixo faz reinjetar substituir em vez de empilhar, e comparar antes de
 * escrever evita repintar a tela à toa. */
dv.io
  .load("sistema/scripts/dashboards.css")
  .then((css) => {
    let tag = document.getElementById("scd-css");
    if (!tag) {
      tag = document.createElement("style");
      tag.id = "scd-css";
      document.head.appendChild(tag);
    }
    if (tag.textContent !== css) tag.textContent = css;
  })
  .catch((e) => console.error("dashboards.css não carregou:", e));

const LIB = {
  DT,
  LIMITE_ESQUECIDA,
  GAVETAS,
  hoje,
  diasDesde,
  ditoEmDias,
  curto,
  abrir,
  aviso,
  ico,
  card,
  tile,
  chip,
  vazio,
  linhaItem,
  faixaFrentes,
  fechadasEm,
  demandas,
  arquivadas,
  emEspera,
  emCurso,
  fechadasDetalhe,
  notasNovas,
  semanaPlanejada,
  marcaFeitas,
  fila,
  porFrente,
  diarios,
  semNarrativa,
};
