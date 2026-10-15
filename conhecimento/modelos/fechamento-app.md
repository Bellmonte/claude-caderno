# Modelo — fechamento de entrega (frente APP, sem chamado)

> Formato de fechamento quando a origem é alinhamento com a gestão ou item de cronograma,
> e não chamado. Sem máquina de SLA e sprint. Público de **negócio**, não de TI: diga o
> efeito, e deixe a mecânica no rastreio do rodapé.

---

### 🚀 [{ref — DEM_APP-NNN ou marco}] — {NATUREZA}: {descrição curta}

> Máximo de 50 caracteres na descrição. NATUREZA = Correção · Divergência · Novo recurso · Alteração.

**Origem:** {qual alinhamento e quando, ou qual item do cronograma} | **Data:** {DD-MM-AAAA}
**Onde aparece:** {o que o usuário vê na aplicação: agente, tela, ação}
**Solicitado por / Para:** {gestão ou área, ou N/A}

**O que muda na prática:** {uma a três linhas, em linguagem de negócio, sobre o efeito para quem usa}
**Por que foi feito:** {a necessidade ou decisão que originou, uma linha}
**Como conferir:** {o que olhar na aplicação para validar, em linguagem de negócio}

**Status:** {Entregue · Em PR (aguardando aprovação) · Validado}

---
🔧 **Rastreio técnico** (para o time, não para o negócio)
**Camadas:** {front · back · API · agente · ação} | **Dependência:** {outro motor, sql ou automacao, ou N/A}
**PR:** {branch → destino · link ou —} | **Teste:** {rodado · verde ou —} | **Commit:** {short-hash}
**Obs.:** {opcional}

---
<!-- INTERNO — não compartilhar. -->
🔒 **Valor (interno)**
**Dor endereçada:** {qual} | **Beneficiário:** {quem}
**Dimensão:** {tempo · confiabilidade · decisão · risco-dependência · adoção · capacidade · custo}
**Antes:** {baseline ou "sem baseline medido"} → **Depois:** {medida ou proxy}
**Confiança:** {alta · média · baixa} | **Contra-argumento:** {o que um cético diria}
**Feedback:** {quem comentou e o quê, com data; ou "nenhum recebido"} | **Visibilidade:** {quem ficou sabendo: área, gestor, diretoria, reunião}
**Competências:** {o que precisou usar ou desenvolver, técnico e comportamental, separado por vírgula}

---

## Princípio de escrita

Nada de nome de arquivo, jargão de Git ou trecho de código no corpo. Isso vive só no rastreio
técnico, e compacto. O corpo fala do efeito para quem usa.

A tabela de tradução de jargão para linguagem de negócio vive no [[fechamento-chamado]] e vale
igual aqui, como em todo documento que sai para a área.

## Casos especiais

- **Entrega parcial:** Status `Entregue (parcial)`, com uma linha sobre o que ficou de fora.
- **Dependência de outro motor:** se depende de view, procedure ou fluxo de automação que não está
  pronto, Status `Em PR` ou `Bloqueado`, e a dependência registrada no rastreio. Não declare
  resolvido.
- **PR já mesclado (Status `Validado`):** feche o galho, apagando a branch da demanda local e
  remota. Nunca toque `main` nem a branch de homologação. Ainda em PR, a poda espera o próximo fecho.
