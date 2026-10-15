#!/usr/bin/env python3
"""Verificador de formatacao de DAX e M, contra o PADRAO_FORMATACAO.

Le .tmdl, .dax, .pq e .m (ou pastas inteiras), extrai cada expressao DAX (medida,
coluna calculada, item de calculo, tabela calculada) e cada expressao M (particao,
expression do expressions.tmdl), desconta a indentacao estrutural do TMDL e aponta
cada violacao com arquivo, objeto, linha e regra. Roda sem rede e nao altera nada.

Uso:
    python lint_formatacao.py CAMINHO [CAMINHO ...]      # lista as violacoes
    python lint_formatacao.py PASTA --relatorio           # total por regra e piores objetos
    python lint_formatacao.py ARQUIVO --delta              # so objetos que mudaram desde o HEAD
    python lint_formatacao.py ... --json                  # saida em JSON

Saida 0 sem violacao, 1 com violacao. O identificador de cada regra e o do padrao.
Regras de revisao humana (DAX-11, M-06 no nome do parametro, M-09) ficam fora daqui.
"""
import argparse
import bisect
import collections
import json
import os
import re
import subprocess
import sys

LIMITE = 100
EXTENSOES = (".tmdl", ".dax", ".pq", ".m")

PALAVRAS_DAX = {"VAR", "RETURN", "IN", "TRUE", "FALSE", "ASC", "DESC", "DAY", "WEEK", "MONTH",
                "QUARTER", "YEAR", "EVALUATE", "DEFINE", "MEASURE", "ORDER", "BY", "NOT"}
SEMPRE_QUEBRA = {"CALCULATE", "CALCULATETABLE"}
OPS_DAX = ["<=", ">=", "<>", "&&", "||", "==", "+", "-", "*", "/", "&", "=", "<", ">", "^"]
OPS_M = ["=>", "<=", ">=", "<>", "+", "-", "*", "/", "&", "=", "<", ">"]
PREFIXO_UNARIO = {"open", "comma", "op", None}
PALAVRAS_ANTES_DE_UNARIO = {"RETURN", "VAR", "IN", "each", "then", "else", "if", "in", "and", "or", "not"}


# ---------------------------------------------------------------- tokens

class Tok:
    __slots__ = ("tipo", "valor", "ini", "fim", "linha", "col", "linha_fim")

    def __init__(self, tipo, valor, ini, fim):
        self.tipo, self.valor, self.ini, self.fim = tipo, valor, ini, fim

    def __repr__(self):
        return "%s(%r)@%d:%d" % (self.tipo, self.valor, self.linha, self.col)


def tokenizar(texto, lang):
    toks, i, n = [], 0, len(texto)
    ops = OPS_DAX if lang == "dax" else OPS_M
    while i < n:
        c = texto[i]
        if c in " \t\r\n":
            i += 1
            continue
        ini = i
        if c == '"' or (lang == "m" and texto.startswith('#"', i)):
            tipo = "qname" if c == "#" else "str"
            i += 2 if c == "#" else 1
            while i < n:
                if texto[i] == '"':
                    if i + 1 < n and texto[i + 1] == '"':
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            toks.append(Tok(tipo, texto[ini:i], ini, i))
            continue
        if lang == "dax" and c == "'":
            i += 1
            while i < n:
                if texto[i] == "'":
                    if i + 1 < n and texto[i + 1] == "'":
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            toks.append(Tok("qname", texto[ini:i], ini, i))
            continue
        if lang == "dax" and c == "[":
            i += 1
            while i < n:
                if texto[i] == "]":
                    if i + 1 < n and texto[i + 1] == "]":
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            toks.append(Tok("bracket", texto[ini:i], ini, i))
            continue
        if texto.startswith("//", i) or (lang == "dax" and texto.startswith("--", i)):
            while i < n and texto[i] != "\n":
                i += 1
            toks.append(Tok("comment", texto[ini:i], ini, i))
            continue
        if texto.startswith("/*", i):
            j = texto.find("*/", i + 2)
            i = n if j < 0 else j + 2
            toks.append(Tok("comment", texto[ini:i], ini, i))
            continue
        if c.isdigit() or (c == "." and i + 1 < n and texto[i + 1].isdigit()):
            while i < n and (texto[i].isalnum() or texto[i] == "."):
                i += 1
            toks.append(Tok("num", texto[ini:i], ini, i))
            continue
        if c.isalpha() or c == "_" or (lang == "m" and c == "#"):
            i += 1
            while i < n and (texto[i].isalnum() or texto[i] in "_."):
                i += 1
            toks.append(Tok("ident", texto[ini:i], ini, i))
            continue
        if c in "([{":
            toks.append(Tok("open", c, i, i + 1))
            i += 1
            continue
        if c in ")]}":
            toks.append(Tok("close", c, i, i + 1))
            i += 1
            continue
        if c == ",":
            toks.append(Tok("comma", c, i, i + 1))
            i += 1
            continue
        for op in ops:
            if texto.startswith(op, i):
                toks.append(Tok("op", op, i, i + len(op)))
                i += len(op)
                break
        else:
            toks.append(Tok("other", c, i, i + 1))
            i += 1
    return toks


