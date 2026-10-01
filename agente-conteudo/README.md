# BXAI Content Squad

Squad de produção de conteúdo para blog e LinkedIn da BudgetXpert, baseado em dados de mercado sobre FP&A, Controllership e Planning.

## Estrutura

- `dados-mercado/`: base de dados por pilar temático, mais o índice central e o backlog de fontes do NotebookLM a processar.
- `agentes/`: prompt de instrução de cada papel do squad (Pesquisador, Processador, Head de Conteúdo, Copywriter, Designer).
- `conteudo/`: artigos de blog, posts de LinkedIn, imagens, e o log de decisões de pauta.

## Fluxo

1. Pesquisador roda diariamente (tarefa agendada), processa o backlog e faz busca de conteúdo novo, grava em dados-mercado.
2. Processador normaliza o que entra, evita duplicação, atualiza o índice.
3. Head de Conteúdo roda semanalmente (tarefa agendada, toda segunda), analisa a base e traz 3 sugestões de pauta, registradas em conteudo/decisoes-pauta.md.
4. Daniel escolhe 1, 2 ou as 3 pautas.
5. Copywriter escreve o artigo de blog e o post de LinkedIn para cada pauta escolhida.
6. Designer gera a imagem de cada post.

## Pilares de dados

Controllership, Finance Automation, Forecasting Methods, FP&A Fundamentals, Integrated Planning, Strategic Planning, Leadership Roles, Organization.
