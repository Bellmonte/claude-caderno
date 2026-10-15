# Teste de regressao do lint_formatacao: um objeto bom (tem que passar limpo) e dois ruins
# com violacoes plantadas (DAX e M). Cada violacao esperada esta listada por linha e regra.
# Uso: python .claude/scripts/testes_lint/conferir.py
import json, subprocess, sys, os
S = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(S, "Teste.SemanticModel", "definition", "tables")
ESPERADO = {
 "Fact_Vendas.tmdl": set(), "Dim_Cliente.tmdl": set(),
 "Ruim_Dax.tmdl": {(4,"DAX-06"),(5,"DAX-06"),(6,"DAX-01"),(6,"DAX-02"),(6,"DAX-07"),(6,"DAX-09"),
   (7,"DAX-04"),(8,"DAX-03"),(8,"DAX-07"),(10,"DAX-02"),(14,"DAX-02"),(16,"DAX-03"),(16,"DAX-05"),
   (17,"DAX-03"),(17,"DAX-05"),(19,"DAX-12"),(20,"DAX-10"),(21,"DAX-08"),(24,"DAX-13"),(26,"DAX-08"),(26,"DAX-13")},
 "Ruim_M.tmdl": {(7,"M-01"),(7,"M-05"),(7,"M-07"),(8,"M-02"),(9,"M-03"),(9,"M-06"),(11,"M-02"),(11,"M-04"),
   (11,"M-08"),(13,"M-03"),(15,"M-01"),(15,"M-08"),(16,"M-01")},
}
ok = True
for arq, esp in ESPERADO.items():
    r = subprocess.run([sys.executable, os.path.join(S, "..", "lint_formatacao.py"),
                        os.path.join(D, arq), "--json"], capture_output=True, text=True, encoding="utf-8")
    obtido = {(v["linha"], v["regra"]) for v in json.loads(r.stdout)["violacoes"]}
    falta, sobra = esp - obtido, obtido - esp
    print("%-18s esperado %2d  obtido %2d  %s" % (arq, len(esp), len(obtido), "OK" if not falta and not sobra else "DIVERGE"))
    if falta: print("   faltou:", sorted(falta)); ok = False
    if sobra: print("   sobrou:", sorted(sobra)); ok = False
sys.exit(0 if ok else 1)
