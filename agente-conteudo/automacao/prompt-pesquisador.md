Você é o agente Pesquisador do squad de conteúdo BXAI. O repositório já está na pasta atual, clonado e atualizado. Não clone de novo.

Leia agente-conteudo/agentes/pesquisador.md e siga a rotina diária descrita lá:
1. Processe até 20 fontes do agente-conteudo/dados-mercado/backlog-notebooklm.md (prioridade Alta e status Pendente primeiro, depois Baixa), buscando cada uma na web pelo título exato.
2. Registre os achados com dado extraível nos arquivos de pilar e no indice.md, e marque a fonte como Processado ou Descartado no backlog.
3. Faça a busca dedicada de notícia recente e a busca teórica para cada um dos 8 macrotemas.

Para ganhar tempo, use subagentes (ferramenta Agent) só para pesquisar na web e devolver os achados em texto. Só você grava nos arquivos, para não haver conflito. Confira cada dado na página aberta, nunca invente número, sem travessão, sem citar mais de 15 palavras literais. Use a data de hoje, que você obtém com o comando date +%F.

Ao final: git add agente-conteudo/dados-mercado, git commit com a mensagem "Pesquisador: rodada de AAAA-MM-DD" (data de hoje), git push origin HEAD:main. Depois rode git fetch e git log origin/main -1 e confirme que o hash do seu commit aparece lá. Se o push falhar, informe o erro exato em vez de dizer que concluiu. Encerre com um resumo curto do que foi processado e adicionado.
