# Modelo: fechamento de chamado (trilho curto e trilho longo)

> Formato do `fechamento.md` (trilho curto) e do `documentacao.md` (trilho longo) quando a
> origem é chamado e existe SLA. Cálculo em [[PADRAO_SLA]]. Público: registro corporativo.
> O bloco de valor é **interno** e só aparece no trilho curto, onde não existe `valor.md`
> separado. Ele nunca vai para documento compartilhado com o solicitante.

---

### 📌 [{ID}] — {TIPO}: {DESCRIÇÃO CURTA} | {COMPLEXIDADE} — {RISCO} — {SLA}

> Título em caixa alta, incluindo o tipo. Descrição com no máximo 40 caracteres.

**ID:** {código da demanda, com o chamado de origem vinculado se houver} | **Solicitante:** {nome ou N/A} | **Marcadores:** {ex.: PBI · FINANCEIRO}
**Objeto afetado:** {nome do objeto} | **Ambiente:** {onde}

**Sprint:** {SPRINT_X - MMM/AA} | **Criação:** {DD-MM-AAAA hh:mm, a data do CHAMADO no sistema} | **No caderno desde:** {DD-MM-AAAA}
**Início previsto:** {DD-MM-AAAA} | **Início real:** {DD-MM-AAAA ou —} | **Prazo:** {DD-MM-AAAA} | **Entrega:** {DD-MM-AAAA ou —}
**SLA:** {status · folga ou atraso em dias úteis} | **Esforço:** {N dias úteis ou —}
**Complexidade:** {Baixa/Média/Alta} | **Risco:** {Baixo/Médio/Alto · justificativa em uma linha}

**Problema:** {uma ou duas linhas}
**Impacto:** {uma linha}
**Causa:** {uma linha}

**Solução (o que foi feito):**
* {bullet}

**Como foi feito:**
* {passo}

**Validação:**
* {como validou} → {resultado}

**Status:** {Entregue · Aguardando validação · Aguardando definição · Bloqueado}
**Obs.:** {opcional}

---
ℹ️ **Como ler este cabeçalho**
**Complexidade** = ambientes envolvidos + porte da alteração · Baixa · Média · Alta
**Risco** = Complexidade × tempo até o prazo × validação
**SLA** = entrega contra o prazo da sprint (S1 → dia 15 · S2 → último dia útil do mês), em dias úteis.
**Criação** é a data do chamado no sistema; **No caderno desde** é quando a pasta nasceu aqui. Chamado antigo registrado depois tem as duas distantes, e só a primeira conta para SLA.

---
<!-- INTERNO: não compartilhar. Só no trilho curto; no longo isto vira valor.md. -->
🔒 **Valor (interno)**
**Dor endereçada:** {qual} | **Beneficiário:** {quem}
**Dimensão:** {tempo · confiabilidade · decisão · risco-dependência · adoção · capacidade · custo}
**Origem da prioridade:** {estratégica · rotina · urgência · volume}
**Antes:** {baseline com data, ou "sem baseline medido"} → **Depois:** {medida ou proxy, marcado como proxy}
**Confiança:** {alta · média · baixa} | **Contra-argumento:** {o que um cético diria}
**Feedback:** {quem comentou e o quê, com data; ou "nenhum recebido"} | **Visibilidade:** {quem ficou sabendo: área, gestor, diretoria, reunião}
**Competências:** {o que precisou usar ou desenvolver, técnico e comportamental, separado por vírgula}

---

## Regras de escrita

- Direto e corporativo, frases curtas, sem floreio.
- Nunca invente. Faltou, escreve `N/A`.
- Sempre separe "o que foi feito" de "como foi feito".
- Sempre registre validação, nem que seja simples.
- Datas, SLA, complexidade e risco saem do [[PADRAO_SLA]], nunca de chute.
- Faltando informação crítica, feche com **Pendente confirmar:** e as dúvidas.

## Linguagem: este documento sai para a área

Este é um dos dois arquivos da pasta que o solicitante lê. O leitor é analista de negócio, e não
conhece o ambiente por dentro. Vale para toda frente, não só para APP.

Escreva o corpo pelo efeito: o que a pessoa passa a ver, onde, o que mudou no resultado, e o que
ela precisa saber para não confundir resultado novo com defeito. Termo técnico que sobrar vira uma
linha `**Rastreio:**` no rodapé, apontando para o `entrega.md` (trilho longo) ou para o
`contexto.md` (trilho curto).

| Não escreva | Escreva |
|---|---|
| `.pbip`, TMDL, JSON, modelo semântico, estado do Desktop | o painel, a tela, a base do painel |
| nome de medida, de tabela, de coluna | o indicador, a informação, o campo que a pessoa vê |
| nome de pipeline, de bloco, de atividade, de notebook, de parâmetro | a rotina geral de cargas, a fila compartilhada, o agendamento |
| id de dataset, GUID, workspace id | o nome do painel |
| gold, silver, bronze, serverless, lakehouse | o repositório de dados da empresa |
| view, procedure, query, `SELECT` | a consulta ao sistema, a origem do dado |
| wikilink para padrão interno | nada; isso fica nos arquivos internos |

O bloco de valor é interno e não sai para ninguém, mas vive no mesmo arquivo. Mantenha a mesma
linguagem ali, para o documento não ficar com dois registros diferentes.

## Casos especiais

- **Entrega parcial:** Status `Encerrado (entrega parcial)` com a data, e o que ficou de fora
  listado em Pendente confirmar. Não dê a entender que resolveu 100%.
- **Solicitação nova durante a validação:** registre em Obs. como escopo novo e provável
  chamado à parte. Não entra na Solução, não afeta SLA nem Status.
