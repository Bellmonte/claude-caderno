# Referência: falso positivo da trava de segredo (pre-commit)

A trava `.githooks/pre-commit` do caderno bloqueia o commit quando encontra, nas linhas adicionadas do diff staged, chave privada PEM, `AKIA...` ou um dos nomes `password`, `passwd`, `senha`, `secret`, `client_secret`, `token`, `access_token` ou `api_key` atribuído com dois-pontos ou sinal de igual a um **literal entre aspas que começa com letra ou número**. Placeholder (`<SECRET>`, `<TOKEN>`), f-string e leitura de cofre passam. Linha marcada com o token `allowlist-secret` é ignorada, e serve só para exemplo e documentação.

A regra já foi mais larga (bastava o nome colado ao operador), e os casos abaixo vêm dessa época. Eles continuam úteis porque a forma de escrever que evita o falso positivo antigo também evita o atual, e porque a régua pode voltar a apertar.

**Pegadinha:** documentar código em markdown que mostre uma atribuição desses nomes (por exemplo `secret`= algo, `token`= algo) pode disparar falso positivo, mesmo sem nenhum valor real. Aconteceu ao descrever, num `contexto.md`, a correção de um notebook, onde a citação colava `secret` no igual da chamada `client.get_secret(...)`.

**O que fazer:** reescrever a frase para o nome não ficar colado ao operador (ex.: "a variável `secret` recebe `client.get_secret(...)`"), ou manter o nome entre crases separado do sinal. Não burlar com `--no-verify`; só usar isso com decisão consciente de que é falso positivo e não há segredo de verdade.

## Caso 2: rótulo de seção em markdown

Um **rótulo de seção** em markdown que termine com um desses nomes colado ao dois-pontos pode disparar igual, mesmo sem valor nenhum. Aconteceu no `entrega.md` de uma demanda de aplicação: um bullet cujo rótulo era a palavra `token` seguida direto do dois-pontos casou o padrão.

**O que fazer:** reescrever o rótulo para o nome não ficar colado ao `:`, por exemplo trocar aquele rótulo por `Split de cache do prompt:`, ou pôr um parêntese entre o nome e o dois-pontos (algo como `Token (cache do prompt):`). Vale igual para os rótulos `senha`, `secret`, `password` e `api key` no mesmo formato de cabeçalho de bullet. De novo: nada de `--no-verify`, é só reescrever o rótulo.

## Caso 3: o documento que ENSINA segurança dispara a própria trava

Ironia recorrente: todo material que ensina "não deixe o `secret` no código" acaba escrevendo, num exemplo, exatamente o nome colado ao `=` ou ao `:`, e a trava barra. Ao fechar um padrão de notebook e seus modelos, a trava disparou **quatro vezes** no mesmo assunto: (a) o exemplo de cofre de chaves onde a variável `client_secret` recebia `kv.get_secret(...)`; (b) a prosa do `entrega.md` que citava essa mesma atribuição; (c) a mensagem de erro com a palavra `token` antes do dois-pontos; (d) a variável `access_token` recebendo o `resp.json()`. Nenhum tinha valor real; era código didático e nome de variável padrão da linguagem.

**O que fazer (mesma regra, aplicada a exemplo de código):** renomear a variável do exemplo para o nome não ficar colado ao operador, sem perder o sentido:
- a variável `client_secret` recebendo o `get_secret(...)` vira a variável `segredo` recebendo o mesmo (com uma nota de que no código real ela se chama `client_secret`).
- a variável `access_token` recebendo o `resp.json()` vira `bearer` recebendo o mesmo.
- a mensagem "Falha ao obter [token]" vira "Falha ao autenticar" (tira a palavra colada ao `:`).
- **Não precisa mexer nas chaves de dicionário:** `"client_secret":` e `["access_token"]` não disparam, porque depois do nome vem `"` (aspas), e não `:`/`=`. O gatilho é só o nome colado direto ao operador.

**Antes de commitar um doc ou modelo que fala de credencial:** rodar o próprio regex do hook no arquivo evita o ciclo de commit, bloqueio e reescrita. O padrão está no `.githooks/pre-commit`. Truque para citar sem colidir: ponha o nome numa crase e o operador fora dela (o próprio primeiro caso acima faz isso). `--no-verify` continua fora de questão; é sempre reescrita.
