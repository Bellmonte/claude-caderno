---
name: validar-tela
description: Valida no navegador o que foi desenvolvido na frente APP (o hub de aplicações e seu assistente de ações), percorrendo o fluxo que a demanda alterou, lendo console e rede, e capturando a tela como evidência do GATE 2. Roda depois do `npm test` verde e antes do `publicar`. Frente APP. NÃO use para Power BI (a validação lá é o próprio Desktop) nem para fluxo de automação.
---

# Skill: validar-tela (evidência de tela no GATE 2)

O fecho da frente APP tinha um buraco: `npm test` prova que a função responde, e não que
a tela funciona. Bug de front, erro de console, chamada de API que volta 500 sem quebrar o
layout, campo que não aparece para um perfil, nada disso o teste unitário pega.

Esta skill fecha esse buraco usando o navegador que o Claude Code já controla. Não instala
nada.

## Quando roda

Depois do `npm test` verde, dentro do GATE 2, antes do `publicar`. Só nas demandas que
tocaram algo que o usuário vê ou clica: tela, componente, rota que a tela consome, resposta
de agente que é renderizada.

**Não roda** quando a demanda foi só de back sem efeito visível, quando é Power BI (lá a
validação é abrir o Desktop) e quando é fluxo de automação (lá quem valida é a checagem da
própria ferramenta de automação).

## Antes de abrir o navegador

1. **Leia o `entrega.md` da demanda** e liste o que mudou. A validação percorre o **delta**,
   não o app inteiro. Varredura completa é auditoria, e isso é papel do `auditor-app`.
2. **Suba o app local.** Descubra como: `package.json` do repositório da aplicação diz o script
   (`npm run dev` de praxe) e a porta sai do `PORT` do `.env` ou do default do server. Se o
   repositório tiver `.claude/launch.json`, use `preview_start` por nome; senão, crie a
   entrada com o comando e a porta reais antes de subir.
3. **Confirme que é ambiente local.** Se a URL não for `localhost`, PARE e pergunte. Nunca
   valide clicando em ambiente de produção: a tela da aplicação dispara ação real (refresh
   de dataset, envio de mensagem, gravação no banco).

## O que fazer na tela

Percorra o caminho que a demanda alterou, do jeito que o usuário faria. Para cada passo:

- **Leia a página pela árvore de acessibilidade** antes de clicar por coordenada. É mais
  confiável e sobrevive a mudança de layout.
- **Confira o console** depois de cada ação. Erro de console que não quebra a tela é o
  defeito mais fácil de passar batido, e é justamente o que o teste unitário não vê.
- **Confira a rede** nas ações que chamam API: status, e se o payload de erro está sendo
  tratado em vez de engolido.
- **Capture a tela** no estado final de cada fluxo validado.
- **Teste a largura pequena** quando a demanda mexeu em layout. O hub é usado em monitor
  de operação e em celular.

## Guarda-corpo

- **Nunca digite credencial.** Se a tela exigir login, peça ao usuário para autenticar e
  seguir dali, ou use a sessão já aberta.
- **Nunca clique no que é irreversível** sem perguntar: disparar refresh, enviar mensagem,
  aprovar, excluir. Se o fluxo alterado termina numa ação dessas, valide até a confirmação
  e pare na porta.
- **Dado que aparecer na tela é corporativo.** Print vai para `local/`, nunca para o
  registro; no `entrega.md` entra o caminho, não a imagem.

## O que registrar

No `entrega.md` da demanda, uma seção curta:

```
### Validação de tela (GATE 2)

**Fluxos percorridos:** <o que foi clicado, em ordem>
**Console:** limpo · ou o erro encontrado, com a mensagem
**Rede:** as chamadas do fluxo e o status de cada uma
**Larguras:** desktop · mobile (quando mexeu em layout)
**Evidência:** `local/<demanda>/tela-<fluxo>.png`
**Veredito:** passou · passou com ressalva (qual) · reprovou (o quê)
```

Reprovou não vira ressalva. Volta para o `desenvolver-app`, conserta, e valida de novo.

## Por que é o navegador do Claude Code e não Playwright

A capacidade já existe embutida: navegação, clique, digitação, leitura da árvore de
acessibilidade, console, rede, screenshot e emulação de largura. Instalar um MCP de
navegador acrescentaria manutenção e nenhuma capacidade.
