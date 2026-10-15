#!/usr/bin/env python3
"""Hook SessionStart: coloca o estado do caderno na mesa antes da primeira pergunta.

Faz duas coisas com a mesma leitura. Injeta o estado como contexto, para a sessao
comecar sabendo onde parou, e grava PAINEL.md, para o mesmo estado ficar legivel
fora da conversa (no Obsidian, no editor, em qualquer lugar).

O painel e derivado: nasce daqui a cada abertura de sessao e nao se mantem a mao.
Fica fora do git de proposito, pela mesma razao do log bruto: e retrato do estado
de uma maquina num instante, e o que atravessa maquinas e o registro destilado.

O desenho e horizontal por escolha. Ele existe para responder "como estao as
coisas" numa olhada, entao o macro vem em tabela e o detalhe longo fica recolhido.
"""
import io
import json
import os
import re
import sys
from datetime import datetime, timedelta

# prefixo do codigo -> nome da frente no painel. Prefixo novo que nao estiver
# aqui aparece pelo proprio prefixo; acrescente a linha quando criar a gaveta.
GAVETAS = {
    "TSK": "Tasks de sprint",
    "INC": "Incidentes",
    "BI": "Projetos de BI",
    "APP": "Aplicacao",
}

# uma demanda sem toque ha mais tempo que isso entra no bloco de esquecidas
LIMITE_ESQUECIDA = 21

# quantas esquecidas o painel mostra antes de mandar para o detalhe recolhido
TETO_ESQUECIDAS = 8


# marcador nao e trabalho na demanda: se contasse, arquivar ou marcar espera
# zeraria o contador de parada e a demanda pareceria recem-tocada
MARCADORES = ("ARQUIVADO.md", "AGUARDANDO.md")


