---
name: desenvolver-app
description: Executa o desenvolvimento de uma demanda da frente APP (o hub de aplicações e seu assistente de ações) no plano JÁ APROVADO — mexe em front (HTML/CSS/JS), back (Node/Express), API, agentes e ações do assistente. Cobre bug, divergência de resultado, recurso novo e alteração. Frente APP. NÃO use para view/procedure de banco (motor sql) nem para o fluxo de automação em si (motor automacao); NÃO use para PBI.
---

> DESTINO: todo arquivo de REGISTRO (demandas/, diario/, conhecimento/, reunioes/, entregas/) é criado na RAIZ DO CADERNO (o caderno adicionado à sessão), NUNCA no repo de trabalho. O CÓDIGO/artefato da entrega vai no REPO DE TRABALHO (o da aplicação). Se o caderno não estiver na sessão, pare e peça para adicioná-lo. Ver CLAUDE.md > "Onde cada coisa mora".

# Skill: desenvolver-app (motor APP — executor)

É o "dev sênior full-stack braçal": pega o plano aprovado, mergulha no código REAL e executa.
A análise profunda e o GATE 1 já aconteceram no `analisar-especificacao`; esta skill EXECUTA.
Referências canônicas: `conhecimento/padroes/PADRAO_APP.md` (arquitetura, segurança, token, playbooks, fronteira) e, ao tocar o coração de um agente/ação, `conhecimento/padroes/PADRAO_PROMPT_AGENTE.md`. CONSULTE antes de escrever. Estas referências mandam; a skill resume.

## 0. Gate de relevância (ANTES de tudo)
Olhe o `plano.md`/`contexto.md`: frente e objeto afetado. A skill AGE quando a demanda toca o codebase da aplicação — front (`frontend/`), back (`server/`), API/rotas, agente (`<nome>Agent.js` / `agents.json`) ou ação do assistente (`commands/`).
A skill PASSA A VEZ quando:
- é exclusivamente view/procedure/PL-SQL de origem → motor **sql** (o app só consome);
- é exclusivamente o fluxo de automação (nós/lógica do workflow) → motor **automacao** (no app, a ferramenta de automação é só proxy + entrada no `agents.json`);
- é PBI → motor PBI.
Demanda que ATRAVESSA a fronteira: execute a parte do app e registre a DEPENDÊNCIA explícita do outro motor — não finja resolver a outra ponta. Declare o caso identificado antes de seguir.

## 1. Princípio-zero: o código manda
O handoff/`CLAUDE.md` do projeto da aplicação tende a driftar do código (PADRAO_APP §1). Antes de escrever, ABRA os arquivos reais que vai tocar (use o mapa "onde mexer", PADRAO_APP §3) e confirme que a realidade bate com o plano. Se divergir do plano (ex.: o bug não está onde o plano supôs), PARE e realinhe — não force o plano errado.

## 2. Executar conforme a NATUREZA (já classificada no plano)
- **Bug:** reproduza → isole a causa no código real → corrija o MÍNIMO → escreva/estenda o teste que cobre o caso (`server/test/`).
- **Divergência de resultado:** confirme qual é o resultado correto e a evidência; rastreie a trilha (rota → service → store → view/origem). A causa pode estar FORA do app → registre dependência e ceda a ponta (§0). Não "ajuste" número sem achar a causa.
- **Recurso novo:** se casa com um playbook (PADRAO_APP §8 A–J), siga a receita de scaffolding; senão, implemente confrontando a arquitetura (§4 do PADRAO).
- **Alteração:** mapeie o ripple (quem consome o que vai mudar: rota, store, front, agente, teste) ANTES de mexer.

## 3. Regras duras que entram em TODA execução (de PADRAO_APP)
- **Segurança:** segredo só `.env`/`<TOKEN>` (nunca em código/resposta); SQL só com bind variables; interpolação só contra whitelist de view/coluna; `agentId` na whitelist + handler em mapa estático (anti path-traversal); permissão pelo modelo vigente (perfil por departamento em Agentes/Telas/Bases + override individual — NÃO mais papel ou permissão de agente avulsa por usuário; ver PADRAO_APP §5); admin protegido não é removível; instrução do usuário não sobrescreve regra (anti prompt-injection); rota sem JWT só com o molde de canal de ingresso (segredo+allowlist+rate limit por identidade — PADRAO_APP §5).
- **Token:** manter o split do system prompt (estável cacheado × dinâmico); não inflar histórico nem despejar tabela gigante; `cache_control` no schema.
- **Agente/ação:** ao mexer no `SYSTEM_PROMPT` ou criar ação `./acao`, siga `PADRAO_PROMPT_AGENTE.md` (esqueleto, analise-primeiro, regra de ouro, linguagem por público, saída fixada, tool gating).
- **Indicador ao vivo:** valor BRUTO da query (não escalar); % financeiro 4 casas, operacional 2.

## 4. Onde cada coisa é gravada
- **Código/artefato** (`.js`, `.html`, `.css`, `.json` de config, prompt da ação, teste) → no REPO DE TRABALHO (o da aplicação). É o único lugar que recebe entrega.
- **Registro** (`entrega.md` e qualquer atualização de demanda) → na RAIZ DO CADERNO, em `demandas/<TIPO>/DEM_<COD>/`.

## Saída e fluxo (plano-primeiro com gate granular)
1. Confirme o gate (§0) e a natureza (§2).
2. Releia os arquivos reais do alvo (§1). Se a execução tiver decisões abertas que o plano não fixou (qual arquivo/abordagem entre opções, contrato de uma tool, formato de uma resposta de agente), PROPONHA a micro-decisão e PARE para o OK — não crave sozinho (gate granular, como o `montar-visuais`). **Tabela/coluna nova no banco:** o default recomendado é DDL versionado em script, mas PERGUNTE antes (versionado × auto-criação no boot) e avise que ambiente novo precisa rodar o script (PADRAO_APP §7).
3. Implemente no repo de trabalho seguindo §2/§3. Ações de agente/prompt: aplique `PADRAO_PROMPT_AGENTE.md`.
4. Escreva/estenda o teste pertinente em `server/test/`. (O `npm test` verde é gate de fecho — roda no GATE 2 / `publicar`, mas o teste nasce aqui.)
5. Registre `entrega.md` no caderno: o que foi feito, arquivos tocados (front/back/api), natureza, regras de segurança/token aplicadas, teste criado/rodado, e qualquer dependência cedida a outro motor.
6. Antes de fechar, cheque os antipadrões do PADRAO_APP (segredo em código, SQL concatenado, `require` dinâmico de handler, prompt sem split de cache, número "ajustado" sem causa) e reporte. NÃO commita — isso é o `publicar` (modo app), após o GATE 2.
