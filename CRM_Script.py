import mysql.connector

conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="admin"
)

cursor = conexao.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS barbearia_crm")
cursor.close()
conexao.close()

# Conectar ao banco
conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="admin",
    database="barbearia_crm"
)
cursor = conexao.cursor()

# --- Tabelas principais ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(100),
    data_cadastro DATE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS funcionarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cargo VARCHAR(50),
    telefone VARCHAR(20),
    salario DECIMAL(10,2)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS servicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    preco DECIMAL(10,2) NOT NULL,
    duracao_min INT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    preco DECIMAL(10,2),
    quantidade_estoque INT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS agendamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT,
    funcionario_id INT,
    servico_id INT,
    data DATETIME,
    status VARCHAR(20) DEFAULT 'Pendente',
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id),
    FOREIGN KEY (servico_id) REFERENCES servicos(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS vendas_produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT,
    produto_id INT,
    quantidade INT,
    data_venda DATE,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS pagamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    agendamento_id INT,
    valor DECIMAL(10,2),
    forma_pagamento VARCHAR(50),
    data_pagamento DATE,
    FOREIGN KEY (agendamento_id) REFERENCES agendamentos(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS avaliacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT,
    funcionario_id INT,
    nota INT CHECK (nota BETWEEN 1 AND 5),
    comentario TEXT,
    data_avaliacao DATE,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS estoque_movimentacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    produto_id INT,
    tipo VARCHAR(10),  -- 'entrada' ou 'saida'
    quantidade INT,
    data_movimentacao DATE,
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS campanhas_marketing (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    descricao TEXT,
    data_inicio DATE,
    data_fim DATE,
    investimento DECIMAL(10,2)
)
""")

conexao.commit()
cursor.close()
conexao.close()

print("✅ Banco de dados 'barbearia_crm' e tabelas criadas com sucesso!")
