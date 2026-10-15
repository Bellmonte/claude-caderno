# Gera o template ATA no formato "action minutes" (registro do que foi decidido).
#
# Mesmo contrato de tags do docxtemplater usado pelo render_ata.py, para qualquer
# aplicacao que ja renderize esse contrato trocar de template sem mudanca de codigo.
# O que muda e a ORDEM e o PESO:
#   topo  -> identificacao + resumo em caixa
#   corpo -> 1 DECISOES (D1, D2...) e 2 ACOES (quadro com dono e prazo)
#   depois-> 3 RISCOS E BLOQUEIOS, 4 PROXIMOS PASSOS
#   fim   -> 5 CONTEXTO E DISCUSSAO (corpo menor), 6 OBSERVACOES
#
# Layout: A4 margens 2cm, Arial 10.5, entrelinha simples, sem recuo de paragrafo,
# titulo de secao na cor de acento com filete, quadro com cabecalho sombreado.
# Paleta neutra (acento #2F6F8F): troque as constantes de cor abaixo pela identidade
# visual da sua empresa.
import sys, zipfile
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SAIDA = sys.argv[1]

FONTE = 'Arial'
CORPO = Pt(10.5)
MENOR = Pt(9.5)
ACENTO = RGBColor(0x2F, 0x6F, 0x8F)
GRAFITE = RGBColor(0x33, 0x3A, 0x40)

doc = Document()

s = doc.sections[0]
s.page_width, s.page_height = Cm(21), Cm(29.7)
s.left_margin = s.right_margin = Cm(2)
s.top_margin, s.bottom_margin = Cm(1.8), Cm(1.8)
s.header_distance = s.footer_distance = Cm(1)

normal = doc.styles['Normal']
normal.font.name = FONTE
normal.font.size = CORPO
normal.font.color.rgb = RGBColor(0, 0, 0)
normal._element.rPr.rFonts.set(qn('w:eastAsia'), FONTE)
pf = normal.paragraph_format
pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
pf.space_before, pf.space_after = Pt(0), Pt(0)
pf.alignment = WD_ALIGN_PARAGRAPH.LEFT



# A ordem dos filhos de pPr/tblPr e' fixa no schema do OOXML: inserir fora de ordem
# gera um .docx que o Word recusa como corrompido.
ORDEM_PPR = ('w:pStyle', 'w:keepNext', 'w:keepLines', 'w:pageBreakBefore', 'w:framePr',
             'w:widowControl', 'w:numPr', 'w:suppressLineNumbers', 'w:pBdr', 'w:shd',
             'w:tabs', 'w:suppressAutoHyphens', 'w:kinsoku', 'w:wordWrap', 'w:overflowPunct',
             'w:topLinePunct', 'w:autoSpaceDE', 'w:autoSpaceDN', 'w:bidi', 'w:adjustRightInd',
             'w:snapToGrid', 'w:spacing', 'w:ind', 'w:contextualSpacing', 'w:mirrorIndents',
             'w:suppressOverlap', 'w:jc', 'w:textDirection', 'w:textAlignment',
             'w:textboxTightWrap', 'w:outlineLvl', 'w:divId', 'w:cnfStyle', 'w:rPr',
             'w:sectPr', 'w:pPrChange')
ORDEM_TBLPR = ('w:tblStyle', 'w:tblpPr', 'w:tblOverlap', 'w:bidiVisual',
               'w:tblStyleRowBandSize', 'w:tblStyleColBandSize', 'w:tblW', 'w:jc',
               'w:tblCellSpacing', 'w:tblInd', 'w:tblBorders', 'w:shd', 'w:tblLayout',
               'w:tblCellMar', 'w:tblLook', 'w:tblCaption', 'w:tblDescription')


def inserir(pai, el, ordem):
    alvo = ordem.index(qn_reverso(el.tag))
    for i, filho in enumerate(pai):
        if qn_reverso(filho.tag) in ordem and ordem.index(qn_reverso(filho.tag)) > alvo:
            pai.insert(i, el)
            return
    pai.append(el)


def qn_reverso(tag):
    return 'w:' + tag.split('}')[-1]


def sombrear(el, cor):
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), cor)
    el.append(shd) if el.tag.endswith('}tcPr') else inserir(el, shd, ORDEM_PPR)


def par(texto='', *, negrito=False, alinha=WD_ALIGN_PARAGRAPH.LEFT, antes=0, depois=0,
        tamanho=None, cor=None, caixa_alta=False, italico=False):
    p = doc.add_paragraph()
    p.paragraph_format.alignment = alinha
    p.paragraph_format.space_before = Pt(antes)
    p.paragraph_format.space_after = Pt(depois)
    if texto:
        r = p.add_run(texto.upper() if caixa_alta else texto)
        r.bold, r.italic = negrito, italico
        if tamanho:
            r.font.size = tamanho
        if cor is not None:
            r.font.color.rgb = cor
    return p


