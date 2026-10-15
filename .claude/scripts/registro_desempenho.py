#!/usr/bin/env python3
"""Gera o registro anual de desempenho a partir das demandas.

Uma linha por entrega com as dez colunas do registro de carreira: entrega, objetivo,
status, prioridade, periodo, impacto, evidencia, feedback, competencias e visibilidade.
Nada aqui e mantido a mao. A fonte e o que ja esta nas pastas de demanda (fechamento,
documentacao, valor, entrega, contexto, solicitacao), e o que nao da para ler vira
lacuna visivel, nunca texto inventado.

Campo declarado no bloco de valor (**Feedback:**, **Competencias:**, **Visibilidade:**)
vence o inferido. Inferido sai marcado com "(inferido)".

Uso:
    python .claude/scripts/registro_desempenho.py         # imprime o resumo
    python .claude/scripts/registro_desempenho.py --md    # grava gerencial/desempenho/
"""
import collections
import datetime
import glob
import json
import os
import re
import sys
import unicodedata

DOCS = ("fechamento.md", "documentacao.md", "valor.md", "entrega.md",
        "contexto.md", "solicitacao.md", "plano.md")

# prefixo do codigo da demanda -> frente. Prefixo novo entra aqui junto com a
# gaveta; o que nao estiver na lista sai como "outra".
FRENTES = {"TSK": "task", "INC": "incidente", "BI": "bi", "APP": "app"}

# competencia -> termos que a denunciam no texto da demanda (ja achatado)
COMPETENCIAS = collections.OrderedDict([
    ("DAX e métricas", (r"\bdax\b", r"\bmedida", r"time intelligence", r"\bkpi")),
    ("Modelagem de dados", (r"power query", r"modelo semantico", r"relacionamento",
                            r"\btmdl\b", r"star schema", r"\bdimens", r"\bfato\b")),
    ("Visualização e UX de painel", (r"visual\.json", r"\bvisua(l|is)\b", r"layout",
                                     r"slicer", r"\bcard", r"\baba\b")),
    ("Engenharia de dados", (r"databricks", r"synapse", r"pipeline", r"notebook",
                             r"lakehouse", r"\betl\b", r"\bdelta\b")),
    ("SQL e banco", (r"\boracle\b", r"\bsql\b", r"\bview\b", r"procedure", r"\bquery\b")),
    ("Automação", (r"\bairflow\b", r"power automate", r"automac", r"agendament", r"\bwebhook")),
    ("Desenvolvimento de aplicação", (r"\bnode\b", r"express", r"\bfront", r"\bback\b",
                                      r"\bapi\b", r"\bpr #?\d")),
    ("IA aplicada", (r"\bagente", r"\bia\b", r"\bllm\b", r"\bclaude\b", r"\bprompt",
                     r"copilot")),
    ("Governança de dados", (r"governanc", r"catalogo", r"linhagem", r"\bacesso",
                             r"seguranc", r"segredo")),
    ("Diagnóstico e causa raiz", (r"causa raiz", r"refut", r"diagnostic", r"hipotese",
                                  r"reconcili")),
    ("Comunicação com o negócio", (r"alinhament", r"reuniao", r"devolutiva",
                                   r"homologa", r"solicitante")),
])

# solicitante que denuncia trabalho interno do proprio time. Acrescente aqui o
# seu nome e o do seu time para a visibilidade sair certa.
INTERNO = re.compile(r"\b(interno|epico|épico|ti\b|n/a|governan|frente dados)",
                     re.IGNORECASE)


def achatar(texto):
    limpo = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in limpo if not unicodedata.combining(c)).lower()


def campo(texto, *rotulos):
    """Valor de **Rotulo:** ate o fim da linha ou o proximo separador |."""
    plano = achatar(texto)
    for rotulo in rotulos:
        padrao = r"\*\*" + achatar(rotulo) + r"[^*\n]{0,40}?:\*\*\s*([^\n|]+)"
        achado = re.search(padrao, plano)
        if achado:
            ini = achado.start(1)
            bruto = texto[ini:ini + len(achado.group(1))].strip()
            bruto = bruto.strip("{}<> ")
            if bruto and not bruto.startswith("{") and bruto.lower() not in ("—", "-", "n/a"):
                return bruto
    return ""


