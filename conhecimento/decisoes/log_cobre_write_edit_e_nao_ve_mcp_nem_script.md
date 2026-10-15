# Decisão: o log automático cobre Write/Edit e não enxerga MCP nem script

**Contexto:** num dia de trabalho pesado em um dashboard, quase tudo foi feito por dois canais que o
`log_acao.py` não vê: as mudanças de modelo entraram por um servidor MCP do Power BI, direto na
sessão do Desktop, e as de layout entraram por script Python rodado no Bash. No fim do dia o log
tinha **uma** escrita da demanda, a do registro no caderno, enquanto o repositório de dashboards
acumulava dez arquivos modificados.

O hook é `PostToolUse` das ferramentas de escrita de arquivo. Ele registra o que passa por
`Write` e `Edit`. Escrita feita por outro caminho acontece fora do gancho e não deixa rastro,
mesmo tocando os mesmos arquivos.

**Decisão:** o log continua como está, e a leitura dele é que muda. Ele responde "o que foi tocado
pelas ferramentas de escrita", e não "todo o trabalho do dia". Ampliar a cobertura exigiria vigiar
o diretório em vez de interceptar a ferramenta, o que é outro instrumento e traria ruído de build,
cache e refresh do próprio Desktop.

**Consequência prática:** a daily e a semanal derivadas do log **subestimam** o dia em que o
trabalho foi de modelo semântico ou de edição em lote. Nesses dias o diário narrado deixa de ser
redundante e passa a ser a fonte principal. Quando o log vier magro num dia de trabalho pesado,
suspeite do canal antes de suspeitar do dia, e confira o `git status` dos dois repositórios, que
enxerga a escrita independentemente de quem a fez.

Vale para a régua já escrita no CLAUDE.md: o log diz o que foi tocado, o campo `Entrega` do
fechamento é que diz o que foi entregue. Agora somam-se duas ressalvas em vez de uma, e a
segunda é sobre o que o log **não** vê.

Antes de cada mudança vale decidir por qual canal ela entra (MCP, edição de arquivo ou script),
porque disso depende quanto dela o log vai registrar. Relacionado:
[[log_automatico_nao_ve_escrita_por_script]].