def idade_em_dias(pasta, agora):
    """Ha quantos dias o arquivo mais recente da demanda foi tocado."""
    recente = 0
    for atual, _, arquivos in os.walk(pasta):
        for arq in arquivos:
            if arq in MARCADORES:
                continue
            try:
                recente = max(recente, os.path.getmtime(os.path.join(atual, arq)))
            except OSError:
                continue
    if not recente:
        return None
    return int((agora.timestamp() - recente) // 86400)


def celula(texto, limite=70):  # limite ajustavel por chamada
    """Texto seguro para dentro de tabela markdown.

    Pipe em celula quebra a tabela: o titulo de um dia do diario costuma ser
    "DEM_X | assunto | STATUS", e sem escapar isso vira coluna a mais.
    """
    if not texto:
        return "-"
    texto = " ".join(texto.split()).replace("|", "\\|")
    if len(texto) > limite:
        texto = texto[:limite - 1].rstrip() + "…"
    return texto


def dito_em_dias(dias):
    if dias is None:
        return "-"
    if dias == 0:
        return "hoje"
    if dias == 1:
        return "1 dia"
    return "%d dias" % dias


def assunto_da_demanda(caminho_solicitacao, slug):
    """O que a demanda e, dito do jeito mais informativo disponivel.

    O titulo dentro do documento e melhor que o slug da pasta, e para tarefa
    filha de epico e a unica fonte: a pasta dela e so o codigo, sem descricao.
    """
    try:
        with io.open(caminho_solicitacao, encoding="utf-8") as fh:
            for linha in fh:
                if linha.startswith("# "):
                    titulo = linha[2:].strip()
                    if "|" in titulo:  # "CODIGO | assunto" -> fica so o assunto
                        titulo = titulo.split("|", 1)[1].strip()
                    # alguns titulos repetem o codigo antes de um travessao;
                    # na coluna estreita isso gasta o espaco do que importa
                    for sep in ("—", " - "):
                        if titulo.startswith("DEM_") and sep in titulo:
                            titulo = titulo.split(sep, 1)[1].strip()
                            break
                    if titulo:
                        return titulo
                    break
    except (OSError, UnicodeDecodeError):
        pass
    return slug


def arquivada(pasta, base):
    """ARQUIVADO.md na propria pasta ou em qualquer pasta acima (ate demandas/).

    Arquivar nao e fechar nem apagar: a demanda sai da cobranca do painel e o
    material fica no lugar. Apagar o marcador traz tudo de volta."""
    atual = pasta
    while True:
        if os.path.isfile(os.path.join(atual, "ARQUIVADO.md")):
            return True
        if os.path.normpath(atual) == os.path.normpath(base):
            return False
        pai = os.path.dirname(atual)
        if pai == atual:
            return False
        atual = pai


def espera_de_terceiro(pasta):
    """AGUARDANDO.md marca demanda travada em terceiro, com quem e desde quando.

    Sem isso o painel diz "parada ha 35 dias" e cobra do usuario o atraso de
    outra pessoa. O frontmatter e simples de proposito: quem, desde, nota."""
    caminho = os.path.join(pasta, "AGUARDANDO.md")
    if not os.path.isfile(caminho):
        return None
    try:
        with io.open(caminho, encoding="utf-8", errors="replace") as fh:
            texto = fh.read()
    except OSError:
        return None
    bloco = re.match(r"^---\s*\n(.*?)\n---", texto, re.S)
    if not bloco:
        return {"quem": "terceiro", "desde": None, "dias": None, "nota": ""}
    campos = {}
    for linha in bloco.group(1).splitlines():
        if ":" in linha:
            chave, valor = linha.split(":", 1)
            campos[chave.strip()] = valor.strip()
    desde = campos.get("desde")
    dias = None
    if desde:
        try:
            dias = (datetime.now() - datetime.strptime(desde[:10], "%Y-%m-%d")).days
        except ValueError:
            dias = None
    return {
        "quem": campos.get("quem", "terceiro"),
        "desde": desde,
        "dias": dias,
        "nota": campos.get("nota", ""),
    }


def demandas_abertas(raiz, agora):
    """Demanda sem fechamento. Epico nao conta: quem fecha sao as filhas.

    Devolve (abertas, arquivadas): as arquivadas saem da cobranca, mas sao
    contadas para o painel dizer que existem."""
    abertas = []
    arquivadas = []
    base = os.path.join(raiz, "demandas")
    if not os.path.isdir(base):
        return abertas, arquivadas
    for atual, pastas, arquivos in os.walk(base):
        nome = os.path.basename(atual)
        if not nome.startswith("DEM_"):
            continue
        if any(p.startswith("DEM_") for p in pastas):
            continue
        if "fechamento.md" in arquivos or "documentacao.md" in arquivos:
            continue
        if "solicitacao.md" not in arquivos:
            continue
        if arquivada(atual, base):
            arquivadas.append(nome)
            continue
        partes = nome.split("_", 2)
        codigo = partes[1] if len(partes) > 1 else nome
        slug = partes[2].replace("-", " ") if len(partes) > 2 else ""
        abertas.append({
            "nome": nome,
            "codigo": codigo,
            "assunto": assunto_da_demanda(os.path.join(atual, "solicitacao.md"), slug),
            "prefixo": codigo.split("-")[0],
            "caminho": os.path.relpath(atual, raiz).replace("\\", "/") + "/solicitacao.md",
            "parada": idade_em_dias(atual, agora),
            "espera": espera_de_terceiro(atual),
        })
    return abertas, arquivadas


def dias_sem_narrativa(raiz, agora, janela=14):
    faltando = []
    for recuo in range(1, janela + 1):
        dia = (agora - timedelta(days=recuo)).strftime("%Y-%m-%d")
        log = os.path.join(raiz, "diario", ".log", dia + ".jsonl")
        if os.path.exists(log) and not os.path.exists(os.path.join(raiz, "diario", dia + ".md")):
            faltando.append(dia)
    return faltando


def ultimos_diarios(raiz, quantos=5):
    """Os ultimos dias narrados, com o titulo que cada um deu ao dia."""
    pasta = os.path.join(raiz, "diario")
    if not os.path.isdir(pasta):
        return []
    nomes = sorted(n for n in os.listdir(pasta)
                   if n.endswith(".md") and n[:4].isdigit())
    saida = []
    for nome in nomes[-quantos:][::-1]:
        titulo = ""
        try:
            with io.open(os.path.join(pasta, nome), encoding="utf-8") as fh:
                for linha in fh:
                    if linha.startswith("## "):
                        titulo = linha[3:].strip()
                        break
        except (OSError, UnicodeDecodeError):
            pass
        saida.append((nome[:-3], titulo))
    return saida


def grade_da_semana(raiz, agora):
    """A grade do plano da semana corrente, se ela foi planejada."""
    semana = agora.strftime("%Y-W%V")
    caminho = os.path.join(raiz, "gerencial", "semana", semana, "plano-semana.md")
    if not os.path.exists(caminho):
        return semana, None, []
    rel = "gerencial/semana/%s/plano-semana.md" % semana
    linhas = []
    try:
        with io.open(caminho, encoding="utf-8") as fh:
            dentro = False
            for linha in fh:
                if linha.startswith("| Dia"):
                    dentro = True
                    continue
                if dentro:
                    if not linha.startswith("|"):
                        break
                    if set(linha.strip()) <= set("|- "):
                        continue
                    linhas.append(linha.rstrip())
    except (OSError, UnicodeDecodeError):
        pass
    return semana, rel, linhas


def escapa(texto):
    """Texto seguro dentro de HTML, ja truncado para caber na coluna."""
    if texto is None:
        return ""
    return (str(texto).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def curto(texto, limite=46):
    """Assunto do tamanho de uma manchete: diz o que e, sem esticar a coluna."""
    if not texto:
        return "-"
    texto = " ".join(str(texto).split())
    if len(texto) <= limite:
        return escapa(texto)
    corte = texto[:limite].rsplit(" ", 1)[0]  # nao parte palavra no meio
    return escapa((corte or texto[:limite]).rstrip(" ,;:-") + "\u2026")


def link(codigo, caminho):
    """Link que o Obsidian reconhece como navegacao interna do cofre."""
    return ('<a class="internal-link" data-href="%s" href="%s">%s</a>'
            % (escapa(caminho), escapa(caminho), escapa(codigo)))


def tabela_html(cabecalhos, linhas):
    saida = ['<table style="width:100%;font-size:0.8em">', "<thead><tr>"]
    saida.extend('<th align="left">%s</th>' % escapa(c) for c in cabecalhos)
    saida.append("</tr></thead><tbody>")
    for linha in linhas:
        saida.append("<tr>" + "".join("<td>%s</td>" % c for c in linha) + "</tr>")
    saida.append("</tbody></table>")
    return "".join(saida)


def bloco(titulo, corpo):
    return ('<div><h4 style="margin:0 0 .4em 0;font-size:.95em">%s</h4>%s</div>'
            % (escapa(titulo), corpo))


def fila_sugerida(incidentes, resto, quantos=5):
    """O que pegar a seguir, derivado do estado. Sem data e sem promessa.

    Ordem: incidente aberto primeiro, porque instabilidade nao espera; depois
    o que esta parado ha mais tempo, com teto de um por frente, para a fila
    girar as frentes em vez de afunilar sempre na mesma.
    """
    fila = []
    for d in incidentes[:2]:
        fila.append((d, "incidente aberto ha %s" % dito_em_dias(d["parada"])))
    vistas = set()
    for d in sorted([x for x in resto if not x.get("espera")],
                    key=lambda x: -(x["parada"] or 0)):
        if len(fila) >= quantos:
            break
        if d["prefixo"] in vistas:
            continue
        vistas.add(d["prefixo"])
        parada = d["parada"] or 0
        fila.append((d, "tocada hoje" if parada == 0 else "parada ha %s" % dito_em_dias(parada)))
    return fila[:quantos]


def escreve_painel(raiz, agora, abertas, sem_narrativa, arquivadas=None):
    incidentes = sorted([d for d in abertas if d["prefixo"] == "INC"],
                        key=lambda x: -(x["parada"] or 0))
    resto = [d for d in abertas if d["prefixo"] != "INC"]
    semana, rel_semana, grade = grade_da_semana(raiz, agora)
    # quem espera terceiro nao esta esquecido: o relogio corre, o atraso nao e daqui
    paradas = len([d for d in resto
                   if (d["parada"] or 0) >= LIMITE_ESQUECIDA and not d.get("espera")])
    ativas = len([d for d in abertas if (d["parada"] or 99) <= 7])

    p = []
    p.append("# Painel do caderno")
    p.append("")
    p.append("> Derivado pelo hook `abrir_dia.py` a cada abertura de sessao. **Nao editar.** "
             "Estado de %s." % agora.strftime("%d-%m-%Y as %H:%M"))
    p.append("")

    p.append("| Abertas | Incidentes | Paradas +%dd | Mexidas na semana | Sem narrativa | Semana |"
             % LIMITE_ESQUECIDA)
    p.append("|---|---|---|---|---|---|")
    p.append("| **%d** | **%d** | **%d** | **%d** | **%d** | %s |" % (
        len(resto), len(incidentes), paradas, ativas, len(sem_narrativa),
        semana + (" planejada" if grade else "")))
    p.append("")
    if arquivadas:
        p.append("> %d demanda(s) arquivada(s) fora da contagem, por marcador `ARQUIVADO.md`. "
                 "Nada foi apagado; tirar o marcador devolve a demanda ao painel." % len(arquivadas))
        p.append("")
    esperando = [d for d in resto if d.get("espera")]
    if esperando:
        p.append("> Em espera de terceiro (`AGUARDANDO.md`), fora da conta de esquecidas: "
                 + " &middot; ".join(
                     "**%s** %s ha %s" % (d["codigo"], d["espera"]["quem"],
                                          dito_em_dias(d["espera"]["dias"]))
                     for d in sorted(esperando, key=lambda x: -(x["espera"]["dias"] or 0))))
        p.append("")

    # --- tres colunas ------------------------------------------------------
    caixas = []

    fila = fila_sugerida(incidentes, resto)
    if fila:
        caixas.append(bloco("O que pegar a seguir", tabela_html(
            ["Demanda", "Por que", "Assunto"],
            [[link(d["codigo"], d["caminho"]), escapa(motivo), curto(d["assunto"], 50)]
             for d, motivo in fila])))

    if incidentes:
        caixas.append(bloco("Incidentes em aberto", tabela_html(
            ["Incidente", "Parado", "Assunto"],
            [[link(d["codigo"], d["caminho"]), dito_em_dias(d["parada"]),
              curto(d["assunto"], 52)] for d in incidentes])))

    if resto:
        caixas.append(bloco("As frentes", tabela_html(
            ["Frente", "Abertas", "Mais parada", "Semana"],
            [[escapa(GAVETAS.get(pfx, pfx)), str(len(g)),
              link(g[0]["codigo"], g[0]["caminho"]) + " " + dito_em_dias(g[0]["parada"]),
              str(len([d for d in g if (d["parada"] or 99) <= 7]))]
             for pfx, g in sorted(
                 ((pfx, sorted([d for d in resto if d["prefixo"] == pfx],
                               key=lambda x: -(x["parada"] or 0)))
                  for pfx in {d["prefixo"] for d in resto}),
                 key=lambda kv: -len(kv[1]))])))

    diarios = ultimos_diarios(raiz, 6)
    if diarios:
        caixas.append(bloco("Ultimos dias narrados", tabela_html(
            ["Dia", "O que foi"],
            [[link(dia[5:], "diario/%s.md" % dia), curto(titulo, 64)]
             for dia, titulo in diarios])))

    if grade:
        caixas.append(bloco("A semana (%s)" % semana, tabela_html(
            ["Dia", "Frente", "Tarefa"],
            [[escapa(c.strip()) for c in
              ([l.strip("|").split("|")[0], l.strip("|").split("|")[2],
                l.strip("|").split("|")[3]] if len(l.split("|")) > 4 else ["", "", l])]
             for l in grade])))

    if sem_narrativa:
        caixas.append(bloco("Dias sem narrativa",
                            '<p style="font-size:0.8em">%s</p>'
                            % escapa(", ".join(sem_narrativa))))

    p.append('<div style="display:grid;grid-template-columns:1fr 1fr;'
             'gap:4px 28px;align-items:start">')
    p.append("".join(caixas))
    p.append("</div>")
    p.append("")

    # --- markdown de novo, largura inteira ---------------------------------
    esquecidas = sorted([d for d in resto
                         if (d["parada"] or 0) >= LIMITE_ESQUECIDA and not d.get("espera")],
                        key=lambda x: -(x["parada"] or 0))
    if esquecidas:
        mostradas, por_frente = [], {}
        for d in esquecidas:
            if por_frente.get(d["prefixo"], 0) >= 2:
                continue
            por_frente[d["prefixo"]] = por_frente.get(d["prefixo"], 0) + 1
            mostradas.append(d)
            if len(mostradas) >= TETO_ESQUECIDAS:
                break
        p.append("## As mais esquecidas")
        p.append("")
        p.append("%d demandas estao sem toque ha mais de %d dias. As mais paradas de cada frente:"
                 % (len(esquecidas), LIMITE_ESQUECIDA))
        p.append("")
        p.append("| Demanda | Parada ha | Frente | Assunto |")
        p.append("|---|---|---|---|")
        for d in mostradas:
            p.append("| [%s](%s) | %s | %s | %s |" % (
                d["codigo"], d["caminho"], dito_em_dias(d["parada"]),
                GAVETAS.get(d["prefixo"], d["prefixo"]), celula(d["assunto"], 62)))
        p.append("")

    if resto:
        # Recolhivel nativo do Obsidian, nao <details> de HTML: dentro de bloco
        # HTML o Markdown nao e processado e a tabela sai como texto corrido.
        p.append("> [!abstract]- Todas as %d demandas sem fechamento" % len(resto))
        p.append("> ")
        p.append("> | Demanda | Parada ha | Frente | Assunto |")
        p.append("> |---|---|---|---|")
        for d in sorted(resto, key=lambda x: (x["prefixo"], -(x["parada"] or 0))):
            p.append("> | [%s](%s) | %s | %s | %s |" % (
                d["codigo"], d["caminho"], dito_em_dias(d["parada"]),
                GAVETAS.get(d["prefixo"], d["prefixo"]), celula(d["assunto"], 62)))
        p.append("")

    with io.open(os.path.join(raiz, "PAINEL.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(p).rstrip() + "\n")


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    raiz = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    hoje = datetime.now()

    abertas, arquivadas = demandas_abertas(raiz, hoje)
    sem_narrativa = dias_sem_narrativa(raiz, hoje, janela=7)

    # o painel e efeito colateral; se falhar, a sessao abre normalmente
    try:
        escreve_painel(raiz, hoje, abertas, dias_sem_narrativa(raiz, hoje, janela=14),
                       arquivadas)
    except Exception:
        pass

    linhas = []
    if abertas:
        nomes = sorted(d["nome"] for d in abertas)
        linhas.append("Demandas sem fechamento (%d): %s" % (len(nomes), ", ".join(nomes[:12])))
    esperando = [d for d in abertas if d.get("espera")]
    if esperando:
        linhas.append("Em espera de terceiro (%d): %s" % (
            len(esperando),
            ", ".join("%s (%s)" % (d["codigo"], d["espera"]["quem"]) for d in esperando)))
    if arquivadas:
        linhas.append("Arquivadas, fora da cobranca (%d): marcador ARQUIVADO.md" % len(arquivadas))
    if sem_narrativa:
        linhas.append("Dias com trabalho logado e sem narrativa: %s" % ", ".join(sem_narrativa))
    if abertas or sem_narrativa or arquivadas:
        linhas.append("Quadro completo e navegavel em PAINEL.md (derivado, regravado agora).")

    if not linhas:
        return 0

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "Estado do caderno em %s:\n%s" % (
                hoje.strftime("%d-%m-%Y"), "\n".join("- " + x for x in linhas)),
        }
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