def primeiro_bullet(texto, secao):
    plano = achatar(texto)
    achado = re.search(r"\*\*" + achatar(secao) + r"[^*\n]*:\*\*\s*\n\s*[*-]\s+([^\n]+)", plano)
    if not achado:
        return ""
    ini = achado.start(1)
    return texto[ini:ini + len(achado.group(1))].strip()


def data(bruto):
    achado = re.search(r"(\d{2})[-/](\d{2})[-/](\d{4})", bruto or "")
    if not achado:
        return None
    try:
        return datetime.date(int(achado.group(3)), int(achado.group(2)), int(achado.group(1)))
    except ValueError:
        return None


def curto(texto, limite=220):
    texto = re.sub(r"\s+", " ", texto or "").strip()
    texto = texto.replace("|", "/")
    texto = re.sub(r"\[\[([^\]|]+)(\|[^\]]+)?\]\]", r"\1", texto)
    return texto if len(texto) <= limite else texto[:limite - 1].rstrip() + "…"


def titulo(textos, nome):
    for arq in ("fechamento.md", "documentacao.md", "valor.md", "solicitacao.md"):
        texto = textos.get(arq, "")
        for linha in texto.splitlines():
            if not linha.startswith("#"):
                continue
            linha = linha.lstrip("#").strip()
            linha = re.sub(r"^[^\w\[]+", "", linha)            # emoji
            linha = re.sub(r"^(Fechamento|Valor|Documentacao|Documentação)\s*[—-]\s*", "", linha)
            linha = re.sub(r"^\[([A-Z]+-[\d.]+)\s*[—-]\s*([^\]]+)\]", r"", linha)  # [ID — X]
            linha = re.sub(r"^\[[^\]]+\]\s*[—-]?\s*", "", linha)  # [ID] —
            linha = re.sub(r"^(DEM_)?[A-Z]+-[\d.]+\s*[—-]\s*", "", linha)  # ID —
            linha = re.sub(r"^[\w.-]+\s*\|\s*", "", linha) if "|" in linha[:30] else linha
            linha = re.split(r"\s+\|\s+\S+\s+[—-]", linha)[0]  # | ALTA — MEDIO — SLA
            if re.match(r"(Documenta[cç][aã]o de (entrega|fechamento)|T\d+ [—-] Documenta)", linha, re.I):
                partes = linha.split(" / ", 1)
                if len(partes) == 2 and len(partes[1]) > 5:
                    return partes[1]
                continue  # cabecalho generico: o titulo real vem no proximo heading
            if len(linha) > 5:
                return linha
    slug = nome.split("_", 2)[-1] if nome.count("_") >= 2 else nome
    return slug.replace("-", " ").capitalize()


def prioridade(textos):
    junto = "\n".join(textos.values())
    origem = achatar(campo(junto, "Origem da prioridade"))
    for termo, nivel in (("urgencia", "Alta"), ("estrategica", "Alta"),
                         ("rotina", "Média"), ("volume", "Baixa")):
        if termo in origem:
            return "%s (%s)" % (nivel, {"urgencia": "urgência", "estrategica": "estratégica"}.get(termo, termo))
    risco = achatar(campo(junto, "Risco"))
    for termo, nivel in (("alto", "Alta"), ("medio", "Média"), ("baixo", "Baixa")):
        if risco.startswith(termo):
            return "%s (pelo risco)" % nivel
    return "—"


