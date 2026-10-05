# A Zillow perdeu US$ 881 milhões sem errar uma única conta, por quê?

Em 2021, a Zillow Offers, braço de compra e venda direta de imóveis da Zillow (zillow.com), maior plataforma de buscas imobiliárias dos Estados Unidos, perdeu US$ 881 milhões comprando casas com um algoritmo de precificação, um programa que estimava quanto cada imóvel valia. Esse algoritmo não calculou errado. Funcionava exatamente como foi treinado para funcionar. O problema foi outro. A estimativa de preço era uma premissa, a hipótese sobre o futuro em que toda a compra se apoiava. Ninguém definiu quem revalidaria essa premissa, com que critério e em que momento.

Até fevereiro de 2021, o algoritmo só gerava estimativas de referência, uma espécie de palpite informativo sobre o valor de um imóvel. A partir daquele mês, a Zillow passou a transformar essa mesma estimativa em oferta de compra vinculante, ou seja, uma oferta que a obrigava a comprar pelo preço calculado. Fez isso sem criar nenhuma camada nova de governança, as regras e os responsáveis que controlam como uma ferramenta é usada. O algoritmo continuou calculando do mesmo jeito. O que mudou foi o tamanho da consequência de cada erro. É o que acontece quando uma premissa muda de papel e ninguém percebe.

## A premissa não é um fato, é uma decisão

Num orçamento, a premissa funciona do mesmo jeito: é a hipótese sobre o futuro em que os números se apoiam. Parece um dado objetivo, mas é uma escolha. Alguém decidiu que o custo ia subir 8%, ou que a taxa de conversão ia se manter em 3%, ou que o preço do produto ficaria estável. Essa escolha foi feita com base em alguma informação disponível naquele momento. Essa informação tem prazo de validade.

O erro mais comum não é escolher a premissa errada. É tratar a premissa como se fosse permanente, como se o momento em que ela foi definida não importasse. Foi exatamente isso que aconteceu com o algoritmo da Zillow: ele tinha sido treinado num mercado imobiliário em alta constante, sem nenhuma representação de um mercado em desaceleração. Quando o mercado esfriou em meados de 2021, o algoritmo seguiu precificando como se a alta continuasse.

Existe uma forma simples de testar se uma premissa está sob controle. Três perguntas, nessa ordem.

## Pergunta 1: quem definiu

Toda premissa precisa ter um dono. Não um dono formal no organograma, um dono de fato, alguém que pode explicar por que aquele número e não outro. No caso da Zillow, a conversão da estimativa em oferta vinculante, em fevereiro de 2021, foi uma decisão de negócio tomada em cima de um algoritmo, mas sem transferir para alguém a responsabilidade de vigiar se aquela premissa ainda fazia sentido depois da mudança de uso. Sem dono claro, a premissa costuma ser herdada de um processo antigo ou copiada de um contexto que já não existe.

## Pergunta 2: com que critério

Depois do dono, vem o critério. Por que esse número e não outro. Em meados de 2021, um projeto interno da Zillow apelidado de "Project Ketchup" fez a gestão sobrescrever manualmente as ofertas do próprio algoritmo para cima, para bater meta de volume de compras. Isso removeu a checagem humana independente que existia antes, exatamente no momento em que o critério original precisava ser mais rigoroso, não menos. Um critério documentado e estável é o que permite auditar a premissa sem depender da pressão do trimestre para decidir o que é razoável.

## Pergunta 3: quando revisar

Essa é a pergunta que mais falta nas empresas, mesmo nas que têm dono e critério definidos. Toda premissa precisa de uma data de validade, um gatilho que diz quando ela deve ser reexaminada, não abandonada, reexaminada. O algoritmo da Zillow também sofria do que a análise da Shackleford, consultoria de liderança em IA, chama de seleção adversa: como a empresa comprava pelo valor médio estimado, donos de imóveis acima da média preferiam vender no mercado aberto, enquanto donos de imóveis com problemas aceitavam a oferta rápido. A Zillow foi, sem perceber, comprando sistematicamente os imóveis que o próprio mercado já estava descontando. Sem um gatilho de revisão, ninguém parou para checar se esse padrão de quem aceitava a oferta tinha mudado.

## O que o caso Zillow confirma

