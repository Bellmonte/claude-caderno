#!/usr/bin/env python3
"""Hook Stop: nao deixa sair tabela de instrucao pedindo o que ja esta no disco.

O erro que este hook existe para impedir: entregar uma tabela "Passo | Onde |
O que observar" pedindo ao usuario um artefato que ja existe. Exemplo tipico:
pedir de novo a exportacao das imagens de fundo de um dashboard quando os PNGs
ja estao parados na pasta de material da demanda ha dias. Uma memoria que cubra
isso existe e nao segura sozinha, entao a conferencia deixou de depender de
lembrar.

Como ele decide: le a ultima resposta, acha a tabela de instrucao, colhe os
caminhos citados entre crases e confere no disco. Se algum ja existe, devolve a
lista com data e tamanho e pede a conferencia linha a linha. Se nenhum existe,
fica quieto: o pedido e legitimo.

E lembrete, nao carcereiro. Cobra uma vez por conjunto de artefatos.
"""
import glob
import hashlib
import json
import os
import re
import sys
from datetime import datetime

# cabecalho da tabela de instrucao da casa: "| # | Passo | Onde | ... |"
CABECALHO = re.compile(r"^\s*\|.*\bpasso\b.*\|", re.IGNORECASE)
LINHA_TABELA = re.compile(r"^\s*\|")
CRASE = re.compile(r"`([^`\n]{2,120})`")
# parece caminho: tem barra, ou tem extensao de arquivo conhecida
PARECE_CAMINHO = re.compile(r"/|\.(png|jpg|jpeg|json|md|csv|xlsx|pbip|tmdl|py|sql|html|pdf|zip)$", re.IGNORECASE)
LIMITE_ALVOS = 40


def ultima_resposta(caminho):
    """Texto da ultima mensagem do assistente no transcript."""
    try:
        with open(caminho, encoding="utf-8") as fh:
            linhas = fh.readlines()
    except OSError:
        return ""
    for bruta in reversed(linhas[-400:]):
        try:
            ev = json.loads(bruta)
        except Exception:
            continue
        if ev.get("type") != "assistant":
            continue
        conteudo = (ev.get("message") or {}).get("content")
        if isinstance(conteudo, str):
            return conteudo
        if isinstance(conteudo, list):
            partes = [b.get("text", "") for b in conteudo if isinstance(b, dict) and b.get("type") == "text"]
            texto = "\n".join(p for p in partes if p)
            if texto.strip():
                return texto
    return ""


def bloco_da_tabela(texto):
    """As linhas da tabela de instrucao, se houver uma."""
    linhas = texto.splitlines()
    for i, linha in enumerate(linhas):
        if not CABECALHO.match(linha):
            continue
        bloco = []
        for seguinte in linhas[i:]:
            if not LINHA_TABELA.match(seguinte):
                break
            bloco.append(seguinte)
        if len(bloco) >= 3:  # cabecalho, separador e ao menos um passo
            return "\n".join(bloco)
    return ""


def raizes(payload):
    saida = []
    projeto = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    saida.append(projeto)
    # o repositorio de codigo (CADERNO_REPO_TRABALHO), que e a segunda pasta de trabalho
    dash = os.environ.get("CADERNO_REPO_TRABALHO", "")
    if dash and os.path.isdir(dash):
        saida.append(dash)
    return saida


