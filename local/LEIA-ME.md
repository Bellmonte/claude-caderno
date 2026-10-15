# local/: área fora do git

Tudo aqui é IGNORADO pelo git, menos este LEIA-ME. É onde mora o material bruto recebido e não
sensível:

- extrações (CSV/XLSX/parquet)
- planilha do solicitante, print, PDF do chamado
- arquivo de transporte

Regra mental: "é dado bruto? vai para `local/`". O registro da demanda referencia o caminho
(`local/<demanda>/`), nunca o conteúdo.

O Claude não lê esta pasta: a regra `Read(local/**)` do `.claude/settings.json` garante isso.
Para levar a pasta entre máquinas e conferir que chegou inteira, use
`python .claude/scripts/pacote_local.py` (empacotar, conferir, extrair). Cópia de leitura de
ambiente é outra coisa e mora em `espelho/`.

Dado sensível de verdade (credencial, dado pessoal protegido por lei) não entra nem aqui.
Credencial vai em `.env` na raiz, também fora do git.
