API Data-Barber

Este arquivo explica de forma simples como funciona a API do sistema Data-Barber, construída em FastAPI e conectada a um banco MySQL.
A API serve como ponte entre o sistema de CRM da barbearia e o banco de dados. Ela permite cadastrar, buscar, atualizar e listar: Clientes, Serviços, Barbeiros, Agendamentos, Vendas.
Tudo é feito por meio de rotas HTTP (GET, POST, PUT, DELETE).
A função get_db() permite que a API se conecte ao banco de dados MySQL. Ela estabelece uma conexão, realiza a ação requerida e, em seguida, encerra a conexão a cada solicitação.
Os dados enviados e recebidos estão em conformidade com os modelos Pydantic, assegurando que o formato esteja sempre correto.

COMO RODAR 
Para rodar a nossa API, você deve seguir os seguintes passos:
1. Ative o ambiente virtual (Windows):
   .\venv\Scripts\activate
2. Rode o servidor FastAPI com Uvicorn:
   uvicorn api:app --reload --port 8000
   
3. Acessar a API que ficará disponível em:
   http://127.0.0.1:8000
4. A documentação automatica estará em
   http://127.0.0.1:8000/docs

   A API Data-Barber é responsável por toda comunicação entre o sistema CRM e o banco de dados, oferecendo rotas simples e organizadas para gerenciar clientes, barbeiros, serviços, vendas e agendamentos.

   Exemplos de Requisições:
   
