---
name: gerar-mockup-validacao
description: Gera um mockup HTML autocontido para validacao visual de uma solucao ou desenho (arquitetura, modelo de dados, contrato, fluxo/pipeline, layout, antes/depois, KPIs de diagnostico). Transversal a todas as frentes. Use no GATE 2 para validar o que foi construido/desenhado, ou no GATE 1 para visualizar a solucao proposta, sempre que o entregavel for visual/estrutural o bastante para se beneficiar. NAO use para fix trivial, doc de texto puro sem estrutura, nem para dashboard PBI cujo proprio Desktop ja e a validacao.
---

> DESTINO: o `.html` gerado vive na PASTA DA DEMANDA na RAIZ DO CADERNO (`demandas/<TIPO>/DEM_<COD>/mockup_<slug>.html`), NUNCA no repo de trabalho. E registro INTERNO do caderno; nao vai para documentacao compartilhada com o cliente, a menos que o usuário peça. Ver CLAUDE.md > "Onde cada coisa mora".

# Skill: gerar-mockup-validacao (aid de validacao visual)

Transforma um entregavel denso de texto (um desenho de arquitetura, um modelo de dados, um contrato, um fluxo) numa pagina HTML que se valida no olho. Nasceu porque um mockup vale mais que tres paginas de tabela markdown na hora de o usuário bater o martelo num gate. E utilitaria e transversal: qualquer frente aciona; ela nao decide arquitetura nem escreve codigo de producao, so espelha o que ja foi decidido numa forma visual.

Principio central: o mockup NAO inventa. Ele espelha o entregavel real (o `plano.md`, o `contexto.md`, o documento de desenho, a `entrega.md`) com os DADOS REAIS do diagnostico semeados nas tabelas e KPIs, nunca placeholder generico. Se o mockup mostra um numero, esse numero saiu do registro.

## 0. Gate de relevancia (ANTES de tudo)

AGE quando o entregavel tem forma visual/estrutural que o texto esconde:
- desenho de arquitetura, modelo de dados (tabelas/colunas/relacao), contrato de interface;
- fluxo/pipeline, grafo de dependencia, cadeia de etapas;
- antes/depois de um refactor, KPIs de um diagnostico, mapa de-para;
- layout/tela proposta antes de construir (mockup de conceito no GATE 1).

PASSA A VEZ (nao gera, e diz por que em uma linha) quando:
- e fix trivial, ajuste pontual, ou doc de texto puro sem estrutura visual;
- ja existe a COISA REAL para validar e o mockup seria redundante — o caso classico e o dashboard PBI, cujo `montar-visuais` entrega o proprio `.pbip` e a validacao e abrir o Desktop (ali o mockup so ajuda como conceito ANTES de montar, nao depois);
- o entregavel ainda esta cru demais (sem numeros/estrutura para espelhar) — nesse caso, espere o desenho amadurecer.

Regra de bolso do "sempre que possivel": gere quando o mockup encurta a validacao de um gate. Se nao encurta, nao gere.

## 1. Insumos

- **O entregavel a espelhar:** o documento canonico da demanda (`plano.md` no GATE 1; o desenho/`entrega.md` no GATE 2). E a fonte da verdade; o mockup nao acrescenta decisao, so visualiza.
- **Os dados do diagnostico:** os numeros e exemplos reais que ja vivem no `contexto.md` e nos insumos (inventarios, mapas, contratos). Vao semeados nas tabelas/KPIs.
- **O template:** dois, na pasta desta skill. Sao o design-system da casa, com paleta neutra nas CSS vars (troque pelas cores da sua empresa ali, se quiser); copie e preencha, nao reinvente o CSS.
  - `template_mockup.html` — RELATORIO de validacao: KPI, antes/depois, tabela, grafo, criterios de aceite. E o default.
  - `template_fluxo_raias.html` — DIAGRAMA de fluxo em raias: trilhas paralelas, marcos e a transferencia de uma raia para outra. Use quando o entregavel e' um PROCESSO com etapas em ambientes/atores diferentes (fluxo de branches, cadeia de ETL, dev -> homolog -> prod, handoff entre areas). Traz a faixa de passos ponta a ponta no topo, o desenho no meio e um card por etapa embaixo.

## 2. Metodo (4 passos)

1. **Ler o entregavel e escolher os blocos.** Do documento, tire as 3 a 6 ideias que se beneficiam de forma visual e mapeie cada uma a um bloco do template (KPI, antes/depois, tabela, fluxo, grafo/dag, criterios). Nao use todos os blocos por usar; use os que contam a historia da validacao.
2. **Semear com o real.** Preencha KPIs e tabelas com numeros e nomes que saiem do registro (ex.: "10 tabelas gold", "14 no-op/dia", os nomes de objeto do inventario). Onde o nome for hipotese do padrao proposto (nao o objeto real que existe hoje), marque "ilustrativo" no rodape, para o mockup nao mentir sobre o que ja existe.
3. **Montar do template.** Copie o template escolhido para `demandas/<TIPO>/DEM_<COD>/mockup_<slug>.html`, mantenha o `<style>` intacto, troque so o miolo das secoes. Numere as secoes (01, 02, ...) e de a cada uma um lead curto de uma linha.
4. **Conferir as regras duras** (secao 3) antes de entregar.

