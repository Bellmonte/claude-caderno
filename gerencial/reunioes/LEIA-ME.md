# Reuniões

Uma pasta por reunião: `AAAA-MM-DD-<assunto>/`.

- A transcrição crua fica como `raw.<ext>` (ou `<nome>-raw.<ext>`) dentro da pasta, e fica FORA do
  git, por segurança. O `.gitignore` já cobre os dois formatos.
- A ata destilada pela skill `ata-reuniao` fica como `ata.md`, versionada. O `.docx` e o `.pdf`
  gerados a partir dela são regeneráveis e também ficam fora do git.
- Transcrição com nome de pessoa de fora do time ou dado sensível é anonimizada antes de virar ata.