def visibilidade(textos, ident, citacoes):
    declarado = campo("\n".join(textos.values()), "Visibilidade")
    if declarado:
        return declarado
    partes = []
    junto = "\n".join(textos.values())
    marcadores = campo(junto, "Marcadores")
    solicitante = campo(junto, "Solicitante", "Solicitado por")
    areas = [m.strip() for m in re.split(r"[·,/]", marcadores) if m.strip()][1:]
    if solicitante and not INTERNO.search(solicitante):
        partes.append("área solicitante" + (" (%s)" % ", ".join(areas[:2]) if areas else ""))
    elif solicitante:
        partes.append("TI / uso interno")
    semanas = sorted(citacoes.get(ident, {}).get("semana", []))
    pai = ident.split(".")[0]
    if not semanas and pai != ident and citacoes.get(pai, {}).get("semana"):
        semanas = ["épico " + pai + ": " + ", ".join(sorted(citacoes[pai]["semana"]))]
    if semanas:
        partes.append("gestão no reporte semanal (%s)" % ", ".join(semanas))
    if citacoes.get(ident, {}).get("dia"):
        partes.append("daily")
    if citacoes.get(ident, {}).get("reuniao"):
        partes.append("reunião registrada")
    return (" · ".join(partes) + " (inferido)") if partes else "não registrado"


def feedback(textos):
    junto = "\n".join(textos.values())
    declarado = campo(junto, "Feedback")
    if declarado:
        return declarado
    plano = achatar(junto)
    sinais = []
    if re.search(r"(aprovad|validad)[a-z]* (pel[oa]|com o) (solicitante|area|usuario|gestor|gerente|rh|comercial)", plano):
        sinais.append("validação aprovada pela área")
    if re.search(r"devolutiva|retorno de validacao|rodada de (validacao|homologacao)", plano):
        sinais.append("houve rodada de devolutiva")
    if re.search(r"elogi|agradec|gostou|parabeniz", plano):
        sinais.append("retorno positivo citado")
    return (" · ".join(sinais) + " (inferido)") if sinais else "não registrado"


def competencias(textos):
    junto = "\n".join(textos.values())
    declarado = campo(junto, "Competências", "Competencias")
    if declarado:
        return declarado, [c.strip() for c in re.split(r"[·,;]", declarado) if c.strip()]
    plano = achatar(junto)
    placar = []
    for nome, termos in COMPETENCIAS.items():
        n = sum(len(re.findall(t, plano)) for t in termos)
        if n >= 2:
            placar.append((n, nome))
    top = [nome for _, nome in sorted(placar, reverse=True)[:3]]
    return ((", ".join(top) + " (inferido)") if top else "não registrado"), top


def ler_citacoes(raiz):
    """Onde cada ID de demanda apareceu: semanal, daily, reuniao."""
    cit = collections.defaultdict(lambda: collections.defaultdict(set))
    prefixos = "|".join(sorted(FRENTES, key=len, reverse=True))
    padrao = re.compile(r"\b((?:DEM_)?(?:%s)-[\d.]+)" % prefixos)
    fontes = (("semana", "gerencial/semana/*/resumo.md"), ("dia", "gerencial/dia/*.md"),
              ("reuniao", "gerencial/reunioes/**/*.md"))
    for tipo, mascara in fontes:
        for caminho in glob.glob(os.path.join(raiz, mascara), recursive=True):
            with open(caminho, encoding="utf-8", errors="replace") as fh:
                texto = fh.read()
            rotulo = os.path.basename(os.path.dirname(caminho)) if tipo == "semana" else caminho
            for achado in set(padrao.findall(texto)):
                chave = achado.replace("DEM_", "").rstrip(".")
                cit[chave][tipo].add(rotulo)
    return cit


