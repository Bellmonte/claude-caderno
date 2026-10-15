# Diário

Uma entrada por dia de trabalho relevante: `AAAA-MM-DD.md`. Registre o que fez, as decisões e os
aprendizados. É matéria-prima do baú, da daily, da semanal e dos 1:1s.

O título do dia vem no primeiro `## ` do arquivo, e é ele que o painel mostra em "Últimos dias
narrados". Se o arquivo já existe, anexe a seção nova sem reescrever o que estava lá.

A pasta `diario/.log/` é o log bruto automático, uma linha por escrita de arquivo, gravado pelo
hook `log_acao.py`. Ela fica fora do git: é rastro de máquina, e o que atravessa máquinas é a
narrativa destilada aqui. O hook `cobrar_diario.py` segura o fim da sessão quando houve trabalho
logado e o dia não foi narrado.
