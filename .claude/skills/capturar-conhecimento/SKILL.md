---
name: capturar-conhecimento
description: Ao fechar uma demanda, destila o aprendizado reaproveitável para o baú e atualiza o caderno e (quando houver decisão nova) a matriz de roteamento. Use no fim da esteira. Transversal.
---

> DESTINO: todo arquivo de registro (demandas/, diario/, conhecimento/, gerencial/) é criado na RAIZ DO CADERNO (o repositório do caderno adicionado à sessão), NUNCA no repo de trabalho. Se o caderno não estiver na sessão, pare e peça para adicioná-lo. Ver CLAUDE.md > "Onde cada coisa mora".

# Skill: capturar-conhecimento (fechamento — atualiza o caderno)

## Papel
Destilar o que é atemporal e reaproveitável e guardar no lugar certo, mantendo o índice atualizado. É a etapa que faz o sistema "se auto-incrementar".

## O que capturar (e o que NÃO)
- CAPTURE: procedimentos que se repetem (runbook), decisões e seus porquês, termos novos (glossário), referências úteis, conceito ou caminho de interface que você teve que descobrir e vai precisar de novo (tutorial).
- NÃO capture: o registro cronológico inteiro (fica no diário/demanda); detalhes que valem só para um caso.

## Fluxo
1. Identifique o que é reaproveitável na demanda fechada.
2. Escreva no lugar certo:
   - `conhecimento/runbooks/<nome>.md` — procedimentos.
   - `conhecimento/decisoes/<nome>.md` — decisões (contexto, decisão, consequência).
   - `contexto/glossario.md` — termos.
   - `conhecimento/referencias/<nome>.md` — links/recortes.
   - `conhecimento/runbooks/<nome>.md` — material didatico: explica um conceito ou ensina o caminho pela interface, para alguem aprender do zero. Diferente do runbook, que e passo a passo de execucao para quem ja sabe o contexto.
3. Atualize `conhecimento/INDICE.md` (crie se ainda não existir).
4. **Matriz de roteamento** (`conhecimento/referencias/ROTEAMENTO_FRENTES.md`): SE a demanda trouxe uma decisão de roteamento NOVA (um caso de uso → qual skill agiu/cedeu que ainda não estava mapeado), incremente a matriz. Se foi caso recorrente, sem novidade, NÃO escreva nada. Crie o arquivo se ainda não existir e houver o primeiro caso a registrar.
5. Atualize o `diario/AAAA-MM-DD.md` marcando a demanda como fechada.
6. **Camada de valor:** acione a skill `capturar-valor` (irmã desta no fechamento) para completar o `valor.md` interno e auto-incrementar o portfolio. Uma cuida do aprendizado (aqui), a outra do impacto. Ela roda autônoma, com interação mínima.
7. Mostre o que foi adicionado e PARE para confirmação.

## Regra
Brevidade é o padrão. Curto e consultável vence completo e abandonado. Sem novidade, não force registro.