# ---------------------------------------------------------------- objetos

class Objeto:
    def __init__(self, arquivo, nome, lang, linhas, linha0, cabecalho=None, inline=False, tabela=None):
        self.arquivo, self.nome, self.lang = arquivo, nome, lang
        self.linhas = linhas            # codigo ja sem o prefixo estrutural
        self.linha0 = linha0            # numero (1-based) no arquivo da primeira linha de self.linhas
        self.cabecalho = cabecalho      # texto do cabecalho sem tabulacao, para DAX-13
        self.inline = inline            # expressao na linha do "="
        self.tabela = tabela

    @property
    def chave(self):
        return (self.tabela or "", self.nome)

    @property
    def texto(self):
        return "\n".join(self.linhas)


RE_CAB = re.compile(r"^(\t*)(measure|column|calculationItem|expression|source)\b\s*(.*)$")


def ler_nome(resto):
    """Nome TMDL no inicio de resto: 'com aspas' ou palavra. Devolve (nome, resto)."""
    resto = resto.strip()
    if resto.startswith("'"):
        i = 1
        while i < len(resto):
            if resto[i] == "'":
                if i + 1 < len(resto) and resto[i + 1] == "'":
                    i += 2
                    continue
                break
            i += 1
        return resto[1:i].replace("''", "'"), resto[i + 1:]
    m = re.match(r"([^\s=]+)(.*)$", resto)
    return (m.group(1), m.group(2)) if m else (resto, "")


def tabs(linha):
    return len(linha) - len(linha.lstrip("\t"))


def extrair_tmdl(caminho, texto):
    linhas = texto.split("\n")
    linhas = [l[:-1] if l.endswith("\r") else l for l in linhas]
    objetos, tabela, particao, i = [], None, None, 0
    while i < len(linhas):
        l = linhas[i]
        m_tab = re.match(r"^table\s+(.*)$", l)
        if m_tab:
            tabela = ler_nome(m_tab.group(1))[0]
        m_part = re.match(r"^\t*partition\s+(.*?)\s*=\s*(\w+)\s*$", l)
        if m_part:
            particao = (ler_nome(m_part.group(1))[0], m_part.group(2).lower())
        m = RE_CAB.match(l)
        if not m:
            i += 1
            continue
        nivel, tipo, resto = tabs(l), m.group(2), m.group(3)
        if tipo == "source":
            if not particao or not resto.strip().startswith("="):
                i += 1
                continue
            nome, lang = "particao " + particao[0], ("m" if particao[1] == "m" else "dax")
            depois = resto.strip()[1:]
        else:
            nome_obj, depois_nome = ler_nome(resto)
            if "=" not in depois_nome:
                i += 1  # coluna de dados, sem expressao
                continue
            depois = depois_nome.split("=", 1)[1]
            nome = "%s '%s'" % (tipo if tipo != "calculationItem" else "item", nome_obj)
            lang = "m" if tipo == "expression" else "dax"
        cab = l.strip()
        if depois.strip().startswith("```"):
            corpo, j = [], i + 1
            while j < len(linhas) and linhas[j].strip() != "```":
                corpo.append(linhas[j])
                j += 1
            ini, i = i + 2, j + 1
        elif depois.strip():
            objetos.append(Objeto(caminho, nome, lang, [depois.strip()], i + 1, cab, True, tabela))
            i += 1
            continue
        else:
            corpo, j = [], i + 1
            while j < len(linhas):
                lj = linhas[j]
                if lj.strip() and tabs(lj) < nivel + 2:
                    break
                corpo.append(lj)
                j += 1
            ini, i = i + 2, j
        while corpo and not corpo[-1].strip():
            corpo.pop()
        # a primeira linha do corpo costuma vir so com as tabulacoes
        while corpo and not corpo[0].strip():
            corpo.pop(0)
            ini += 1
        if not corpo:
            continue
        prefixo = min(tabs(x) for x in corpo if x.strip())
        codigo = [x[prefixo:] if x.strip() else "" for x in corpo]
        objetos.append(Objeto(caminho, nome, lang, codigo, ini, cab, False, tabela))
    return objetos