def secao(numero, titulo, *, antes=13):
    """Titulo de secao: numero + titulo na cor de acento, com filete embaixo."""
    p = par(f'{numero}  {titulo}', negrito=True, caixa_alta=True, cor=ACENTO,
            tamanho=Pt(10), antes=antes, depois=5)
    pPr = p._p.get_or_add_pPr()
    bd = OxmlElement('w:pBdr')
    b = OxmlElement('w:bottom')
    b.set(qn('w:val'), 'single'); b.set(qn('w:sz'), '6')
    b.set(qn('w:space'), '2'); b.set(qn('w:color'), 'C5D3DB')
    bd.append(b); inserir(pPr, bd, ORDEM_PPR)
    return p


def item(numid, texto, *, tamanho=None, cor=None, esquerda=0.8, pendura=0.8, depois=4):
    p = doc.add_paragraph()
    fmt = p.paragraph_format
    fmt.alignment = WD_ALIGN_PARAGRAPH.LEFT
    fmt.left_indent, fmt.first_line_indent = Cm(esquerda), Cm(-pendura)
    fmt.space_before, fmt.space_after = Pt(0), Pt(depois)
    pPr = p._p.get_or_add_pPr()
    numPr = OxmlElement('w:numPr')
    ilvl = OxmlElement('w:ilvl'); ilvl.set(qn('w:val'), '0')
    num = OxmlElement('w:numId'); num.set(qn('w:val'), str(numid))
    numPr.append(ilvl); numPr.append(num)
    inserir(pPr, numPr, ORDEM_PPR)
    r = p.add_run(texto)
    if tamanho:
        r.font.size = tamanho
    if cor is not None:
        r.font.color.rgb = cor
    return p


# ── cabecalho de pagina: identificacao curta + paginacao ─────────────────────
cab = s.header.paragraphs[0]
cab.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = cab.add_run('Ata de reunião  ·  ')
r.font.size = Pt(8); r.font.color.rgb = RGBColor(0x8A, 0x93, 0x9A); r.font.name = FONTE
fld = OxmlElement('w:fldSimple'); fld.set(qn('w:instr'), 'PAGE')
rr = OxmlElement('w:r')
rPr = OxmlElement('w:rPr')
sz = OxmlElement('w:sz'); sz.set(qn('w:val'), '16'); rPr.append(sz)
rr.append(rPr)
t = OxmlElement('w:t'); t.text = '1'; rr.append(t); fld.append(rr)
cab._p.append(fld)

# ── titulo ──────────────────────────────────────────────────────────────────
par('{titulo}', negrito=True, tamanho=Pt(16), cor=ACENTO, depois=2)

# ── identificacao ───────────────────────────────────────────────────────────
ident = doc.add_table(rows=4, cols=2)
ident.alignment = WD_TABLE_ALIGNMENT.LEFT
ident.autofit = False
linhas = (('Data', '{data}'), ('Tipo', '{tipo}'),
          ('Participantes', '{participantes_txt}'),
          ('Ausente', '{#tem_ausentes}{ausentes_txt}{/tem_ausentes}'))
for i, (rotulo, valor) in enumerate(linhas):
    for j, (txt, bold, cor) in enumerate(((rotulo, True, GRAFITE), (valor, False, None))):
        c = ident.cell(i, j)
        c.width = Cm(3.2) if j == 0 else Cm(13.8)
        p = c.paragraphs[0]
        p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(1), Pt(1)
        run = p.add_run(txt); run.bold = bold; run.font.size = MENOR
        if cor is not None:
            run.font.color.rgb = cor
bd = OxmlElement('w:tblBorders')
for lado in ('top', 'bottom', 'left', 'right', 'insideH', 'insideV'):
    b = OxmlElement(f'w:{lado}'); b.set(qn('w:val'), 'none')
    b.set(qn('w:sz'), '0'); b.set(qn('w:space'), '0'); b.set(qn('w:color'), 'auto')
    bd.append(b)
inserir(ident._tbl.tblPr, bd, ORDEM_TBLPR)

# ── resumo em caixa ─────────────────────────────────────────────────────────
resumo = par('{resumo_executivo}', antes=10, depois=2, tamanho=MENOR)
resumo.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
resumo.paragraph_format.left_indent = Cm(0.25)
resumo.paragraph_format.right_indent = Cm(0.25)
rPr_p = resumo._p.get_or_add_pPr()
sombrear(rPr_p, 'F1F5F8')
bd = OxmlElement('w:pBdr')
for lado, cor, tam in (('left', '2F6F8F', '18'), ('top', 'E0E8ED', '6'),
                       ('bottom', 'E0E8ED', '6'), ('right', 'E0E8ED', '6')):
    b = OxmlElement(f'w:{lado}')
    b.set(qn('w:val'), 'single'); b.set(qn('w:sz'), tam)
    b.set(qn('w:space'), '6'); b.set(qn('w:color'), cor)
    bd.append(b)
inserir(rPr_p, bd, ORDEM_PPR)

# ── 1 decisoes ──────────────────────────────────────────────────────────────
secao('1', 'Decisões')
item(201, '{#decisoes}{.}{/decisoes}')

