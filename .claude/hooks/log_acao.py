#!/usr/bin/env python3
"""Hook PostToolUse: registra em log bruto toda escrita de arquivo do trabalho.

E a camada determinista do registro. Nao depende de ninguem lembrar de nada:
toda vez que um arquivo e escrito, uma linha entra no log do dia. A daily, a
semanal e o fechamento leem esse log em vez de reconstruir de memoria.

Cobre DOIS repositorios: o caderno (registro) e o de codigo apontado pela
variavel CADERNO_REPO_TRABALHO (o trabalho tecnico em si, por exemplo os
dashboards). Sem o segundo o log mostra so a documentacao do trabalho.

Cada linha carrega, alem do arquivo, o que da para inferir sem abrir nada:
a etapa da esteira, a camada do dashboard tocada, e - em fechamento - a data
de entrega DECLARADA no proprio documento, que e o que separa entrega do dia
de versionamento tardio de trabalho antigo.
"""
import json
import os
import re
import sys
import time
from datetime import datetime

# extensoes que valem registro; binario e temporario ficam de fora
EXTENSOES = (".md", ".py", ".html", ".json", ".tmdl", ".dax", ".sql", ".yml", ".yaml")

# repositorio de codigo (dashboards): caminho em CADERNO_REPO_TRABALHO; o nome
# da pasta serve de marcador, porque o caminho absoluto muda de maquina para
# maquina e o nome da pasta nao. Sem a variavel, o log cobre so o caderno.
MARCADOR_DASHBOARDS = os.path.basename(
    os.path.normpath(os.environ.get("CADERNO_REPO_TRABALHO", ""))) if os.environ.get("CADERNO_REPO_TRABALHO") else ""

PADROES_SHELL = (
    r">>?\s*['\"]?([^\s'\"|;&>]+)",          # redirecao: > arquivo  e  >> arquivo
    r"\bsed\s+-i[^\s]*\s+(?:-e\s+[^\s]+\s+)*['\"]?([^\s'\"|;&]+)",
    r"\btee\s+(?:-a\s+)?['\"]?([^\s'\"|;&]+)",
    r"\b(?:cp|mv)\s+(?:-\w+\s+)*[^\s]+\s+['\"]?([^\s'\"|;&]+)",
    # script python inline: io.open("x","w") / open("x","w"). Sem isso, todo
    # arquivo escrito por script embutido some do log.
    r"\b(?:io\.)?open\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"][wa]",
)

# nome do arquivo -> etapa da esteira
ETAPA_POR_ARQUIVO = {
    "solicitacao.md": "abertura",
    "contexto.md": "analise",
    "plano.md": "planejamento",
    "entrega.md": "entrega",
    "fechamento.md": "fechamento",
    "documentacao.md": "fechamento",
    "valor.md": "valor",
    "retro.md": "retro",
    "aguardando.md": "marcador",
    "arquivado.md": "marcador",
}

# arquivos cuja escrita declara uma entrega
ARQUIVOS_DE_FECHAMENTO = ("fechamento.md", "documentacao.md")


def alvos_de_shell(comando):
    """Extrai, de forma conservadora, os arquivos que um comando escreve.

    Heuristica de proposito estreita: so caminhos com extensao conhecida. Prefere
    perder uma escrita a poluir o log com falso positivo. O texto do comando so
    levanta CANDIDATOS; quem confirma e o mtime (ver mexeu_agora), senao comando
    que apenas MENCIONA um caminho vira registro de escrita que nunca houve.
    """
    if not comando:
        return []
    achados = []
    for padrao in PADROES_SHELL:
        for alvo in re.findall(padrao, comando):
            if alvo.startswith(("/dev/", "/tmp/")) or "$" in alvo:
                continue
            if alvo.lower().endswith(EXTENSOES):
                achados.append(alvo)
    return achados


JANELA_MTIME = 90  # segundos


def mexeu_agora(absoluto):
    """O arquivo foi mesmo escrito por este comando?

    Vale so para alvo extraido de texto de shell. Sem isso, mencionar o caminho
    num heredoc, num script de exemplo ou num teste ja gera linha no log.
    """
    try:
        return (time.time() - os.path.getmtime(absoluto)) <= JANELA_MTIME
    except OSError:
        return False


def caminho_absoluto(alvo, raiz, cwd):
    p = alvo.replace("\\", "/")
    if not os.path.isabs(p):
        p = os.path.join(cwd or raiz, p)
    return os.path.normpath(p).replace("\\", "/")


def localizar(absoluto, raiz):
    """Diz de que repositorio o arquivo e, e o caminho relativo dentro dele."""
    r = absoluto.replace("\\", "/")
    base = os.path.normpath(raiz).replace("\\", "/").rstrip("/")
    if r.lower().startswith(base.lower() + "/"):
        return "caderno", r[len(base) + 1:]
    if not MARCADOR_DASHBOARDS:
        return None, None
    m = re.search(r"/%s/(.+)$" % re.escape(MARCADOR_DASHBOARDS), r, re.I)
    if m:
        return "dashboards", m.group(1)
    return None, None


