---
name: abrir-demanda
description: Abre uma demanda nova a partir do material bruto do chamado ou do alinhamento, grava o SLA e decide o trilho (curto, longo ou incidente) pela triagem dos sete sinais. Primeira etapa da esteira. Use antes de analisar-especificacao.
---

# Skill: abrir-demanda (entrada da esteira)

Duas ações e mais nada: **cria a pasta com a solicitação** e **decide o trilho**. Não analisa
o modelo, não confronta com a realidade técnica, não desenvolve. A inteligência técnica é da
`analisar-especificacao`, logo depois.

## 1. Nome e lugar da pasta

`demandas/<TIPO>/DEM_<COD>_<slug>/`, onde `<TIPO>` é a gaveta do prefixo (mapa no `CLAUDE.md`).
Prefixo sem gaveta cria `PREFIXO_descricao/` no mesmo padrão.

- **Com chamado:** usa o código principal. `TSK-1042` com o chamado `[CH-2210]` vinculado vira
  `DEM_TSK-1042_<slug>`, e o vinculado entra num campo dentro do arquivo.
- **Sem chamado** (auditoria, reconciliação, app por alinhamento): `DEM_<SUB>-NNN`. Para o
  sequencial, conte só as pastas `DEM_<PREFIXO>-*` da gaveta e use o próximo número.
- **Filha de épico:** `DEM_<COD>.NN` dentro da pasta do pai.
- Nome curto e estável. Título e vínculos vão dentro do arquivo, não no nome.

## 2. SLA e as três datas (capturadas agora, na abertura)

**Obtenha a data real do sistema** (`date +%d-%m-%Y`). Nunca assuma data.

Três datas diferentes, e confundir duas delas estraga a contagem do dia:

- **Chamado aberto em** = a data que o card mostra no sistema de atendimento. É ela que
  ancora o SLA e a sprint, conforme [[PADRAO_SLA]]. Sem chamado, `N/A`.
- **Entrou no caderno em** = hoje, o dia em que a pasta nasceu. Não afeta SLA nem esforço,
  serve para saber quando o registro passou a existir. Chamado antigo versionado hoje tem
  as duas datas bem distantes, e é assim que se enxerga isso.
- **Trabalho iniciado em** = o dia em que a mão entrou de verdade. Na abertura costuma ser
  hoje; quando ainda não começou, escreva `a iniciar` e preencha depois.

- **Sprint** = calculada sobre a data do chamado: dia `<= 15` vira `SPRINT_1`, senão
  `SPRINT_2`. Label `SPRINT_<n> - <MMM>/<AA>`. Sem chamado, use a data de entrada no caderno.

Régua completa em [[PADRAO_SLA]].

## 3. Triagem do trilho (a decisão que define o peso do registro)

**Saída antecipada, antes de qualquer sinal.** Se o usuário abriu a demanda dizendo que o
trabalho já foi feito, ou se o pedido é ajuste trivial e reversível (largura de coluna, texto,
cor, ordem de campo), o trilho é **DIRETO** e os sete sinais não rodam. Escreve a
`solicitacao.md`, escreve o `fechamento.md` e encerra. Não pede ambiente aberto, não roda
consulta para confirmar o que ele afirmou, não chama auditor, não oferece GATE. O que ele disse
sobre o estado do ambiente é o resultado da validação, e entra no `fechamento.md` como tal.


Antes de escrever o arquivo, passe o pedido pelos **sete sinais**. Todos são verificáveis na
entrada, sem abrir o modelo:

1. o pedido se quebra em tarefas independentes, que viram filhas
2. toca mais de uma frente (pbi + dados, app + sql, …)
3. tem homologação formal, com rodadas de validação do solicitante
4. depende de terceiro (outra área, fornecedor, TI) para concluir
5. mexe em estrutura: modelo semântico, origem, ETL, banco, pipeline
6. é objeto novo do zero (greenfield)
7. o objeto alvo já tem histórico de retorno de validação em `gerencial/objetos/`

**Leia o sinal 7 de verdade**: se existe `gerencial/objetos/<objeto>.md`, abra e olhe a taxa de
retrabalho antes de decidir. Objeto que já devolveu três vezes não merece trilho curto.

| Sinais acesos | Trilho |
|---|---|
| nenhum | **CURTO** |
| um | **CURTO**, e você diz em voz alta qual sinal acendeu |
| dois ou mais | **LONGO** |

Quebra ou instabilidade não-planejada não entra aqui. Isso é **INCIDENTE** e vai pela skill
`registrar-incidente`.

O veredito é proposta, não sentença. Diga o trilho, liste os sinais que acenderam e siga. Se o
usuário discordar, troque sem discutir.

## 4. Saída

Crie `demandas/<TIPO>/DEM_<COD>_<slug>/solicitacao.md`:

```markdown
# <COD> | <TÍTULO>

**Chamado vinculado:** <código do chamado, ex.: CH-xxxx, ou N/A>
**Chamado aberto em:** <DD-MM-AAAA, do card no sistema, ou N/A>
**Entrou no caderno em:** <DD-MM-AAAA, hoje>
**Trabalho iniciado em:** <DD-MM-AAAA ou "a iniciar">
**Sprint:** <SPRINT_X - MMM/AA>
**Trilho:** <curto | longo | incidente>  ·  **Sinais:** <nenhum | lista dos que acenderam>
**Objeto alvo:** <nome do objeto, ou N/A>

## Solicitação (bruta)
<o material como chegou, transcrito e organizado, sem interpretar>
```

Variante sem chamado: troque `Chamado vinculado` e `Chamado aberto em` por
`**Origem:** <qual alinhamento e quando, ou qual item do cronograma>`. A sprint continua sendo
calculada sobre a entrada no caderno, como bucket temporal.

**Campo `Objeto alvo`:** preencha sempre que der. É ele que liga a demanda ao prontuário em
`gerencial/objetos/` no fechamento, e é o que permite enxergar retrabalho por objeto.

## 5. Material que veio junto

Planilha, export, print, PDF do solicitante: nada disso entra na pasta da demanda. Vai para
`local/<DEM_COD>/` e o registro guarda **o caminho**, nunca o conteúdo. Regra dura do `CLAUDE.md`.

## Fim

Confirme a pasta criada e o trilho decidido. Pare. Análise é outro comando.
