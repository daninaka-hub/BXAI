# Forecasting Methods

Dados, pesquisas, conclusões e estratégias sobre métodos de previsão (rolling forecast, driver-based planning, beyond budgeting), coletados pelo BXAI Content Squad.

Cada entrada deve conter: dado ou conclusão, fonte, link (se houver), data de coleta.

---

45% das empresas ainda planejam a partir de orçamentos estáticos anuais, apesar da disponibilidade de ferramentas de planejamento contínuo baseado em drivers.
Fonte: Jedox, "Driver Based Planning for FP&A Improve Forecast Accuracy".
Link: https://www.jedox.com/en/blog/driver-based-planning/
Data de coleta: 2026-10-01

[Teórico] Rolling forecast é um modelo de planejamento que prevê continuamente o desempenho futuro, sempre mantendo um horizonte fixo à frente (ex: 12 meses). Ao final de cada período, o resultado real substitui a previsão daquele mês e um novo mês é adicionado ao final, mantendo o horizonte sempre completo. Atualização típica: mensal ou trimestral. Difere do orçamento estático anual, que fixa o ano inteiro de uma vez e só é revisto na virada do ciclo seguinte.
Fonte: IBM, "Rolling Forecast".
Link: https://www.ibm.com/think/topics/rolling-forecast
Data de coleta: 2026-10-01


O guia da AFP (publicado em março de 2024) define o modelo baseado em drivers como o que liga poucos direcionadores operacionais aos resultados financeiros, com ganho de velocidade, alinhamento e flexibilidade para cenários e rolling forecasts. Os fatores de sucesso citados são validação entre áreas, drivers com poder preditivo comprovado, o menor número possível de drivers e testes e ajustes contínuos. O guia também alerta que relações históricas podem não prever o futuro.
Fonte: AFP, "AFP FP&A Guide to Driver-based Models and Plans".
Link: https://www.pelotongroup.com/wp-content/uploads/2024/12/EPM-2024-fpa-guide-to-driver-based-models-and-plans.pdf
Data de coleta: 2026-10-05

Segundo o AFP FP&A Benchmarking Survey 2026, só 14% das equipes de finanças acompanham formalmente a acurácia do forecast, e 86% não têm medição estruturada. O dado aparece em artigo de opinião publicado em 28/04/2026 no site da AFP, assinado pelo CEO da FinHelm, que propõe um score de 0 a 100 combinando acurácia, viés, volatilidade e persistência do erro.
Fonte: AFP, "Your Forecast Doesn't Have a Score. It Should." (Jason Brisbane, 28/04/2026).
Link: https://www.financialprofessionals.org/training-resources/resources/articles/Details/your-forecast-does-not-have-a-score-it-should
Data de coleta: 2026-10-05

[Teórico] A McKinsey propõe quatro frentes para melhorar o forecast. Primeiro, montar um momentum case, uma linha de base sem viés, separada do plano de negócios, para que o orçamento não vire forecast. Segundo, usar insumos operacionais (como produtividade e entregas no prazo) e externos, não só dados financeiros. Terceiro, automatizar a coleta de dados com ferramentas simples. Quarto, medir a efetividade com granularidade, para detectar indicadores ignorados antes que o problema chegue ao resultado. O texto cita que rolling forecasts, com atualizações frequentes, tiveram melhor satisfação dos CFOs que o forecast anual. Texto de 13/03/2020.
Fonte: McKinsey & Company, "Bringing the real world into your forecasting process" (13/03/2020).
Link: https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights/bringing-a-real-world-edge-to-forecasting
Data de coleta: 2026-10-05

