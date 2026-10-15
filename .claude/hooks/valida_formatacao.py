#!/usr/bin/env python3
"""Hook de formatacao: todo DAX e M escrito sai no PADRAO_FORMATACAO.

A instrucao sozinha e a camada mais fraca: cada sessao lembra o estilo de um jeito.
Este hook confere na hora da escrita, com o lint_formatacao.py, e devolve as violacoes
com codigo 2 para o Claude corrigir antes de seguir.

Dois momentos, no mesmo arquivo:

- PostToolUse (Write, Edit, MultiEdit, Bash, PowerShell): confere o .tmdl, .dax, .pq ou .m
  tocado. So o que a escrita mexeu: no Edit, os objetos que contem o trecho novo; no Write
  e em script, os objetos que mudaram desde o HEAD do git. Legado que ninguem tocou nao
  trava a edicao, porque o painel inteiro e assunto da auditoria completa e de uma rodada
  dedicada de formatacao.
- PreToolUse (powerbi-modeling-mcp, medida, coluna e particao): confere a expressao antes
  de ela ir para o modelo aberto, que nenhum hook de arquivo enxerga.

Fica de fora a pasta de testes do proprio lint, que tem objetos ruins de proposito, e as
consultas avulsas do DAXQueries.
"""
import json
import os
import re
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "scripts"))
import lint_formatacao as lint  # noqa: E402

EXT = lint.EXTENSOES
IGNORAR = ("testes_lint", "DAXQueries")
RECENTE_SEG = 120
MAX_LINHAS = 30
RE_CAMINHO = re.compile(r"[^\s\"'|;&<>]+\.(?:tmdl|dax|pq|m)\b", re.I)

# repositorio de dashboards: o nome da pasta apontada por CADERNO_REPO_TRABALHO serve de
# marcador num comando de script, como no log_acao.py. Sem a variavel, vale so o .SemanticModel.
MARCADOR_DASHBOARDS = os.path.basename(
    os.path.normpath(os.environ.get("CADERNO_REPO_TRABALHO", ""))) if os.environ.get("CADERNO_REPO_TRABALHO") else ""


def ignorado(caminho):
    partes = re.split(r"[\\/]", caminho)
    return any(p in IGNORAR for p in partes)


def ler(caminho):
    return open(caminho, encoding="utf-8-sig", errors="replace").read()


def nomes(caminho):
    defin = lint.raiz_modelo(caminho)
    return lint.nomes_do_modelo(defin) if defin else None


def verificar_objetos(objetos, caminho):
    n = nomes(caminho)
    saida = []
    for o in objetos:
        saida += lint.Verificador(o, n).rodar()
    return saida


def span(o):
    """Linhas do arquivo que o objeto ocupa, cabecalho incluido."""
    ini = o.linha0 if o.inline else o.linha0 - 1
    return ini, o.linha0 + len(o.linhas)


def linhas_do_trecho(texto, trecho):
    """Numeros de linha (1-based) onde o trecho aparece no texto."""
    faixas, k = [], texto.find(trecho)
    while trecho and k >= 0:
        a = texto.count("\n", 0, k) + 1
        faixas.append((a, a + trecho.count("\n")))
        k = texto.find(trecho, k + 1)
    return faixas


def pos_edicao(caminho, tool_input):
    texto = ler(caminho)
    objetos = lint.extrair(caminho, texto)
    trechos = [tool_input.get("new_string")] + [e.get("new_string") for e in tool_input.get("edits") or []]
    faixas = []
    for t in trechos:
        if t and t.strip():
            faixas += linhas_do_trecho(texto.replace("\r\n", "\n"), t.replace("\r\n", "\n"))
    if not faixas:
        return []
    tocados = [o for o in objetos if any(a <= span(o)[1] and b >= span(o)[0] for a, b in faixas)]
    return verificar_objetos(tocados, caminho)


def pos_arquivo_inteiro(caminho):
    objetos = lint.so_alterados(caminho, lint.extrair(caminho, ler(caminho)))
    return verificar_objetos(objetos, caminho)


def raiz_git(pasta):
    try:
        return subprocess.run(["git", "-C", pasta, "rev-parse", "--show-toplevel"], capture_output=True,
                              text=True, check=True, timeout=5).stdout.strip()
    except Exception:
        return None


def alterados_agora(raiz):
    """Arquivos de codigo com mudanca no git e gravados nos ultimos segundos: a escrita por script."""
    try:
        r = subprocess.run(["git", "-C", raiz, "status", "--porcelain", "-uall"], capture_output=True,
                           text=True, encoding="utf-8", check=True, timeout=10).stdout
    except Exception:
        return []
    agora, achados = time.time(), []
    for linha in r.splitlines():
        rel = linha[3:].strip().strip('"')
        if " -> " in rel:
            rel = rel.split(" -> ", 1)[1]
        if not rel.lower().endswith(EXT):
            continue
        p = os.path.join(raiz, rel)
        try:
            if agora - os.path.getmtime(p) <= RECENTE_SEG:
                achados.append(p)
        except OSError:
            pass
    return achados


