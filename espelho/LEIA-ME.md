# espelho/

Cópia de **leitura** dos ambientes que o caderno opera de fora: a ferramenta de automação, o
repositório de pipelines, o workspace de notebooks, o banco. Existe para o Claude consultar o que
está em produção sem tocar em produção.

Esta pasta fica fora do git e **este LEIA-ME é a única coisa que viaja**, para a outra máquina
saber o que ela é e como repovoar. O conteúdo é regenerável em minutos, costuma pesar dezenas de
MB e divergiria entre máquinas se fosse versionado.

## Por que não vive em `local/`

Elas parecem parecidas e são opostas.

`local/` guarda material **bruto recebido**: planilha do solicitante, extração de ambiente,
print, PDF do chamado, arquivo de transporte. Aquilo é dado corporativo cru, e o Claude não
lê nem deve ler. A regra `Read(local/**)` no `.claude/settings.json` garante isso.

`espelho/` guarda **cópia de leitura do ambiente**, exportada por script. Ela existe exatamente
para ser lida, e sem isso o desenho de handoff por arquivo não funciona: ninguém propõe ajuste
sobre código que não pode abrir.

A cópia sai **fiel**, com segredo como está no ambiente. Isso é proposital. Espelho redigido
esconderia justamente o que precisa ser achado, que é credencial digitada direto num fluxo ou
num notebook. Quem protege é a fronteira: a pasta fica fora do git, a trava em
`.githooks/pre-commit` barra segredo no commit, e a régua do `CLAUDE.md` proíbe citar valor em
qualquer texto que saia daqui. Ao citar algo do espelho, mascare sempre
(`Client-Token: <SECRET>`).

Quando precisar de uma cópia que vai sair da máquina, o exportador deve oferecer uma opção de
redigir (por exemplo `--redigir`). Racional completo em
[[processo_espelho_separado_do_material_bruto]].

## Uma pasta por ambiente

O caderno não traz exportador pronto, porque cada empresa tem os seus ambientes. Monte uma pasta
por ambiente e um script por pasta, no formato abaixo:

| Pasta | Ambiente (exemplo) | Como repovoar |
|---|---|---|
| `automacao/` | fluxos da ferramenta de automação | script que lê a API da ferramenta e grava um arquivo por fluxo |
| `notebooks/` | notebooks da plataforma de dados | script que usa o CLI da plataforma para exportar o workspace |
| `pipelines/` | pipelines e triggers versionados em git | `git clone` uma vez, depois `fetch` mais `pull --ff-only` |

Os scripts podem morar em `.claude/scripts/` (quando servem a todo o caderno) ou na pasta
`ferramentas/` da demanda que os criou. Credencial vem de `.env` na raiz, fora do git, e o
`.env.example` versionado leva só placeholder (`<TOKEN>`).

Todos são **somente leitura**: nenhum importa, publica, ativa ou executa. Depois da primeira
exportação, audite o resultado: conte o que foi redigido (se redigiu) e varra o que sobrou com
cara de credencial.

## As duas regras que não mudam

**Reexporte antes de mexer.** Propor ajuste sobre código velho é a armadilha do trabalho por
arquivo. O espelho é cópia; se divergir do ambiente, o ambiente manda. `espelho/` velho ou ausente
não prova estado de ambiente nenhum: peça a saída.

**Escrita é só por arquivo, e quem aplica é humano.** O Claude lê o espelho, entrega o ajuste
como arquivo em `proposto/` dentro da demanda, e o usuário importa no ambiente.
