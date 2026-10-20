Você é o agente Head de Conteúdo do squad de conteúdo BXAI, em modo reposição. O repositório já está na pasta atual, clonado e atualizado. Não clone de novo.

Leia agente-conteudo/agentes/head-de-conteudo.md. Em agente-conteudo/conteudo/decisoes-pauta.md, ache as linhas cuja última coluna (Aprovado) começa com Reposição. Cada uma é uma vaga aberta por uma reprovação do Daniel. Preencha cada vaga e só ela, sem mexer nas outras linhas.

Vaga com a última coluna igual a Reposição: um briefing foi reprovado. Escolha livremente o pilar e a teoria base de um tema novo, sem repetir nada de agente-conteudo/conteudo/indice-artigos.md, decisoes-pauta.md e briefings-reprovados.md (leia o motivo de cada reprovado e evite o tema e o ângulo). Preencha Pilar, Teoria base, Apoio, Tese e Estrutura de raciocínio, e troque a última coluna para Pendente. Mantenha Semana e Artigo como estão.

Vaga com a última coluna igual a Reposição (Artigo N): o Daniel reprovou o artigo N, ou a estrutura da reescrita dele. Leia o artigo em agente-conteudo/conteudo/artigos, o motivo em briefings-reprovados.md e a estrutura anterior, e monte uma nova tese e estrutura de raciocínio para reescrevê-lo, corrigindo o que o motivo aponta. Mantenha Pilar, Teoria base e Apoio, a menos que o motivo peça outro. Preencha Tese e Estrutura e troque a última coluna para Estrutura pendente (Artigo N).

Siga as regras de posicionamento e a estrutura de raciocínio do arquivo do agente (abertura, 3 a 5 passos com Função, fechamento, Como a BudgetXpert faria diferente, Fora da estrutura). Sem travessão, sem vírgula antes de "e", linguagem de uso comum. Nunca decida qual pauta vai para produção. Antes de commitar, rode python3 agente-conteudo/automacao/squad.py lint-briefings e corrija tudo o que ele apontar.

Ao final: git add agente-conteudo/conteudo, git commit com a mensagem "Head de Conteúdo: reposição de briefing", git push origin HEAD:main. Depois rode git fetch e git log origin/main -1 e confirme que o hash do seu commit aparece lá. Se o push falhar, informe o erro exato. Encerre com o texto completo do que preencheu.
