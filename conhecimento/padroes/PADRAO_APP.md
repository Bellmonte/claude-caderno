# Padrão APP — referência canônica (hub de aplicações e assistente de ações)

> Destilado do handoff técnico da aplicação: um hub interno de agentes de IA, telas e indicadores,
> em implementação contínua, que pode ter mais de um dev, e o motor app atende todos eles.
> A skill de desenvolvimento e o agente `auditor-app` apontam para cá. Esta referência resume; o
> CÓDIGO manda (ver §1). Decisões batidas marcadas com ✓. Nomes de arquivo, tabela e rota abaixo
> descrevem a arquitetura de referência; ajuste ao que o seu repositório tiver.

## 1. Princípio-zero: o código é a fonte da verdade
- ✓ O handoff e o `CLAUDE.md` do projeto da aplicação driftam do código com o tempo (exemplos típicos: agente registrado num backend no doc e rodando em outro no código; backend novo que o doc não cita; portões a mais no router; o doc ainda descrevendo um modelo de permissão já superado, como o RBAC por allowlist+roles trocado pelo perfil por departamento de §5). NUNCA decida pelo doc.
- Antes de propor ou tocar qualquer coisa: ABRA os arquivos reais do alvo (o "confronto técnico", análogo a ler o `.pbip` no PBI). Use o mapa da §3 para achar onde olhar.
- O handoff serve de mapa e de playbook; a verdade é o estado atual dos arquivos no repo.

## 2. Natureza da demanda — classifique antes de agir (a abordagem muda)
- ✓ Toda demanda do motor app cai em um de quatro tipos. Declare qual antes do plano.
- **Bug** (quebrou / erro): reproduzir → isolar a causa no código real → corrigir o mínimo → teste que cobre o caso.
- **Divergência de resultado** (funciona, mas o número/saída está diferente do esperado): NÃO assuma bug. Confirme qual é o resultado correto e a evidência; rastreie a trilha de dados/lógica (rota → service → store → view/origem); a causa pode estar fora do app (→ §9 fronteira).
- **Recurso novo**: ver se casa com um playbook conhecido (§8); se casar, é scaffolding guiado; se não, desenho do zero confrontando a arquitetura (§4).
- **Alteração** (mudar recurso existente): mapear o ripple (quem consome o que vai mudar: rota, store, front, agente, teste) antes de mexer.

## 3. Mapa de onde mexer (arquitetura de referência)
| Quero… | Mexo em… |
|---|---|
| Roteamento de chat / registrar handler | `server/services/agentRouter.js` |
| Loop Claude+tools | `server/services/agents/_core/agenticLoop.js` |
| Assistente geral (web/code exec) | `server/services/agents/_core/anthropicEngine.js` |
| Persona de agente de dados | `server/services/agents/<nome>Agent.js` |
| Registro de agentes | `server/config/agents.json` |
| Tools de Power BI e de outras fontes | `server/services/agents/tools/` |
| Auth / JWT / Entra | `server/middleware/auth.js`, `server/routes/auth.js` |
| Rate limit / token | `server/middleware/rateLimiter.js` |
| Persistência | `server/services/db*Store.js`, `db.js` |
| Indicadores ao vivo | `server/services/dashboard*.js`, `routes/dashboard.js`, `frontend/js/dashboard.js` |
| Jobs agendados | `server/jobs/scheduler.js` e um arquivo por job |
| Frontend chat/agentes | `frontend/js/chat.js`, `agents.js`, `conversations.js`, `api.js` |
| Admin (front) | `frontend/js/admin-*.js` |
| Ação do assistente | `server/services/agents/assistente/commands/<nome>/` + `registry.js` |
| Testes | `server/test/*.test.js` (rodar `npm test`) |

