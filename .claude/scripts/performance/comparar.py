#!/usr/bin/env python3
"""Compara a linha de base com a remedicao de uma auditoria de performance.

Le as pastas de saida dos scripts de medicao (antes e depois) e monta a tabela de
medicao do relatorio: grandeza, mediana e faixa de cada lado, variacao e se a diferenca
e mensuravel. Mensuravel so quando as faixas (minimo a maximo) nao se sobrepoem.

Recusa comparar medicoes feitas em versoes diferentes do Desktop, porque o Desktop muda
todo mes e misturar versao com correcao invalida a comparacao. --aceitar-versao-diferente
passa por cima, e a tabela sai com o aviso escrito.

Uso:
    python comparar.py --antes local/performance/<painel>/antes --depois local/performance/<painel>/depois [--md saida.md]

O resultado so tem agregados e nomes de visual, e pode ir para o relatorio.
"""
import argparse
import csv
import json
import os
import statistics
import sys
from collections import defaultdict


def ler_csv(pasta, nome):
    caminho = os.path.join(pasta, nome)
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def ler_meta(pasta, nome):
    caminho = os.path.join(pasta, nome)
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding="utf-8-sig") as f:
        return json.load(f)


def num(s):
    return float(str(s).replace(",", ".")) if s not in (None, "") else None


def serie(valores):
    v = [x for x in valores if x is not None]
    if not v:
        return None
    return {"med": statistics.median(v), "min": min(v), "max": max(v), "n": len(v)}


def pct(x):
    return f"{x:+.1%}".replace(".", ",")


def comparar(a, d):
    if not a or not d:
        return "", "sem par"
    var = (d["med"] - a["med"]) / a["med"] if a["med"] else 0
    sobrepoe = not (d["max"] < a["min"] or d["min"] > a["max"])
    if sobrepoe:
        return pct(var), "sem diferença mensurável"
    return pct(var), "melhora mensurável" if var < 0 else "piora mensurável"


def fmt(s, casas=1):
    if not s:
        return "N/A", "N/A"
    return (f"{s['med']:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", "."),
            f"{s['min']:,.{casas}f} a {s['max']:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", "."))


def blocos(execucoes, cache):
    """Soma por rodada das consultas de cada bloco: o tempo de motor da pagina."""
    if not execucoes:
        return {}
    soma = defaultdict(lambda: defaultdict(float))
    for e in execucoes:
        if e["cache"] == cache:
            soma[e.get("bloco", "")][e["rodada"]] += num(e["ms"])
    return {b: serie(list(r.values())) for b, r in soma.items()}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--antes", required=True)
    p.add_argument("--depois", required=True)
    p.add_argument("--md")
    p.add_argument("--aceitar-versao-diferente", action="store_true")
    a = p.parse_args()

    avisos = []
    versoes = {}
    for lado, pasta in (("antes", a.antes), ("depois", a.depois)):
        for nome in ("tamanho_meta.json", "atualizacao_meta.json", "consultas_meta.json"):
            m = ler_meta(pasta, nome)
            if m:
                versoes.setdefault(lado, set()).add(m.get("versao_desktop"))
                if nome == "consultas_meta.json" and not m.get("frio_valido", True):
                    avisos.append(f"A medição a frio de {lado} não passou na conferência do cache.")
    todas = set().union(*versoes.values()) if versoes else set()
    if len(todas) > 1:
        msg = "Versões do Desktop diferentes entre as medições: " + ", ".join(sorted(map(str, todas)))
        if not a.aceitar_versao_diferente:
            sys.exit(msg + ". Comparação recusada.")
        avisos.append(msg + ". Comparação feita por decisão explícita, e a variação pode ser da versão.")

    linhas = []

    ta, td = ler_meta(a.antes, "tamanho_meta.json"), ler_meta(a.depois, "tamanho_meta.json")
    if ta or td:
        va = ta and ta["total_bytes"] / 2**20
        vd = td and td["total_bytes"] / 2**20
        var = pct((vd - va) / va) if va and vd else ""
        fa = f"{va:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if va else "N/A"
        fd = f"{vd:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if vd else "N/A"
        linhas.append(("Tamanho do modelo", "MB", fa, "leitura única", fd, "leitura única", var,
                       "leitura determinística" if var else "sem par"))

    def atual(pasta):
        r = ler_csv(pasta, "atualizacao.csv")
        return r and serie([num(x["segundos"]) for x in r if x["aquecimento"] in ("0", "False")])
    sa, sd = atual(a.antes), atual(a.depois)
    if sa or sd:
        linhas.append(("Atualização completa", "s", *fmt(sa, 2), *fmt(sd, 2), *comparar(sa, sd)))

    ea, ed = ler_csv(a.antes, "consultas_execucoes.csv"), ler_csv(a.depois, "consultas_execucoes.csv")
    ra, rd = ler_csv(a.antes, "consultas_resumo.csv") or [], ler_csv(a.depois, "consultas_resumo.csv") or []
    bloco_de = {r["consulta"]: r["bloco"] for r in ra + rd}
    titulo_de = {r["consulta"]: r["visual_titulo"] or r["visual_tipo"] or r["visual_id"] for r in ra + rd}
    for lista in (ea or [], ed or []):
        for e in lista:
            e["bloco"] = bloco_de.get(e["consulta"], "")
    for cache in ("frio", "quente"):
        ba, bd = blocos(ea, cache), blocos(ed, cache)
        for b in sorted(set(ba) | set(bd), key=lambda x: int(x or 0)):
            linhas.append((f"Motor do bloco {b}, a {cache}", "ms", *fmt(ba.get(b)), *fmt(bd.get(b)),
                           *comparar(ba.get(b), bd.get(b))))

    def por_consulta(execs, cache):
        g = defaultdict(list)
        for e in execs or []:
            if e["cache"] == cache:
                g[e["consulta"]].append(num(e["ms"]))
        return {k: serie(v) for k, v in g.items()}
    ca, cd = por_consulta(ea, "frio"), por_consulta(ed, "frio")
    ordem = sorted(set(ca) | set(cd), key=lambda k: -(ca.get(k) or {"med": 0})["med"])
    for k in ordem[:10]:
        linhas.append((f"{k} {titulo_de.get(k, '')}, a frio", "ms", *fmt(ca.get(k)), *fmt(cd.get(k)),
                       *comparar(ca.get(k), cd.get(k))))

    cab = ("Grandeza", "Unidade", "Antes (mediana)", "Antes (faixa)", "Depois (mediana)",
           "Depois (faixa)", "Variação", "Diferença")
    out = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    out += ["| " + " | ".join(map(str, l)) + " |" for l in linhas]
    if avisos:
        out += [""] + [f"> {x}" for x in avisos]
    texto = "\n".join(out)
    print(texto)
    if a.md:
        with open(a.md, "w", encoding="utf-8") as f:
            f.write(texto + "\n")


if __name__ == "__main__":
    main()