def ler_demandas(raiz):
    citacoes = ler_citacoes(raiz)
    linhas = []
    base = os.path.join(raiz, "demandas")
    for atual, pastas, arquivos in os.walk(base):
        nome = os.path.basename(atual)
        if not nome.startswith("DEM_") or any(p.startswith("DEM_") for p in pastas):
            continue  # epico: quem entrega sao as filhas
        textos = {}
        for arq in DOCS:
            caminho = os.path.join(atual, arq)
            if os.path.exists(caminho):
                with open(caminho, encoding="utf-8", errors="replace") as fh:
                    textos[arq] = fh.read()
        if not textos:
            continue
        rel = os.path.relpath(atual, raiz).replace(os.sep, "/")
        arquivada = any(os.path.exists(os.path.join(p, "ARQUIVADO.md"))
                        for p in _ancestrais(atual, base))
        aguardando = os.path.exists(os.path.join(atual, "AGUARDANDO.md"))
        fechada = "fechamento.md" in textos or "documentacao.md" in textos
        final = "\n".join(textos.get(a, "") for a in ("fechamento.md", "documentacao.md"))
        tudo = "\n".join(textos.values())

        ident = re.match(r"DEM_([A-Z]+-[\d.]+)", nome)
        ident = ident.group(1) if ident else nome
        frente = FRENTES.get(ident.split("-")[0], "outra")

        entrega = data(campo(final, "Entrega", "Encerramento", "Data")) if fechada else None
        if fechada and not entrega:
            entrega = data(campo(tudo, "Entrega", "Encerramento", "Data"))
        criacao = data(campo(tudo, "Criação", "Criacao", "Data de criacao", "Data de criação",
                             "No caderno desde", "Data"))
        if arquivada:
            status = "arquivada"
        elif fechada:
            st = achatar(campo(final, "Status"))
            status = "entregue" if not st or re.search(r"entreg|validad|conclu|encerr|estabiliz", st) else "entregue (%s)" % curto(campo(final, "Status"), 40)
        elif aguardando:
            status = "aguardando terceiro"
        else:
            status = "em andamento"

        objetivo = (campo(tudo, "Dor endereçada", "Dor enderecada") or campo(final, "Problema")
                    or campo(final, "Por que foi feito") or campo(tudo, "Objetivo"))
        impacto = (campo(tudo, "O que mudou (depois)", "O que mudou", "Depois")
                   or campo(final, "O que muda na prática", "O que muda na pratica")
                   or primeiro_bullet(final, "Solução") or primeiro_bullet(final, "Solucao"))
        evid = campo(tudo, "Medida ou proxy") or campo(tudo, "Evidência", "Evidencia") \
            or primeiro_bullet(final, "Validação") or primeiro_bullet(final, "Validacao")
        comp_txt, comp_lista = competencias(textos)

        periodo = entrega or criacao or data_git(raiz, rel, fechada)
        linhas.append({
            "id": ident, "pasta": rel, "frente": frente,
            "entrega": curto(titulo(textos, nome), 90),
            "objetivo": curto(objetivo) if objetivo else "não registrado",
            "status": status,
            "prioridade": prioridade(textos),
            "periodo": periodo.isoformat() if periodo else "",
            "periodo_tipo": "entrega" if entrega else ("abertura" if criacao else ""),
            "impacto": curto(impacto) if impacto and fechada else ("—" if not fechada else "não registrado"),
            "evidencia": curto(evid) if evid and fechada else ("—" if not fechada else "não registrado"),
            "feedback": feedback(textos) if fechada else "—",
            "competencias": comp_txt, "competencias_lista": comp_lista,
            "visibilidade": visibilidade(textos, ident, citacoes),
        })
    return linhas


def data_git(raiz, rel, fechada):
    """Ultimo recurso: quando o documento nao traz data, vale o commit dele."""
    import subprocess
    alvo = rel + ("/documentacao.md" if fechada else "")
    try:
        saida = subprocess.run(["git", "-C", raiz, "log", "-1", "--format=%as", "--", alvo, rel + "/fechamento.md"],
                               capture_output=True, text=True, timeout=20).stdout.strip()
        return datetime.date.fromisoformat(saida) if saida else None
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def _ancestrais(atual, base):
    while True:
        yield atual
        if os.path.normpath(atual) == os.path.normpath(base):
            return
        atual = os.path.dirname(atual)


def fmt_data(iso):
    return "%s-%s-%s" % (iso[8:10], iso[5:7], iso[0:4]) if iso else "—"