def classificar_dashboard(rel, texto_novo):
    """Objeto e camada tocados no repositorio de dashboards.

    A camada sai do caminho. A unica excecao e origem x modelo: os dois moram no
    mesmo arquivo de tabela (a consulta M e uma particao dela), entao so o texto
    da edicao distingue. Sem texto, fica 'modelo', que e o mais conservador.
    """
    partes = rel.split("/")
    objeto = ""
    for i, parte in enumerate(partes):
        if ".SemanticModel" in parte or ".Report" in parte:
            objeto = partes[i - 1] if i else ""
            break
    if not objeto and len(partes) > 1:
        objeto = partes[1] if len(partes) > 2 else partes[0]

    baixo = rel.lower()
    if "/cultures/" in baixo:
        camada = "cultura"
    elif "/visuals/" in baixo:
        camada = "visual"
    elif baixo.endswith("page.json") or baixo.endswith("pages.json"):
        camada = "pagina"
    elif "/bookmarks/" in baixo or baixo.endswith("report.json"):
        camada = "relatorio"
    elif re.search(r"/tables/medidas[^/]*\.tmdl$", baixo):
        camada = "medida"
    elif "/tables/" in baixo or baixo.endswith(("relationships.tmdl", "model.tmdl", "expressions.tmdl")):
        camada = "modelo"
        if texto_novo and re.search(r"\blet\b|Table\.[A-Z]|\beach\b", texto_novo):
            camada = "origem"
    else:
        camada = "projeto"
    return objeto, camada


def etapa_de(rel, nome):
    if nome in ETAPA_POR_ARQUIVO:
        return ETAPA_POR_ARQUIVO[nome]
    if rel.startswith("gerencial/objetos/"):
        return "prontuario"
    if rel.startswith("conhecimento/"):
        return "bau"
    if rel.startswith("diario/"):
        return "diario"
    if rel.startswith("gerencial/"):
        return "gerencial"
    return ""


# campos que declaram o fim do trabalho, por trilho, na ordem em que valem:
# chamado fecha com Entrega, incidente com Encerramento (depois da janela de
# observacao), entrega da frente APP com Data.
CAMPOS_DE_FIM = ("Entrega", "Encerramento", "Data")


def entrega_declarada(caminho):
    """Le do proprio documento a data em que aquele trabalho terminou.

    E o campo que impede confundir 'escrevi o fechamento hoje' com 'entreguei
    hoje': demanda encerrada semanas atras e versionada agora fica marcada.
    Cada trilho nomeia essa data do seu jeito, e o vocabulario de cada um e
    respeitado em vez de forcado a um campo unico.
    """
    try:
        with open(caminho, "r", encoding="utf-8", errors="replace") as fh:
            cabecalho = fh.read(4000)
    except OSError:
        return ""
    for campo in CAMPOS_DE_FIM:
        m = re.search(r"\*\*%s:\*\*\s*(\d{2})[-/](\d{2})[-/](\d{4})" % campo, cabecalho)
        if m:
            return "%s-%s-%s" % m.groups()
    return ""


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    tool = payload.get("tool_name", "")
    raiz = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    cwd = payload.get("cwd") or raiz
    entrada = payload.get("tool_input") or {}
    texto_novo = ""

    por_texto = False
    if tool in ("Write", "Edit", "NotebookEdit", "MultiEdit"):
        alvos = [(entrada.get("file_path", ""), "criou" if tool == "Write" else "editou")]
        texto_novo = entrada.get("content") or entrada.get("new_string") or ""
    elif tool in ("Bash", "PowerShell"):
        # Escrita por shell tambem conta. Sem isso o log perde tudo que passa por
        # cat >>, sed -i, tee, cp, mv e script python embutido. Cada candidato
        # ainda passa pelo teste de mtime la embaixo.
        alvos = [(a, "editou") for a in alvos_de_shell(entrada.get("command", ""))]
        por_texto = True
        texto_novo = entrada.get("command", "")
    else:
        return 0

    agora = datetime.now()
    hoje = agora.strftime("%d-%m-%Y")
    destino = os.path.join(raiz, "diario", ".log", agora.strftime("%Y-%m-%d") + ".jsonl")
    vistos = set()

    for alvo, acao in alvos:
        if not alvo:
            continue
        absoluto = caminho_absoluto(alvo, raiz, cwd)
        repo, rel = localizar(absoluto, raiz)
        if not repo or rel in vistos:
            continue

        # ruido que nao vale log
        if "/.log/" in rel or rel.startswith((".git/", "../")):
            continue
        if not os.path.exists(absoluto):
            continue  # so registra o que de fato existe
        if por_texto and not mexeu_agora(absoluto):
            continue  # o comando citou o caminho, mas nao escreveu nele
        vistos.add(rel)

        nome = os.path.basename(rel).lower()
        linha = {
            "hora": agora.strftime("%H:%M"),
            "acao": acao,
            "repo": repo,
            "arquivo": rel,
            "area": rel.split("/")[0] if "/" in rel else "raiz",
        }

        if repo == "caderno":
            # de que demanda e este arquivo (inferido do caminho, nao do modelo)
            demanda = ""
            for parte in rel.split("/"):
                if parte.startswith("DEM_"):
                    demanda = parte
            if demanda:
                linha["demanda"] = demanda
            etapa = etapa_de(rel, nome)
            if etapa:
                linha["etapa"] = etapa
            if nome in ARQUIVOS_DE_FECHAMENTO:
                entrega = entrega_declarada(absoluto)
                if entrega:
                    linha["entrega_declarada"] = entrega
                    if entrega != hoje:
                        linha["retroativo"] = True
        else:
            objeto, camada = classificar_dashboard(rel, texto_novo)
            if objeto:
                linha["objeto"] = objeto
            linha["camada"] = camada
            linha["etapa"] = "desenvolvimento"

        linha["sessao"] = (payload.get("session_id") or "")[:8]

        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with open(destino, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(linha, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
