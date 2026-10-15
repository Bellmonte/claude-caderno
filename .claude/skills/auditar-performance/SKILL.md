---
name: auditar-performance
description: Mede a performance de um dashboard Power BI aberto no Desktop (tamanho do modelo, tempo de atualização, tempo de página a frio e a quente), cruza os números com o .pbip e o catálogo de causas e grava o relatório de auditoria. Dois modos, diagnóstico (linha de base) e remedição (depois da correção, comparando). Não altera modelo nem relatório. Frente PBI. Disparada só pelo usuário.
disable-model-invocation: true
---

# Skill: auditar-performance (PBI, medição antes e depois)

Mede, diagnostica e relata. **Não conserta**: a correção entra pela esteira normal, com o
`auditor-pbi` revisando como sempre. Régua completa em `conhecimento/padroes/PADRAO_PERFORMANCE_PBI.md`
(leia antes de começar). Relatório no modelo `conhecimento/modelos/auditoria-performance.md`.
Scripts em `.claude/scripts/performance/`.

Esta skill ocupa o Desktop por vários minutos e pode disparar atualização do modelo. Por isso só roda
quando o usuário chama, e a atualização só roda com autorização dada naquela hora.

## 0. Entrada

O usuário diz o painel e o modo:

- **diagnóstico**: a linha de base. Se ainda não existe épico da auditoria, rode a `abrir-demanda`
  antes (`DEM_BI-NNN_performance-<painel>`, sem chamado). O relatório nasce na pasta do épico.
- **remedição**: depois da correção. Leia o `auditoria-performance.md` existente e as medições em
  `local/performance/<painel>/antes`; a nova rodada vai para `.../depois`.

Pasta de trabalho: `local/performance/<painel>/`, com `<painel>` em slug ASCII. **Só os scripts leem
e escrevem ali** (exceção registrada no PADRAO, seção 3). Nunca abra arquivo de `local/` com Read,
nunca mostre texto de consulta.

## 1. Pedir o JSON do analisador

É a única parte que precisa de clique. Passe o roteiro curto e espere o usuário responder que salvou:

1. Abrir a página no Desktop, com **só esse Desktop aberto** na máquina.
2. Exibir > Analisador de desempenho > Iniciar gravação.
3. Atualizar visuais uma vez. Para várias páginas no mesmo arquivo, trocar de página durante a gravação.
4. Exportar e salvar em `local/performance/<painel>/analisador_<pagina ou geral>.json`.

## 2. Primeira foto, na hora

```powershell
.\.claude\scripts\performance\medir_consultas.ps1 -Json <json> -SoListar
```

Devolva: número de visuais e de consultas, o tempo que o analisador registrou para cada consulta e
os visuais mais lentos. O tempo de cada página a quente é o que o próprio analisador mostrou na
gravação (duração por visual, na tela do Desktop ou no JSON exportado).
Blocos com zero consultas são o Desktop reaproveitando resultado e saem da mediana. Isso já é
diagnóstico útil, antes de qualquer repetição.

## 3. Conferir a conexão e o modelo

- `Get-PbiInstancias` (em `_comum.ps1`) lista porta e título da janela. Mais de um Desktop aberto é
  ruído de medição: peça para fechar os outros antes de seguir.
- O `powerbi-modeling-mcp` pode ser usado para listar instâncias e ler nomes de tabela e coluna. O
  aceite dos termos da Microsoft é decisão do usuário: pergunte antes do primeiro uso. A
  cronometragem nunca passa pelo MCP, porque a ida e volta dele entra no tempo medido.
- Confirme que o modelo conectado é o mesmo painel do JSON: as tabelas e colunas que o `-SoListar`
  e o ranking de tamanho mostram precisam existir no modelo aberto. Divergiu, pare.

## 4. Medir

Peça ao usuário que não mexa no Desktop enquanto isso. Saída em `local/performance/<painel>/antes`
(ou `/depois` na remedição).

```powershell
.\.claude\scripts\performance\tamanho_modelo.ps1 -Saida <pasta>
.\.claude\scripts\performance\medir_consultas.ps1 -Json <json> -Saida <pasta>
# só com autorização dada agora, porque ocupa o Desktop e demora:
.\.claude\scripts\performance\medir_atualizacao.ps1 -Saida <pasta>
```

Confira antes de usar o número:

- `medir_consultas` avisa quando o frio não passou na conferência. Rodada assim **não serve** de
  linha de base: descubra o motivo e repita.
- Atualização com faixa acima de uns 5% indica ruído no ambiente (outro Desktop, outro processo
  pesado). Diga isso, e repita se der.
- Tamanho: a leitura vale depois de atualização completa. Quando houver atualização, leia de novo
  depois dela e confira que bate.

## 5. Diagnosticar

Chame o agente `auditor-pbi` no **modo 3 (diagnóstico de performance)**, passando o caminho do
`.pbip` e o **resumo agregado** das medições (a saída de tela dos scripts, que não tem texto de
consulta). Ele liga cada número à causa provável no catálogo e prioriza por impacto e esforço.

## 6. Relatar

Grave `auditoria-performance.md` na pasta do épico, no modelo. A tabela de medição sai do
`comparar.py` (na remedição, com `--antes` e `--depois`; no diagnóstico, só o antes preenchido).
Deixe claro o que é motor (consulta repetida por script) e o que é página a quente (analisador).

Na remedição:

- repita as **mesmas** consultas do JSON original. Se a correção mudou um visual, as consultas dele
  mudam; peça um JSON novo só daquela página e meça com `-Consultas` ou com o JSON novo;
- confira que a paridade está registrada antes de afirmar qualquer melhora;
- afirme melhora só onde o `comparar.py` disser "melhora mensurável".

Quando a correção reduzir espera de gente de verdade, sinalize para a `capturar-valor` no fechamento
do épico: o relatório é a linha de base e o depois.

## Regras duras

- Não altera `.pbip`, modelo publicado nem relatório. Nunca mede contra o serviço.
- Resultado bruto e export do analisador ficam em `local/performance/`. Relatório só com agregados.
- Linha de base e remedição na mesma máquina e na mesma versão do Desktop; o `comparar.py` recusa
  versões diferentes, e passar por cima disso é decisão do usuário, escrita no relatório.
- Mediana e faixa, nunca um número só.