No terceiro trimestre de 2021, a Zillow registrou US$ 304 milhões de baixa contábil, o reconhecimento de uma perda no balanço, só no estoque de imóveis, parte dos US$ 881 milhões perdidos no ano. A empresa chegou a acumular US$ 3,8 bilhões em estoque de casas e vendeu cerca de 7.000 delas com prejuízo, tendo pago acima do valor de mercado em 65% dos imóveis que comprou. No anúncio do encerramento da Zillow Offers, em novembro de 2021, cortou cerca de 2.000 funcionários, um quarto do quadro da divisão. As ações caíram 18% no dia, fechando o ano com queda acumulada de 50%. O CEO da Zillow, Rich Barton, resumiu o problema como a incapacidade do próprio algoritmo de prever com confiabilidade quanto capital a empresa precisaria arriscar no futuro. Recusou atribuir a causa a eventos externos imprevisíveis.

Nenhum desses números veio de uma conta errada. Vieram de uma premissa sem dono que vigiasse a mudança de contexto, sem critério protegido da pressão de meta e sem gatilho que avisasse quando o padrão do mercado mudou.

## Erros comuns ao tentar aplicar isso

Três confusões aparecem com frequência quando uma empresa tenta colocar essas perguntas em prática.

A primeira é confundir revisão com mudança de meta. Revisar uma premissa não é afrouxar um objetivo, é checar se a base de cálculo daquele objetivo ainda reflete a realidade. Uma meta pode continuar a mesma mesmo depois que a premissa por trás dela foi atualizada.

A segunda é tratar o critério como propriedade de uma pessoa, em vez de um registro da empresa. Quando o critério mora só na cabeça de quem fez a conta, ele desaparece junto com essa pessoa na primeira saída ou troca de função. Um critério documentado sobrevive à equipe que o criou.

A terceira é esperar o fechamento do trimestre ou do ano para revisar qualquer coisa. A data de revisão de uma premissa não precisa seguir o calendário fiscal, precisa seguir a velocidade real da variável que ela tenta prever. Uma premissa de custo de matéria-prima em mercado volátil pode precisar de revisão mensal, mesmo dentro de um ciclo orçamentário anual.

## Como aplicar na prática

Antes de fechar qualquer premissa de orçamento, três respostas precisam existir por escrito, não na memória de quem fez a conta. Quem é o responsável por esse número. Qual foi o critério ou a fonte usada para chegar nele. Quando essa premissa será reexaminada e sob qual gatilho.

Pode começar como uma coluna extra na própria planilha de orçamento, ao lado de cada premissa relevante. O que importa não é a ferramenta, é o hábito de nunca deixar uma premissa sem essas três respostas antes de ela entrar no orçamento oficial.

## Por que isso é mais importante do que parece

Essas perguntas são a diferença entre uma empresa que toma uma decisão consciente de manter uma premissa e uma empresa que simplesmente não percebeu que a premissa envelheceu. A primeira é um risco calculado. A segunda é um ponto cego.

O dado da EY, rede global de auditoria e consultoria, citado pelo Journal of Accountancy, revista profissional de contabilidade, mostra que 86% dos controllers, os responsáveis pelo controle financeiro e contábil das empresas, esperam que o próprio papel mude de forma significativa nos próximos cinco anos. Parte dessa mudança é justamente essa, sair da função de registrar o número fechado e assumir a função de garantir que cada premissa por trás do número tenha dono, critério e data de revisão. Isso é controladoria, não é auditoria. Auditoria encontra o problema depois que ele já aconteceu. As três perguntas evitam que ele aconteça.

## O que fica

A pergunta que a maioria das empresas faz é se a premissa está certa. A pergunta certa é se alguém ainda é dono dela. A Zillow não perdeu US$ 881 milhões porque seu algoritmo calculava mal. Perdeu porque uma premissa pode nascer certa e morrer errada sem que ninguém tenha tomado uma única decisão errada no caminho, ela só ficou velha em silêncio, porque ninguém tinha a tarefa de notar isso. Dono, critério e data de revisão não evitam o erro de cálculo. Evitam que esse erro fique invisível até custar caro.

Fonte: EY (ey.com), rede global de serviços profissionais de auditoria e consultoria, "Global DNA of the Financial Controller Survey" (2024), citado pelo Journal of Accountancy. Caso Zillow: Shackleford, consultoria de liderança em IA (shackleford.coach), "Zillow Offers Loss: A $881M Study in AI Model Risk". GeekWire, "Why the iBuying algorithms failed Zillow, and what it says about the business world's love affair with AI". IdeaProof, "Why Did Zillow Offers Fail? $0 Lost & What Went Wrong (2021)".
