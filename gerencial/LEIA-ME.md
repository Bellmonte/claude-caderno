# gerencial/

A camada de leitura da gestão: público que lê pouco e quer resultado. Diferente de `demandas/`,
que guarda o trabalho, e de `diario/`, que guarda a narrativa cronológica. Aqui mora o que
atravessa demandas e o que é comunicado para fora.

## Estrutura

- `dia/<AAAA-MM-DD>.md`: a daily do dia, no formato de bloco para WhatsApp, gravada pela
  skill `reporte-dia`. Cada uma alimenta a retrospectiva da seguinte.
- `semana/<AAAA-Www>/`: uma pasta por semana ISO (ex.: `2026-W28/`), gravada pela
  `reporte-semana` na sexta, última hora:
  - `resumo.md`: a fonte da verdade em markdown, lida pela semanal seguinte para dar continuidade.
  - `resumo.html`: o template preenchido, com a identidade visual de [[PADRAO_VISUAL_REPORTE]].
  - `resumo.pdf`: a one-page final, o que vai para a gerência.
  - `email.md`: o texto de encaminhamento que acompanha o PDF.
  - `plano-semana.md`: o calendário da semana seguinte, gravado pela `planejar-semana` e
    consumido pela `reporte-dia` para já oferecer a tarefa do dia.
- `objetos/<objeto>.md`: o prontuário de cada objeto nomeado (dashboard, agente, pipeline),
  que cresce uma linha por fechamento e acumula retrabalho e tempo de homologação. Formato em
  [[prontuario-objeto]].
- `valor/`: o consolidado de valor, INTERNO. O `rollup.md` é derivado dos blocos de valor das
  demandas por `python .claude/scripts/rollup_valor.py --md`, e o `portfolio-valor.md` é
  incrementado pela `capturar-valor` a cada fechamento.
- `desempenho/`: o registro de carreira, INTERNO e pessoal: `registro-<ano>.md` com uma linha
  por entrega (entrega, objetivo, status, prioridade, período, impacto, evidência, feedback,
  competências, visibilidade) e `painel-<ano>.html`, a leitura visual do ano. Os dois são
  derivados por `python .claude/scripts/registro_desempenho.py --md` e nunca editados à mão.
  Serve para conversa de aumento ou promoção, para o 1:1 com o gestor e para enxergar a
  evolução quando bate a sensação de estar parado. Racional em [[processo_registro_de_desempenho]].
- `reunioes/<AAAA-MM-DD-assunto>/`: a ata destilada de cada reunião, escrita pela `ata-reuniao`.
- `divulgacao/`: o briefing das peças visuais que explicam o trabalho para fora: roteiro de
  infográfico, one-page de apresentação, material de divulgação interna. Cada arquivo guarda a
  ficha da peça, o texto exato de cada bloco, a identidade visual e os cuidados. A arte final
  não mora aqui; o que mora é o que a arte tem que dizer.

Cadência nova (mensal, trimestral) entra como subgrupo próprio, ao lado de `semana/`.