def markdown(ano, regs):
    entregues = [r for r in regs if r["status"].startswith("entregue")]
    abertas = [r for r in regs if r["status"] in ("em andamento", "aguardando terceiro")]
    comp = collections.Counter(c for r in entregues for c in r["competencias_lista"])
    frentes = collections.Counter(r["frente"] for r in entregues)
    na_gestao = sum(1 for r in entregues if "reporte semanal" in r["visibilidade"])
    com_feedback = sum(1 for r in entregues if r["feedback"] != "não registrado")
    com_impacto = sum(1 for r in entregues if r["impacto"] != "não registrado")
    L = [
        "# Registro de desempenho %s (derivado)" % ano,
        "",
        "> INTERNO e pessoal. Gerado por `.claude/scripts/registro_desempenho.py` a partir das",
        "> demandas. **Não editar à mão**: para corrigir uma linha, corrija o fechamento ou o bloco",
        "> de valor da demanda e rode o script de novo. O painel visual é [[painel-%s]]." % ano,
        "> Campo marcado `(inferido)` saiu da leitura do texto e vale como pista, não como fato.",
        "",
        "## Resumo do ano",
        "",
        "- Entregas: **%d** · em aberto: **%d**" % (len(entregues), len(abertas)),
        "- Com impacto registrado: **%d** · com feedback registrado ou inferido: **%d** · citadas no reporte semanal: **%d**"
        % (com_impacto, com_feedback, na_gestao),
        "- Por frente: " + " · ".join("%s %d" % kv for kv in frentes.most_common()),
        "- Competências mais exercidas: " + " · ".join("%s %d" % kv for kv in comp.most_common(6)),
        "",
    ]
    cab = ("| Período | Entrega | Objetivo | Status | Prioridade | Impacto | Evidência | "
           "Feedback | Competências | Visibilidade |")
    por_mes = collections.defaultdict(list)
    for r in regs:
        por_mes[r["periodo"][:7] or "sem data"].append(r)
    meses = ("", "janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
             "agosto", "setembro", "outubro", "novembro", "dezembro")
    for mes in sorted(por_mes, reverse=True):
        rot = "%s de %s" % (meses[int(mes[5:7])], mes[:4]) if mes != "sem data" else mes
        L += ["## %s" % rot.capitalize(), "", cab, "|" + "---|" * 10]
        for r in sorted(por_mes[mes], key=lambda x: x["periodo"], reverse=True):
            per = fmt_data(r["periodo"]) + ("" if r["periodo_tipo"] != "abertura" else " (abertura)")
            L.append("| %s | **%s** [[%s\\|%s]] | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                per, r["entrega"], os.path.basename(r["pasta"]), r["id"], r["objetivo"],
                r["status"], r["prioridade"], r["impacto"], r["evidencia"], r["feedback"],
                r["competencias"], r["visibilidade"]))
        L.append("")
    return "\n".join(L) + "\n"


def painel(ano, regs, raiz):
    modelo = os.path.join(raiz, "conhecimento", "modelos", "painel-desempenho.html")
    with open(modelo, encoding="utf-8") as fh:
        html = fh.read()
    dados = json.dumps({"ano": ano, "gerado": datetime.date.today().isoformat(),
                        "linhas": regs}, ensure_ascii=False)
    return html.replace("/*__DADOS__*/null", dados.replace("</", "<\\/"))


def main():
    raiz = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    regs = [r for r in ler_demandas(raiz) if r["status"] != "arquivada"]
    por_ano = collections.defaultdict(list)
    for r in regs:
        por_ano[r["periodo"][:4] or str(datetime.date.today().year)].append(r)

    if "--md" not in sys.argv:
        for ano in sorted(por_ano):
            ent = sum(1 for r in por_ano[ano] if r["status"].startswith("entregue"))
            print("%s: %d linhas, %d entregues" % (ano, len(por_ano[ano]), ent))
        return 0

    destino = os.path.join(raiz, "gerencial", "desempenho")
    os.makedirs(destino, exist_ok=True)
    for ano, lista in sorted(por_ano.items()):
        with open(os.path.join(destino, "registro-%s.md" % ano), "w", encoding="utf-8") as fh:
            fh.write(markdown(ano, lista))
        with open(os.path.join(destino, "painel-%s.html" % ano), "w", encoding="utf-8") as fh:
            fh.write(painel(ano, lista, raiz))
        print("gravado gerencial/desempenho/registro-%s.md e painel-%s.html (%d linhas)"
              % (ano, ano, len(lista)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
