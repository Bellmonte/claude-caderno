'use strict';

/* Barra de atalhos do caderno de trabalho.
 *
 * JS puro em CommonJS: sem build, sem TypeScript, sem npm. O mínimo de código
 * mora aqui de propósito, porque mexer neste arquivo exige reiniciar o Obsidian,
 * enquanto os scripts do painel recarregam ao reabrir a nota.
 */

const { Plugin, ItemView, setIcon, Notice } = require('obsidian');

const VIEW_TYPE = 'caderno-nav';

/* troque a sigla e o subtítulo pelos seus (iniciais, nome do repositório) */
const MARCA = { sigla: 'CT', titulo: 'Caderno de trabalho', sub: 'claude-caderno' };

/* Cada item aceita:
 *   caminho  - a nota que o clique abre
 *   arvore   - pasta que o item expande, navegável como o explorador
 *   ordem    - 'desc' põe o mais recente em cima (diário, gerencial)
 *   busca    - abre a busca global no lugar de abrir nota
 * Ícones são nomes do Lucide, que o Obsidian já embute. */
const NAV = [
  { itens: [
      { icone: 'layout-dashboard', texto: 'Início', caminho: 'sistema/dashboards/inicio.md' },
  ]},
  { secao: 'Trabalho', itens: [
      { icone: 'folder-open', texto: 'Demandas',  caminho: 'demandas/LEIA-ME.md',  arvore: 'demandas' },
      { icone: 'line-chart',  texto: 'Gerencial', caminho: 'gerencial/LEIA-ME.md', arvore: 'gerencial', ordem: 'desc' },
      { icone: 'hard-drive',  texto: 'Espelho',   caminho: 'espelho/LEIA-ME.md',   arvore: 'espelho' },
  ]},
  { secao: 'Registro', itens: [
      { icone: 'book-open', texto: 'Diário', caminho: 'diario/LEIA-ME.md',      arvore: 'diario', ordem: 'desc' },
      { icone: 'library',   texto: 'Baú',    caminho: 'conhecimento/INDICE.md', arvore: 'conhecimento' },
  ]},
  { secao: 'Buscas', itens: [
      { icone: 'alert-triangle', texto: 'Incidentes em aberto', busca: 'path:demandas/INC_incidentes -path:fechamento' },
      { icone: 'clock',          texto: 'Demandas em aberto',   busca: 'path:demandas file:solicitacao -file:fechamento' },
      { icone: 'calendar-range', texto: 'Diário deste mês',     busca: 'path:diario ' + new Date().toISOString().slice(0, 7) },
  ]},
  { secao: 'Sistema', itens: [
      { icone: 'scroll-text', texto: 'Regras',    caminho: 'CLAUDE.md' },
      { icone: 'shield',      texto: 'Segurança', caminho: 'SECURITY.md' },
      { icone: 'file-text',   texto: 'Leia-me',   caminho: 'README.md' },
  ]},
];

class PainelNav extends ItemView {
  getViewType() { return VIEW_TYPE; }
  getDisplayText() { return 'Atalhos'; }
  getIcon() { return 'notebook-pen'; }

  async onOpen() {
    this.desenhar();
    /* O evento entrega o arquivo aberto, e é por isso que ele é usado aqui.
       Chamar getActiveFile() no lugar falhava: quando o clique parte da
       própria barra, a view ativa é a sidebar e o retorno vem nulo, então o
       destaque congelava no último item clicado. */
    this.registerEvent(this.app.workspace.on('file-open', (file) => this.destacar(file)));
  }

  desenhar() {
    const raiz = this.contentEl;
    raiz.empty();
    raiz.addClass('cnav');

    const marca = raiz.createDiv({ cls: 'cnav-marca' });
    marca.createDiv({ cls: 'cnav-sigla', text: MARCA.sigla });
    const txt = marca.createDiv();
    txt.createDiv({ cls: 'cnav-marca-tit', text: MARCA.titulo });
    txt.createDiv({ cls: 'cnav-marca-sub', text: MARCA.sub });

    this.itens = [];
    for (const grupo of NAV) {
      if (grupo.secao) raiz.createDiv({ cls: 'cnav-secao', text: grupo.secao });
      for (const it of grupo.itens) this.item(raiz, it);
    }

    this.destacar();

    const rodape = raiz.createDiv({ cls: 'cnav-rodape' });
    const cfg = rodape.createDiv({ cls: 'cnav-item' });
    setIcon(cfg.createSpan({ cls: 'cnav-ico' }), 'settings');
    cfg.createSpan({ text: 'Configurações' });
    cfg.onclick = () => this.app.setting.open();
  }

  item(pai, d) {
    const el = pai.createDiv({ cls: 'cnav-item' });

    /* a seta vem antes do ícone e é o único ponto que expande: clicar no texto
       continua abrindo a nota, que é o gesto mais frequente */
    if (d.arvore) {
      const seta = el.createSpan({ cls: 'cnav-seta' });
      setIcon(seta, 'chevron-right');
      seta.onclick = (ev) => {
        ev.stopPropagation();
        this.alternar(el, d.arvore, d.ordem, 1);
      };
    }

    setIcon(el.createSpan({ cls: 'cnav-ico' }), d.icone);
    el.createSpan({ text: d.texto });
    if (d.caminho) el.dataset.caminho = d.caminho;
    el.onclick = () => (d.busca ? this.buscar(d.busca) : this.abrir(d.caminho));
    this.itens.push(el);
    return el;
  }

