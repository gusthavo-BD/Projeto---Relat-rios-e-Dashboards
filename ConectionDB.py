import mysql.connector
conexao = mysql.connector.connect(
    host="localhost",      # servidor
    user="root",           # usuário do MySQL
    password="QPOLMNio889*ç",  # senha do MySQL
    database="barbearia"     # nome do banco que você criou
)
cursor = conexao.cursor()
cursor.execute("""

CREATE DATABASE IF NOT EXISTS barbearia;

USE barbearia;

CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    telefone VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS servicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    preco DECIMAL(10,2)
);

CREATE TABLE IF NOT EXISTS agendamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT,
    servico_id INT,
    data DATE,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (servico_id) REFERENCES servicos(id)
);

print("✅ Conectado e tabela criada (se não existia).")

