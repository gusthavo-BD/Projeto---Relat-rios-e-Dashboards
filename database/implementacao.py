# ---------- Configurações de conexão ----------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "2110",  # ajuste sua senha aqui
    "database": "barbearia",
    "auth_plugin": "mysql_native_password"
}

def ensure_database_exists(cfg):
    """
    Tenta conectar ao banco especificado; se não existir, cria o banco e retorna.
    """
    try:
        c = mysql.connector.connect(
            host=cfg["host"],
            user=cfg["user"],
            password=cfg["password"],
            auth_plugin=cfg.get("auth_plugin")
        )
        cur = c.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{cfg['database']}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        c.commit()
        cur.close()
        c.close()
    except Exception as e:
        # Se não conseguir criar o DB, repassa o erro
        raise

def get_connection():
    """
    Garante que o banco exista e retorna uma conexão com o database.
    """
    try:
        ensure_database_exists(DB_CONFIG)
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            auth_plugin=DB_CONFIG.get("auth_plugin")
        )
        return conn
    except Exception as e:
        raise

# inicialização da conexão e cursor
try:
    conexao = get_connection()
    cursor = conexao.cursor(buffered=True)
except Exception as e:
    st.error(f"Erro conectando ao banco: {e}")
    st.stop()

# ---------- Criação das tabelas se não existirem ----------
def criar_tabelas():
    statements = [
            CREATE TABLE IF NOT EXISTS clientes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(150) NOT NULL,
            telefone VARCHAR(30),
            email VARCHAR(150),
            data_cadastro DATE DEFAULT (CURRENT_DATE),
            observacoes TEXT
        ),
            CREATE TABLE IF NOT EXISTS clientes_enderecos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cliente_id INT NOT NULL,
            rua VARCHAR(200),
            numero VARCHAR(50),
            complemento VARCHAR(100),
            bairro VARCHAR(100),
            cidade VARCHAR(100),
            estado VARCHAR(50),
            cep VARCHAR(20),
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
        ),
            CREATE TABLE IF NOT EXISTS categorias_servico (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL
        ),
            CREATE TABLE IF NOT EXISTS servicos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(150) NOT NULL,
            descricao TEXT,
            categoria_id INT,
            duracao_min INT DEFAULT 30,
            preco DECIMAL(10,2) NOT NULL,
            ativo TINYINT(1) DEFAULT 1,
            FOREIGN KEY (categoria_id) REFERENCES categorias_servico(id) ON DELETE SET NULL
        ),
            CREATE TABLE IF NOT EXISTS funcionarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(150) NOT NULL,
            cargo VARCHAR(100),
            telefone VARCHAR(30),
            email VARCHAR(150),
            ativo TINYINT(1) DEFAULT 1
        ),
            CREATE TABLE IF NOT EXISTS horarios_funcionario (
            id INT AUTO_INCREMENT PRIMARY KEY,
            funcionario_id INT NOT NULL,
            dia_semana TINYINT, -- 0=domingo ... 6=sabado
            hora_inicio TIME,
            hora_fim TIME,
            FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id) ON DELETE CASCADE
        ),
            CREATE TABLE IF NOT EXISTS agendamentos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cliente_id INT NOT NULL,
            funcionario_id INT,
            data DATE NOT NULL,
            hora TIME,
            status ENUM('agendado','confirmado','realizado','cancelado') DEFAULT 'agendado',
            total DECIMAL(10,2) DEFAULT 0,
            observacoes TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
            FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id) ON DELETE SET NULL
        ),
            CREATE TABLE IF NOT EXISTS agendamento_itens (
            id INT AUTO_INCREMENT PRIMARY KEY,
            agendamento_id INT NOT NULL,
            servico_id INT NOT NULL,
            preco_servico DECIMAL(10,2),
            duracao_min INT,
            FOREIGN KEY (agendamento_id) REFERENCES agendamentos(id) ON DELETE CASCADE,
            FOREIGN KEY (servico_id) REFERENCES servicos(id) ON DELETE CASCADE
        ),
            CREATE TABLE IF NOT EXISTS produtos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(150) NOT NULL,
            descricao TEXT,
            preco_compra DECIMAL(10,2),
            preco_venda DECIMAL(10,2),
            unidade VARCHAR(30),
            ativo TINYINT(1) DEFAULT 1
        ),
            CREATE TABLE IF NOT EXISTS estoque (
            id INT AUTO_INCREMENT PRIMARY KEY,
            produto_id INT NOT NULL,
            quantidade DECIMAL(10,2) DEFAULT 0,
            minimo DECIMAL(10,2) DEFAULT 0,
            ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
        ),
            CREATE TABLE IF NOT EXISTS fornecedores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(200),
            telefone VARCHAR(50),
            email VARCHAR(150),
            observacoes TEXT
        ),
            CREATE TABLE IF NOT EXISTS compras (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fornecedor_id INT,
            data_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            valor_total DECIMAL(10,2),
            observacoes TEXT,
            FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id) ON DELETE SET NULL
        ),
            CREATE TABLE IF NOT EXISTS compras_itens (
            id INT AUTO_INCREMENT PRIMARY KEY,
            compra_id INT NOT NULL,
            produto_id INT NOT NULL,
            quantidade DECIMAL(10,2),
            preco_unit DECIMAL(10,2),
            FOREIGN KEY (compra_id) REFERENCES compras(id) ON DELETE CASCADE,
            FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
        ),
            CREATE TABLE IF NOT EXISTS vendas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            agendamento_id INT,
            cliente_id INT,
            data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            valor_total DECIMAL(10,2) NOT NULL,
            forma_pagamento ENUM('dinheiro','cartao','pix','parcelado','outros') DEFAULT 'dinheiro',
            observacoes TEXT,
            FOREIGN KEY (agendamento_id) REFERENCES agendamentos(id) ON DELETE SET NULL,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE SET NULL
        ),
            CREATE TABLE IF NOT EXISTS feedbacks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cliente_id INT NOT NULL,
            agendamento_id INT,
            nota TINYINT,
            comentario TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
            FOREIGN KEY (agendamento_id) REFERENCES agendamentos(id) ON DELETE SET NULL
        ),
        CREATE TABLE IF NOT EXISTS promocoes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            titulo VARCHAR(150),
            descricao TEXT,
            desconto_percent DECIMAL(5,2),
            data_inicio DATE,
            data_fim DATE,
            ativo TINYINT(1) DEFAULT 1
        )
    ]

    for s in statements:
        cursor.execute(s)
    conexao.commit()