## 4. Arquitetura essencial (o que confrontar)
- **Stack:** SPA HTML/CSS/JS puro (sem framework) + Node/Express como BFF/API Gateway + banco relacional (ex.: Oracle). LLM = Claude (`@anthropic-ai/sdk`). Node 20+ e o client nativo do banco quando o driver exigir.
- **Fluxo de chat:** `POST /api/chat {agentId, message, history}` → valida JWT → rate limit de token → `agentRouter.routeToAgent()` (valida `agentId` na whitelist, checa permissão, injeta instruções pessoais) → despacha por `agent.backend` → (se agentic) loop Claude+tools com SSE → grava em `APP_MENSAGENS` + audita + contabiliza tokens.
- **Backends:** `anthropic` (assistente geral), `powerbi-mcp` (personas via `agenticLoop`), `assistente` (comandos `./acao`), `automacao` (proxy para a ferramenta de automação), `coming-soon` (mensagem estática).
- **Multi-container (canal de mensageria, ex.: WhatsApp):** o conector do canal é um microsserviço IRMÃO = **transporte burro** (só fala/ouve o canal; ZERO IA, ZERO chave). Toda IA/chave/formatação fica na aplicação. Trocar o provedor do canal (biblioteca não oficial × API oficial) mexe só nesse container. A aplicação recebe em `/api/<canal>/inbound` e converte os eventos de interface rica (cards) em texto por um renderizador server-side, porque no canal não há card. Use um número dedicado, não o oficial da empresa.
- **`agentRouter.js`:** whitelist `AGENT_IDS_VALIDOS` do `agents.json` no boot; `POWERBI_HANDLERS` é **mapa estático** (registrar agente = import + entrada no mapa — NUNCA `require` dinâmico); restrição por e-mail, permissão e `defaultForNewUser`.
- **`agenticLoop.js`:** modelo por `deepAnalysis` (Opus×Sonnet); system prompt em 2 blocos (estável cacheado × dinâmico com data/instrução); histórico truncado (ex.: 6 trocas no agentic / 20 no assistente geral); tools em 3 fases (anuncia em ordem → roda em paralelo `Promise.all` → monta results na mesma ordem com `cache_control`); resultado de consulta (`ExecuteQuery`) truncado (ex.: 30000 chars); tools interceptadas (`solicitar_esclarecimento`, `registrar_raciocinio`) não vão à API.
- **Personas (`powerbi-mcp`):** cada uma é `<nome>Agent.js` com `SYSTEM_PROMPT` + array de tools + delega a `runAgenticLoop`. Agente que calcula valor de negócio sensível (preço, juro, imposto) é caso especial: orquestrador stateful que fala com o ERP, e o Claude NUNCA calcula, sempre via tool.
- **Assistente de ações (`assistente/`):** ação conversacional em andamento → comando `./acao` → conversa livre. `commands/registry.js` = array estático `MODULOS`. Cada ação = pasta `commands/<nome>/` com `index.js` (`{name, type, handle|run}`) + engine/prompt/schema. Para o conteúdo do prompt da ação, ver `PADRAO_PROMPT_AGENTE.md`.

## 5. Segurança (DURA — inegociável; é o eixo onde o auditor pesa mais)
- ✓ NUNCA escrever segredo/token/connection string em código NEM em resposta. Placeholder `<TOKEN>`. Segredos vêm do `.env`.
- ✓ NUNCA `git add -A` cego — listar staged e farejar segredo/dado bruto. Dado corporativo/PII fora do git (LGPD).
- `agentId` sempre validado contra whitelist; handlers em **mapa estático** (anti path-traversal).
- SQL só com **bind variables** (`:1`, `:nome`) — nunca concatenar. Interpolação só contra **whitelist** de views/colunas (ver `dashboardIndicadorBase.js`).
- RBAC (modelo de referência — perfil por departamento): a autorização fina pós-login é governada por **perfil = DEPARTAMENTO** (vindo do diretório, ex.: Graph API), em **3 dimensões** — Agentes · Telas · Bases (`server/config/acesso.js` = catálogos fixos). Permissão do depto em `APP_PERFIS` (1 linha/depto, JSON), override individual em `APP_USUARIOS.ACESSO_OVERRIDE` (`true` libera / `false` revoga mesmo herdado), depto em `APP_USUARIOS.DEPARTAMENTO`. Baseline aberto a todos salvo revogação (as telas de uso geral + a base de produção); telas sensíveis (ex.: painel de gestão, políticas) ficam gated. Resolução por uma função única na store de acesso (`resolverAcessoUsuario`); `middleware/acesso.js exigirTela(key)` gateia rota por tela; o endpoint do usuário logado (`me.js`) degrada LIBERANDO (não esconde por falha de DB). O antigo modelo de papel/permissão de agente avulsa por usuário foi SUPERADO — não raciocine mais por ele. Admin protegido não pode ser removido (anti-lockout).
- Prompt injection: instrução do usuário entra em bloco que **não** sobrescreve regra/segurança.
- **Canal de ingresso sem JWT** (molde do canal de mensageria, `routes/<canal>.js`): é a superfície pública do projeto. Quando uma rota não tem JWT, a segurança é em camadas obrigatórias: **segredo compartilhado** (header próprio, ex.: `X-Canal-Secret`; rota responde 503 se o segredo não estiver setado) + **allowlist** (ex.: tabela `APP_CANAL_ALLOWLIST` por telefone) + **rate limit pela identidade do canal** (telefone, não IP, porque tudo vem do mesmo container) + limite diário de token fail-secure + **usuário sintético** (`{id:'<canal>:'+tel, roles:['user']}`) + a rota só existir na rede interna do Docker. No `agentRouter`, `canal` ('web'|'<canal>') no `routeToAgent`; no canal não-web o acesso já foi gated pela allowlist, então pula a checagem de tela/perfil. Tratar QUALQUER mexida em rota sem JWT com cuidado redobrado.
- Em prod, garantir `SESSION_JWT_SECRET` (não cair no `DEV_JWT_SECRET`). Token Entra nunca vai pro cookie; roles vêm da própria aplicação (allowlist no banco), não do Azure.