## 3. Regras duras (o que nao pode quebrar)

- **Autocontido.** Zero dependencia externa: sem CDN, sem fonte remota, sem imagem por URL, sem fetch. Tudo inline; imagem, se precisar, vira `data:` URI. (Alem de politica de artefato, e o que faz o arquivo abrir em qualquer lugar e sobreviver versionado.)
- **Tema claro/escuro.** Ja resolvido no template por `prefers-color-scheme` + o override `data-theme` do botao "alternar tema". Nao hardcode cor fora das CSS vars.
- **Responsivo.** O body nunca rola na horizontal. Tabela larga vai sempre dentro de `.tbl-scroll`; bloco largo idem.
- **Seguranca (regra dura da casa).** NUNCA um segredo/token/connection string no HTML. NUNCA dado corporativo bruto: numero agregado do diagnostico pode; linha de dado real de cliente/pessoa, nao. Dado pessoal de terceiro e anonimizado (LGPD). Na duvida, agregue ou rotule.
- **Nao mentir sobre o real.** Nome de objeto que e proposta do padrao (ainda nao existe em campo) vai marcado como ilustrativo. O mockup e de validacao, nao pode passar hipotese como fato.

## 4. Saida e fluxo

1. Confirme o gate de relevancia (0). Se passar a vez, diga em uma linha por que e siga sem gerar.
2. Gere `demandas/<TIPO>/DEM_<COD>/mockup_<slug>.html` do template, semeado com o real.
3. Entregue renderizado para o usuário validar no olho (o arquivo abre no Browser pane; se util, aponte o caminho clicavel). O mockup e aid do gate, nao um entregavel a mais: some no fluxo normal (GATE 1 ajuda a aprovar o plano; GATE 2 ajuda a validar o que foi construido).
4. Nao commite por conta propria; o mockup entra no commit da demanda pela `publicar`, como o resto do registro. Se o usuário pedir ajuste visual, itere no mesmo arquivo.

## 5. Onde encaixa na esteira

Transversal, chamada por outra skill ou avulsa:
- **GATE 1 (analisar-especificacao):** quando a solucao proposta e conceitual/estrutural, um mockup do desenho proposto ajuda a aprovar o plano com mais confianca.
- **GATE 2 (desenvolvimento de qualquer frente):** quando o que foi construido/desenhado se le melhor visualmente (modelo de dados, arquitetura, contrato, fluxo). E o caso mais forte.
- **Avulsa:** "gera um mockup pra eu validar isso" em cima de qualquer documento de desenho ja pronto.

Nao substitui a validacao real (abrir o Desktop no PBI, rodar a cadeia nos dados): e um espelho para decidir mais rapido, nao a prova final.

## 6. PDF e GIF do mockup (`render.py`)

O mockup nasce HTML, mas as vezes precisa virar anexo (PDF) ou entrar numa apresentacao (GIF).
O `render.py` desta pasta faz os dois com o Chrome instalado, sem dependencia de rede:

```
python render.py pdf  mockup.html saida.pdf [--retrato] [--claro] [--com-margem] [--check]
python render.py gif  mockup.html saida.gif --estagios 8 [--largura 920] [--ms 1100]
```

**NAO gere o PDF mandando imprimir na mao.** O Chrome usa a largura do PAPEL como viewport
(A4 paisagem ~1054px, retrato ~733px), abaixo do breakpoint do template — o CSS responsivo
empilha tudo e o layout quebra. Escalar com `zoom` ou com `transform` sozinho tambem nao
resolve, porque a caixa de layout continua do tamanho original e o Chrome pagina igual. O
script renderiza numa largura fixa, neutraliza as media queries e reduz a pagina inteira.

**E nao confie em conferir numa janela larga**: nela o breakpoint nao dispara, entao o layout
aparece certo enquanto o PDF sai quebrado (isso ja custou algumas idas e voltas). O `--check`
salva duas capturas, larga e estreita: se as duas saem iguais, o layout nao depende mais do
viewport e o PDF esta correto.

Por padrao o PDF sai em paisagem, tema escuro e SEM margem — o fundo sangra ate a borda, sem
faixa branca. Para impressao em papel de verdade, use `--com-margem --claro`.

**Para o GIF**, marque no HTML o que aparece em cada estagio:

| marca | efeito |
|---|---|
| `data-s="3"` | aparece A PARTIR do estagio 3 e fica (o desenho se constroi) |
| `data-on="3"` ou `data-on="3 4 5"` | fica esmaecido e ACENDE nos estagios listados (o passo corrente) |
| sem marca | cenario: visivel desde o primeiro quadro |

Vale para qualquer elemento, do SVG ou do HTML — e o que deixa o desenho, a caixa do passo e o
card da etapa se moverem juntos. Para testar as duas saidas, rode o `render.py` direto sobre os
templates desta pasta: o `template_fluxo_raias.html` ja traz marcas `data-s` de exemplo para o
GIF, e os dois servem para conferir o PDF.
