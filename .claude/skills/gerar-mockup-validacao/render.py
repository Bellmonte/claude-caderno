"""
render.py — transforma um mockup HTML autocontido em PDF de uma pagina ou GIF animado.
Skill gerar-mockup-validacao. Sem dependencia de rede: usa o Chrome instalado + Pillow.

    python render.py pdf  mockup.html saida.pdf [--retrato] [--claro] [--com-margem]
    python render.py gif  mockup.html saida.gif --estagios 8 [--largura 920] [--ms 1100]

POR QUE ESTE SCRIPT EXISTE (as tres armadilhas que ele resolve)

1. O PDF sai quebrado se voce so mandar imprimir.
   O Chrome usa a LARGURA DO PAPEL como viewport. A4 paisagem da ~1054px e retrato ~733px,
   abaixo do breakpoint do mockup — entao o CSS responsivo empilha tudo e o layout quebra.
   Aqui o conteudo e' renderizado numa largura FIXA, as media queries sao neutralizadas com
   !important e a pagina inteira e' reduzida por transform:scale.

2. Escalar com `zoom` ou com transform sem largura fixa NAO resolve a paginacao.
   A caixa de layout continua do tamanho original e o Chrome pagina igual (as vezes gera
   ate uma pagina a mais). Por isso a escala anda junto com width fixa + overflow hidden.

3. Conferir com @media screen numa janela larga MENTE.
   Nessa largura o breakpoint nao dispara e o layout aparece certo enquanto o PDF sai
   quebrado. O modo --check renderiza nas regras de impressao e em DUAS larguras: se as
   duas saem iguais, o layout nao depende mais do viewport e o PDF esta correto.

O GIF revela o desenho por estagios: cada elemento com data-s="N" aparece a partir do
estagio N (elemento sem data-s e' o cenario, aparece sempre). O script escreve data-stage
no <html>, captura um quadro por estagio e monta o GIF com paleta unica (sem cintilacao).
"""
import argparse, os, re, shutil, subprocess, sys, tempfile

CHROME = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]
PX_MM = 96 / 25.4          # 1mm em px CSS a 96dpi
LARGURA_BASE = 1040        # a largura em que o mockup foi desenhado

# Neutraliza o responsivo e compacta a tipografia para o formato impresso.
CSS_IMPRESSAO = """
    .themetog{display:none !important}
    .wrap{width:%(base)dpx;max-width:%(base)dpx;padding:0;margin:0}
    h1{font-size:22px;margin-bottom:3px} .sub{font-size:12.5px}
    .passos{margin-top:16px} .passo{padding:9px 9px}
    .passo .l{font-size:9px;margin-bottom:3px} .passo .v{font-size:11px}
    .seta{font-size:13px;padding:0 5px}
    .board{margin-top:14px;padding:6px 6px 2px}
    .etapas{margin-top:14px;gap:12px} .et{padding:12px 14px}
    .et h2{font-size:14px} .et p{font-size:11.5px;margin:8px 0 10px}
    pre{font-size:10.5px;padding:9px 10px;line-height:1.55}
    footer{margin-top:14px;font-size:10.5px}
    .passos{flex-direction:row !important;overflow:visible !important}
    .passo{text-align:center !important}
    .seta{transform:none !important}
    .etapas{grid-template-columns:1fr 1fr !important}
"""


def chrome():
    for c in CHROME:
        if os.path.exists(c):
            return c
    sys.exit("Chrome/Edge nao encontrado. Ajuste a lista CHROME no topo do script.")


def roda(args):
    subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)


def url(p):
    return "file:///" + os.path.abspath(p).replace("\\", "/")


def com_tema(html, claro):
    tema = "light" if claro else "dark"
    return re.sub(r"<html([^>]*)>", lambda m: "<html%s data-theme=\"%s\">" % (
        re.sub(r'\s*data-theme="[^"]*"', "", m.group(1)), tema), html, count=1)