## 6. Custo / latência de token (LLM)
- Manter o split do system prompt: estável (persona+datasets, **cacheado**) × dinâmico (data de hoje + instrução do usuário, fora do cache).
- Não inflar histórico nem despejar tabela gigante no contexto (truncar; refinar a query/DAX antes).
- `cache_control` no schema/tools. Medir tokens (input + output + cache_read + cache_write).
- Reuso de container de code-execution entre iterações (uma store persiste o `container_id`).

## 7. Persistência no banco
- Módulo de conexão (`db.js`): pool (ex.: 2–10), `autoCommit:true`, CLOB→string/BLOB→Buffer automático; `executar()` e `executarTransacao()` (rollback em erro). **Sempre bind variables.**
- Tabelas `APP_*`: as ORIGINAIS podem ser auto-criadas no 1º uso (`ensureSchema()` em cada store). **MAS isso não vale para todas** — tabelas e colunas recentes (perfis, feedback, logs, `ALTER` em tabela existente) exigem **DDL manual** (script versionado, rodado antes de subir em ambiente novo). Ao criar tabela/coluna nova, o default RECOMENDADO é **DDL versionado em script** (rastreável/seguro) — mas o motor PERGUNTA antes (versionado × auto-criação no boot) e só segue após o OK do usuário; e sempre avisa que ambiente novo precisa rodar o script. Uma store por domínio (`db*Store.js`).
- Views de indicador ao vivo: prefixo próprio (ex.: `VW_INDICADOR_*`). `dashboardIndicadorBase.js` tem whitelist de views/colunas antes de interpolar — respeitar.
- **Regra do dono dos indicadores:** card mostra o valor BRUTO da query (não multiplicar/escalar); % financeiro 4 casas, operacional 2 casas.

## 8. Playbooks de scaffolding (receita quando o "novo" casa com padrão conhecido)
- **A) Agente novo (Power BI):** `<nome>Agent.js` espelhando um agente de dados existente → registrar em `POWERBI_HANDLERS` (`agentRouter.js`) → entrada em `agents.json` (`backend`, `handler`, `datasets[]` com name/artifactId/description, permissão, `welcomeMessage`, `suggestions`) → prewarm pega os artifactId → rodar `agent-router.test.js`.
- **B) Agente de automação / coming-soon:** só entrada em `agents.json` (automação: com `endpoint`; coming-soon: `online:false` + `welcomeMessage`).
- **C) Ação do assistente:** pasta `commands/<nome>/` + `index.js` + registrar no `registry.js`. Prompt segue `PADRAO_PROMPT_AGENTE.md`.
- **D) Indicador ao vivo:** view/coluna na whitelist de `dashboardIndicadorBase.js` → `dashboard<Nome>.js` (expressão SQL) → rota em `routes/dashboard.js` → card em `frontend/js/dashboard.js` (`DASHBOARD_LIVE_INDICATORS`).
- **E) CRUD de admin:** `routes/admin-*.js` (adminMiddleware) → `db*Store.js` (com `ensureSchema`) → tela no front.
- **F) Plugar dataset novo num agente:** objeto em `datasets[]` do agente no `agents.json` (precisa do `artifactId` correto).
- **G) Ajuste de UX/texto/ícone:** baixo risco; sincronizar dark mode em todas as telas; não quebrar SSE/typewriter.
- **H) Modelo / limite de token:** variáveis de modelo (ex.: `ANTHROPIC_MODEL`, uma por uso) no `.env`; `deepAnalysis` decide Opus×Sonnet.
- **I) Novo canal de ingresso** (molde do canal de mensageria): rota sem JWT + segredo compartilhado + allowlist + rate limit pela identidade do canal + usuário sintético + `canal` no `routeToAgent` + renderizador server-side dos eventos de interface rica (não há card fora do front). Transporte é um container irmão burro (ver §4). Segurança: ver §5 "canal de ingresso sem JWT".
- **J) Gerir acesso** (modelo vigente): NÃO é mais permissão de agente avulsa por usuário. É editar o **perfil do departamento** (`APP_PERFIS`, dimensões Agentes/Telas/Bases) ou o **override individual** (`APP_USUARIOS.ACESSO_OVERRIDE`). Via `routes/admin-acesso.js` + as telas de admin de acesso.

