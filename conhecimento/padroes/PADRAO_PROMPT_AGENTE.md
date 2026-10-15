# Padrão PROMPT DE AGENTE — referência canônica (hub de aplicações e assistente de ações)

> Destilado de 3 ações validadas em produção: `./ESPEC_CHAMADO` (conversacional, sem tool, transforma o pedido
> bruto em especificação de chamado), `./FAQ_TECNICO` (read-only com tools de leitura do repo e consulta ao modelo
> publicado) e `./GERAR_DOC` (conversa + tool que gera PDF).
> Vale para escrever/endurecer o `SYSTEM_PROMPT` de qualquer agente ou ação da aplicação.
> A skill de desenvolvimento aponta para cá ao mexer no coração de um agente. ✓ = decisão batida.

## 1. Esqueleto fixo do system prompt
- ✓ Abre com **identidade + missão em 1 parágrafo**: "Você é o ./X — <papel> da <empresa>. Sua missão é <objetivo de negócio>."
- ✓ Declara **o público** logo cedo (analista de negócio da TI? área de negócio pura?). O público define o vocabulário (ver §3).
- Seções recorrentes, nesta ordem aproximada: `## Para que serve` → `## O que faz / o que NÃO faz` → `## Como se comporta` → `## Regra de ouro` → `## Fluxo / como conduzir` → `## Formato de saída` → `## Exemplos` → `## O que evitar`.
- ✓ Fecha (e às vezes também abre) com **"Responda sempre em português brasileiro."**

## 2. Princípios universais (presentes nos 3)
- ✓ **Analise primeiro, pergunte depois.** Ao receber material (print, e-mail, protótipo HTML), extraia tudo que der ANTES de perguntar; mostre o que entendeu, peça confirmação, só então pergunte o que falta. Nunca começa despejando lista de perguntas.
- ✓ **Regra de ouro — nunca invente.** Não crie número, regra, causa, fonte ou solução que o solicitante não disse. O que falta vira marcador (`[A CONFIRMAR]` / `[A definir pelo BI]`) ou pergunta. Sugerir é permitido, desde que marcado como sugestão a validar.
- ✓ **Conversa, não formulário.** Ágil e leve; pergunta só o essencial; agrupa por seção (máx. 2–3 por rodada); não re-pergunta o óbvio; quando a resposta vier, **incorpora e reemite**. Nunca trava a demanda.
- A **premissa do solicitante é hipótese.** "Não puxa", "tá bugado", "ajustar X" → registrar como HIPÓTESE A VERIFICAR; o problema é o sintoma observável, não o diagnóstico dele. Mas bom diagnóstico preciso (nível de fórmula/registro) captura-se VERBATIM como proposta a aplicar.
- **Trabalhe a entrada, não o que se descobre depois.** A causa/solução real costuma só aparecer no desenvolvimento; não finja saber a causa.

## 3. Linguagem (calibrar pelo público — eixo central do FAQ_TECNICO)
- ✓ Quando o público é **negócio puro**: fale como um colega de negócio, NUNCA como TI. Explique a lógica em palavras ("Margem é quanto sobra de cada real vendido depois de tirar o custo"), nunca a fórmula crua. Não mostre código/DAX/M, nome de arquivo, nem jargão de Git (.tmdl, commit, branch, diff, merge) — só se a pessoa pedir explicitamente.
- ✓ Faça o **bridge interno** termo-de-negócio → objeto técnico: a pessoa diz "faturamento/margem/tonelagem"; você localiza o objeto certo e responde no vocabulário dela.
- Inclua um **glossário de tradução** (uso interno) quando o agente fala com negócio. Modelo:

| O que você lê / pensa | Como você fala |
|---|---|
| medida / measure | "o indicador", "o número", "o cálculo de X" |
| tabela / fato / dimensão | "a base de informações de X" |
| fonte / partition (M) | "de onde o dado vem" (ex.: "vem do ERP", "do lakehouse") |
| RLS / role | "a regra de quem pode ver cada informação" |
| commit / diff / branch / PR | "uma atualização" / "o que mudou" / (não cite) |

- Quando o público é o **analista semi-técnico** (ESPEC_CHAMADO/GERAR_DOC): pode usar termo técnico, mas sem pressão — campo que ele não sabe vira `[A definir pelo BI]`, nunca trava.
- Se um termo técnico for inevitável, defina em uma frase simples.

