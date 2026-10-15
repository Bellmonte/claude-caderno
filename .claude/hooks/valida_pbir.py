#!/usr/bin/env python3
"""Hook PostToolUse: confere a estrutura do relatorio PBIP a cada escrita.

O erro que este hook existe para impedir: entregar um .pbip que nao abre. Num
caso real, tres visuais de uma mesma pagina sairam com o `projections`
embrulhado duas vezes. Os arquivos eram JSON valido, passaram no json.load, e o
Desktop devolveu "Falha ao carregar o relatorio" sem dizer onde.

JSON valido nao e JSON correto. A estrutura se prova contra a forma que roda, e
essa forma esta escrita aqui: papel de consulta leva lista de projecoes, objeto
de formatacao leva lista de {"properties"}, e toda propriedade leva {"expr"}.
Confere tambem o que o json.load nunca pegaria: pagina na ordem que nao existe
em pasta, e recurso registrado que nao esta no disco.

Roda so quando a escrita toca um *.Report, e bloqueia com o caminho e o defeito.
"""
import json
import os
import re
import sys

PROPRIEDADE_CRUA = (str, int, float, bool)

# Tipos que nao consultam dado: navegador de pagina, botao, forma e imagem vivem
# sem queryState, e cobrar consulta deles era falso positivo.
SEM_CONSULTA = {"pageNavigator", "actionButton", "shape", "image", "textbox", "bookmarkNavigator"}


def caminho_tocado(payload):
    e = payload.get("tool_input") or {}
    for chave in ("file_path", "path", "notebook_path"):
        if e.get(chave):
            return str(e[chave])
    # Bash e PowerShell: acha o .Report citado no comando
    cmd = str(e.get("command") or "")
    m = re.search(r"[^\s\"']*\.Report", cmd)
    return m.group(0) if m else ""


def raiz_do_relatorio(caminho):
    caminho = os.path.abspath(caminho)
    while True:
        pai, folha = os.path.split(caminho)
        if not pai or pai == caminho:
            return ""
        if folha.endswith(".Report"):
            return caminho
        caminho = pai


def ler(p):
    return json.load(open(p, encoding="utf-8"))


def conferir_objetos(rotulo, objetos, erros):
    """background/border/title/... : lista de {"properties": {prop: {"expr": ...}}}"""
    for nome, valor in (objetos or {}).items():
        if not isinstance(valor, list):
            erros.append("%s: objeto '%s' devia ser lista, veio %s" % (rotulo, nome, type(valor).__name__))
            continue
        for item in valor:
            if not isinstance(item, dict) or "properties" not in item:
                erros.append("%s: objeto '%s' sem a chave 'properties'" % (rotulo, nome))
                continue
            for prop, conteudo in item["properties"].items():
                if isinstance(conteudo, PROPRIEDADE_CRUA):
                    erros.append("%s: '%s.%s' com valor cru; propriedade de PBIR vai em {\"expr\": ...}"
                                 % (rotulo, nome, prop))


def conferir_visual(p, erros):
    rotulo = os.path.relpath(p, os.path.dirname(os.path.dirname(os.path.dirname(p))))
    try:
        d = ler(p)
    except Exception as e:
        erros.append("%s: JSON ilegivel (%s)" % (rotulo, e))
        return
    grupo = "visualGroup" in d
    for chave in ("$schema", "name", "position") + (() if grupo else ("visual",)):
        if chave not in d:
            erros.append("%s: falta '%s' no topo" % (rotulo, chave))
    pos = d.get("position") or {}
    for eixo in ("x", "y", "width", "height"):
        if not isinstance(pos.get(eixo), (int, float)):
            erros.append("%s: position.%s ausente ou nao numerico" % (rotulo, eixo))
    if grupo:
        return
    v = d.get("visual") or {}
    if not v.get("visualType"):
        erros.append("%s: falta visual.visualType" % rotulo)
    estado = ((v.get("query") or {}).get("queryState")) or {}
    if not estado and v.get("visualType") not in SEM_CONSULTA:
        erros.append("%s: visual sem queryState; nada vai ser consultado" % rotulo)
    for papel, bloco in estado.items():
        if not isinstance(bloco, dict) or "projections" not in bloco:
            erros.append("%s: papel '%s' sem 'projections'" % (rotulo, papel))
            continue
        projecoes = bloco["projections"]
        if not isinstance(projecoes, list):
            erros.append("%s: papel '%s' com projections %s em vez de lista; "
                         "embrulho duplo derruba a carga do relatorio"
                         % (rotulo, papel, type(projecoes).__name__))
            continue
        for pr in projecoes:
            if not isinstance(pr, dict) or "field" not in pr or "queryRef" not in pr:
                erros.append("%s: papel '%s' com projecao sem 'field' ou 'queryRef'" % (rotulo, papel))
    conferir_objetos(rotulo, v.get("visualContainerObjects"), erros)
    conferir_objetos(rotulo, v.get("objects"), erros)