## 9. Fronteira com os outros motores
- ✓ O motor **app PARA no Node/JS/front/api**. A view de indicador e qualquer procedure/PL-SQL de origem são do motor **sql** — o app só CONSOME (e respeita a whitelist).
- ✓ O fluxo de automação em si (nós, lógica do workflow) é do motor **automacao**. No app, a ferramenta de automação é só proxy + entrada no `agents.json`.
- Quando a demanda atravessa a fronteira, registrar a DEPENDÊNCIA explicitamente e sinalizar qual motor resolve a outra ponta (não "fingir" que resolve sozinho).

## 10. Fecho da esteira (modo app — difere do PBI)
- ✓ GATE 2 = validação LOCAL por quem desenvolveu (subir a aplicação + rodar `npm test`) ANTES de qualquer push. `npm test` VERDE é gate: não commita se vermelho.
- ✓ **Fluxo de duas etapas: valida na branch de homologação, promove para a `main` por cherry-pick.** Nos exemplos abaixo a branch de homologação se chama `develop`; troque pelo nome que o seu repositório usa.

  **Etapa 1 — desenvolver e validar.** Branch de feature tirada da **`develop`**, altera, sobe, PR para `develop`, merge e validação em homologação. Nada vai para a `main` antes de rodar em homologação.

  ```bash
  git fetch origin
  git checkout -b <tipo>/<slug> origin/develop
  # ... altera, npm test verde, commita ...
  git push -u origin <tipo>/<slug>          # PR com base develop
  ```

  **Etapa 2 — promover só o que foi validado.** Branch nova tirada da **`main`** e cherry-pick APENAS dos commits daquela alteração. Nome da branch = o da etapa 1 com sufixo `-main` (ex.: `feat/ajusta-nome-agente-main`).

  ```bash
  git checkout -b <tipo>/<slug>-main origin/main
  git cherry-pick <sha1> <sha2>             # só os commits da alteração
  git push -u origin <tipo>/<slug>-main     # PR com base main
  ```

  **Por que cherry-pick e não PR de `develop` para `main`.** A `develop` é integração compartilhada e acumula trabalho de várias pessoas; ela costuma viver dezenas de commits à frente da `main`. Um PR `develop` -> `main` arrastaria tudo o que estiver lá dentro, validado ou não, junto com a sua alteração. O cherry-pick leva só o que passou em homologação, e a `main` recebe uma mudança por vez, rastreável.

  **Antes de empurrar a branch `-main`, rode a suíte nela.** Passar na `develop` não garante passar na `main`: são bases diferentes, e os arquivos que você tocou podem ter divergido entre as duas. Se o cherry-pick der conflito, é aí que ele aparece. Confira também `git log origin/main..HEAD` (só os seus commits) e `git diff --stat origin/main` (só os seus arquivos), para garantir que nada da `develop` veio de carona.

  - A `main` é PROTEGIDA: push direto é rejeitado com `GH013` ("Changes must be made through a pull request"). O merge final é de quem responde pelo repositório, nunca do Claude.
- Antes do commit: listar staged, farejar segredo/dado bruto (§5), NUNCA `git add -A` cego. Mensagem = título conventional commit (ASCII) + corpo curto em linguagem de negócio; sem coautor Claude. O caderno (registro) é commitado à parte, por tarefa.
- Documentação da entrega: `fechar-demanda`, escrevendo para público de NEGÓCIO — objetivo, sem floreios, com o rastreio técnico compacto no rodapé. Não pressuponha chamado: aqui a origem é alinhamento de gestão ou item de cronograma, e o texto tem que fazer sentido para quem não é dev.
