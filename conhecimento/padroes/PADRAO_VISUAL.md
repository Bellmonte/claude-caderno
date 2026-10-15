# Padrão Visual: porta de entrada

> Governa TODO pixel que a casa produz: protótipo de tela, dashboard PBI, tela de aplicação e mockup de validação.
> Este arquivo NÃO repete token que já mora em outro lugar. Ele diz **qual superfície** você está desenhando, aponta a **referência canônica** dela e fixa o que é **comum às três**.
> Lido por: `montar-visuais` · `gerar-mockup-validacao` · `desenvolver-app` · qualquer etapa de protótipo antes do desenvolvimento.
> Regra de ouro: **nenhum desenho começa sem declarar a superfície.** Pular esse passo é exatamente como nasce a salada de fruta.
> A paleta abaixo é um ponto de partida neutro (acento `#2F6F8F`). Troque pelos tons da identidade da sua empresa, mantendo a estrutura de papéis. Cresce por convergência (§7), não por planejamento de uma vez só.

## 1. As três superfícies

| Superfície | Onde o pixel vive de verdade | Identidade | Referência canônica |
|---|---|---|---|
| **Dashboard PBI** | tema JSON + PNG de fundo + medida HTML/DAX | Segoe UI · acento `#2F6F8F` · destaque âmbar `#B7791F` | [PADRAO_VISUAL_DASHBOARDS.md](PADRAO_VISUAL_DASHBOARDS.md), completo, é a lei |
| **Tela de aplicação** | HTML/CSS/JS no repositório da aplicação | um par de fontes título + corpo (ex.: Montserrat + Open Sans) · acento `#2F6F8F` · neutros zinc | §3 deste arquivo, até a aplicação ganhar doc visual própria |
| **Documento interno** (mockup de validação, runbook HTML, one-page) | HTML autocontido na pasta da demanda | stack de sistema · accent do template | `template_mockup.html` da skill `gerar-mockup-validacao` |

O protótipo **não é uma quarta superfície**. Ele desenha PARA uma das três e usa os tokens dela desde a primeira tela. Um protótipo "genérico bonito" é retrabalho garantido, porque nada dele sobrevive à implementação.

## 2. Núcleo comum (vale nas três, sem exceção)

Decisões independentes de superfície:

1. **Uma cor de acento institucional.** Ponto de partida neutro: `#2F6F8F` (`hsl(200, 51%, 37%)`, contraste de cerca de 5,5:1 sobre branco). É a MESMA cor nas três superfícies. O que muda é o papel, nunca o tom: onde o acento é marca, o status usa outra família; onde o verde é status, a marca é outra cor. Nunca os dois papéis na mesma tela. Derivação permitida é só de luminosidade sobre a mesma matiz (`hsl(200, 51%, L)`); matiz diferente é cor de outra empresa. Ao trocar pela identidade da sua empresa, confira o contraste AA (4,5:1 para texto).
2. **Destaque é acento secundário, nunca marca.** Serve para destacar um item dentro do conjunto (carteira, projetado, série secundária).
3. **Gramática semântica única:** positivo = verde · atenção = âmbar · negativo = vermelho-tijolo · neutro/inativo = cinza. Setas `▴` alta e `▾` baixa. Vale no dash, na tela e no documento.
4. **Uma fonte por superfície.** Misturar família dentro da mesma tela é proibido; o par título + corpo da tela de aplicação é a única dupla, e cada fonte tem papel fixo (título ou corpo).
5. **Hierarquia por peso e tamanho, não por cor.** Cor carrega significado (§2.3); usar cor só para "dar destaque" quebra a leitura do status.
6. **Nada de dado corporativo real no protótipo.** Número de protótipo é ilustrativo e rotulado como tal. Dado pessoal de terceiro nunca entra (LGPD). Mesma regra dura que a `gerar-mockup-validacao` já carrega.
7. **Artefato HTML é autocontido.** Zero CDN, zero fonte remota, zero fetch. Vale para o mockup, o runbook HTML e o protótipo.
8. **Sem hex cru onde existe token.** No PBI é `ColorId N` do tema; na aplicação é `var(--app-*)`; no documento é `var(--*)` do template. Hex solto no meio do código é dívida.

## 3. Tokens da tela de aplicação (ponto de partida)

Enquanto o `PADRAO_APP.md` não ganhar uma seção visual própria, esta tabela é a referência. Os valores são neutros; troque os de marca pela identidade da empresa.