def extrair_solto(caminho, texto):
    lang = "dax" if caminho.lower().endswith(".dax") else "m"
    linhas = [l.rstrip("\r") for l in texto.split("\n")]
    while linhas and not linhas[-1].strip():
        linhas.pop()
    nome, cab, ini = os.path.basename(caminho), None, 1
    if lang == "dax" and linhas:
        m = re.match(r"^([^\s].*?)\s*=\s*(.*)$", linhas[0])
        if m and not re.match(r"^(VAR|EVALUATE|DEFINE)\b", linhas[0], re.I):
            nome, cab = m.group(1), linhas[0].strip()
            if m.group(2).strip():
                return [Objeto(caminho, nome, lang, [m.group(2).strip()], 1, cab, True)]
            linhas, ini = linhas[1:], 2
    return [Objeto(caminho, nome, lang, linhas, ini, cab, False)]


def extrair(caminho, texto):
    if caminho.lower().endswith(".tmdl"):
        return extrair_tmdl(caminho, texto)
    return extrair_solto(caminho, texto)


# ---------------------------------------------------------------- nomes do modelo (DAX-06)

def raiz_modelo(caminho):
    p = os.path.abspath(caminho)
    while True:
        if p.endswith(".SemanticModel") and os.path.isdir(os.path.join(p, "definition")):
            return os.path.join(p, "definition")
        pai = os.path.dirname(p)
        if pai == p:
            return None
        p = pai


_cache_nomes = {}


def nomes_do_modelo(definicao):
    if definicao in _cache_nomes:
        return _cache_nomes[definicao]
    colunas, medidas = set(), set()
    pasta = os.path.join(definicao, "tables")
    for f in os.listdir(pasta) if os.path.isdir(pasta) else []:
        if not f.endswith(".tmdl"):
            continue
        for l in open(os.path.join(pasta, f), encoding="utf-8-sig", errors="replace"):
            m = re.match(r"^\t(column|measure)\s+(.*)$", l.rstrip("\r\n"))
            if m:
                nome = ler_nome(m.group(2))[0].lower()
                (colunas if m.group(1) == "column" else medidas).add(nome)
    _cache_nomes[definicao] = (colunas, medidas)
    return colunas, medidas


# ---------------------------------------------------------------- verificacao