  /* Abre e fecha um galho. A sublista nasce como IRMÃ do item, não filha, para
     o recuo ser só visual e o fechar ser um remove() simples. */
  alternar(el, caminho, ordem, nivel) {
    const proximo = el.nextElementSibling;
    if (proximo && proximo.hasClass('cnav-sub')) {
      proximo.remove();
      el.removeClass('is-aberto');
      return;
    }
    if (nivel > 3) return new Notice('Fundo demais para a barra: use o explorador.');
    const sub = createDiv({ cls: 'cnav-sub' });
    el.insertAdjacentElement('afterend', sub);
    el.addClass('is-aberto');
    this.ramo(sub, caminho, ordem, nivel);
  }

  /* Um nível da árvore: pasta vira linha expansível, nota vira linha clicável. */
  ramo(pai, caminho, ordem, nivel) {
    const pasta = this.app.vault.getAbstractFileByPath(caminho);
    if (!pasta || !pasta.children) return;

    const pastas = pasta.children.filter((f) => f.children);
    const notas = pasta.children.filter((f) => !f.children && f.extension === 'md');

    const porNome = (a, b) => (a.name || '').localeCompare(b.name || '', 'pt-BR');
    pastas.sort(porNome);
    notas.sort(porNome);
    /* Mais recente em cima. Funciona porque os nomes do diário e do gerencial
       são datas em AAAA-MM-DD, que ordenam sozinhas: inverter o alfabético já
       é inverter o tempo, sem precisar ler mtime de cada arquivo. */
    if (ordem === 'desc') {
      pastas.reverse();
      notas.reverse();
    }

    for (const f of pastas) {
      const el = pai.createDiv({ cls: 'cnav-sub-item is-pasta' });
      setIcon(el.createSpan({ cls: 'cnav-seta' }), 'chevron-right');
      setIcon(el.createSpan({ cls: 'cnav-ico' }), 'folder');
      el.createSpan({ text: f.name });
      el.onclick = (ev) => {
        ev.stopPropagation();
        this.alternar(el, f.path, ordem, nivel + 1);
      };
    }

    for (const f of notas) {
      const el = pai.createDiv({ cls: 'cnav-sub-item' });
      setIcon(el.createSpan({ cls: 'cnav-ico' }), 'file-text');
      el.createSpan({ text: f.basename });
      el.dataset.caminho = f.path;
      el.onclick = (ev) => {
        ev.stopPropagation();
        this.abrir(f.path);
      };
      this.itens.push(el);
    }

    if (!pastas.length && !notas.length) {
      pai.createDiv({ cls: 'cnav-sub-vazio', text: 'vazio' });
    }
  }

  /* Nunca abrir na própria sidebar: sem isso o arquivo nasce aqui dentro e
     some ao trocar de view. Pega o leaf mais recente da área principal. */
  async abrir(caminho) {
    const alvo = this.app.vault.getAbstractFileByPath(caminho);
    if (!alvo) return new Notice('Não achei: ' + caminho);

    /* Pasta não abre como nota. O mais próximo de navegar é revelá-la no
       explorador, já expandida; a busca fica como último recurso. */
    if (!alvo.extension) {
      const exp = this.app.internalPlugins.getPluginById('file-explorer');
      if (exp && exp.instance && exp.instance.revealInFolder) {
        exp.instance.revealInFolder(alvo);
        return;
      }
      return this.buscar('path:"' + caminho + '"');
    }

    const ws = this.app.workspace;
    const leaf = ws.getMostRecentLeaf(ws.rootSplit) || ws.getLeaf('tab');
    await leaf.openFile(alvo);
  }

  buscar(consulta) {
    const busca = this.app.internalPlugins.getPluginById('global-search');
    if (!busca || !busca.instance) return new Notice('A busca global está desligada.');
    busca.instance.openGlobalSearch(consulta);
  }

  destacar(file) {
    const alvo = file || this.app.workspace.getActiveFile();
    const caminho = alvo ? alvo.path : '';
    for (const el of this.itens || []) {
      el.toggleClass('is-active', !!el.dataset.caminho && el.dataset.caminho === caminho);
    }
  }
}

module.exports = class CadernoNav extends Plugin {
  async onload() {
    /* a lib do painel consome o setIcon daqui, porque ele não está no escopo
       do dataviewjs */
    this.setIcon = setIcon;

    this.registerView(VIEW_TYPE, (leaf) => new PainelNav(leaf));
    this.addRibbonIcon('notebook-pen', 'Atalhos do caderno', () => this.ativar());
    this.addCommand({
      id: 'abrir-navegacao',
      name: 'Abrir os atalhos do caderno',
      callback: () => this.ativar(),
    });

    this.app.workspace.onLayoutReady(() => this.ativar());
  }

  /* reaproveita o leaf existente antes de criar outro, senão cada boot
     empilha mais uma cópia da barra */
  async ativar() {
    const ws = this.app.workspace;
    const achados = ws.getLeavesOfType(VIEW_TYPE);
    if (achados.length) return ws.revealLeaf(achados[0]);
    const leaf = ws.getLeftLeaf(false);
    await leaf.setViewState({ type: VIEW_TYPE, active: true });
    ws.revealLeaf(leaf);
  }

  onunload() {
    this.app.workspace.detachLeavesOfType(VIEW_TYPE);
  }
};
