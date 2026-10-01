A Zillow perdeu US$ 500 milhões usando o modelo de orçamento mais comum do mercado. Existe um método que teria evitado isso.
.
.
.
.
Chama-se rolling forecast. Em vez de fechar o ano inteiro em dezembro e só revisar 12 meses depois, a empresa mantém sempre um horizonte fixo à frente, geralmente 12 meses. A atualização é mês a mês: o real substitui a previsão e um mês novo entra no final da janela.

O algoritmo da Zillow funcionava como orçamento estático em alta velocidade: fixava a premissa de preço e repetia, sem ciclo de revisão. Rolling forecast obriga essa pergunta a cada atualização: o dado que uso hoje ainda reflete o mercado de hoje?

Não precisa de algoritmo pra esse risco existir. A maioria das empresas descobre que a premissa envelheceu no mesmo momento em que descobre o prejuízo, porque são a mesma descoberta. Rolling forecast não é uma técnica mais sofisticada. É a decisão de não deixar em aberto de quanto em quanto tempo uma premissa deixa de valer.

Artigo completo, com a análise do caso Zillow: [link do artigo]

#ForecastingMethods #RollingForecast #FPA #CFO