class Verificador:
    def __init__(self, obj, nomes=None):
        self.o, self.nomes, self.v = obj, nomes, []
        self.texto = obj.texto
        self.inicios = [0]
        for k, ch in enumerate(self.texto):
            if ch == "\n":
                self.inicios.append(k + 1)
        self.toks = tokenizar(self.texto, obj.lang)
        for t in self.toks:
            t.linha, t.col = self.pos(t.ini)
            t.linha_fim = self.pos(max(t.fim - 1, t.ini))[0]
        self.sig = [t for t in self.toks if t.tipo != "comment"]
        self.casar()

    def pos(self, k):
        ln = bisect.bisect_right(self.inicios, k) - 1
        return ln, k - self.inicios[ln]

    def add(self, regra, linha, msg):
        self.v.append({"arquivo": self.o.arquivo, "objeto": self.o.nome, "tabela": self.o.tabela,
                       "linha": self.o.linha0 + linha, "regra": regra, "msg": msg})

    def recuo(self, ln):
        l = self.o.linhas[ln]
        return len(l) - len(l.lstrip(" "))

    def primeiro_da_linha(self, t):
        return not self.texto[self.inicios[t.linha]:t.ini].strip()

    def casar(self):
        """Pares de abertura e fechamento sobre os tokens significativos."""
        self.par, pilha = {}, []
        for k, t in enumerate(self.sig):
            if t.tipo == "open":
                pilha.append(k)
            elif t.tipo == "close" and pilha:
                a = pilha.pop()
                self.par[a], self.par[k] = k, a
        self.prof = []
        d = 0
        for t in self.sig:
            if t.tipo == "close":
                d -= 1
            self.prof.append(d)
            if t.tipo == "open":
                d += 1

    def itens(self, a):
        """Itens de primeiro nivel entre a abertura a e seu fechamento: listas de indices."""
        f = self.par.get(a)
        if f is None:
            return []
        itens, atual, d = [], [], 0
        m = self.o.lang == "m"
        for k in range(a + 1, f):
            t = self.sig[k]
            if t.tipo == "open" or (m and t.tipo == "ident" and t.valor == "let"):
                d += 1
            elif t.tipo == "close" or (m and t.tipo == "ident" and t.valor == "in" and d > 0):
                d -= 1
            if t.tipo == "comma" and d == 0:
                if atual:  # item vazio (a, , b) nao conta
                    itens.append(atual)
                atual = []
            else:
                atual.append(k)
        if atual:
            itens.append(atual)
        return itens

    # ---------- regras de linha

    def regras_de_linha(self):
        dax = self.o.lang == "dax"
        em_texto = [[] for _ in self.o.linhas]
        for t in self.toks:
            if t.tipo == "str":
                for ln in range(t.linha, t.linha_fim + 1):
                    a = max(t.ini, self.inicios[ln])
                    b = min(t.fim, self.inicios[ln] + len(self.o.linhas[ln]))
                    em_texto[ln].append((a - self.inicios[ln], b - self.inicios[ln]))
        for ln, l in enumerate(self.o.linhas):
            dentro = sum(b - a for a, b in em_texto[ln])
            fora = "".join(ch for k, ch in enumerate(l) if not any(a <= k < b for a, b in em_texto[ln]))
            if len(l) - dentro > LIMITE:
                self.add("DAX-10" if dax else "M-08", ln, "linha com %d caracteres fora de texto (limite %d)" % (len(l) - dentro, LIMITE))
            if "\t" in fora:
                self.add("DAX-12" if dax else "M-08", ln, "tabulação dentro do código; use espaço")
        for t in self.sig:
            if t.tipo == "comma" and self.primeiro_da_linha(t):
                self.add("DAX-05" if dax else "M-08", t.linha, "vírgula no começo da linha")
        if not dax:
            for t in self.toks:
                if t.tipo == "comment" and not self.primeiro_da_linha(t):
                    self.add("M-07", t.linha, "comentário no fim da linha; ponha acima do passo")

    # ---------- operadores

    def gerado_pelo_desktop(self):
        """Indices dentro de meta [...] (parametro de M), que o Desktop escreve e reescreve."""
        dentro = set()
        for a, t in enumerate(self.sig):
            if t.valor == "[" and a in self.par and a and self.sig[a - 1].valor == "meta":
                dentro.update(range(a, self.par[a] + 1))
        return dentro

    def regras_de_operador(self):
        dax = self.o.lang == "dax"
        pular = set() if dax else self.gerado_pelo_desktop()
        for k, t in enumerate(self.sig):
            if t.tipo != "op" or k in pular:
                continue
            ant = self.sig[k - 1] if k else None
            if t.valor in "+-" and (ant is None or ant.tipo in PREFIXO_UNARIO or
                                    (ant.tipo == "ident" and ant.valor in PALAVRAS_ANTES_DE_UNARIO)):
                continue
            antes = self.texto[t.ini - 1] if t.ini else "\n"
            depois = self.texto[t.fim] if t.fim < len(self.texto) else "\n"
            if antes not in " \t\n" or depois not in " \t\n":  # tabulacao e da DAX-12
                self.add("DAX-07" if dax else "M-05", t.linha, "operador '%s' sem espaço em volta" % t.valor)

    # ---------- chamadas e blocos quebrados

    def conferir_quebra(self, a, regra, rotulo):
        """Bloco que ocupa mais de uma linha: abre no fim da linha, um item por linha
        com 4 espacos a mais, e fecha sozinho alinhado com a linha de abertura."""
        f = self.par[a]
        ab, fe = self.sig[a], self.sig[f]
        base = self.recuo(ab.linha)
        if a + 1 < f and self.sig[a + 1].linha == ab.linha:
            self.add(regra, ab.linha, "%s quebrado deve abrir no fim da linha" % rotulo)
            return
        for item in self.itens(a):
            t0 = self.sig[item[0]]
            if not self.primeiro_da_linha(t0) or t0.col != base + 4:
                self.add(regra, t0.linha, "%s quebrado: cada item numa linha própria, com %d espaços" % (rotulo, base + 4))
        if not self.primeiro_da_linha(fe) or fe.col != base:
            self.add(regra, fe.linha, "%s quebrado: o fechamento fica sozinho, com %d espaços" % (rotulo, base))

    def regras_de_chamada(self):
        dax = self.o.lang == "dax"
        for a, t in enumerate(self.sig):
            if t.tipo != "open" or a not in self.par:
                continue
            f = self.par[a]
            fe = self.sig[f]
            ant = self.sig[a - 1] if a else None
            chamada = t.valor == "(" and ant is not None and ant.tipo == "ident" and \
                not (ant.valor.upper() in PALAVRAS_DAX and ant.valor.upper() not in ("TRUE", "FALSE", "NOT"))
            multi = fe.linha != t.linha
            if dax and t.valor == "(":
                self.espaco_parenteses(a, f, ant if chamada else None)
            if not dax and t.valor in "[{":
                if ant is None or ant.valor != "meta":
                    self.lista_ou_registro(a, ant)
                continue
            if not chamada:
                continue
            nome = ant.valor.upper()
            if dax and ant.valor != nome:
                self.add("DAX-01", ant.linha, "função '%s' em maiúsculas: %s" % (ant.valor, nome))
            if multi:
                self.conferir_quebra(a, "DAX-03" if dax else "M-03", "parêntese")
                if dax and nome not in SEMPRE_QUEBRA and self.cabe_numa_linha(a - 1, f):
                    self.add("DAX-02", ant.linha, "%s cabe numa linha só" % nome)
            elif dax:
                if nome in SEMPRE_QUEBRA and self.itens(a):
                    self.add("DAX-04", ant.linha, "%s sempre quebra, um argumento por linha" % nome)
                elif self.tem_chamada_multiarg(a, f):
                    self.add("DAX-03", ant.linha, "%s tem chamada com vários argumentos dentro; quebre" % nome)

    def espaco_parenteses(self, a, f, func):
        t, fe = self.sig[a], self.sig[f]
        if func is not None and (func.linha != t.linha or self.texto[func.fim:t.ini] != " "):
            self.add("DAX-01", t.linha, "um espaço entre '%s' e o parêntese" % func.valor)
        if f == a + 1:
            if fe.ini != t.fim:
                self.add("DAX-02", t.linha, "parêntese vazio fica '()'")
            return
        prox = self.sig[a + 1]
        if prox.linha == t.linha and self.texto[t.fim:prox.ini] != " ":
            self.add("DAX-02", t.linha, "um espaço depois do '('")
        ult = self.sig[f - 1]
        if ult.linha == fe.linha and not self.primeiro_da_linha(fe) and self.texto[ult.fim:fe.ini] != " ":
            self.add("DAX-02", fe.linha, "um espaço antes do ')'")

    def tem_chamada_multiarg(self, a, f):
        for k in range(a + 1, f):
            t = self.sig[k]
            if t.tipo == "open" and t.valor == "(" and k in self.par and self.sig[k - 1].tipo == "ident":
                if len(self.itens(k)) > 1:
                    return True
        return False

    def cabe_numa_linha(self, ini_func, f):
        t0, fe = self.sig[ini_func], self.sig[f]
        trecho = self.toks_entre(t0.ini, fe.fim)
        if any(t.tipo == "comment" or (t.tipo == "str" and t.linha != t.linha_fim) or
               (t.tipo == "ident" and t.valor.upper() in ("VAR", "RETURN")) for t in trecho):
            return False
        if self.tem_chamada_multiarg(ini_func + 1, f):
            return False
        corrido = re.sub(r"\(\s+", "( ", re.sub(r"\s+\)", " )", re.sub(r"\s+", " ", self.texto[t0.ini:fe.fim])))
        antes = self.o.linhas[t0.linha][:t0.col]
        depois = self.o.linhas[fe.linha][fe.col + 1:]
        return len(antes) + len(corrido) + len(depois) <= LIMITE

    def toks_entre(self, ini, fim):
        return [t for t in self.toks if ini <= t.ini < fim]

    def lista_ou_registro(self, a, ant):
        """M: { } e [ ] literais. Acesso a item (Fonte{0}) e a campo ([Coluna]) ficam fora."""
        t = self.sig[a]
        if ant is not None and (ant.tipo in ("ident", "qname", "close") and ant.valor not in ("each", "in", "then", "else")):
            if not (ant.tipo == "ident" and ant.valor in ("type", "table")):
                return
        itens = self.itens(a)
        if t.valor == "[" and not any(self.sig[i].tipo == "op" and self.sig[i].valor == "=" and
                                      self.prof[i] == self.prof[a] + 1 for item in itens for i in item):
            return  # acesso a campo, nao registro
        if self.sig[self.par[a]].linha != t.linha:
            self.conferir_quebra(a, "M-04", "lista" if t.valor == "{" else "registro")
            return
        compostos = sum(1 for item in itens if self.sig[item[0]].tipo == "open" or
                        (len(item) > 1 and self.sig[item[0]].tipo == "ident" and self.sig[item[1]].valor == "("))
        if compostos > 3:
            self.add("M-04", t.linha, "%s com %d itens compostos numa linha; um item por linha" %
                     ("lista" if t.valor == "{" else "registro", compostos))

    # ---------- DAX: VAR / RETURN, nomes, colunas

    def regras_var(self):
        ultimo_var = {}
        for k, t in enumerate(self.sig):
            if t.tipo != "ident":
                continue
            up = t.valor.upper()
            prox = self.sig[k + 1] if k + 1 < len(self.sig) else None
            if up in PALAVRAS_DAX and t.valor != up and not (prox and prox.tipo in ("open", "bracket") and prox.ini == t.fim):
                self.add("DAX-01", t.linha, "palavra-chave '%s' em maiúsculas" % t.valor)
            if up not in ("VAR", "RETURN"):
                continue
            d = self.prof[k]
            if not self.primeiro_da_linha(t):
                self.add("DAX-08", t.linha, "%s começa a linha" % up)
            if d == 0 and t.col != 0:
                self.add("DAX-08", t.linha, "%s no nível da medida fica na coluna zero" % up)
            if up == "VAR":
                ultimo_var[d] = t
                if prox and prox.tipo == "ident" and not re.match(r"^(v_[a-z0-9_]+|_[a-z0-9_]+)$", prox.valor):
                    self.add("DAX-09", t.linha, "variável '%s' fora do padrão v_snake_case" % prox.valor)
                if k + 3 < len(self.sig) and self.sig[k + 2].valor == "=":
                    expr = self.sig[k + 3]
                    if expr.linha != t.linha and (not self.primeiro_da_linha(expr) or expr.col != t.col + 4):
                        self.add("DAX-08", expr.linha, "expressão da variável desce com %d espaços" % (t.col + 4))
            else:
                v = ultimo_var.get(d)
                if v is not None and v.col != t.col:
                    self.add("DAX-08", t.linha, "RETURN alinhado com o VAR (%d espaços)" % v.col)
                if prox is not None:
                    if prox.linha == t.linha:
                        self.add("DAX-08", t.linha, "a expressão do RETURN vai na linha seguinte")
                    elif not self.primeiro_da_linha(prox) or prox.col != t.col + 4:
                        self.add("DAX-08", prox.linha, "expressão do RETURN com %d espaços" % (t.col + 4))

    def regras_de_nome(self):
        if not self.nomes:
            return
        colunas, medidas = self.nomes
        em_nameof = set()
        for a, t in enumerate(self.sig):
            if t.tipo == "open" and a in self.par and a and self.sig[a - 1].valor.upper() == "NAMEOF":
                em_nameof.update(range(a, self.par[a]))
        for k, t in enumerate(self.sig):
            if t.tipo != "bracket" or k in em_nameof:
                continue
            nome = t.valor[1:-1].replace("]]", "]").lower()
            ant = self.sig[k - 1] if k else None
            com_tabela = ant is not None and ant.tipo in ("qname", "ident") and ant.fim == t.ini
            if not com_tabela and nome in colunas and nome not in medidas:
                self.add("DAX-06", t.linha, "coluna %s sem a tabela" % t.valor)
            if com_tabela and nome in medidas and nome not in colunas:
                self.add("DAX-06", t.linha, "medida %s com a tabela; referencie só %s" % (t.valor, t.valor))

    def regra_cabecalho(self):
        o = self.o
        if o.cabecalho is None:
            return
        if o.inline:
            if any(t.tipo == "ident" and t.valor.upper() == "VAR" for t in self.sig):
                self.add("DAX-13", 0, "expressão com VAR começa na linha seguinte ao '='")
            elif len(o.cabecalho) > LIMITE:
                self.add("DAX-13", 0, "expressão longa começa na linha seguinte ao '='")
            return
        uteis = [l for l in o.linhas if l.strip()]
        if len(uteis) == 1 and not any(t.tipo in ("comment",) or t.valor.upper() == "VAR" for t in self.toks) \
                and len(o.cabecalho) + 1 + len(uteis[0].strip()) <= LIMITE:
            self.add("DAX-13", 0, "expressão curta fica na linha do '='")

    # ---------- M: let / in, passos, each

    def regras_m(self):
        lets, d_let, top = [], 0, None
        for k, t in enumerate(self.sig):
            if t.tipo != "ident":
                continue
            if t.valor == "let":
                if d_let == 0 and top is None and self.prof[k] == 0:
                    top = k
                d_let += 1
            elif t.valor == "in" and d_let:
                d_let -= 1
                if d_let == 0 and top is not None and self.prof[k] == 0:
                    lets.append((top, k))
                    top = None
        for l_ini, l_fim in lets[:1]:
            tl, ti = self.sig[l_ini], self.sig[l_fim]
            if tl.col != 0 or not self.primeiro_da_linha(tl):
                self.add("M-01", tl.linha, "'let' na coluna zero")
            if ti.col != 0 or not self.primeiro_da_linha(ti):
                self.add("M-01", ti.linha, "'in' alinhado com o 'let'")
            if l_fim + 1 < len(self.sig):
                fin = self.sig[l_fim + 1]
                if fin.linha == ti.linha or fin.col != 4:
                    self.add("M-01", fin.linha, "passo final na linha seguinte ao 'in', com 4 espaços")
            inicio_passo, d_let2 = True, 0
            for k in range(l_ini + 1, l_fim):
                t = self.sig[k]
                if t.tipo == "ident" and t.valor == "let":
                    d_let2 += 1
                elif t.tipo == "ident" and t.valor == "in" and d_let2:
                    d_let2 -= 1
                if self.prof[k] != 0 or d_let2:
                    continue
                if inicio_passo:
                    inicio_passo = False
                    if not self.primeiro_da_linha(t) or t.col != 4:
                        self.add("M-01", t.linha, "passo começa a linha com 4 espaços")
                    if t.tipo == "qname":
                        self.add("M-02", t.linha, "passo %s: dê um nome sem espaço e sem acento" % t.valor)
                    elif t.tipo == "ident" and not t.valor.isascii():
                        self.add("M-02", t.linha, "passo '%s' com acento" % t.valor)
                if t.tipo == "comma":
                    inicio_passo = True
        for k, t in enumerate(self.sig):
            if t.tipo == "ident" and t.valor == "each":
                d, fim_linha = self.prof[k], t.linha
                for j in range(k + 1, len(self.sig)):
                    u = self.sig[j]
                    if self.prof[j] < d or (self.prof[j] == d and u.tipo == "comma"):
                        break
                    fim_linha = max(fim_linha, u.linha_fim)
                if fim_linha != t.linha:
                    self.add("M-06", t.linha, "'each' com lógica longa; use (linha) => ... quebrado em linhas")

    def rodar(self):
        self.regras_de_linha()
        self.regras_de_operador()
        self.regras_de_chamada()
        if self.o.lang == "dax":
            self.regras_var()
            self.regras_de_nome()
            self.regra_cabecalho()
        else:
            self.regras_m()
        vistos, unicos = set(), []
        for x in sorted(self.v, key=lambda x: (x["linha"], x["regra"])):
            chave = (x["linha"], x["regra"], x["msg"])
            if chave not in vistos:
                vistos.add(chave)
                unicos.append(x)
        return unicos


