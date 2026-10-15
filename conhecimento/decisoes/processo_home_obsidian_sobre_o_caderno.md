# A Home do Obsidian e o painel derivado dividem o trabalho

**A pergunta que ordenou tudo.** Antes de construir, a dúvida era se a Home em
`dataviewjs` duplicaria o `PAINEL.md` que o hook já gera. A resposta veio de uma
pergunta simples: o Claude precisa do painel para atuar? Não. O `abrir_dia.py`
injeta o estado como contexto no início de cada sessão, então o cálculo chega
pronto sem abrir arquivo. O `PAINEL.md` sempre foi para consumo **humano**.

Com isso a divisão fica limpa e não há duplicação de propósito:

| | Quem consome | Quando atualiza |
|---|---|---|
| Contexto do hook | o Claude | a cada abertura de sessão |
| `sistema/dashboards/inicio.md` | o usuário, no Obsidian | ao abrir a nota, lendo o vault ao vivo |
| `PAINEL.md` | quem estiver fora do Obsidian | a cada abertura de sessão |

## Por que a Home é mais fresca que o painel

O painel depende de uma sessão do Claude abrir para ser regravado. A Home lê o
vault no instante em que você olha, então nunca mostra estado velho. Foi por isso
que ela dispensou botões de sincronizar: não há o que sincronizar, o dado é lido
na hora.

## A regra que evita as duas telas mentirem

A leitura de demandas está escrita duas vezes, em Python no hook e em JavaScript na
lib, e isso é dívida assumida: linguagens diferentes, ambientes diferentes. O que
protege é um **teste de paridade**, que roda a mesma varredura nos dois e compara.
Na primeira execução deu 51 abertas, 6 incidentes e 45 fora, idêntico dos dois
lados. Ao mexer na regra de uma, rode a outra e confira: número que diverge sem
ninguém notar é pior que número ausente.

A regra em si: pasta `DEM_*` com `solicitacao.md`, sem `fechamento.md` nem
`documentacao.md`, e épico não conta porque quem fecha são as filhas.

## O que aprendi montando

**A nota de dashboard tem que ser burra.** Três linhas chamando o script, com
`cssclasses: [sc-dash]` para esconder título inline, bloco de propriedades e o
padding do editor. Sem isso a tela nunca vira painel, continua sendo nota com
coisas dentro.

**Código do painel fora do plugin.** Mexer no `main.js` do plugin exige reiniciar o
Obsidian; script e CSS carregados por `dv.io.load` recarregam ao reabrir a nota. O
ciclo cai de vinte segundos para dois, e isso muda quanto se refina o visual. Por
isso o plugin guarda só a barra, e tudo mais mora em `sistema/scripts/`.

**O `new Function` é síncrono**, então a lib não pode ter `await` de topo. Onde
precisa de assincronia, `.then()`.

**Abrir arquivo pega o leaf da área principal**, com
`getMostRecentLeaf(rootSplit)`. Abrir direto na sidebar faz a nota nascer dentro
dela e sumir na troca de view.

**O `setIcon` não está no escopo do dataviewjs**, então o plugin expõe o dele e a
lib consome via `app.plugins.plugins["caderno-nav"]`.

## O custo que foi aceito

A Home exige o plugin Dataview com JavaScript Queries ligado, o que reverte a
decisão anterior de não instalar plugin de comunidade. A troca é consciente: o
ganho é uma leitura do estado que não depende de rotina nenhuma ter rodado. O
`PAINEL.md` continua sendo gerado como saída de fallback, legível fora do Obsidian
e por qualquer editor, e não custa manutenção porque é subproduto de um hook que
já roda.

Ver [[processo_painel_derivado_do_estado]] e [[obsidian_uso_no_dia_a_dia]].
