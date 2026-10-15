---
name: analisar-especificacao
description: Ponto de entrada da esteira de desenvolvimento. Lê a solicitação bruta de um chamado, confronta com a realidade técnica (modelo/.pbip existente ou, se for novo, trata a solicitação como spec de desenvolvimento), classifica tipo e frente, e produz UMA de três saídas — plano de solução viável, documentação de impedimento, ou pergunta por informação faltante. Transversal a todas as frentes. Use ao iniciar uma demanda.
---

> DESTINO: todo arquivo de registro (demandas/, diario/, conhecimento/, gerencial/) é criado na RAIZ DO CADERNO (o repositório do caderno adicionado à sessão), NUNCA no repo de trabalho. Se o caderno não estiver na sessão, pare e peça para adicioná-lo. Ver CLAUDE.md > "Onde cada coisa mora".

# Skill: analisar-especificacao (START da esteira)

NÃO é um validador de formulário. É a ponte entre o que foi PEDIDO e o que é tecnicamente POSSÍVEL.
A spec recebida é uma solicitação válida porém ingênua quanto ao técnico: humano e máquina entendem o pedido, mas ela NÃO consultou o modelo nem considerou limitação técnica. Esse skill resolve isso.

Importante: esta skill é o START, não a esteira inteira. Ela vai ATÉ o gate do plano e PARA. Não desenvolve.

## Entrada
No início, a pasta da demanda contém SÓ `demandas/<TIPO>/DEM-XXX/solicitacao.md` (a solicitação bruta, já padronizada pelo processo de abertura). O resto dos arquivos nasce nas etapas seguintes — não os procure aqui nem os crie antecipadamente.

## Passo 1 — Ler e entender a solicitação
Padrão esperado da spec: Título · Solicitante/Área · Objeto afetado · Problema · Evidência · O que precisa ser feito (com IN-SCOPE) · Como deve ficar/aceite · Observações (ripple, período de validação).

## Passo 2 — Classificar
- TIPO (mesmo vocabulário do fechar-demanda): feat · fix · refactor · style · docs · chore · verif.
- FRENTE: pbi · dados · sql · app · automacao.
- Greenfield (dash/objeto novo) OU manutenção (altera algo existente)?

## Passo 3 — Confrontar com a realidade técnica (o coração)
- **Manutenção:** leia o estado atual (o `.pbip`/modelo, a procedure, o pipeline — conforme a frente). Localize os objetos citados. Confirme ou REFUTE a hipótese do solicitante. Mapeie o ripple (o que mais é afetado).
- **Greenfield:** não há "atual" para confrontar — a própria solicitação é a especificação de desenvolvimento. Avalie completude e coerência técnica do que foi pedido.

## Passo 4 — Decidir quais frentes técnicas entram
Pela frente e pelo escopo, decida quais skills do motor serão acionadas no desenvolvimento. Para PBI:
- toca estrutura/M → `modelagem-dados`
- toca medida/cálculo/KPI → `medidas-dax`
- toca layout/visual → `montar-visuais`
- frequentemente é um subconjunto (manutenção raramente usa as três).
Para APP (a aplicação e os agentes de IA dela):
- toca front/back/API/agente/ação → `desenvolver-app`
- toca exclusivamente view ou procedure do banco (ex.: Oracle) → cede pro motor **sql** (registra a dependência)
- toca exclusivamente o fluxo da ferramenta de automação → cede pro motor **automacao** (no app, a automação entra só como proxy)
- o confronto técnico lê o CÓDIGO real da aplicação (handoff e CLAUDE.md do projeto costumam driftar do código); ver `PADRAO_APP §1/§3`.
Consulte a matriz de roteamento (`conhecimento/referencias/ROTEAMENTO_FRENTES.md`) SE existir: match acelera e dá consistência. Sem match (caso novo), NÃO trave nem force encaixe — siga estas diretrizes, roteie pelo melhor julgamento e adapte-se ao feedback. A matriz nunca é a única verificação.

## Passo 5 — Produzir UMA de três saídas
**(a) Plano de solução — quando viável.**
Escreva `demandas/<TIPO>/DEM-XXX/contexto.md` (pedido como chegou, premissas verificadas, tipo, frente, objeto afetado, critérios de aceite, ripple) e proponha `demandas/<TIPO>/DEM-XXX/plano.md` (abordagem, passos, quais frentes técnicas entram, riscos). PARE para aprovação (gate 1).

> Camada de valor (baseline barato). Você já está lendo o estado atual aqui; este é o único momento barato de capturar o "antes". De forma leve e sem virar formulário, semeie `demandas/<TIPO>/DEM-XXX/valor.md` (do `_TEMPLATE-DEM/valor.md`) com só o bloco de baseline: dor endereçada, beneficiário, origem da prioridade, dimensão candidata, o baseline do estado atual com a data de hoje, e o horizonte. Deixe os campos de resultado em branco para o fechamento (skill `capturar-valor`). É registro INTERNO, nunca vai para doc compartilhada com o cliente. Se o baseline não der para medir, escreva "sem baseline medido" e siga; não trave a análise por isso.

> Validação visual (aid de gate, opcional). Quando a solução proposta for conceitual/estrutural (arquitetura, modelo de dados, contrato, fluxo, antes/depois) e um desenho ajudar o usuário a aprovar o plano com mais confiança, gere um mockup pela skill `gerar-mockup-validacao` (aplique o gate de relevância dela: se não encurta a validação, não gere). No GATE 1 o mockup espelha a SOLUÇÃO PROPOSTA do plano; o mockup do que foi de fato construído/desenhado é mais forte no GATE 2, no desenvolvimento da frente. É registro INTERNO na pasta da demanda; não vira etapa obrigatória.

**(b) Documentação de impedimento — quando inviável.**
Quando a realidade técnica diz que não dá (ou não dá do jeito pedido), documente o impedimento de forma CURTA e objetiva, em `demandas/<TIPO>/DEM-XXX/contexto.md`:
- Pedido: o que foi solicitado.
- Por que não é possível: a limitação técnica concreta encontrada no modelo/sistema.
- O que destravaria: alternativa viável ou pré-requisito, se houver.
- Decisão necessária: o que você precisa decidir/aprovar.
Brevidade é regra. Não desenvolva, não force uma solução ruim só para "entregar algo".

**(c) Pergunta — quando falta informação para decidir.**
Se a spec tem lacuna que impede decidir viabilidade (ex.: campos `[A CONFIRMAR]`, ambiguidade de escopo), PERGUNTE antes de concluir. Liste objetivamente o que falta. Não chute.

## Regra de ouro
A premissa do solicitante é HIPÓTESE a verificar contra o modelo, não verdade. "Está tudo errado" quase sempre é um caso específico; confirme antes de planejar.