# ---------------------------------------------------------------- delta contra o git

def texto_no_head(caminho):
    pasta = os.path.dirname(os.path.abspath(caminho))
    try:
        raiz = subprocess.run(["git", "-C", pasta, "rev-parse", "--show-toplevel"], capture_output=True,
                              text=True, check=True).stdout.strip()
        rel = os.path.relpath(os.path.abspath(caminho), raiz).replace("\\", "/")
        r = subprocess.run(["git", "-C", raiz, "show", "HEAD:" + rel], capture_output=True, check=True)
        return r.stdout.decode("utf-8-sig", errors="replace")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def so_alterados(caminho, objetos):
    antigo = texto_no_head(caminho)
    if antigo is None:
        return objetos
    antes = {o.chave: o.texto for o in extrair(caminho, antigo)}
    return [o for o in objetos if antes.get(o.chave) != o.texto]


# ---------------------------------------------------------------- entrada

def arquivos(caminhos):
    for c in caminhos:
        if os.path.isdir(c):
            for raiz, subs, fs in os.walk(c):
                # consultas avulsas da visao de consulta do Desktop, nao sao o modelo
                subs[:] = [x for x in subs if x != "DAXQueries"]
                for f in sorted(fs):
                    if f.lower().endswith(EXTENSOES):
                        yield os.path.join(raiz, f)
        elif c.lower().endswith(EXTENSOES) and os.path.exists(c):
            yield c


