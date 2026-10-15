---
name: modelagem-dados
description: Projeta e implementa a camada de dados de um dashboard Power BI — tabelas fato/dimensão/auxiliares em Power Query (M), grão, relacionamentos e star schema. Use em dashboards novos (greenfield) ou em manutenções que alterem a estrutura de dados/modelo. Frente PBI. NÃO use para demandas que só mexem em DAX ou visual.
---

# Skill: modelagem-dados (PBI — frente de autoria/estrutura)

Projeta a camada de dados seguindo o padrão de modelagem dimensional da casa.
Opera plano-primeiro: PROPÕE o desenho do modelo, você aprova, e SÓ ENTÃO escreve o M/estrutura.

## 0. Gate de relevância (faça ANTES de qualquer coisa)
Olhe o tipo/frente e o escopo definidos na análise da demanda (demandas/<TIPO>/DEM-XXX/contexto.md e plano.md).
- Se a demanda NÃO toca estrutura de dados / M (ex.: só criar/ajustar medida DAX, mover/colorir visual, ajuste de slicer), **declare-se fora de escopo e passe a vez** para `medidas-dax` / `montar-visuais`. Não force modelagem onde não cabe.
- Prossiga apenas se for: dashboard novo (greenfield) OU manutenção que cria/altera tabela, coluna de origem, relacionamento ou transformação em M.
Diga explicitamente qual caso identificou antes de seguir.

## 1. Classificação por PAPEL (o prefixo segue a decisão, não a substitui)
Critério objetivo (não decore prefixo, decida pelo papel no grafo de filtro):
- **Fact_**: você quer SOMAR/CONTAR. Lado many de todas as relações; contém colunas numéricas aditivas e as chaves estrangeiras; cresce com o tempo. (Fact_Proj_ para projeção/forecast.)
- **Dim_**: você quer FATIAR por ela. Lado one, chave única, não soma, volume estável; responde quem/o quê/quando.
- **Out_**: NÃO participa de relação nenhuma. Metadado/UI (ex.: timestamp de carga), consumida só por medida/cartão.
- **Bridge_**: mapeamento/ligação many-to-many.

Dimensão degenerada (regra importante): um atributo descritivo vira **coluna na própria fato** — NÃO uma Dim_ — a menos que (a) seja reutilizado por mais de uma fato, ou (b) precise de hierarquia/ordenação própria. Só então promova a Dim_.

## 2. Grão da fato (defina ANTES do SQL)
- Escreva o grão em UMA frase de negócio: "uma linha por X por Y" (ex.: "uma linha por item de pedido por produto por nota").
- Garanta que as chaves dessa frase estejam no SELECT; o grão é estabelecido no GROUP BY/WHERE da origem (visível e versionado no .tmdl).
- Medidas só podem ser aditivas nesse grão.

## 3. Origem das tabelas (VARIÁVEL — pergunte, não assuma)
A origem de cada tabela é decisão por demanda, não regra fixa. Fato, dimensão, bridge ou Out podem vir de Oracle, Synapse, Excel ou base manual no PBI — caso a caso.
- Ao montar o plano, pergunte/registre de onde vem CADA tabela.
- Regra que NÃO varia: servidor e data-corte SEMPRE via parâmetro (query group Parametros), nunca hard-coded.

## 4. Padrão de M (Power Query) — o coração
Uma query por tabela. Três passos nomeados em português, renomeação sempre por último:
```
let
    Fonte          = <origem>                                  // 1. ORIGEM
    TiposAjustados = Table.TransformColumnTypes(Fonte, {...})  // 2. TIPAGEM (nomes técnicos)
    Renomeadas     = Table.RenameColumns(TiposAjustados, {...})// 3. RENOMEAÇÃO -> nome de negócio
in
    Renomeadas
```
- Passos em português e descritivos (TiposAjustados, Renomeadas, Distintas, ColunasRemovidas) — nunca os #"Tipo Alterado" automáticos.
- Tipagem usa nome técnico; renomeação para nome de negócio é o ÚLTIMO passo.

### Fronteira SQL × M (a diretriz central)
**SQL-first para o que o SQL faz bem; M para o que é da camada M.**
- Empurre para a ORIGEM (SQL) toda transformação de CONJUNTO/VOLUME: filtro, join, agregação, CASE de regra de negócio, normalização. Isso folda e reduz volume.
- Reserve o M para: renomeação técnica -> nome de negócio, tipagem específica, e colunas derivadas complexas que não fariam sentido/manutenção no SQL.
- SMELL a evitar: lógica de conjunto (filtro/agregação) deixada no M que poderia foldar na origem.
- Quando a origem NÃO é SQL (Excel, base manual), o passo de Origem muda, mas a disciplina tipar -> renomear permanece.
- Princípio-mor: resolva o mais cedo (mais à esquerda) possível — origem > M > DAX.
- Registre rastreabilidade: comentário no SQL quando uma lógica migrou de M/DAX para a origem, ou quando corrige um bug.

## 5. Relacionamentos
- Estrela **single-direction** (dimensão 1 -> fato *). NUNCA bidirecional (evita ambiguidade/loop).
- *:1 implícito; só explicite cardinalidade quando fugir do padrão.
- Role-playing: relação **inativa** (isActive:false) + USERELATIONSHIP na medida.
- Out_: sem relação nenhuma (proposital).
- Many-to-many por grão grosso (ex.: Ano) para ligar duas dimensões sem fato-ponte, quando necessário.

## 6. Calendário e higiene (INVARIANTES — valem em todo dash)
- **Dim_Calendario SEMPRE gerada em M** (não vem do banco), com janela dinâmica (ex.: de pDataInicialCalendario até 31/dez do ano corrente). Traz Ano, Mes, Dia, NomeMes, ordenações com sortByColumn, etc.
- **Auto date/time DESLIGADO** (__PBI_TimeIntelligenceEnabled = 0) — regra fixa; não deve haver LocalDateTable_*.
- Query groups: Parametros (0) -> Tabelas Dimensao (1) -> Tabelas Fato (2). Out_ ficam sem grupo.

## 7. Anti-padrões que a skill PROÍBE em projeto novo (e sinaliza em manutenção)
- Relações `AutoDetected_*` — o grafo deve ser 100% intencional. Renomeie/recrie explicitamente e desligue autodetecção.
- `LocalDateTable_*` (auto date/time) — proibido.
- Passo morto / coluna calculada nunca usada — não deixar lixo no M nem no modelo.
- Filtro bidirecional sem justificativa.

## Saída e fluxo (plano-primeiro)
1. Confirme o gate (seção 0) e a origem de cada tabela (seção 3).
2. PROPONHA o `plano.md` de modelagem: lista de tabelas com papel (Fact_/Dim_/Out_/Bridge_), grão de cada fato em frase de negócio, origem de cada uma, relacionamentos (cardinalidade/direção), e o que será SQL vs M. **PARE para sua aprovação.**
3. Após aprovado, escreva o M/estrutura seguindo sec. 4–6, e registre em `demandas/<TIPO>/DEM-XXX/entrega.md` o que foi feito + a evidência.
4. Antes de fechar, rode a checagem da seção 7 e reporte qualquer anti-padrão encontrado.
5. Guardrail de load (o erro só aparece no Desktop): valide que o TMDL editado carrega sem erro de schema; descrição `///` é padrão da casa e NÃO quebra; comentário `//` em JSON companheiro quebra o parse. Coluna calculada é mais segura que mexer no M do partition (edição de M já derrubou o load antes). TMDL gravado por script sai com quebra de linha CRLF, como o Desktop grava, e só com o Desktop fechado.
