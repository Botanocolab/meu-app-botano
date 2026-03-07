Como meu CTO e Engenheiro Sênior de Trading Esportivo, sua tarefa agora é refatorar e expandir o app.py do Botano+. O objetivo é transformar o app de um simples scanner de 1x2 em uma Engine de Mercados Alternativos e Múltiplas de Valor, com foco em edge real, robustez operacional e gestão de risco.

VISÃO DO PRODUTO

1. Expansão de Mercados
O motor deve estar preparado para processar e exibir oportunidades nos mercados:
- Vencedor (1x2)
- Over/Under Gols (1.5, 2.5)
- BTTS
- Escanteios
- Cartões

Importante:
- O código deve processar apenas mercados realmente retornados pela API.
- Mercados ausentes devem ser ignorados sem quebrar a aplicação.
- A arquitetura deve ficar pronta para expansão futura.

2. Inteligência de Múltiplas
Crie uma seção chamada “Sugestão de Tripla do Dia”.
Ela deve combinar automaticamente 3 entradas com melhor Score Botano, respeitando:
- evitar repetir o mesmo jogo na tripla
- evitar mercados fortemente correlacionados
- evitar composições com risco inflado artificialmente
- exibir odd combinada, EV médio e score consolidado

3. Interface Premium
Layout em duas colunas:
- Esquerda: cards de oportunidades com badges de mercado (“1x2”, “Gols”, “BTTS”, “Cantos”, “Cartões”)
- Direita: painel de gestão com simulador, ROI real, win rate real, banca atual e resumo da Tripla do Dia

Toda a interface deve seguir a identidade dark/orange premium inspirada em plataformas de betting, com CSS customizado e sem blocos brancos ilegíveis.

4. Persistência Total
Toda aposta registrada via botão deve ser gravada na tabela apostas_simuladas do Supabase com os campos mínimos:
- created_at
- evento
- liga
- mercado
- linha
- selecao
- odd
- odd_media
- fair_prob
- ev_percent
- score_botano
- stake
- casa
- status
- resultado
- ticket_tipo

Se for múltipla, incluir também:
- grupo_id_multipla

5. Gestão de Risco
Toda oportunidade deve ser analisada sob ótica de risco.
Se o EV for positivo mas a odd representar alta variância, o sistema deve sinalizar isso visualmente com alerta de risco.
Distinguir:
- oportunidade premium
- oportunidade boa
- oportunidade agressiva
- oportunidade de risco elevado

REGRAS DE ENTREGA

- Entregue o arquivo app.py inteiro, completo e pronto para deploy.
- Não use placeholders.
- Não entregue trechos soltos.
- Use try-except em todas as chamadas da API e do Supabase.
- Evite qualquer erro de sintaxe, indentação ou caracteres que possam gerar tela branca.
- Siga PEP8.
- Estruture o código em funções claras, mesmo sendo um único arquivo.
- O botão de ação deve ser explícito, por exemplo:
  “Apostar no simulador: Over 2.5 em Flamengo x Vasco”
- Se algum mercado não estiver disponível na API atual, mantenha a estrutura pronta, mas não invente dados.
- Antes do código, explique a arquitetura, a lógica matemática (fair probability, EV, score, risco, múltiplas) e o fluxo dos dados entre API, motor do app e banco.

Agora gere o app.py completo do Botano+ V5.
