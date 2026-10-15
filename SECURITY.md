# Segurança: regras em linguagem humana

Para qualquer pessoa que use este repositório.

1. Segredo (senha, chave, token, connection string) nunca entra em arquivo nem em resposta. Use o placeholder `<TOKEN>`.
2. Dado corporativo bruto e sensível vive em `local/` (fora do git) ou nos sistemas sancionados da empresa, nunca no repositório.
3. Dado pessoal de terceiros é sensível (LGPD): anonimize antes de registrar.
4. Ative a trava com `git config core.hooksPath .githooks`. Ela barra commit com cara de segredo, mas não é infalível: olhe a lista de arquivos antes de commitar.
5. Segredo que já foi commitado uma vez continua no histórico. Troque o segredo, considerando-o comprometido, e limpe o histórico.
6. O caderno guarda o seu trabalho. Mantenha o seu repositório privado, mesmo que este modelo seja público.

Encontrou uma falha no próprio sistema (um hook que deixa segredo passar, por exemplo)? Abra uma issue sem colar o segredo.
