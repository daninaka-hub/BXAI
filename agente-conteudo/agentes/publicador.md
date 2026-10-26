# Agente: Publicador

## Objetivo
Publicar no LinkedIn o post do artigo aprovado, na data e hora que o Daniel escolher, e registrar o artigo publicado na aba Publicado do painel.

## Diferença dos outros agentes
Não é uma execução de IA. É uma automação mecânica dentro de squad.py, acionada pelos botões do painel, sem julgamento de conteúdo. O post já está pronto (escrito pelo Copywriter); o Publicador só agenda e confirma.

## Entrada
Artigo com status "Aprovado" no índice, e o texto já pronto em conteudo/posts-linkedin/{slug}.md.

## Fluxo
1. Artigo vira "Aprovado" (botão Aprovar do card) e passa a aparecer na aba Agendar, sem agendamento ainda, com o botão "Publicar".
2. Daniel clica em "Publicar". A página pergunta o link do artigo já publicado no blog (para substituir o texto "[link do artigo]" do post) e a data e hora do agendamento, horário de São Paulo. Confirmando, abre uma issue pré-preenchida "Agendar publicação: Artigo N (AAAA-MM-DD HH:MM)".
3. A Action aprovar.yml roda `squad.py agendar N "data-hora" "link"`, que chama a API do Typefully (POST /v2/social-sets/{id}/drafts, campo publish_at com o horário escolhido) e grava o retorno em status/publicacoes.json.
4. O card segue na aba Agendar, agora mostrando "Agendado para DD/MM às HH:MM" e o botão "Marcar como publicado".
5. Quando o post sai no LinkedIn, Daniel confere e clica em "Marcar como publicado" (issue "Marcar como publicado: Artigo N"). A Action roda `squad.py publicado N`, tenta buscar o link do post publicado no Typefully e move o artigo para a aba Publicado.

## Pré-requisitos (fora do squad, só o Daniel faz)
- Conta no Typefully com o perfil do LinkedIn da BudgetXpert conectado.
- Gerar a API key em Typefully (Configurações, API) e pegar o social_set_id.
- Cadastrar dois segredos no repositório daninaka-hub/BXAI (Settings, Secrets and variables, Actions): TYPEFULLY_API_KEY e TYPEFULLY_SOCIAL_SET_ID.
Sem os dois segredos, o botão Publicar devolve o aviso "Faltam as credenciais do Typefully" na issue, sem travar o resto do painel.

## Regras
- Nunca agenda sem o link do artigo no post. Se o texto ainda tem o marcador "[link do artigo]" depois de tentar a substituição, a issue é recusada com a instrução de abrir de novo com o link preenchido.
- A confirmação de que o post realmente saiu é sempre manual (decisão do Daniel, 26/10): a automação não promete que o horário agendado no Typefully é o horário real de publicação.
- Um artigo só sai da aba Agendar quando o Daniel confirma a publicação, nunca sozinho por tempo.

## Como gravar
Estado em status/publicacoes.json (por código de artigo: estado agendado ou publicado, quando, typefully_id, link_artigo, link_post). Não editar à mão; só squad.py agendar e squad.py publicado escrevem nesse arquivo.
