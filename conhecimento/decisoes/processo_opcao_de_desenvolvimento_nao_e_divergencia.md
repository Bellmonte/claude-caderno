# Opção de desenvolvimento não é divergência do documento

> Decidido pelo usuário no fechamento de uma demanda de dashboard que ia para homologação.

## Contexto

Fiz a checagem crítica de um painel novo contra o documento de especificação, item a item, e
listei seis pontos em que a implementação seguiu caminho diferente do texto. Apresentei os seis sob
o título "o que não está atendido" e recomendei resolver três antes de publicar.

Entre eles: um filtro de unidade no grão de filial em vez do grupo de empresas, o título do banner
diferente do escrito, uma classificação de produto saindo de lista de grupos em vez do campo de tipo
do cadastro, uma categoria entrando quase vazia e um tipo de movimento aparecendo onde o leitor não
esperava.

## Decisão

Nenhum deles é pendência. A demanda vai para homologação sem pendência aberta, e esses pontos
seguem como **observação**, e não como divergência.

A régua: a especificação descreve **o que a área precisa enxergar**. O caminho até lá é decisão
técnica de quem desenvolve. Um ponto só vira pendência quando **muda o número** ou quando **a área
diz que atrapalha**.

## Consequência

- Diferença que é escolha visual (rótulo, título, grão de um filtro que não altera resultado) entra
  na documentação como opção tomada no desenvolvimento, sem cobrança de resposta.
- Comportamento que surpreende mas tem explicação no dado (categoria quase vazia porque a operação
  em aberto é posição, tipo de movimento porque o cadastro o marca assim) entra como observação,
  para a área saber o porquê se estranhar.
- Levar tudo como pendência gasta a rodada do solicitante com coisa já decidida, e ainda dá ao
  documento um tom de entrega incompleta que não corresponde ao que foi feito.
- O que **muda número** continua sendo pendência, sem exceção. Na mesma demanda, um recorte de
  horizonte errado e um de-para invertido foram corrigidos antes de publicar, e nunca foram
  tratados como opção.

## Onde isso me pega

O viés é meu e vale nomear: eu tendia a tratar "diferente do texto" como sinônimo de "errado".
Numa checagem contra especificação, separar os achados em **muda número** e **muda aparência**
antes de escrever, e só a primeira lista se chama pendência.

É o mesmo padrão de outro erro conhecido: conclusão apressada sobre o que o outro lado já decidiu.
Antes de chamar algo de divergência, confira no diff ou no registro se aquilo foi escolha.
