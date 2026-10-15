# Instalar em uma máquina nova

As ferramentas do caderno moram em `.claude/`, dentro do próprio repositório: skills, agentes,
hooks, scripts e permissões. Elas chegam pelo `git clone` e viajam no `git pull`, então não há
nada para espelhar nem manter em paralelo.

O que é **por máquina**, e por isso está aqui: o `~/.claude/CLAUDE.md` global (persona e régua
de escrita, que vale em todo projeto), o Python que os hooks chamam, e o
`.claude/settings.local.json`, que não versiona de propósito.

---

## Prompt para colar na máquina nova

Abra o Claude Code na pasta onde o caderno vai ficar e cole isto:

```
Vou instalar meu caderno de trabalho nesta máquina. As ferramentas vivem em .claude/ dentro
do próprio repositório, então o clone já traz tudo.

Faça o seguinte, nesta ordem, e me mostre o resultado de cada passo:

1. Verifique se já existe uma pasta do caderno nesta máquina. Se existir e o git status
   estiver limpo, faça git pull --ff-only. Se o git status NÃO estiver limpo, PARE e me
   mostre o que está pendente antes de qualquer coisa: pode ser trabalho que só existe aqui
   e ainda não subiu. Se não existir a pasta, clone <url do seu repositório do caderno>

2. Confirme que o Python está no PATH rodando "python --version". Os hooks do caderno
   dependem disso. Se não estiver, me avise e pare.

3. Teste os hooks a partir da raiz do repositório, com CLAUDE_PROJECT_DIR apontando para ela
   em caminho Windows (C:\...), não em caminho MSYS (/c/...), senão o teste falha
   silenciosamente. Rode o log_acao.py com um payload simulado e confirme que a linha entrou
   em diario/.log/, e rode o abrir_dia.py e confirme que ele devolve JSON. Se o log também
   deve cobrir um repositório de código, defina a variável CADERNO_REPO_TRABALHO com o
   caminho dele. Apague o que o teste criou (diario/.log/ e PAINEL.md).

4. Confira o ~/.claude desta máquina. Se houver pasta de skill ou de agente lá com o mesmo
   nome de alguma que vem no .claude/ do repositório, ela duplica e deve sair. Me mostre a
   lista antes de apagar.

5. Copie conhecimento/modelos/CLAUDE-global.md do repositório para ~/.claude/CLAUDE.md e
   me peça os dados da seção "Quem sou" para trocar os placeholders.

6. No fim, abra o CLAUDE.md do repositório e me explique em poucas linhas como funciona a
   triagem de trilho, para eu conferir que carregou certo.
```

---

## Passo a passo manual, se preferir fazer na mão

**1. Trazer o repositório.**

```bash
git clone <url do seu repositório do caderno>
```

Se a máquina já tem o caderno, não clone por cima: confira que o `git status` está limpo e
puxe com `git pull --ff-only`.

**2. Python no PATH.** Os hooks são scripts Python chamados pelo `.claude/settings.json`.
Confirme com `python --version`. Sem Python, o Claude Code segue funcionando e apenas os hooks
não rodam, o que significa perder o log automático.

**3. Quase nada mais a instalar.** Skills, agentes, scripts e permissões já estão em
`.claude/`, e o plugin próprio da barra de atalhos vem em `.obsidian/plugins/caderno-nav/`.
Ative a trava de segredo do commit com `git config core.hooksPath .githooks`, e, se o log deve
cobrir também o repositório de código, defina a variável de ambiente `CADERNO_REPO_TRABALHO`
com o caminho dele.

O que **não** vem no clone é o **Dataview**, porque plugin de terceiro não se versiona: é 1,3 MB
de código compilado que o Obsidian instala e atualiza sozinho, e congelar a versão no
repositório só cria problema. Instale por Configurações → Plugins não oficiais → Procurar →
`Dataview`, e ligue **Enable JavaScript Queries** nas opções dele. Sem isso a tela de início
não renderiza; o resto do caderno funciona igual.

**4. Cuidado com skill duplicada.** Skill e agente que estejam soltos em `~/.claude/skills/` ou
`~/.claude/agents/` com o mesmo nome dos que vêm no repositório aparecem duas vezes. O lugar
das ferramentas do caderno é o `.claude/` do repositório; o `~/.claude` fica só com o que vale
em todo projeto.

**5. O `settings.local.json`** é por máquina e fica fora do git. Ele não é copiado nem
sincronizado, e é onde ficam as permissões que você aceitou naquela máquina.

---

## Repovoar o espelho

O `espelho/` fica fora do git de propósito, porque é pesado e regenerável, então numa máquina
nova ele chega vazio, só com o LEIA-ME. Ele volta por script, e **nenhuma ponta deveria precisar
de exportação manual**. Vale dizer isso em voz alta porque é fácil esquecer que os scripts
existem e acabar baixando artefato na mão, que dá trabalho, envelhece rápido e ainda sai
diferente do que o script produz.

O caderno não traz exportador pronto, porque cada ambiente tem o seu: repositório de pipelines,
workspace de notebooks, ferramenta de automação, banco. O desenho que funciona, e que vale
seguir ao escrever o seu, está em `espelho/LEIA-ME.md`: um script por ambiente, somente leitura,
que grava em `espelho/<ambiente>/` e pode ser rodado de novo a qualquer hora.

Três cuidados que costumam aparecer na primeira rodada numa máquina nova:

- **Credencial é passo humano.** Login que abre navegador, token de API e chave ficam com o
  usuário. A chave vai num `.env` fora do git (o `.gitignore` já cobre), e o `.env.example` com
  placeholder (`<TOKEN>`) é o que se versiona.