def verificar(caminhos, delta=False):
    violacoes, total_obj = [], 0
    for arq in arquivos(caminhos):
        texto = open(arq, encoding="utf-8-sig", errors="replace").read()
        objetos = extrair(arq, texto)
        if delta:
            objetos = so_alterados(arq, objetos)
        defin = raiz_modelo(arq)
        nomes = nomes_do_modelo(defin) if defin else None
        for o in objetos:
            total_obj += 1
            violacoes += Verificador(o, nomes).rodar()
    return violacoes, total_obj


def painel(arquivo):
    p = os.path.abspath(arquivo)
    while True:
        pai = os.path.dirname(p)
        if p.endswith(".SemanticModel"):
            return os.path.basename(pai)
        if pai == p:
            return os.path.basename(os.path.dirname(os.path.abspath(arquivo)))
        p = pai


def rotulo(v):
    return ("%s / %s" % (v["tabela"], v["objeto"])) if v["tabela"] else v["objeto"]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("caminhos", nargs="+")
    ap.add_argument("--delta", action="store_true", help="so objetos que mudaram desde o HEAD do git")
    ap.add_argument("--relatorio", action="store_true", help="total por regra e objetos piores")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--top", type=int, default=15)
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    violacoes, total_obj = verificar(a.caminhos, a.delta)
    if a.json:
        print(json.dumps({"objetos": total_obj, "violacoes": violacoes}, ensure_ascii=False, indent=1))
    elif a.relatorio:
        por_regra = collections.Counter(v["regra"] for v in violacoes)
        por_obj = collections.Counter((v["arquivo"], rotulo(v)) for v in violacoes)
        limpos = total_obj - len({(v["arquivo"], rotulo(v)) for v in violacoes})
        print("%d objetos verificados, %d sem violação, %d violações" % (total_obj, limpos, len(violacoes)))
        print("\nPor regra:")
        for r, n in sorted(por_regra.items()):
            print("  %-7s %5d" % (r, n))
        print("\nObjetos com mais violações:")
        for (arq, nome), n in por_obj.most_common(a.top):
            print("  %5d  %s  (%s)" % (n, nome, painel(arq)))
    else:
        for v in violacoes:
            print("%s:%d  [%s] %s: %s" % (v["arquivo"], v["linha"], v["regra"], rotulo(v), v["msg"]))
        if violacoes:
            print("\n%d violações em %d objetos verificados" % (len(violacoes), total_obj))
    return 1 if violacoes else 0


if __name__ == "__main__":
    sys.exit(main())
