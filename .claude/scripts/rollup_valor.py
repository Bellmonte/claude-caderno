#!/usr/bin/env python3
"""Gera os numeros da camada de valor a partir da fonte distribuida.

A fonte da verdade sao os blocos de valor dentro das demandas: valor.md no trilho
longo e o bloco "Valor (interno)" do fechamento.md no trilho curto. O consolidado
e DERIVADO daqui e nunca mantido a mao em paralelo, que foi exatamente como o
antigo razao-valor.csv se perdeu.

Uso:
    python .claude/scripts/rollup_valor.py         # imprime
    python .claude/scripts/rollup_valor.py --md    # grava gerencial/valor/rollup.md
"""
import collections
import os
import re
import sys
import unicodedata

DIMENSOES = ("risco-dependencia", "confiabilidade", "capacidade", "decisao",
             "adocao", "tempo", "custo")
CONFIANCAS = ("alta", "media", "baixa")
ORIGENS = ("estrategica", "rotina", "urgencia", "volume")

PADROES = {
    "dimensao": r"\*\*Dimens[a-zA-Zà-ü]*[^:]*:\*\*\s*([^\n]+)",
    "origem_prioridade": r"\*\*Origem da prioridade:\*\*\s*([^\n]+)",
    "confianca": r"\*\*Confian[a-zA-Zà-ü]*:\*\*\s*([^|\n]+)",
    "esforco_dias": r"\*\*Esfor[a-zA-Zà-ü]*[^:]*:\*\*\s*(\d+)",
}


def achatar(texto):
    """Minuscula sem acento, para casar termo mesmo com encoding sujo."""
    limpo = unicodedata.normalize("NFKD", texto)
    limpo = "".join(c for c in limpo if not unicodedata.combining(c))
    return limpo.lower()


def normalizar(bruto, vocabulario):
    """Reduz texto livre ao primeiro termo do vocabulario que aparecer nele."""
    plano = achatar(bruto)
    melhor, posicao = None, len(plano) + 1
    for termo in vocabulario:
        onde = plano.find(termo)
        if 0 <= onde < posicao:
            melhor, posicao = termo, onde
    return melhor or "nao classificado"


def extrair(texto):
    reg = {}
    for chave, padrao in PADROES.items():
        achado = re.search(padrao, texto, re.IGNORECASE)
        if achado:
            reg[chave] = achado.group(1).strip().strip("{}<>")
    for chave, vocab in (("dimensao", DIMENSOES), ("confianca", CONFIANCAS),
                         ("origem_prioridade", ORIGENS)):
        if reg.get(chave):
            reg[chave] = normalizar(reg[chave], vocab)
    return reg


def ler_demandas(raiz):
    """Devolve (registros com valor, demandas fechadas sem valor)."""
    registros, sem_valor = [], []
    base = os.path.join(raiz, "demandas")
    for atual, pastas, arquivos in os.walk(base):
        nome = os.path.basename(atual)
        if not nome.startswith("DEM_"):
            continue
        if any(p.startswith("DEM_") for p in pastas):
            continue  # epico: quem conta sao as filhas

        achou = False
        for arq in ("valor.md", "fechamento.md", "documentacao.md"):
            caminho = os.path.join(atual, arq)
            if not os.path.exists(caminho):
                continue
            try:
                with open(caminho, encoding="utf-8", errors="replace") as fh:
                    texto = fh.read()
            except OSError:
                continue
            if arq != "valor.md" and "Valor (interno)" not in texto:
                continue
            reg = extrair(texto)
            if reg.get("dimensao"):
                reg["demanda"] = nome
                reg["fonte"] = arq
                registros.append(reg)
                achou = True
                break
        if not achou and ("fechamento.md" in arquivos or "documentacao.md" in arquivos):
            sem_valor.append(nome)
    return registros, sem_valor


def main():
    raiz = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    registros, sem_valor = ler_demandas(raiz)

    contagens = {c: collections.Counter() for c in ("dimensao", "origem_prioridade", "confianca")}
    esforco = 0
    for reg in registros:
        for campo in contagens:
            contagens[campo][reg.get(campo) or "nao classificado"] += 1
        try:
            esforco += int(reg.get("esforco_dias", 0))
        except (TypeError, ValueError):
            pass

    total = len(registros) + len(sem_valor)
    linhas = [
        "# Rollup da camada de valor (derivado)",
        "",
        "Gerado por `.claude/scripts/rollup_valor.py` a partir dos blocos de valor dentro das",
        "demandas. **Nao editar a mao.** Para atualizar, rode o script de novo.",
        "",
        "- Demandas fechadas: **%d**" % total,
        "- Com valor registrado: **%d** (%.0f%%)" % (
            len(registros), 100.0 * len(registros) / total if total else 0),
        "- Lacunas, fechadas sem valor: **%d**" % len(sem_valor),
    ]
    if esforco:
        linhas.append("- Esforco declarado somado: **%d dias**" % esforco)

    rotulos = {"dimensao": "dimensao primaria", "origem_prioridade": "origem da prioridade",
               "confianca": "confianca"}
    for campo in ("dimensao", "origem_prioridade", "confianca"):
        if not contagens[campo]:
            continue
        linhas += ["", "## Por %s" % rotulos[campo], "", "| Valor | Entregas |", "|---|---|"]
        for chave, qtd in contagens[campo].most_common():
            linhas.append("| %s | %d |" % (chave, qtd))

    if sem_valor:
        linhas += ["", "## Lacunas", "",
                   "Demanda fechada sem bloco de valor. Lacuna existe para ficar visivel, nunca",
                   "para ser preenchida com registro inventado.", ""]
        linhas.append(", ".join("`%s`" % d for d in sorted(sem_valor)))

    texto = "\n".join(linhas) + "\n"
    if "--md" in sys.argv:
        destino = os.path.join(raiz, "gerencial", "valor", "rollup.md")
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with open(destino, "w", encoding="utf-8") as fh:
            fh.write(texto)
        print("gravado em gerencial/valor/rollup.md")
    else:
        sys.stdout.write(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
