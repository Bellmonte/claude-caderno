#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Transporte da pasta `local/` entre maquinas, com conferencia de integridade.

A `local/` guarda material BRUTO recebido (planilha do solicitante, extracao, print, PDF) e
fica fora do git de proposito. Quando o trabalho troca de maquina, ela precisa ir junto, e
precisa chegar inteira: arquivo que falta em silencio vira analise feita sobre base incompleta.

Esta ferramenta existe porque o Claude NAO pode conferir isso por conta propria. A regra
`Read(local/**)` do `.claude/settings.json` nega o acesso dele aquela pasta, inclusive por
Bash, e a regra nao se afrouxa para uma conveniencia. Entao quem roda e o usuario, e o que
atravessa e o VEREDITO, nunca o conteudo.

O manifesto guarda caminho, tamanho e sha256. Nenhuma linha dele carrega conteudo de arquivo.

## Uso

    # na maquina de origem
    python .claude/scripts/pacote_local.py empacotar

    # na maquina de destino, com o local.zip baixado na raiz do caderno
    python .claude/scripts/pacote_local.py conferir
    python .claude/scripts/pacote_local.py extrair     # traz so o que falta ou difere
    python .claude/scripts/pacote_local.py conferir    # e confere de novo

O `local.zip` fica na raiz do caderno e ja esta no `.gitignore`. Ele e dado bruto em transporte:
nao vai para o git, nao vai para anexo de e-mail e nao sobrevive ao fim da troca de maquina.
Apague depois de o `conferir` dar tudo igual.
"""

import hashlib
import os
import sys
import zipfile

MANIFESTO = "_MANIFESTO.txt"
PASTA = "local"
ZIP = "local.zip"
IGNORAR = {".DS_Store", "Thumbs.db", "desktop.ini"}


def raiz_caderno():
    """A raiz do caderno a partir da localizacao do script (.claude/scripts/ -> raiz)."""
    aqui = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(aqui, "..", ".."))


def sha256(caminho, bloco=1024 * 1024):
    h = hashlib.sha256()
    with open(caminho, "rb") as fh:
        for pedaco in iter(lambda: fh.read(bloco), b""):
            h.update(pedaco)
    return h.hexdigest()


def varre(base):
    """Todo arquivo sob `base`, como {caminho relativo: (sha256, tamanho)}.

    O proprio manifesto fica de fora: ele muda a cada geracao e se incluir a si mesmo nunca
    fecha. Caminho sai sempre com barra normal, para o manifesto ser igual no Windows e fora."""
    achados = {}
    for pasta, _, arquivos in os.walk(base):
        for nome in sorted(arquivos):
            if nome in IGNORAR or nome == MANIFESTO:
                continue
            inteiro = os.path.join(pasta, nome)
            rel = os.path.relpath(inteiro, base).replace(os.sep, "/")
            try:
                achados[rel] = (sha256(inteiro), os.path.getsize(inteiro))
            except (OSError, PermissionError) as erro:
                print("  nao consegui ler {}: {}".format(rel, erro))
    return achados


def escreve_manifesto(achados, destino):
    with open(destino, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# manifesto da pasta local/ | caminho, tamanho e sha256\n")
        fh.write("# gerado por .claude/scripts/pacote_local.py, nao editar a mao\n")
        for rel in sorted(achados):
            digest, tamanho = achados[rel]
            fh.write("{}\t{}\t{}\n".format(digest, tamanho, rel))


def le_manifesto(linhas):
    achados = {}
    for linha in linhas:
        linha = linha.rstrip("\n")
        if not linha or linha.startswith("#"):
            continue
        partes = linha.split("\t")
        if len(partes) != 3:
            continue
        digest, tamanho, rel = partes
        achados[rel] = (digest, int(tamanho))
    return achados


def humano(n):
    for unidade in ("B", "KB", "MB", "GB"):
        if n < 1024 or unidade == "GB":
            return "{:.0f} {}".format(n, unidade) if unidade == "B" else "{:.1f} {}".format(n, unidade)
        n /= 1024.0


def empacotar(raiz):
    base = os.path.join(raiz, PASTA)
    if not os.path.isdir(base):
        print("a pasta {}/ nao existe nesta maquina. Nada a empacotar.".format(PASTA))
        return 1

    print("lendo {}/ ...".format(PASTA))
    achados = varre(base)
    if not achados:
        print("a pasta {}/ esta vazia. Nada a empacotar.".format(PASTA))
        return 1

    caminho_manifesto = os.path.join(base, MANIFESTO)
    escreve_manifesto(achados, caminho_manifesto)

    total = sum(t for _, t in achados.values())
    print("{} arquivos, {}".format(len(achados), humano(total)))

    destino = os.path.join(raiz, ZIP)
    print("compactando em {} ...".format(ZIP))
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(caminho_manifesto, MANIFESTO)
        for i, rel in enumerate(sorted(achados), 1):
            z.write(os.path.join(base, rel), rel)
            if i % 50 == 0:
                print("  {} de {}".format(i, len(achados)))

    print("\npronto: {} ({})".format(destino, humano(os.path.getsize(destino))))
    print("Leve o arquivo para a outra maquina, ponha na raiz do caderno e rode la:")
    print("  python .claude/scripts/pacote_local.py conferir")
    return 0


def compara(origem, aqui):
    """Tres listas: o que falta, o que so existe aqui, e o que existe nos dois e difere."""
    faltando = sorted(k for k in origem if k not in aqui)
    sobrando = sorted(k for k in aqui if k not in origem)
    diferente = sorted(k for k in origem if k in aqui and origem[k][0] != aqui[k][0])
    return faltando, sobrando, diferente


def carrega_zip(caminho_zip):
    """O manifesto de dentro do zip, e a lista real de arquivos que o zip carrega.

    Os dois nem sempre batem: download interrompido produz zip que abre e vem incompleto."""
    with zipfile.ZipFile(caminho_zip) as z:
        nomes = [n for n in z.namelist() if not n.endswith("/")]
        if MANIFESTO not in nomes:
            return None, None
        with z.open(MANIFESTO) as fh:
            manifesto = le_manifesto(fh.read().decode("utf-8").splitlines())
        return manifesto, set(n for n in nomes if n != MANIFESTO)


def conferir(raiz):
    caminho_zip = os.path.join(raiz, ZIP)
    if not os.path.isfile(caminho_zip):
        print("nao achei o {} na raiz do caderno ({}).".format(ZIP, raiz))
        print("Baixe o pacote da outra maquina e ponha ele ali.")
        return 1

    try:
        manifesto, no_zip = carrega_zip(caminho_zip)
    except zipfile.BadZipFile:
        print("o {} esta corrompido e nem abre. O download foi interrompido, baixe de novo."
              .format(ZIP))
        return 1

    if manifesto is None:
        print("o {} nao tem {} dentro. Ele nao foi gerado por esta ferramenta, e sem manifesto"
              .format(ZIP, MANIFESTO))
        print("nao da para afirmar que chegou inteiro. Gere de novo na origem com 'empacotar'.")
        return 1

    # 1. O zip esta inteiro?
    faltam_no_zip = sorted(k for k in manifesto if k not in no_zip)
    if faltam_no_zip:
        print("O PROPRIO ZIP ESTA INCOMPLETO: {} de {} arquivos do manifesto nao estao dentro dele."
              .format(len(faltam_no_zip), len(manifesto)))
        for rel in faltam_no_zip[:20]:
            print("  {}".format(rel))
        if len(faltam_no_zip) > 20:
            print("  ... e mais {}".format(len(faltam_no_zip) - 20))
        print("\nO download foi interrompido. Baixe de novo antes de qualquer outra coisa.")
        return 1

    print("o zip esta inteiro: {} arquivos, batendo com o manifesto".format(len(manifesto)))

    # 2. E a pasta local/ desta maquina, como esta?
    base = os.path.join(raiz, PASTA)
    if not os.path.isdir(base):
        print("\na pasta {}/ nao existe aqui ainda. Tudo do pacote esta faltando.".format(PASTA))
        aqui = {}
    else:
        print("lendo {}/ desta maquina ...".format(PASTA))
        aqui = varre(base)

    faltando, sobrando, diferente = compara(manifesto, aqui)
    iguais = len(manifesto) - len(faltando) - len(diferente)

    print("\n" + "=" * 70)
    print("{:<28} {}".format("iguais nas duas maquinas", iguais))
    print("{:<28} {}".format("faltando aqui", len(faltando)))
    print("{:<28} {}".format("diferentes", len(diferente)))
    print("{:<28} {}".format("so existem aqui", len(sobrando)))
    print("=" * 70)

    def lista(titulo, itens, nota=""):
        if not itens:
            return
        print("\n{} ({}){}".format(titulo, len(itens), nota))
        for rel in itens[:40]:
            print("  {}".format(rel))
        if len(itens) > 40:
            print("  ... e mais {}".format(len(itens) - 40))

    lista("FALTANDO nesta maquina", faltando)
    lista("DIFERENTES", diferente,
          "\n  mesmo caminho, conteudo diferente. O 'extrair' sobrescreve com a versao da origem.")
    lista("SO EXISTEM AQUI", sobrando,
          "\n  o 'extrair' nao mexe nestes. Podem ser trabalho feito nesta maquina.")

    if not faltando and not diferente:
        print("\nO pacote chegou inteiro e a pasta local/ desta maquina esta em dia.")
        print("Pode apagar o {}.".format(ZIP))
        return 0

    print("\nPara trazer o que falta e o que difere:")
    print("  python .claude/scripts/pacote_local.py extrair")
    return 2


def extrair(raiz):
    caminho_zip = os.path.join(raiz, ZIP)
    if not os.path.isfile(caminho_zip):
        print("nao achei o {} na raiz do caderno.".format(ZIP))
        return 1

    manifesto, no_zip = carrega_zip(caminho_zip)
    if manifesto is None:
        print("o {} nao tem manifesto. Gere de novo na origem com 'empacotar'.".format(ZIP))
        return 1

    base = os.path.join(raiz, PASTA)
    aqui = varre(base) if os.path.isdir(base) else {}
    faltando, _, diferente = compara(manifesto, aqui)
    trazer = sorted(set(faltando) | set(diferente))

    if not trazer:
        print("nada a trazer: a pasta local/ desta maquina ja bate com o pacote.")
        return 0

    print("trazendo {} arquivos ({} faltando, {} diferentes) ...".format(
        len(trazer), len(faltando), len(diferente)))
    os.makedirs(base, exist_ok=True)
    with zipfile.ZipFile(caminho_zip) as z:
        for rel in trazer:
            z.extract(rel, base)
            print("  {}".format(rel))

    print("\nPronto. Rode o conferir de novo para fechar:")
    print("  python .claude/scripts/pacote_local.py conferir")
    return 0


def main():
    modos = {"empacotar": empacotar, "conferir": conferir, "extrair": extrair}
    modo = sys.argv[1] if len(sys.argv) > 1 else ""
    if modo not in modos:
        print("Transporte da pasta local/ entre maquinas, com conferencia de integridade.\n")
        print("Uso: pacote_local.py [empacotar|conferir|extrair]\n")
        print("  empacotar  na maquina de ORIGEM: gera o manifesto e o local.zip na raiz")
        print("  conferir   na de DESTINO: diz se o zip chegou inteiro e o que falta em local/")
        print("  extrair    na de DESTINO: traz so o que falta ou difere, sem tocar no resto")
        print("\nO local.zip e dado bruto em transporte: fica no disco, fora do git, e se apaga")
        print("depois que o conferir der tudo igual.")
        return 2
    return modos[modo](raiz_caderno())


if __name__ == "__main__":
    sys.exit(main())