A velocidade de replanejamento continua sendo o gargalo: apenas 4% das organizações conseguem atualizar uma previsão em um dia, e 54% das equipes se descrevem apenas como conseguindo dar conta do trabalho. Dados da pesquisa FP&A Trends 2026, citados pela Board International, que patrocina o levantamento. A mesma página propõe o conceito que a Board chama de Agency Shift, a transferência da iniciativa analítica de humanos para sistemas, com o argumento de que o ganho está em reduzir a latência de decisão e mover o ciclo de planejamento de dirigido por calendário para dirigido por evento, mantendo em finanças a accountability, o julgamento e a propriedade da decisão. Dado de segunda mão.
Fonte: Board International, "AI in FP&A: Who Acts First in Financial Planning and Analysis?" (cita FP&A Trends 2026).
Link: https://www.board.com/blog/ai-in-fpa-who-acts-first-in-financial-planning-and-analysis
Data de coleta: 2026-10-06

Na mesma pesquisa do Gartner com 160 líderes seniores de finanças (campo de janeiro a abril de 2026), 55% dos CFOs relataram retorno positivo geral das iniciativas de IA de 2025, mas 57% disseram que o retorno era pouco claro quando avaliado caso de uso por caso de uso. Entre os objetivos declarados de IA em 2025, 73% citaram produtividade e 59% redução de custo, com objetivos ligados a risco, resiliência e receita na faixa de 20% a 30%. A recomendação do Gartner é não deixar o apelo do retorno rápido deslocar casos de uso de maturação mais lenta, e o planejamento de cenários e o forecasting aparecem justamente nesse grupo lento. Dados lidos na cobertura do CFO Dive e do CPA Practice Advisor, porque a página do Gartner devolveu erro de acesso.
Fonte: Gartner, "Gartner Says CFOs Must Take a More Disciplined Approach to Finance AI Investment" (24/09/2026), via CFO Dive e CPA Practice Advisor.
Link: https://www.cfodive.com/news/cfos-need-realistic-ai-time-value-expectations-gartner/831315/
Data de coleta: 2026-10-06

[Teórico] O capítulo de acurácia de "Forecasting: Principles and Practice" (3a edição), de Rob Hyndman e George Athanasopoulos (Monash University), define a disciplina de medir previsão separando os dados em conjunto de treino, usado para estimar o modelo, e conjunto de teste, usado só para avaliar. A recomendação é reservar cerca de 20% da série para teste, com teste pelo menos do tamanho do horizonte máximo de previsão, e o alerta central é que ajustar bem o treino não garante prever bem. O texto distingue resíduo de erro de previsão: o resíduo vem do treino e de previsão de um passo, o erro de previsão vem do conjunto de teste e pode envolver múltiplos passos. São três famílias de métricas. Erros dependentes de escala, com MAE (média dos erros absolutos) e RMSE (raiz da média dos erros ao quadrado), ficam na unidade original e por isso não comparam séries diferentes; minimizar RMSE leva a previsões de média e minimizar MAE leva a previsões de mediana. Erros percentuais, com o MAPE, permitem comparar entre conjuntos de dados, mas o MAPE é indefinido ou infinito quando o observado é zero e só faz sentido quando a escala tem zero significativo, o que invalida casos como temperatura em Celsius. A variante sMAPE foi criada para corrigir a penalização assimétrica entre erro para cima e para baixo, mas segue problemática perto de zero e os autores recomendam não usá-la. Erros escalados, com MASE e RMSSE, normalizam o erro contra um método ingênuo de referência, e valor abaixo de um indica desempenho melhor que o ingênuo. O encadeamento prático é separar treino e teste, calcular o erro no teste e escolher a métrica conforme o objetivo, seja comparar a mesma série, séries de escalas diferentes, ou medir contra benchmark.
Fonte: Rob J. Hyndman e George Athanasopoulos, "Forecasting: Principles and Practice" (3a edição), seção 5.8 Evaluating point forecast accuracy, Monash University.
Link: https://otexts.com/fpp3/accuracy.html
Data de coleta: 2026-10-06

