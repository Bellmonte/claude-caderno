# PADRÃO_SLA: régua de prazo, esforço, complexidade e risco

> A lei do cabeçalho de fechamento. Mora aqui, fora da skill, para poder ser consultada
> sozinha e valer em qualquer trilho. Quem escreve fechamento **calcula por aqui e não chuta**.

## Sprint

Duas por mês, no formato `SPRINT_<1|2> - <MMM>/<AA>` (ex.: `SPRINT_1 - JUL/26`). É a
cadência que o caderno traz de fábrica; se o seu time usa outra, troque as regras abaixo e o
rodapé do [[fechamento-chamado]] junto.

- **SPRINT_1:** dia 1 ao 15. Prazo = dia 15.
- **SPRINT_2:** dia 16 ao fim do mês. Prazo = último dia útil do mês.
- Primeiro dia útil da sprint = primeiro dia útil `>= 1` (S1) ou `>= 16` (S2).

Não existe data mínima. Trabalha-se com data máxima a cumprir.

## Datas

Tudo em dias úteis, de segunda a sexta. Feriado não conta; havendo feriado no intervalo,
marque "aprox.".

- **Data de criação:** a do chamado em atendimento (campo `Chamado aberto em`), nunca a do
  pai ou do épico vinculado, e **nunca** a data em que a pasta nasceu no caderno. As duas
  divergem sempre que o chamado é versionado depois, e tratar uma pela outra infla a contagem
  de entregas do dia.
- **Entrada no caderno:** o dia em que a pasta foi criada (campo `Entrou no caderno em`). Não
  entra em nenhum cálculo de SLA, esforço ou sprint. Existe para separar trabalho do dia de
  registro tardio.
- **Início previsto** = `max(primeiro dia útil da sprint, data de criação)`.
- **Início real** = o campo `Trabalho iniciado em` da demanda. Sem isso, o que o usuário
  informar; sem isso, a data do primeiro commit do resumo; sem isso, `—`.
- **Entrega** = a data do fechamento (hoje) ou a do último commit. Sem desenvolvimento,
  `—` e SLA "Em andamento".
- **Esforço** = dias úteis de início real até entrega, inclusive. Faltando uma ponta, `—`.
  Atenção: quando o início real vem do primeiro commit e o hábito é comitar só no fim, o
  esforço sai subestimado. Prefira a data real.

Com o log automático ligado (`diario/.log/`), o início real e a entrega saem do próprio log:
o primeiro e o último dia com ação registrada naquela demanda. Use o log antes de perguntar.

## SLA (entrega contra prazo, em dias úteis)

- Entrega `<=` prazo → **Dentro do prazo**, com folga de N dias úteis.
- Entrega `>` prazo → **Em atraso**, com N dias úteis de atraso.
- Sem entrega → **Em andamento**, com N dias úteis de runway, ou "prazo estourado".

## Complexidade

- **Baixa:** ajuste isolado e reversível, em um ambiente só.
- **Média:** mudanças contidas no report (DAX, Power Query, visual com lógica), um ou dois
  ambientes.
- **Alta:** mudança estrutural (modelo semântico, base, banco, plataforma de dados), múltiplos
  ambientes, objeto novo do zero, refatoração (topo da escala).

## Risco

`Risco = Complexidade × Pressão de prazo × Estado de validação`.

Pressão, em dias úteis inclusive, de início real (ou previsto) até o prazo:
`>= 6` baixa · `3 a 5` média · `<= 2` alta.

| Complexidade ↓ / Pressão → | Baixa | Média | Alta |
|---|---|---|---|
| Baixa | Baixo | Baixo | Médio |
| Média | Baixo | Médio | Alto |
| Alta | Médio | Alto | Alto |

- **Modificador:** sobe um nível se foi aplicado direto em produção, sem homologação.
- **Validação:** chamado validado e encerrado pelo solicitante não soma o modificador, mas
  mantém o risco-base.
- **Teto:** sem alteração em produção (verificação, no-op) ou mudança trivial e reversível,
  o risco fica no máximo Baixo.
- **Agravante de esforço:** esforço curto demais para a complexidade (objeto novo ou
  refatoração em um ou dois dias) eleva o risco mesmo com pressão baixa.

Saída: o rótulo mais uma linha de justificativa citando os fatores que pesaram.

## Tipo (prefixo do título)

`feat` (novo) · `fix` (correção) · `refactor` (reestrutura sem mudar resultado) ·
`style` (visual) · `docs` · `chore` (config/metadados) · `verif` (investigação no-op).

Formato: `tipo: descrição curta`, no máximo 40 caracteres.

## Como ler o cabeçalho (rodapé fixo dos documentos)

**Complexidade** = ambientes envolvidos + porte da alteração · Baixa · Média · Alta
**Risco** = Complexidade × tempo até o prazo × validação
**SLA** = entrega contra o prazo da sprint (S1 → dia 15 · S2 → último dia útil do mês), em dias úteis.