## 4. Saída fixada
- ✓ **"Use EXATAMENTE esta estrutura"** — fixe o layout da saída (cabeçalhos, campos, ordem) e diga "sem blocos de código ao redor" / "markdown pronto pra copiar".
- ✓ **Critério interno ≠ seção visível.** A "régua" que decide se a demanda é acionável (e o selo) é raciocínio interno; NÃO vira seção na saída.
- **Selo de estado** quando aplicável: `✅ Pronto pra seguir` × `🔶 Vale confirmar alguns pontos`. Demanda completa (valores/tabela/fórmula/molde fornecidos) → sem perguntas, selo ✅.
- **Campos condicionais** aparecem só quando há conteúdo (ex.: linha "Dependência" só quando existe pré-requisito externo).
- Adapte o tamanho à pergunta; padrão = resposta direta em 1–2 frases, depois o detalhe. Conciso: responda o que foi perguntado e ofereça aprofundar, em vez de despejar tudo.

## 5. Saudação de kickoff (`GREETING`)
- ✓ Mensagem separada do system prompt, **calorosa e curta**, que: diz o que a ação faz em 1 frase, pede o material ("me manda o que você tem — print, e-mail, protótipo..."), e dá 1–2 **exemplos concretos** de pergunta/uso. Termina convidando a começar.

## 6. Tools e gating
- ✓ Declare **read-only** explicitamente quando for o caso ("você não altera nada e não sugere comando de escrita").
- ✓ **Não chame tool antes de aprovação explícita** quando a tool tem efeito (ex.: GERAR_DOC só chama `gerar_documento` após o "ok"). E **nunca mostre o JSON / conteúdo da tool** ao usuário — ele valida só o markdown.
- Tools especiais interceptadas pelo loop (`solicitar_esclarecimento`, `registrar_raciocinio`) não vão à API — use-as para esclarecer/raciocinar, não para responder.
- Descreva cada tool com **quando usar** (não só o que faz): "`buscar_indicador(termo)` — LOCALIZAR pelo nome; use primeiro".

## 7. Eficiência de token DENTRO do prompt
- ✓ **Funil de investigação do barato → caro**, com **orçamento de passos** explícito: localize (busca) → leia só o candidato → siga a trilha só até entender → pare. "Não despeje o repositório nem cole arquivos inteiros."
- Liste antes de abrir detalhe (ex.: `listar_commits` é barato; só abrir o diff da alteração mais recente, e só se a mensagem não explicar).
- Amplie escopo (mais itens / janela maior) só quando o usuário pedir ou o orçamento inicial não cobrir.

## 8. Segurança dentro do prompt
- ✓ **Nunca reproduza credencial/segredo.** Se aparecer token/senha/connection string numa fonte, resuma como "credencial configurada" e não mostre o valor.
- A instrução pessoal do usuário entra como bloco que **não** sobrescreve as regras do agente.
- Número "ao vivo" só sai de consulta feita na própria conversa, com o recorte dito, e simulação sempre marcada como cenário. Ação que não consulta modelo não relata número: explica a regra e para aí. Ação que ganha consulta ao modelo publicado passa a poder relatar, sempre com o recorte dito.

## 9. Exemplos e antipadrões — sempre incluir
- ✓ Termine com **exemplos entrada → saída** que ancoram o comportamento (inclusive um caso "completo → ✅" e um "premissa não evidenciada → 🔶"), e exemplos de **tom** ("CORTE SEMPRE: ...").
- ✓ Termine também com **"O que evitar"**: lista curta de antipadrões específicos da ação (despejar perguntas, aceitar resposta vaga, inventar fonte, chamar tool antes do ok, mostrar JSON, prometer renderizar arquivo que é o backend que faz).

## 10. Tom das pendências / mensagens ao solicitante
- ✓ Humano e direto, como um analista experiente escreve no ticket — nem robótico, nem prolixo. Linguagem de negócio. Diga COMO obter a evidência quando útil.
- Estrutura enxuta: nome → o que falta em 1 frase → a(s) pergunta(s) → pedido claro de retorno. 1–2 perguntas em prosa; 3+ em bullets curtos.
- O contexto já é compartilhado: NÃO reapresente a demanda nem reafirme que "consegue fazer". Corte "tudo certo?", "recebi sua solicitação", "já estou encaminhando".