# ── 2 acoes ─────────────────────────────────────────────────────────────────
secao('2', 'Ações')
tab = doc.add_table(rows=2, cols=3)
tab.alignment = WD_TABLE_ALIGNMENT.LEFT
tab.autofit = False
larguras = (Cm(9.2), Cm(3.6), Cm(4.2))
cabecalhos = ('O que fazer', 'Responsável', 'Prazo')
celulas = ('{#acoes}{acao}', '{responsavel}', '{prazo}{/acoes}')
for i, (cab_txt, cel_txt) in enumerate(zip(cabecalhos, celulas)):
    for linha, texto, negrito in ((0, cab_txt, True), (1, cel_txt, False)):
        c = tab.cell(linha, i)
        c.width = larguras[i]
        if linha == 0:
            sombrear(c._tc.get_or_add_tcPr(), 'EAF0F4')
        p = c.paragraphs[0]
        p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(3), Pt(3)
        run = p.add_run(texto); run.bold = negrito; run.font.size = MENOR
        if linha == 0:
            run.font.color.rgb = GRAFITE

bd = OxmlElement('w:tblBorders')
for lado, cor, tam in (('top', '2F6F8F', '12'), ('bottom', '2F6F8F', '12'),
                       ('insideH', 'D9E2E8', '6')):
    b = OxmlElement(f'w:{lado}')
    b.set(qn('w:val'), 'single'); b.set(qn('w:sz'), tam)
    b.set(qn('w:space'), '0'); b.set(qn('w:color'), cor)
    bd.append(b)
for lado in ('left', 'right', 'insideV'):
    b = OxmlElement(f'w:{lado}'); b.set(qn('w:val'), 'none')
    b.set(qn('w:sz'), '0'); b.set(qn('w:space'), '0'); b.set(qn('w:color'), 'auto')
    bd.append(b)
inserir(tab._tbl.tblPr, bd, ORDEM_TBLPR)
for i, linha_tab in enumerate(tab.rows):
    trPr = linha_tab._tr.get_or_add_trPr()
    trPr.append(OxmlElement('w:cantSplit'))
    if i == 0:
        trPr.append(OxmlElement('w:tblHeader'))

# ── 3 riscos e 4 proximos passos ────────────────────────────────────────────
secao('3', 'Riscos e bloqueios')
item(202, '{#riscos}{.}{/riscos}')

secao('4', 'Próximos passos')
item(203, '{#proximos_passos}{.}{/proximos_passos}')

# ── 5 contexto e discussao (rebaixado, corpo menor) ─────────────────────────
secao('5', 'Contexto e discussão')
ctx = par('{contexto_objetivo}', tamanho=MENOR, cor=GRAFITE, depois=5)
ctx.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
item(204, '{#discussoes}{.}{/discussoes}', tamanho=MENOR, cor=GRAFITE)

# ── 6 observacoes ───────────────────────────────────────────────────────────
secao('6', 'Observações')
item(205, '{#observacoes}{.}{/observacoes}', tamanho=MENOR, cor=GRAFITE)

doc.save(SAIDA)

# ── numeracao: D1 D2 nas decisoes, marcador nas demais listas ───────────────
def abstract(aid, fmt, texto, esquerda, pendura, fonte=None):
    f = f'<w:rFonts w:ascii="{fonte}" w:hAnsi="{fonte}" w:hint="default"/>' if fonte else ''
    return (f'<w:abstractNum w:abstractNumId="{aid}"><w:multiLevelType w:val="singleLevel"/>'
            f'<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="{fmt}"/>'
            f'<w:lvlText w:val="{texto}"/><w:lvlJc w:val="left"/>'
            f'<w:pPr><w:ind w:left="{esquerda}" w:hanging="{pendura}"/></w:pPr>'
            f'<w:rPr>{f}</w:rPr></w:lvl></w:abstractNum>')

blocos = (abstract('910', 'decimal', 'D%1', '454', '454')
          + abstract('911', 'bullet', '•', '454', '454', 'Arial'))
nums = ''.join(
    f'<w:num w:numId="{n}"><w:abstractNumId w:val="{a}"/>'
    f'<w:lvlOverride w:ilvl="0"><w:startOverride w:val="1"/></w:lvlOverride></w:num>'
    for n, a in ((201, '910'), (202, '911'), (203, '911'), (204, '911'), (205, '911')))

with zipfile.ZipFile(SAIDA) as z:
    partes = {i.filename: z.read(i.filename) for i in z.infolist()}
    ordem = z.infolist()
num_xml = partes['word/numbering.xml'].decode('utf-8')
num_xml = num_xml.replace('<w:num ', blocos + '<w:num ', 1) if '<w:num ' in num_xml \
    else num_xml.replace('</w:numbering>', blocos + '</w:numbering>')
num_xml = num_xml.replace('</w:numbering>', nums + '</w:numbering>')
partes['word/numbering.xml'] = num_xml.encode('utf-8')
with zipfile.ZipFile(SAIDA, 'w', zipfile.ZIP_DEFLATED) as z:
    for it in ordem:
        z.writestr(it, partes[it.filename])

print('template action minutes gerado:', SAIDA)
