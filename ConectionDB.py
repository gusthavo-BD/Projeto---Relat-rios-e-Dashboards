import mysql.connector

# 1 - Conexão inicial (sem banco selecionado)
conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="admin"  # coloque sua senha do MySQL
)

cursor = conexao.cursor()

# 2 - Criar o banco se não existir
cursor.execute("CREATE DATABASE IF NOT EXISTS barbearia")
print("✅ Banco 'barbearia' criado (ou já existia).")

cursor.close()
conexao.close()

# 3 - Conectar já no banco barbearia
conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="admin",
    database="barbearia"
)
cursor = conexao.cursor()

# 4 - Criar tabelas
cursor.execute("""
CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    telefone VARCHAR(20)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS servicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    preco DECIMAL(10,2) NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS agendamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT,
    servico_id INT,
    data DATE,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (servico_id) REFERENCES servicos(id)
)
""")

print("✅ Tabelas criadas/verificadas.")

# 5 - Inserir serviços padrão se ainda não existirem
cursor.execute("SELECT COUNT(*) FROM servicos")
qtd = cursor.fetchone()[0]

if qtd == 0:
    cursor.executemany(
        "INSERT INTO servicos (nome, preco) VALUES (%s, %s)",
        [
            ("Corte de Cabelo", 45.00),
            ("Barba", 35.00),
            ("Corte + Barba", 70.00),
            ("Sobrancelha", 20.00),
            ("Hidratação Capilar", 50.00)
        ]
    )
    conexao.commit()
    print("✅ Serviços padrão inseridos.")
else:
    print("ℹ️ Serviços já existentes, nada foi inserido.")

cursor.close()
conexao.close()
print("🚀 Setup do CRM de barbearia concluído!")