def resolver(alvo, raizes_busca):
    """Caminho existente para o alvo citado, ou vazio."""
    alvo = alvo.strip().strip("/\\")
    if not alvo:
        return ""
    if os.path.isabs(alvo) and os.path.exists(alvo):
        return alvo
    for raiz in raizes_busca:
        direto = os.path.join(raiz, alvo.replace("/", os.sep))
        if os.path.exists(direto):
            return direto
    # citado por sufixo ("F2_prototipo/material/"), sem o caminho inteiro:
    # procura so no caderno, que e pequeno; o repo de codigo fica de fora.
    # Nome solto so vale quando a busca acha UM. Assim "Fundo@1x.png" entra e
    # "page.json", que existe em toda pagina de todo relatorio, fica de fora em
    # vez de casar com um homonimo qualquer e virar ruido na conferencia.
    padrao = os.path.join(raizes_busca[0], "**", alvo.replace("/", os.sep))
    achados = []
    try:
        for achado in glob.iglob(padrao, recursive=True):
            relativo = os.path.relpath(achado, raizes_busca[0]).replace(os.sep, "/")
            if relativo.startswith(("local/", ".git/", "espelho/")):
                continue  # material bruto e espelho nao sao entrega de passo
            achados.append(achado)
            if len(achados) > 1:
                break
    except Exception:
        return ""
    if len(achados) == 1:
        return achados[0]
    return ""


def descrever(caminho, raiz):
    rotulo = os.path.relpath(caminho, raiz).replace(os.sep, "/")
    if os.path.isdir(caminho):
        try:
            itens = [f for f in os.listdir(caminho) if not f.startswith(".")]
        except OSError:
            return "%s (pasta)" % rotulo
        if not itens:
            return ""  # pasta vazia nao prova nada
        novo = max(os.path.getmtime(os.path.join(caminho, f)) for f in itens)
        quando = datetime.fromtimestamp(novo).strftime("%d-%m-%Y %H:%M")
        return "%s tem %d arquivos, o mais novo de %s" % (rotulo, len(itens), quando)
    try:
        quando = datetime.fromtimestamp(os.path.getmtime(caminho)).strftime("%d-%m-%Y %H:%M")
        tam = os.path.getsize(caminho)
    except OSError:
        return rotulo
    return "%s existe, %d bytes, de %s" % (rotulo, tam, quando)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    if payload.get("stop_hook_active"):
        return 0

    transcript = payload.get("transcript_path")
    if not transcript or not os.path.exists(transcript):
        return 0

    tabela = bloco_da_tabela(ultima_resposta(transcript))
    if not tabela:
        return 0

    busca = raizes(payload)
    alvos, vistos = [], set()
    for citado in CRASE.findall(tabela)[:LIMITE_ALVOS]:
        if not PARECE_CAMINHO.search(citado) or citado in vistos:
            continue
        vistos.add(citado)
        achado = resolver(citado, busca)
        if not achado:
            continue
        raiz = next((r for r in busca if achado.startswith(r)), busca[0])
        linha = descrever(achado, raiz)
        if linha:
            alvos.append(linha)

    if not alvos:
        return 0

    projeto = busca[0]
    sessao = (payload.get("session_id") or "")[:8]
    assinatura = hashlib.md5("|".join(sorted(alvos)).encode("utf-8")).hexdigest()[:10]
    pasta_flag = os.path.join(projeto, "diario", ".log")
    flag = os.path.join(pasta_flag, ".instrucao-%s-%s" % (sessao, assinatura))
    if os.path.exists(flag):
        return 0
    try:
        os.makedirs(pasta_flag, exist_ok=True)
        with open(flag, "w", encoding="utf-8") as fh:
            fh.write("cobrado")
    except OSError:
        pass

    sys.stderr.write(
        "CONFERENCIA ANTES DA INSTRUCAO. A resposta tem uma tabela de passos para o "
        "usuario, e estes artefatos citados nela JA EXISTEM no disco:\n\n  - %s\n\n"
        "Releia a tabela linha a linha. Passo que produz artefato que ja esta ai sai da "
        "tabela, e o que voce diz no lugar e que ele ja existe, com a data. Repetir "
        "pedido atendido atrapalha.\n\nSe o passo continua valendo "
        "mesmo com o artefato no lugar, por exemplo porque a fonte mudou depois, "
        "mantenha, e diga na propria linha por que o que esta la nao serve mais.\n"
        % "\n  - ".join(alvos)
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