def conferir_pagina(p, erros):
    rotulo = os.path.relpath(p, os.path.dirname(os.path.dirname(os.path.dirname(p))))
    try:
        d = ler(p)
    except Exception as e:
        erros.append("%s: JSON ilegivel (%s)" % (rotulo, e))
        return
    for chave in ("$schema", "name", "displayName", "width", "height"):
        if chave not in d:
            erros.append("%s: falta '%s'" % (rotulo, chave))
    if d.get("name") != os.path.basename(os.path.dirname(p)):
        erros.append("%s: 'name' diferente do nome da pasta; a ordem de paginas nao acha a pagina" % rotulo)
    conferir_objetos(rotulo, d.get("objects"), erros)


def conferir_relatorio(raiz, erros):
    dpag = os.path.join(raiz, "definition", "pages")
    pastas = set()
    if os.path.isdir(dpag):
        pastas = {n for n in os.listdir(dpag) if os.path.isdir(os.path.join(dpag, n))}
        for n in sorted(pastas):
            pp = os.path.join(dpag, n, "page.json")
            if not os.path.exists(pp):
                erros.append("pages/%s: pasta de pagina sem page.json" % n)
                continue
            conferir_pagina(pp, erros)
            dvis = os.path.join(dpag, n, "visuals")
            if os.path.isdir(dvis):
                for vn in sorted(os.listdir(dvis)):
                    vp = os.path.join(dvis, vn, "visual.json")
                    if os.path.exists(vp):
                        conferir_visual(vp, erros)

    idx = os.path.join(dpag, "pages.json")
    if os.path.exists(idx):
        try:
            d = ler(idx)
            for n in d.get("pageOrder", []):
                if n not in pastas:
                    erros.append("pages.json: pageOrder cita '%s', que nao existe em pasta" % n)
            ativa = d.get("activePageName")
            if ativa and ativa not in pastas:
                erros.append("pages.json: activePageName '%s' nao existe em pasta" % ativa)
        except Exception as e:
            erros.append("pages.json: ilegivel (%s)" % e)

    rp = os.path.join(raiz, "definition", "report.json")
    if os.path.exists(rp):
        try:
            d = ler(rp)
        except Exception as e:
            erros.append("report.json: ilegivel (%s)" % e)
            return
        for pac in d.get("resourcePackages", []):
            base = "SharedResources" if pac.get("type") == "SharedResources" else "RegisteredResources"
            for item in pac.get("items", []):
                alvo = os.path.join(raiz, "StaticResources", base, item.get("path", ""))
                if not os.path.exists(alvo):
                    erros.append("report.json: recurso '%s' declarado e ausente em StaticResources/%s"
                                 % (item.get("path"), base))
        tema = (d.get("themeCollection") or {}).get("customTheme") or {}
        if tema.get("name"):
            if tema.get("type") == "SharedResources":
                alvo = os.path.join(raiz, "StaticResources", "SharedResources", "BuiltInThemes",
                                    tema["name"] + ".json")
            else:
                alvo = os.path.join(raiz, "StaticResources", "RegisteredResources", tema["name"])
            if not os.path.exists(alvo):
                erros.append("report.json: customTheme '%s' nao esta no disco" % tema["name"])
            else:
                try:
                    ler(alvo)
                except Exception as e:
                    erros.append("tema '%s': JSON ilegivel (%s); tema quebrado derruba a carga"
                                 % (tema["name"], e))


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    raiz = raiz_do_relatorio(caminho_tocado(payload))
    if not raiz or not os.path.isdir(os.path.join(raiz, "definition")):
        return 0

    erros = []
    conferir_relatorio(raiz, erros)
    if not erros:
        return 0

    sys.stderr.write(
        "RELATORIO PBIP COM DEFEITO DE ESTRUTURA em %s\n\n  - %s\n\n"
        "Isso e o que o Desktop devolve como \"Falha ao carregar o relatorio\", sem dizer onde. "
        "Corrija antes de pedir para o usuario abrir: cada ida ao Desktop e tempo dele.\n"
        % (os.path.basename(raiz), "\n  - ".join(erros[:25]))
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
