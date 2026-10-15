# Runbook: medir o conflito que a MINHA mudança acrescenta aos galhos dos outros

**Quando usar:** antes de avisar o time que uma alteração vai gerar conflito, ou para saber quem
precisa rebasar. Nasceu num repositório de aplicação com `main` e `Desenv` divergindo e vários
galhos vivos ao mesmo tempo.

## O erro que este runbook evita

A medida óbvia é comparar cada galho vivo contra o galho novo e listar o que conflita. Em
repositório com duas linhas de integração divergentes, essa medida **não diz nada**: o galho do
colega saiu da `main`, o seu saiu da `Desenv`, e o merge dos dois traz toda a distância entre as
duas linhas. No caso de origem essa leitura acusou vinte e um arquivos conflitados, sendo que a
alteração tocava três.

Aviso assim não é acionável. Quem recebe olha a lista, não reconhece nada, e ignora.

## A medida certa

Conflito que **você** acrescenta = o que conflita depois da sua mudança, menos o que já
conflitava antes dela.

```bash
conf() { git merge-tree --write-tree --name-only "$1" "$2" 2>/dev/null \
         | sed -n '2,$p' | grep -vE '^(Auto-merging|CONFLICT|Merge)' | sort -u; }

for b in $(git branch -r --no-merged origin/Desenv --format='%(refname:short)' | grep -vE 'HEAD|^origin$'); do
  antes=$(conf  "$b" origin/Desenv)
  depois=$(conf "$b" meu-galho-novo)
  novo=$(comm -13 <(echo "$antes") <(echo "$depois") | tr '\n' ' ')
  printf "%-46s => %s\n" "${b#origin/}" "${novo:-nada novo}"
done
```

`git merge-tree --write-tree` faz um merge de três pontas de verdade, sem encostar na cópia de
trabalho e sem criar commit. Exige git 2.38 ou mais novo.

## Como ler o resultado

O padrão que aparece costuma ser limpo: quem está sincronizado com a linha de integração de
destino não pega nada, e quem está com galho de outra linha pega os mesmos poucos arquivos. Esse
é o recado que se manda, com o nome dos arquivos e de quem está afetado.

Também vale separar antes, pelo `git merge-base --is-ancestor <galho> <destino>`, os galhos que já
estão contidos no destino. Eles aparecem na listagem de galhos remotos e não precisam de nada, e
citá-los no aviso só gera ruído.

## O que mandar junto com o aviso

Além da lista de arquivos, mande **a informação que evita a pergunta**. No caso do renome de
agentes, era uma frase: nenhum identificador mudou, só o nome na tela. Sem ela, cada pessoa que
abrisse o conflito ia parar para entender se precisava trocar chave em algum lugar.

## Antes de medir

Não fabrique o conflito antes de medi-lo. Arquivo de configuração que todo mundo edita (um JSON
de lista de agentes, de rotas, de permissões) conflita por qualquer linha mexida; quando der,
acrescente no fim ou em bloco próprio em vez de reordenar o que já existe.
