#!/usr/bin/env python3
"""Hook Stop: nao deixa a sessao terminar com trabalho feito e nada registrado.

Compara o log bruto do dia com o diario do dia. Se houve trabalho de verdade e
a narrativa nao foi escrita, devolve a instrucao para o Claude escrever antes de
encerrar. Cobra UMA vez por sessao: lembrete, nao carcereiro.
"""
import json
import os
import sys
from datetime import datetime

def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    # ja estamos num ciclo disparado por este hook: nao insiste
    if payload.get("stop_hook_active"):
        return 0

    raiz = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    hoje = datetime.now().strftime("%Y-%m-%d")
    log = os.path.join(raiz, "diario", ".log", hoje + ".jsonl")
    if not os.path.exists(log):
        return 0

    sessao = (payload.get("session_id") or "")[:8]
    flag = os.path.join(raiz, "diario", ".log", ".cobrado-%s-%s" % (hoje, sessao))
    if os.path.exists(flag):
        return 0

    # Verdade sobre "o diario foi escrito": o mtime do arquivo, nao o log.
    # O log so enxerga as ferramentas de edicao; escrita por shell (cat >>, sed -i,
    # tee) passa por fora dele. O mtime nao depende de por onde a escrita veio.
    diario_escrito = False
    caminho_diario = os.path.join(raiz, "diario", hoje + ".md")
    if os.path.exists(caminho_diario):
        inicio_do_dia = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        try:
            if os.path.getmtime(caminho_diario) >= inicio_do_dia.timestamp():
                diario_escrito = True
        except OSError:
            pass

    acoes, demandas = 0, set()
    try:
        with open(log, encoding="utf-8") as fh:
            for bruta in fh:
                try:
                    ev = json.loads(bruta)
                except Exception:
                    continue
                if ev.get("sessao") and sessao and ev["sessao"] != sessao:
                    continue
                arq = ev.get("arquivo", "")
                if arq == "diario/%s.md" % hoje:
                    diario_escrito = True
                    continue
                if ev.get("area") in ("demandas", "conhecimento", "gerencial", ".claude"):
                    acoes += 1
                    if ev.get("demanda"):
                        demandas.add(ev["demanda"])
    except Exception:
        return 0

    # pouco trabalho ou narrativa ja escrita: nada a cobrar
    if diario_escrito or acoes < 3:
        return 0

    try:
        with open(flag, "w", encoding="utf-8") as fh:
            fh.write("cobrado")
    except Exception:
        pass

    alvos = ", ".join(sorted(demandas)) if demandas else "sem demanda vinculada"
    sys.stderr.write(
        "REGISTRO PENDENTE. Esta sessao gravou %d alteracoes (%s) e diario/%s.md nao "
        "foi escrito.\n\nAntes de encerrar, leia diario/.log/%s.jsonl e acrescente a "
        "narrativa do dia em diario/%s.md: o que foi feito, a decisao que foi tomada e "
        "o que ficou aberto. Se o arquivo ja existe, ANEXE a secao nova sem reescrever o "
        "que ja estava la. Siga a regua de escrita do CLAUDE.md.\n\nSe o trabalho desta "
        "sessao nao merece registro (ajuste trivial, exploracao sem resultado), diga isso "
        "em uma linha e encerre.\n" % (acoes, alvos, hoje, hoje, hoje)
    )
    return 2

if __name__ == "__main__":
    sys.exit(main())