| Papel | Token | Valor |
|---|---|---|
| Fundo de página | `--app-bg-page` | `#f7f7f5` |
| Fundo de cartão | `--app-bg-card` / `-hover` | `#ffffff` / `#fafafa` |
| Borda | `--app-border` / `-strong` | `#e5e5e3` / `#d4d4d2` |
| Texto | `--app-text-primary` a `-faint` | `#171717` · `#525252` · `#737373` · `#a3a3a3` |
| Marca (acento) | `--app-accent` / `-dim` | `#2F6F8F` / `#255A74` |
| Acento de apoio | `--app-accent-soft` / `-border` | `rgba(47,111,143,.10)` / `.30` |
| Positivo | `--app-green` (+ soft `.10` / border `.30`) | `#16a34a` |
| Atenção | `--app-amber` (+ soft `.12` / border `.32`) | `#d97706` |
| Negativo | `--app-red` (+ soft `.10` / border `.30`) | `#dc2626` |
| Neutro/inativo | `--app-slate` (+ soft `.07` / border `.28`) | `#475569` |
| Sombra de cartão | `--app-shadow-card` | `0 1px 2px rgba(0,0,0,.04)` |
| Tipografia | título / corpo | `Montserrat` 600-700 / `Open Sans` |
| Rótulo de seção | fonte de título 11px, 500-600, `uppercase`, `letter-spacing .06-.09em` | |

Padrão de estado: cada semântico vem em trio (cor sólida para texto/ícone, `soft` para fundo de pílula, `border` para contorno). Ao criar um estado novo, siga o trio; não invente cor solta.

**Troca de marca.** A troca é de valor de token, sem mexer na estrutura: só `--app-accent`, `-dim`, `-soft` e `-border` mudam, e todo consumidor que usa `var(--app-accent*)` acompanha sozinho. Mantenha o `-dim` como o mesmo passo de escuro (cerca de 7 pontos de luminosidade abaixo da base) e confira o contraste nas duas direções, acento sobre branco e branco sobre acento.

## 4. A salada declarada (conflitos em aberto)

Registre de propósito, porque o que não está escrito volta a divergir sozinho. Nada aqui é urgente; cada linha se resolve quando encostar numa demanda real. As linhas abaixo são os conflitos que costumam aparecer primeiro.

| # | Conflito | Como está hoje | Custo real | Caminho sugerido | Status |
|---|---|---|---|---|---|
| C1 | **Três tipografias** | PBI Segoe UI · aplicação com par título + corpo · documento stack de sistema | Baixo dentro de cada superfície, alto quando aparecem juntos num reporte | Manter separado (cada meio tem sua restrição técnica) e padronizar só o **peso e a escala** | Em aberto |
| C2 | **Accent azul do template de mockup** | `#1f6feb` não existe em nenhuma outra superfície | Mockup parece de outra empresa | `--accent` vira o acento da casa no tema claro e uma versão clareada da mesma matiz no escuro (ex.: `#65AACD`, porque o tom base sobre fundo escuro perde contraste) | Em aberto |
| C3 | **Aplicação sem doc visual própria** | Tokens vivem só no CSS e nesta §3 | Cada tela nova arrisca reinventar | Promover a §3 para uma seção visual no `PADRAO_APP.md` quando a segunda tela for desenhada | Em aberto |
| C4 | **Escala de espaçamento** | Nenhuma superfície declara ritmo (4/8px) | Espaçamento decidido no olho a cada tela | Adotar múltiplos de 4 e registrar aqui na primeira tela prototipada | Em aberto |

## 5. Protocolo de protótipo

Antes de desenhar qualquer tela:

1. **Declarar a superfície** (§1) em uma linha. Se a demanda não encaixa em nenhuma, pare e pergunte, sem improvisar.
2. **Carregar os tokens da superfície** da referência canônica dela. O protótipo lê, não inventa.
3. **Desenhar com token, não com hex.** O protótipo já nasce com as variáveis CSS certas, porque é isso que faz o HTML ser reaproveitável depois (direto na aplicação, ou como CSS de medida DAX no PBI).
4. **Token que faltar vira pergunta, não invenção.** Se o desenho precisa de algo que não existe no padrão (um estado novo, um componente inédito), proponha, marque como novo no protótipo e registre no §6 quando for aprovado.
5. **Fechar com destino:** HTML do protótipo na pasta da demanda + PNG exportado. O HTML é registro versionado; o PNG é o insumo de pixel que o `montar-visuais` pede.

## 6. Diário de convergência

Cada decisão visual batida entra aqui com data. É o que transforma uso em padrão.

| Data | Decisão | Onde nasceu | Onde vale |
|---|---|---|---|
| (preencher) | Acento institucional definido (troca do `#2F6F8F` neutro pela cor da empresa), com escala de luminosidade base, escuro e claro para fundo escuro | Decisão do usuário | Transversal |
| (preencher) | Trio sólido/soft/border para cada semântico | Primeira tela de aplicação | App |

## 7. Como este arquivo cresce

Três regras para ele não virar documento morto:

- **Só entra token que já foi usado em campo pelo menos uma vez.** Nada aspiracional. Se ninguém desenhou ainda, fica no §4 como conflito em aberto.
- **Detalhe fino desce para o filho.** Token de dashboard vai para o `PADRAO_VISUAL_DASHBOARDS.md`, token de aplicação vai para o `PADRAO_APP.md` (quando existir a seção). Aqui fica só o que é transversal ou o que ainda não tem casa.
- **Conflito resolvido sai do §4 e entra no §6** com data. O §4 encolhendo é a medida de que a convergência está acontecendo.