def pos_script(payload):
    cmd = str((payload.get("tool_input") or {}).get("command") or "")
    cwd = payload.get("cwd") or os.getcwd()
    caminhos = set()
    for m in RE_CAMINHO.findall(cmd):
        p = m if os.path.isabs(m) else os.path.join(cwd, m)
        if os.path.isfile(p):
            caminhos.add(os.path.abspath(p))
    raizes = {r for r in (raiz_git(os.path.dirname(p)) for p in caminhos) if r}
    marcadores = [r"\.SemanticModel"] + ([re.escape(MARCADOR_DASHBOARDS)] if MARCADOR_DASHBOARDS else [])
    if ".semanticmodel" in cmd.lower() or (MARCADOR_DASHBOARDS and MARCADOR_DASHBOARDS.lower() in cmd.lower()):
        for m in re.findall(r"[^\s\"'|;&<>]*(?:%s)" % "|".join(marcadores), cmd, re.I):
            base = m if os.path.isabs(m) else os.path.join(cwd, m)
            if os.path.isdir(base):
                r = raiz_git(base)
                if r:
                    raizes.add(r)
    for r in raizes:
        caminhos.update(os.path.abspath(p) for p in alterados_agora(r))
    saida = []
    for p in sorted(caminhos):
        if not ignorado(p):
            saida += pos_arquivo_inteiro(p)
    return saida


def pre_mcp(payload):
    nome_tool = payload.get("tool_name", "")
    req = (payload.get("tool_input") or {}).get("request") or {}
    if str(req.get("operation", "")).lower() not in ("create", "update"):
        return []
    tipo = "particao" if "partition" in nome_tool else ("coluna" if "column" in nome_tool else "medida")
    saida = []
    for d in req.get("definitions") or []:
        nome = "%s '%s'" % (tipo, d.get("name") or "")
        pares = []
        if tipo == "particao":
            if d.get("expression"):
                pares.append(("m", d["expression"]))
            if d.get("query"):
                pares.append(("dax", d["query"]))
        elif d.get("expression"):
            pares.append(("dax", d["expression"]))
        for lang, expr in pares:
            linhas = expr.replace("\r\n", "\n").split("\n")
            while linhas and not linhas[0].strip():
                linhas.pop(0)
            while linhas and not linhas[-1].strip():
                linhas.pop()
            o = lint.Objeto("MCP " + nome_tool.split("__")[-1], nome, lang, linhas, 1, None, False, d.get("tableName"))
            saida += lint.Verificador(o, None).rodar()
    return saida


def relatar(violacoes, antes_de_gravar):
    linhas = ["%s:%d  [%s] %s: %s" % (os.path.basename(v["arquivo"]), v["linha"], v["regra"],
                                       lint.rotulo(v), v["msg"]) for v in violacoes]
    extra = len(linhas) - MAX_LINHAS
    corpo = "\n  - ".join(linhas[:MAX_LINHAS]) + ("\n  ... e mais %d" % extra if extra > 0 else "")
    quando = "A gravação no modelo foi barrada" if antes_de_gravar else "O arquivo foi gravado"
    qtd = "1 violação" if len(violacoes) == 1 else "%d violações" % len(violacoes)
    sys.stderr.write(
        "FORMATAÇÃO FORA DO PADRÃO (%s). %s. Corrija o código e grave de novo:\n\n  - %s\n\n"
        "Regras em conhecimento/padroes/PADRAO_FORMATACAO.md. Formatar nunca muda resultado: só espaço, "
        "quebra, caixa de função e nome de VAR ou de passo.\n" % (qtd, quando, corpo))
    return 2


def main():
    # o payload chega em UTF-8 e o caminho pode ter acento ("Análise de Vendas"); a mensagem
    # volta em UTF-8. O padrao do Windows (cp1252) corromperia os dois.
    sys.stderr.reconfigure(encoding="utf-8")
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))
    except Exception:
        return 0
    evento = payload.get("hook_event_name", "")
    tool = payload.get("tool_name", "")
    try:
        if evento == "PreToolUse":
            if tool.startswith("mcp__powerbi-modeling-mcp__"):
                v = pre_mcp(payload)
                return relatar(v, True) if v else 0
            return 0
        entrada = payload.get("tool_input") or {}
        if tool in ("Bash", "PowerShell"):
            v = pos_script(payload)
        else:
            caminho = str(entrada.get("file_path") or "")
            if not caminho.lower().endswith(EXT) or ignorado(caminho) or not os.path.isfile(caminho):
                return 0
            v = pos_edicao(caminho, entrada) if tool in ("Edit", "MultiEdit") else pos_arquivo_inteiro(caminho)
    except Exception as e:  # o hook nunca derruba a sessao por defeito proprio
        sys.stderr.write("valida_formatacao: falha interna (%s), escrita nao conferida\n" % e)
        return 0
    return relatar(v, False) if v else 0


if __name__ == "__main__":
    sys.exit(main())