Economic Letter do Fed de São Francisco, de 5 de outubro de 2026, testa a qualidade das previsões feitas por diretores financeiros usando os dados do The CFO Survey, conduzido trimestralmente pela Duke Fuqua com os Feds de Richmond e Atlanta. A amostra do segundo trimestre de 2026 teve cerca de 530 respondentes de empresas de portes variados nos principais setores. Os autores montaram uma série anual de expectativas de salário a partir de 2001, pegando sempre a expectativa do quarto trimestre para o ano calendário seguinte, agregaram ponderando por emprego e mediram a acurácia pelo erro quadrático médio contra o realizado, usando o Wage Growth Tracker do Fed de Atlanta e dados de folha. O resultado central é um raro benchmark de acurácia de previsão de executivo de finanças: entre 2002 e 2025, a expectativa de crescimento salarial dos CFOs teve erro de previsão de 0,69 ponto percentual. Nas três janelas testadas, 2002 a 2025, 2014 a 2025 e o período pós pandemia, as previsões dos CFOs ficaram melhores que as do Michigan Surveys of Consumers e que as do Survey of Consumer Expectations do Fed de Nova York. Para 2026, os CFOs projetam 4% de crescimento nominal de salários e 2,4% de crescimento de emprego em tempo integral, contra cerca de 3,5% que projetavam para 2024 e 2025, com pico da série em 7,0% em 2022 e crescimento real de salários projetado em apenas 0,4 ponto percentual.
Fonte: FRBSF Economic Letter 2026-28, "What Do Financial Officers Predict for the Labor Market?" (Stephie Fried, Tobin Graf, Simar Malhotra e Sanjay R. Singh, 05/10/2026).
Link: https://frbsf.org/research-and-insights/publications/economic-letter/2026/10/what-do-financial-officers-predict-for-labor-market
Data de coleta: 2026-10-07

A 2026 AFP FP&A Benchmarking Survey, com 332 praticantes e campo em agosto e setembro de 2025, dá o retrato de adoção de prática de previsão: 43% usam rolling forecast, 38% usam planejamento de cenários estruturado e o ciclo orçamentário médio é de 8,7 semanas. A leitura da própria AFP é que o cenário estruturado separa os times de melhor desempenho. Publicação de 20 de janeiro de 2026, portanto fora da janela de três meses, registrada por ser dado de associação profissional com amostra declarada.
Fonte: AFP (Association for Financial Professionals), release da 2026 AFP FP&A Benchmarking Survey (20/01/2026).
Link: https://www.financialprofessionals.org/about/learn-more/press-releases/Details/afp-survey-reveals-structured-scenario-planning-separates-top-performing-corporate-finance-teams
Data de coleta: 2026-10-07

[Teórico] Forecast Value Added (FVA) é o framework que mede se cada etapa do processo de previsão realmente melhora o número final. A definição usada é a de Gilliland (2002): a mudança em uma métrica de desempenho de previsão que pode ser atribuída a uma etapa ou participante específico do processo. O ponto de partida é um benchmark ingênuo, tipicamente o random walk, em que a previsão do próximo período é o realizado do período anterior. A partir daí cada etapa seguinte é medida contra a anterior: previsão estatística, ajustes de julgamento, revisão gerencial, consenso. Etapas que não melhoram a métrica são classificadas como desperdício de processo, e a recomendação é eliminá-las. O caso Newell Rubbermaid citado ilustra o mecanismo: o naive entregou 60% de acurácia, a previsão estatística acrescentou 5 pontos percentuais e a revisão gerencial subtraiu 3 pontos, ou seja, destruiu valor. Morlidge (2014b) analisou oito empresas de bens de consumo e industriais e encontrou que 52% das previsões não conseguiram superar o benchmark ingênuo, com a recomendação de focar menos em otimizar o processo e mais em detectar onde ele está gravemente ruim. A revisão de Lawrence et al. (2006), que cobriu mais de 200 estudos, conclui que o julgamento humano pode trazer benefício relevante mas também está sujeito a vieses relevantes, que é exatamente a tensão que o FVA se propõe a medir de forma objetiva. Nota: a lista completa de autores e a data da referência não apareceram na página lida, então a autoria registrada se limita às citações internas.
Fonte: "Forecasting: theory and practice", capítulo de prática, versão online da referência enciclopédica da área.
Link: https://forecasting-encyclopedia.com/practice.html
Data de coleta: 2026-10-07