def altura_do_conteudo(html_path, largura, tmp):
    """Renderiza numa janela alta e acha a ultima linha que difere do fundo."""
    from PIL import Image
    png = os.path.join(tmp, "medir.png")
    roda([chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars",
          "--window-size=%d,2400" % largura, "--screenshot=" + png, url(html_path)])
    im = Image.open(png).convert("RGB"); w, h = im.size; px = im.load(); bg = px[3, h - 3]
    for y in range(h - 1, -1, -1):
        if any(sum(abs(a - b) for a, b in zip(px[x, y], bg)) > 18 for x in range(0, w, 6)):
            return y + 6
    return h


def gerar_pdf(entrada, saida, retrato, claro, com_margem, check):
    html = com_tema(open(entrada, encoding="utf-8").read(), claro)
    larg_mm, alt_mm = (210, 297) if retrato else (297, 210)
    margem = 8 if com_margem else 0          # margem 0 = fundo sangra ate a borda
    resp = 0 if com_margem else 30           # sem margem, o respiro vira padding interno
    pag_w, pag_h = round(larg_mm * PX_MM), round(alt_mm * PX_MM)
    util_w, util_h = pag_w - 2 * round(margem * PX_MM), pag_h - 2 * round(margem * PX_MM)

    with tempfile.TemporaryDirectory() as tmp:
        base_css = CSS_IMPRESSAO % {"base": LARGURA_BASE}
        medir = os.path.join(tmp, "medir.html")
        open(medir, "w", encoding="utf-8").write(
            html.replace("</head>", "<style>%s</style></head>" % base_css))
        alt = altura_do_conteudo(medir, LARGURA_BASE, tmp)

        esc = round(min((util_w - 2 * resp) / LARGURA_BASE, (util_h - 2 * resp) / alt) - 0.006, 4)
        offx = round((util_w - LARGURA_BASE * esc) / 2)
        offy = round((util_h - alt * esc) / 2)
        css = """<style>
  @page{ size:A4 %s; margin:%dmm; }
  @media print{
    html,body{width:100%%;height:100%%;margin:0;overflow:hidden;background:var(--bg) !important;
      -webkit-print-color-adjust:exact;print-color-adjust:exact}
%s
    .wrap{transform:translate(%dpx,%dpx) scale(%s);transform-origin:top left}
  }
</style>""" % ("portrait" if retrato else "landscape", margem, base_css, offx, offy, esc)
        alvo = os.path.join(tmp, "print.html")
        open(alvo, "w", encoding="utf-8").write(html.replace("</head>", css + "</head>"))
        roda([chrome(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
              "--print-to-pdf=" + os.path.abspath(saida), url(alvo)])

        if check:  # duas larguras: se saem iguais, o layout nao depende do viewport
            from PIL import Image
            ck = os.path.join(tmp, "check.html")
            open(ck, "w", encoding="utf-8").write(
                open(alvo, encoding="utf-8").read().replace("@media print{", "@media screen{", 1))
            for nome, w in (("larga", util_w), ("estreita", round(util_w * 0.7))):
                p = os.path.splitext(saida)[0] + "_check_" + nome + ".png"
                roda([chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                      "--window-size=%d,%d" % (w, util_h), "--screenshot=" + p, url(ck)])
                print("  conferencia:", p)

    d = open(saida, "rb").read()
    print("PDF:", saida, "|", d.count(b"/Type /Page") - d.count(b"/Type /Pages"), "pagina(s) |",
          larg_mm, "x", alt_mm, "mm | escala", esc, "|", round(len(d) / 1024), "KB")


def gerar_gif(entrada, saida, estagios, largura, ms, ms_final, claro, janela):
    from PIL import Image
    html = com_tema(open(entrada, encoding="utf-8").read(), claro)
    if 'data-stage' not in html:
        html = html.replace("<html", "<html data-stage=\"%d\"" % estagios, 1)
    # data-s="N"    -> aparece A PARTIR do estagio N e fica (o desenho se constroi)
    # data-on="N"   -> fica esmaecido e ACENDE nos estagios listados (aceita "3" ou "3 4 5")
    # sem marca   -> cenario, visivel desde o primeiro quadro
    css = ["<style id=\"anim\">", ".themetog{display:none}",
           "[data-s]{opacity:0}", "[data-on]{opacity:.30}"]
    for k in range(1, estagios + 1):
        vis = ",".join('[data-stage="%d"] [data-s="%d"]' % (k, j) for j in range(1, k + 1))
        css.append(vis + "{opacity:1}")
        css.append('[data-stage="%d"] [data-on~="%d"]{opacity:1}' % (k, k))
    css.append("</style>")
    html = html.replace("</head>", "\n".join(css) + "\n</head>")

    with tempfile.TemporaryDirectory() as tmp:
        quadros = []
        for k in range(1, estagios + 1):
            f = os.path.join(tmp, "f%d.html" % k)
            open(f, "w", encoding="utf-8").write(
                re.sub(r'data-stage="\d+"', 'data-stage="%d"' % k, html, count=1))
            png = os.path.join(tmp, "q%d.png" % k)
            roda([chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                  "--window-size=%d,%d" % janela, "--screenshot=" + png, url(f)])
            quadros.append(Image.open(png).convert("RGB"))

        # corta o vazio abaixo do conteudo (usa o ultimo quadro, o mais cheio)
        im = quadros[-1]; w, h = im.size; px = im.load(); bg = px[3, h - 3]
        ult = h - 1
        for y in range(h - 1, -1, -1):
            if any(sum(abs(a - b) for a, b in zip(px[x, y], bg)) > 18 for x in range(0, w, 6)):
                ult = y; break
        alt = min(h, ult + 22)
        nh = round(alt * largura / w)
        quadros = [q.crop((0, 0, w, alt)).resize((largura, nh), Image.LANCZOS) for q in quadros]
        # paleta unica do quadro mais cheio: sem ela as cores cintilam entre os quadros
        pal = quadros[-1].convert("P", palette=Image.ADAPTIVE, colors=200)
        quadros = [q.quantize(palette=pal, dither=Image.NONE) for q in quadros]
        dur = [ms] * (estagios - 1) + [ms_final]
        quadros[0].save(saida, save_all=True, append_images=quadros[1:], duration=dur,
                        loop=0, optimize=True, disposal=2)
    print("GIF:", saida, "|", largura, "x", nh, "|", estagios, "quadros |",
          round(os.path.getsize(saida) / 1024), "KB |", sum(dur) / 1000, "s")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="modo", required=True)

    p = sub.add_parser("pdf", help="PDF de uma pagina")
    p.add_argument("entrada"); p.add_argument("saida")
    p.add_argument("--retrato", action="store_true", help="A4 em pe (padrao: paisagem)")
    p.add_argument("--claro", action="store_true", help="tema claro (padrao: escuro)")
    p.add_argument("--com-margem", action="store_true",
                   help="margem branca de 8mm (padrao: sem margem, fundo ate a borda)")
    p.add_argument("--check", action="store_true", help="salva as duas capturas de conferencia")

    g = sub.add_parser("gif", help="GIF animado por estagios (data-s no SVG)")
    g.add_argument("entrada"); g.add_argument("saida")
    g.add_argument("--estagios", type=int, required=True)
    g.add_argument("--largura", type=int, default=920)
    g.add_argument("--ms", type=int, default=1100, help="ms por quadro")
    g.add_argument("--ms-final", type=int, default=2600, help="ms do ultimo quadro")
    g.add_argument("--claro", action="store_true")
    g.add_argument("--janela", default="1080x1000", help="janela de captura, ex 1080x1000")

    a = ap.parse_args()
    if a.modo == "pdf":
        gerar_pdf(a.entrada, a.saida, a.retrato, a.claro, a.com_margem, a.check)
    else:
        jw, jh = (int(x) for x in a.janela.lower().split("x"))
        gerar_gif(a.entrada, a.saida, a.estagios, a.largura, a.ms, a.ms_final, a.claro, (jw, jh))


if __name__ == "__main__":
    main()
