# Renderiza um template de ata .docx com tags no padrao docxtemplater (por exemplo
# conhecimento/modelos/ata-reuniao.docx) com os dados da ata.
# Replica o subconjunto de docxtemplater que o template usa: substituicao simples,
# loop de paragrafo ({#lista}{.}{/lista}), loop de linha de tabela ({#acoes}...{/acoes})
# e bloco condicional ({#tem_ausentes}...{/tem_ausentes}).
import json, re, shutil, sys, zipfile

TPL = sys.argv[1]
DADOS = sys.argv[2]
SAIDA = sys.argv[3]

def esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))

d = json.load(open(DADOS, encoding='utf-8'))
d['participantes_txt'] = ', '.join(d.get('participantes') or [])
d['ausentes_txt'] = ', '.join(d.get('ausentes') or [])
d['tem_ausentes'] = bool([a for a in (d.get('ausentes') or []) if a])

zin = zipfile.ZipFile(TPL)
xml = zin.read('word/document.xml').decode('utf-8')

P = re.compile(r'<w:p(?: [^>]*)?>.*?</w:p>', re.S)
TR = re.compile(r'<w:tr(?: [^>]*)?>.*?</w:tr>', re.S)

def bloco_que_contem(rx, marca):
    for m in rx.finditer(xml):
        if marca in m.group(0):
            return m.group(0)
    raise SystemExit('marca nao encontrada: ' + marca)

# 1) tabela de acoes: repete a linha modelo
linha = bloco_que_contem(TR, '{#acoes}')
saidas = []
for a in d.get('acoes') or []:
    novo = linha
    novo = novo.replace('{#acoes}{acao}', esc(a['acao']))
    novo = novo.replace('{responsavel}', esc(a['responsavel']))
    novo = novo.replace('{prazo}{/acoes}', esc(a['prazo']))
    saidas.append(novo)
xml = xml.replace(linha, ''.join(saidas))

# 2) loops de bullet
for chave in ('decisoes', 'discussoes', 'riscos', 'proximos_passos', 'observacoes'):
    par = bloco_que_contem(P, '{#%s}' % chave)
    saidas = []
    for item in d.get(chave) or []:
        novo = par
        novo = novo.replace('{#%s}' % chave, '').replace('{/%s}' % chave, '')
        novo = novo.replace('{.}', esc(item))
        saidas.append(novo)
    xml = xml.replace(par, ''.join(saidas))

# 3) bloco condicional de ausentes
par = bloco_que_contem(P, '{#tem_ausentes}')
if d['tem_ausentes']:
    novo = par.replace('{#tem_ausentes}', '').replace('{/tem_ausentes}', '')
    novo = novo.replace('{ausentes_txt}', esc(d['ausentes_txt']))
    xml = xml.replace(par, novo)
else:
    # Se o paragrafo mora numa celula, apagar so ele deixa a celula sem <w:p>,
    # o que o Word recusa como arquivo corrompido: nesse caso sai a linha inteira.
    alvo = par
    for m in TR.finditer(xml):
        if '{#tem_ausentes}' in m.group(0):
            alvo = m.group(0)
            break
    xml = xml.replace(alvo, '')

# 4) substituicoes simples
for chave in ('titulo', 'data', 'participantes_txt', 'tipo', 'resumo_executivo', 'contexto_objetivo'):
    xml = xml.replace('{%s}' % chave, esc(d[chave]))

sobrou = re.findall(r'\{[^}]{1,40}\}', xml)
if sobrou:
    raise SystemExit('tags nao resolvidas: %r' % sobrou)

shutil.copy(TPL, SAIDA)
zout_tmp = SAIDA + '.tmp'
with zipfile.ZipFile(SAIDA) as zsrc, zipfile.ZipFile(zout_tmp, 'w', zipfile.ZIP_DEFLATED) as zdst:
    for it in zsrc.infolist():
        dados = zsrc.read(it.filename)
        if it.filename == 'word/document.xml':
            dados = xml.encode('utf-8')
        zdst.writestr(it, dados)
shutil.move(zout_tmp, SAIDA)
print('ok:', SAIDA)

# 5) rotulos fixos do template estao em ASCII; documento da casa sai acentuado.
ACENTOS = {
    '3. Principais decisoes': '3. Principais decisões',
    '4. Discussoes-chave': '4. Discussões-chave',
    '5. Pendencias e acoes': '5. Pendências e ações',
    '7. Proximos passos': '7. Próximos passos',
    '8. Observacoes': '8. Observações',
    '>Acao<': '>Ação<',
    '>Responsavel<': '>Responsável<',
}
with zipfile.ZipFile(SAIDA) as z:
    partes = {i.filename: z.read(i.filename) for i in z.infolist()}
    ordem = z.infolist()
doc = partes['word/document.xml'].decode('utf-8')
for a, b in ACENTOS.items():
    doc = doc.replace(a, b)
partes['word/document.xml'] = doc.encode('utf-8')
with zipfile.ZipFile(SAIDA, 'w', zipfile.ZIP_DEFLATED) as z:
    for it in ordem:
        z.writestr(it, partes[it.filename])
print('rotulos acentuados')
