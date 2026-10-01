# O que é rolling forecast, e por que ele resolve o problema que quebrou a Zillow

A Zillow perdeu US$ 500 milhões em 2021 comprando casas com um algoritmo que precificava usando dados de até 30 dias atrás. O problema não foi falta de tecnologia. Foi um modelo de planejamento que não se atualizava rápido o suficiente para um mercado em queda.

Existe um método pensado exatamente para esse problema: o rolling forecast.

## O que é

Rolling forecast é um modelo de previsão contínua. Em vez de fechar um orçamento para o ano inteiro e só revisar na virada do ciclo seguinte, a empresa mantém sempre um horizonte fixo à frente, por exemplo 12 meses. Ao final de cada mês, o resultado real substitui a previsão daquele período, e um novo mês entra no final da janela. O horizonte nunca encolhe.

A atualização costuma ser mensal ou trimestral. É esse ritmo que separa o rolling forecast do orçamento estático: o orçamento estático fixa premissas em dezembro e vive com elas o ano inteiro. O rolling forecast questiona a premissa a cada ciclo.

## Por que isso teria mudado o caso Zillow

O algoritmo da Zillow operava como um orçamento estático, só que em alta velocidade: a premissa de preço era fixada e aplicada repetidamente, sem um ciclo de revisão que perguntasse se ela ainda fazia sentido. Um modelo de rolling forecast, aplicado à mesma decisão, teria forçado uma pergunta simples a cada atualização: os dados que uso hoje ainda refletem o mercado de hoje, ou já estão defasados?

Essa é a mesma lógica do artigo sobre a Zillow: toda premissa precisa de três respostas, quem definiu, com que critério, quando revisar. O rolling forecast institucionaliza a terceira resposta. Ele cria o ciclo de revisão como parte do processo, não como exceção.

## Para quem lida com orçamento todo mês

Rolling forecast não é só para empresa de tecnologia com algoritmo de precificação. Qualquer orçamento com premissa de crescimento, custo ou conversão se beneficia do mesmo princípio: revisar com a frequência que o negócio muda, não com a frequência que o calendário fiscal dita.

A pergunta prática não é se vale a pena adotar rolling forecast. É se o seu ciclo de revisão atual é mais rápido ou mais lento que a velocidade real do seu mercado.

**Fonte:** IBM, "Rolling Forecast". Caso Zillow: SphereOI, "How Zillow could have avoided its $500M AI mistake" (ver artigo completo sobre o caso).