- **Certificado incompleto trava o Python.** Servidor que manda só o certificado final, sem o
  intermediário, funciona no navegador (que busca o elo que falta sozinho) e falha no Python com
  `CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate`. O contorno que mantém a
  validação inteira é montar um bundle a partir do `certifi`, acrescentar o intermediário no fim
  e apontar `SSL_CERT_FILE` para ele. O conserto de verdade é do lado do servidor, enviando a
  cadeia completa. Nunca desligue a verificação de certificado.
- **Exportador só lê.** Nenhum script de espelho faz push, publica ou executa no ambiente. Se
  usar git para clonar um repositório de pipelines, é `fetch` mais `pull --ff-only`.

---

## CLAUDE.md global

O `~/.claude/CLAUDE.md` guarda apenas o que vale em **todo** projeto: quem você é, a régua das
primitivas, a régua de escrita, acentuação, segurança e a regra de commit. Tudo que é do
trabalho mora no `CLAUDE.md` do repositório, e o que for de outro contexto (estudo, projeto
pessoal) mora no `CLAUDE.md` do repositório daquele contexto.

O conteúdo está versionado em [CLAUDE-global.md](../modelos/CLAUDE-global.md).
Copie de lá para `~/.claude/CLAUDE.md`.

---

## Como o dia funciona

**Ao abrir a sessão**, o `abrir_dia.py` injeta o estado: demandas sem fechamento e dias que
tiveram trabalho mas ficaram sem narrativa. Você já começa sabendo onde parou.

**Durante o trabalho**, cada arquivo escrito entra no log em `diario/.log/`. Isso é
determinístico e não depende de ninguém lembrar. O log fica fora do git de propósito: é rastro
de máquina, e o que atravessa máquinas é a narrativa destilada.

**Ao encerrar**, se houve trabalho e o diário do dia não foi escrito, o `cobrar_diario.py`
segura a saída e pede a narrativa. Cobra uma vez por sessão, então é lembrete e não carcereiro.

**Na daily e na semanal**, `reporte-dia` e `reporte-semana` leem o log e o diário e montam o
reporte. Elas perguntam só o que o log não pode saber: se algo concluiu de verdade, o que foi
conversa e não virou arquivo, e o que vem a seguir.

**Ao fechar uma demanda**, `fechar-demanda` também acrescenta a linha no prontuário do objeto
em `gerencial/objetos/`, marcando se a entrega foi retorno de validação. Esse é o dado que
mais se perde e o que mais vale depois.

## Sincronizar entre máquinas

É git puro, sem skill no meio:

```bash
git pull --ff-only
```

no início, e `publicar` no fim. Como `.claude/` é versionado, skill ou hook que você mexer em
uma máquina chega na outra no mesmo pull.

### As três coisas que o pull não traz

| Pasta | Por que fica fora | O que fazer do outro lado |
|---|---|---|
| `espelho/` | cópia de leitura do ambiente, pesada e regenerável. A fonte da verdade é sempre o ambiente | regerar com os seus scripts de exportação (seção "Repovoar o espelho") |
| `local/` | material bruto recebido, dado corporativo cru, e a única das três que não se regenera | levar pelo `pacote_local.py`, abaixo |
| `diario/.log/` | rastro de máquina, gravado pelo hook a cada escrita | nada. A narrativa destilada do `diario/` é que atravessa |

Dois arquivos menores no mesmo caso: o `.claude/settings.local.json`, que é config por máquina, e o
`PAINEL.md`, que o hook de abertura regrava sozinho. O `CLAUDE.md` global tem seção própria acima.

### Levar a `local/`, e conferir que ela chegou inteira

Ela vai zipada, e o zip é dado bruto em trânsito. O que faz isso merecer ferramenta em vez de um
unzip é que **o Claude não pode conferir essa transferência**. A regra `Read(local/**)` do
`.claude/settings.json` nega o acesso dele àquela pasta, inclusive por Bash, e ela não se afrouxa
por conveniência. Se a conferência dependesse dele, ou a regra caía ou a conferência não acontecia.
Por isso ela é uma ferramenta que você roda, e o que atravessa para a conversa é o veredito, nunca o
conteúdo. O manifesto guarda caminho, tamanho e sha256, e nenhuma linha dele carrega conteúdo de
arquivo.

Na máquina de **origem**:

```bash
python .claude/scripts/pacote_local.py empacotar
```

Leve o `local.zip` da raiz do caderno para a outra máquina. Ele não vai para o git, que já o ignora,
e não vira anexo de e-mail.

Na máquina de **destino**, com o zip na raiz do caderno:

```bash
python .claude/scripts/pacote_local.py conferir
```

Ele responde em duas etapas, e a ordem importa. Primeiro se o **próprio zip** está inteiro, porque
download interrompido produz arquivo que abre e vem pela metade, e é isso que engana. Depois, o que
falta, o que difere e o que só existe ali.

```bash
python .claude/scripts/pacote_local.py extrair
```

Traz só o que falta e o que difere. Arquivo que só existe no destino não é tocado, porque pode ser
trabalho feito lá. Rode o `conferir` de novo para fechar, e apague o `local.zip` quando ele der tudo
igual: dado bruto em transporte não fica morando no disco.

Conferir em vez de confiar no unzip é a mesma régua de conferir uma carga de dados antes de usá-la.
Arquivo que falta em silêncio vira análise feita sobre base incompleta, e o erro só aparece no número final, quando já
custou caro. O unzip não reclama de um pacote que chegou pela metade se o que chegou estiver bem
formado, e contagem de arquivo sozinha não pega arquivo truncado. O sha256 pega os dois casos.
