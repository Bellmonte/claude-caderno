# PADRÃO_VISUAL_REPORTE: identidade dos reportes e documentos gerados

> A lei visual de tudo que sai do caderno em HTML ou PDF: reporte semanal, prontuário de
> objeto, estudo de caso, mockup de validação. O caderno vem com uma paleta neutra, de acento
> azul petróleo, pensada para funcionar em qualquer empresa sem parecer marca de ninguém.
> **Para usar a identidade da sua empresa, troque os tokens desta tabela** (e os mesmos tokens
> nos modelos HTML), nunca cor solta no meio do CSS.
>
> Modelos prontos em `conhecimento/modelos/`:
> [modelo-reporte.html](../modelos/modelo-reporte.html) (relatório longo, web, com tema claro e escuro),
> [reporte-semanal-a4.html](../modelos/reporte-semanal-a4.html) (one-page A4 para PDF do gestor),
> [prontuario-objeto.html](../modelos/prontuario-objeto.html) (prontuário de objeto) e
> [painel-desempenho.html](../modelos/painel-desempenho.html) (registro de desempenho).
> A mesma paleta vale para o painel do Obsidian em `sistema/scripts/dashboards.css`, que
> herda o acento do tema do cofre.

## Tokens de cor

Definidos em `:root`, com o par escuro em `@media (prefers-color-scheme: dark)` guardado por
`:root:not([data-theme="light"])` e repetido em `:root[data-theme="dark"]`.

| Token | Claro | Escuro | Uso |
|---|---|---|---|
| `--ground` | `#F6F7F9` | `#0F141A` | fundo da página |
| `--surface` | `#FFFFFF` | `#161D25` | cartão, bloco |
| `--surface-2` | `#EEF1F4` | `#1D2630` | fundo de apoio, cabeçalho de tabela |
| `--ink` | `#1A2230` | `#E4E9EF` | texto principal |
| `--ink-2` | `#3D4757` | `#BAC4CF` | texto secundário |
| `--muted` | `#6B7585` | `#8A95A3` | detalhe, legenda |
| `--line` | `#DDE2E8` | `#263140` | divisória |
| `--line-strong` | `#C5CCD5` | `#364354` | divisória de ênfase |
| `--acento` | `#2F6F8F` | `#7DB3CC` | cor da casa, positivo, entregue |
| `--acento-claro` | `#4F8FAD` | `#9CC6D9` | apoio do acento |
| `--acento-wash` | `#E3EEF3` | `#172832` | fundo de chip positivo |
| `--ambar` | `#9A6B10` | `#D6A74A` | atenção |
| `--ambar-wash` | `#F6EEDC` | `#2A2317` | fundo de chip de atenção |
| `--terra` | `#B23A2B` | `#E0796A` | risco, negativo |
| `--terra-wash` | `#F7E6E3` | `#2B1A17` | fundo de chip negativo |

Sombra: `0 1px 2px rgba(26,34,48,.05), 0 8px 24px -16px rgba(26,34,48,.28)` no claro.

No one-page A4, que é só claro e vai para impressão, as cores entram direto no CSS do modelo
pelos mesmos valores: acento `#2F6F8F` para entregue, `#41557F` para em andamento, `#B07D1A`
para reuniões, `#B23A2B` para risco e `#6A539D` para a próxima semana. Os pares de cor das
pílulas ficam na skill `reporte-semana` e acompanham esta paleta; trocou o modelo, troque os
pares junto.

**Regra dura de tema.** Nunca defina uma cor só dentro de um bloco de media query. A paleta
clara mora no `:root` puro; o escuro apenas redefine. O `body` sempre recebe fundo explícito
por token, porque fundo transparente empresta o tema do hospedeiro.

## Tipografia

- **Fonte única:** Inter, pesos 400, 500, 600 e 700, para título, número de KPI e texto.
- Fallback obrigatório: `"Segoe UI", system-ui, sans-serif`. Sem acesso ao Google Fonts, a
  fonte do sistema assume e o documento continua legível.

O one-page A4 usa Archivo, porque o preset compacto de página única foi calibrado nessa
métrica. Trocar a fonte dele exige recalibrar e conferir que continua em `/Count 1`. Enquanto
isso não for feito, **a cor alinha e a tipografia não**.

## Componentes

| Classe | O que é |
|---|---|
| `.kpi` / `.kpis` | cartão de número grande com rótulo; variantes `.good`, `.warn` e `.alert` |
| `.chip` | selo de status: `.ok` · `.mid` · `.off` · `.bad` |
| `.callout` | bloco destacado; variantes `.warn` e `.crit` |
| `.finding` | achado, com número e texto |
| `.bar` / `.bars` | barra proporcional |
| `.eyebrow` | rótulo pequeno acima do título |
| `.tablewrap` | envelope com `overflow-x:auto` para tabela larga |
| `.note` / `.dim` / `.mut` | texto de apoio |
| `.quote` / `.why` | citação e justificativa |

## Regras de layout

- Toda tabela larga vive dentro de `.tablewrap`, com rolagem própria. A página nunca rola na
  horizontal.
- Unidade relativa, flexbox ou grid, e `max-width:100%` em imagem.
- No A4, a regra de ouro é caber em **uma página**. A primeira alavanca é o preset compacto
  (escala de fonte, espaçamento e padding), nunca cortar resultado.
- Documento que sai do time não leva nome de pessoa nem dado bruto. Exemplo em modelo é
  sempre fictício.

## Renderização de PDF

Edge headless, com os flags validados na skill `reporte-semana`. As pegadinhas que custaram
tempo e não podem ser esquecidas: use `--headless` clássico e nunca `--headless=new`, que
retorna sucesso sem gerar arquivo; use `--user-data-dir` próprio apontando para pasta
temporária, nunca para dentro do caderno; dê `--virtual-time-budget` para a fonte carregar; e
confira o arquivo em laço, porque a escrita é assíncrona e o processo retorna antes.

Valide sempre a assinatura `%PDF` e o `/Count` de páginas.
