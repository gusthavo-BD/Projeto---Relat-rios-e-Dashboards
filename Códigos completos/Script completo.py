"""
1) Instale dependências (no terminal/PowerShell):
   pip install streamlit mysql-connector-python pandas matplotlib

2)  Rodar a interface Streamlit:
   streamlit run c:/caminho/para/Projeto-uninove.py

Observações:
- Ajuste host/user/password conforme seu MySQL.
"""

import streamlit as st
import pandas as pd
import mysql.connector
import mysql.connector.errors
import matplotlib.pyplot as plt
from datetime import date, datetime, time

#------------Tela de Login---------------------

def login_page():
    st.title("🔐 Data-Barber - Login")

    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if username == "admin" and password == "admin":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos!")

# Inicializa sessão
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Se não estiver logado → mostra tela de login
if not st.session_state.authenticated:
    login_page()
    st.stop()
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

# inicializa conexão e cursor
try:
    conexao = get_connection()
    cursor = conexao.cursor(buffered=True)
except Exception as e:
    st.error(f"Erro conectando ao banco: {e}")
    st.stop()

# ---------- Criação das tabelas se não existirem ----------
def criar_tabelas():
    statements = [
        """CREATE TABLE IF NOT EXISTS clientes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(150) NOT NULL,
            telefone VARCHAR(30),
            email VARCHAR(150),
            data_cadastro DATE DEFAULT (CURRENT_DATE),
            observacoes TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS clientes_enderecos (
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
        )""",
        """CREATE TABLE IF NOT EXISTS categorias_servico (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS servicos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(150) NOT NULL,
            descricao TEXT,
            categoria_id INT,
            duracao_min INT DEFAULT 30,
            preco DECIMAL(10,2) NOT NULL,
            ativo TINYINT(1) DEFAULT 1,
            FOREIGN KEY (categoria_id) REFERENCES categorias_servico(id) ON DELETE SET NULL
        )""",
        """CREATE TABLE IF NOT EXISTS funcionarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(150) NOT NULL,
            cargo VARCHAR(100),
            telefone VARCHAR(30),
            email VARCHAR(150),
            ativo TINYINT(1) DEFAULT 1
        )""",
        """CREATE TABLE IF NOT EXISTS horarios_funcionario (
            id INT AUTO_INCREMENT PRIMARY KEY,
            funcionario_id INT NOT NULL,
            dia_semana TINYINT, -- 0=domingo ... 6=sabado
            hora_inicio TIME,
            hora_fim TIME,
            FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id) ON DELETE CASCADE
        )""",
        """CREATE TABLE IF NOT EXISTS agendamentos (
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
        )""",
        """CREATE TABLE IF NOT EXISTS agendamento_itens (
            id INT AUTO_INCREMENT PRIMARY KEY,
            agendamento_id INT NOT NULL,
            servico_id INT NOT NULL,
            preco_servico DECIMAL(10,2),
            duracao_min INT,
            FOREIGN KEY (agendamento_id) REFERENCES agendamentos(id) ON DELETE CASCADE,
            FOREIGN KEY (servico_id) REFERENCES servicos(id) ON DELETE CASCADE
        )""",
        """CREATE TABLE IF NOT EXISTS produtos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(150) NOT NULL,
            descricao TEXT,
            preco_compra DECIMAL(10,2),
            preco_venda DECIMAL(10,2),
            unidade VARCHAR(30),
            ativo TINYINT(1) DEFAULT 1
        )""",
        """CREATE TABLE IF NOT EXISTS estoque (
            id INT AUTO_INCREMENT PRIMARY KEY,
            produto_id INT NOT NULL,
            quantidade DECIMAL(10,2) DEFAULT 0,
            minimo DECIMAL(10,2) DEFAULT 0,
            ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
        )""",
        """CREATE TABLE IF NOT EXISTS fornecedores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(200),
            telefone VARCHAR(50),
            email VARCHAR(150),
            observacoes TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS compras (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fornecedor_id INT,
            data_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            valor_total DECIMAL(10,2),
            observacoes TEXT,
            FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id) ON DELETE SET NULL
        )""",
        """CREATE TABLE IF NOT EXISTS compras_itens (
            id INT AUTO_INCREMENT PRIMARY KEY,
            compra_id INT NOT NULL,
            produto_id INT NOT NULL,
            quantidade DECIMAL(10,2),
            preco_unit DECIMAL(10,2),
            FOREIGN KEY (compra_id) REFERENCES compras(id) ON DELETE CASCADE,
            FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
        )""",
        """CREATE TABLE IF NOT EXISTS vendas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            agendamento_id INT,
            cliente_id INT,
            data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            valor_total DECIMAL(10,2) NOT NULL,
            forma_pagamento ENUM('dinheiro','cartao','pix','parcelado','outros') DEFAULT 'dinheiro',
            observacoes TEXT,
            FOREIGN KEY (agendamento_id) REFERENCES agendamentos(id) ON DELETE SET NULL,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE SET NULL
        )""",
        """CREATE TABLE IF NOT EXISTS feedbacks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cliente_id INT NOT NULL,
            agendamento_id INT,
            nota TINYINT,
            comentario TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
            FOREIGN KEY (agendamento_id) REFERENCES agendamentos(id) ON DELETE SET NULL
        )""",
        """CREATE TABLE IF NOT EXISTS promocoes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            titulo VARCHAR(150),
            descricao TEXT,
            desconto_percent DECIMAL(5,2),
            data_inicio DATE,
            data_fim DATE,
            ativo TINYINT(1) DEFAULT 1
        )"""
    ]

    for s in statements:
        cursor.execute(s)
    conexao.commit()

# cria tabelas na inicialização
criar_tabelas()

# ---------- Funções utilitárias CRUD ----------
def cadastrar_cliente(nome, telefone, email=None, observacoes=None):
    sql = "INSERT INTO clientes (nome, telefone, email, observacoes) VALUES (%s,%s,%s,%s)"
    cursor.execute(sql, (nome, telefone, email, observacoes))
    conexao.commit()
    st.success(f"✅ Cliente {nome} cadastrado com sucesso!")

def listar_clientes(limit=200):
    # usa f-string apenas para LIMIT (valor controlado internamente)
    n = int(limit)
    cursor.execute(f"SELECT id, nome, telefone, email, data_cadastro FROM clientes ORDER BY data_cadastro DESC LIMIT {n}")
    rows = cursor.fetchall()
    return rows

def cadastrar_categoria(nome):
    cursor.execute("INSERT INTO categorias_servico (nome) VALUES (%s)", (nome,))
    conexao.commit()

def cadastrar_servico(nome, preco, duracao, categoria_id=None, descricao=None):
    cursor.execute(
        "INSERT INTO servicos (nome, preco, duracao_min, categoria_id, descricao) VALUES (%s,%s,%s,%s,%s)",
        (nome, preco, duracao, categoria_id, descricao)
    )
    conexao.commit()

def listar_servicos():
    cursor.execute("SELECT s.id, s.nome, s.preco, s.duracao_min, c.nome FROM servicos s LEFT JOIN categorias_servico c ON s.categoria_id = c.id")
    return cursor.fetchall()

def cadastrar_funcionario(nome, cargo, telefone=None, email=None):
    cursor.execute("INSERT INTO funcionarios (nome, cargo, telefone, email) VALUES (%s,%s,%s,%s)", (nome, cargo, telefone, email))
    conexao.commit()

def listar_funcionarios():
    cursor.execute("SELECT id, nome, cargo, telefone, email FROM funcionarios WHERE ativo=1")
    return cursor.fetchall()

def cadastrar_produto(nome, preco_venda, preco_compra=None, unidade='un'):
    # reparado para inserir corretamente preco_compra e preco_venda
    cursor.execute("INSERT INTO produtos (nome, preco_compra, preco_venda, unidade) VALUES (%s,%s,%s,%s)",
                   (nome, preco_compra, preco_venda, unidade))
    conexao.commit()
    pid = cursor.lastrowid
    # criar um registro no estoque com quantidade zero
    cursor.execute("INSERT INTO estoque (produto_id, quantidade, minimo) VALUES (%s, %s, %s)", (pid, 0, 0))
    conexao.commit()

def listar_produtos():
    cursor.execute("""SELECT p.id, p.nome, p.preco_venda, COALESCE(e.quantidade, 0) AS qnt
                      FROM produtos p
                      LEFT JOIN estoque e ON p.id = e.produto_id""")
    return cursor.fetchall()

def registrar_agendamento(cliente_id, funcionario_id, data_str, hora_str, observacoes=None):
    sql = "INSERT INTO agendamentos (cliente_id, funcionario_id, data, hora, observacoes) VALUES (%s,%s,%s,%s,%s)"
    cursor.execute(sql, (cliente_id, funcionario_id, data_str, hora_str, observacoes))
    conexao.commit()
    return cursor.lastrowid

def adicionar_item_agendamento(agendamento_id, servico_id, preco, duracao):
    cursor.execute("INSERT INTO agendamento_itens (agendamento_id, servico_id, preco_servico, duracao_min) VALUES (%s,%s,%s,%s)",
                   (agendamento_id, servico_id, preco, duracao))
    conexao.commit()

def listar_agendamentos(periodo_inicio=None, periodo_fim=None):
    if periodo_inicio and periodo_fim:
        cursor.execute("""SELECT a.id, c.nome, f.nome, a.data, a.hora, a.status, a.total
                          FROM agendamentos a
                          LEFT JOIN clientes c ON a.cliente_id = c.id
                          LEFT JOIN funcionarios f ON a.funcionario_id = f.id
                          WHERE a.data BETWEEN %s AND %s
                          ORDER BY a.data DESC, a.hora""", (periodo_inicio, periodo_fim))
    else:
        cursor.execute("""SELECT a.id, c.nome, f.nome, a.data, a.hora, a.status, a.total
                          FROM agendamentos a
                          LEFT JOIN clientes c ON a.cliente_id = c.id
                          LEFT JOIN funcionarios f ON a.funcionario_id = f.id
                          ORDER BY a.data DESC, a.hora LIMIT 200""")
    return cursor.fetchall()

def registrar_venda(agendamento_id, cliente_id, valor_total, forma_pagamento):
    cursor.execute("INSERT INTO vendas (agendamento_id, cliente_id, valor_total, forma_pagamento) VALUES (%s,%s,%s,%s)",
                   (agendamento_id, cliente_id, valor_total, forma_pagamento))
    conexao.commit()

def cadastrar_promocao(titulo, desconto, inicio, fim, descricao=None):
    cursor.execute("INSERT INTO promocoes (titulo, descricao, desconto_percent, data_inicio, data_fim) VALUES (%s,%s,%s,%s,%s)",
                   (titulo, descricao, desconto, inicio, fim))
    conexao.commit()

def registrar_feedback(cliente_id, agendamento_id, nota, comentario=None):
    cursor.execute("INSERT INTO feedbacks (cliente_id, agendamento_id, nota, comentario) VALUES (%s,%s,%s,%s)",
                   (cliente_id, agendamento_id, nota, comentario))
    conexao.commit()

# ---------- Layout Streamlit ----------
st.set_page_config(page_title="Data-Barber CRM (Expanded)", layout="wide")
st.title("💈 Data-Barber - CRM para Barbearias ")

menu = [
    "Criar Cliente", "Listar Clientes", "Registrar Agendamento", "Listar Agendamentos",
    "Serviços", "Funcionários", "Produtos / Estoque", "Vendas / Pagamentos",
    "Promoções", "Feedbacks", "Dashboard"
]
choice = st.sidebar.selectbox("Menu", menu)

# ---------------- Criar Cliente ----------------
if choice == "Criar Cliente":
    st.subheader("🧑‍💼 Cadastrar Novo Cliente")
    nome = st.text_input("Nome")
    telefone = st.text_input("Telefone")
    email = st.text_input("Email (opcional)")
    obs = st.text_area("Observações (opcional)")
    if st.button("Criar"):
        if nome.strip():
            cadastrar_cliente(nome.strip(), telefone.strip(), email.strip() if email else None, obs.strip() if obs else None)
        else:
            st.warning("Nome é obrigatório.")

# ---------------- Listar Clientes ----------------
elif choice == "Listar Clientes":
    st.subheader("📋 Lista de Clientes")
    rows = listar_clientes()
    df = pd.DataFrame(rows, columns=["ID", "Nome", "Telefone", "Email", "Data Cadastro"])
    st.dataframe(df)

# ---------------- Serviços ----------------
elif choice == "Serviços":
    st.subheader("✂️ Gerenciar Serviços")
    tab1, tab2 = st.tabs(["Adicionar Serviço", "Listar/Editar Serviços"])
    with tab1:
        nome = st.text_input("Nome do Serviço")
        preco = st.number_input("Preço (R$)", min_value=0.0, format="%.2f")
        duracao = st.number_input("Duração (min)", min_value=10, value=30)
        # lista de categorias
        cursor.execute("SELECT id, nome FROM categorias_servico")
        cats = cursor.fetchall()
        cats_dict = {c[1]: c[0] for c in cats}
        cat_sel = st.selectbox("Categoria (opcional)", ["---"] + list(cats_dict.keys()))
        descricao = st.text_area("Descrição")
        if st.button("Adicionar Serviço"):
            if not nome.strip():
                st.warning("Nome do serviço é obrigatório.")
            else:
                cat_id = cats_dict.get(cat_sel) if cat_sel != "---" else None
                cadastrar_servico(nome.strip(), float(preco), int(duracao), cat_id, descricao.strip() if descricao else None)
                st.success("Serviço adicionado.")
    with tab2:
        servs = listar_servicos()
        df = pd.DataFrame(servs, columns=["ID", "Nome", "Preço", "Duração", "Categoria"])
        st.dataframe(df)

# ---------------- Funcionários ----------------
elif choice == "Funcionários":
    st.subheader("👥 Funcionários")
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Nome")
        cargo = st.text_input("Cargo")
        telefone = st.text_input("Telefone")
        email = st.text_input("Email")
        if st.button("Adicionar Funcionário"):
            if nome:
                cadastrar_funcionario(nome, cargo, telefone, email)
                st.success("Funcionário adicionado.")
            else:
                st.warning("Preencha o nome.")
    with col2:
        st.markdown("**Funcionários ativos**")
        f = listar_funcionarios()
        df = pd.DataFrame(f, columns=["ID", "Nome", "Cargo", "Telefone", "Email"])
        st.dataframe(df)

# ---------------- Produtos / Estoque ----------------
elif choice == "Produtos / Estoque":
    st.subheader("📦 Produtos e Estoque")
    tab1, tab2 = st.tabs(["Adicionar Produto", "Estoque"])
    with tab1:
        nome = st.text_input("Nome do Produto")
        preco_venda = st.number_input("Preço de Venda", min_value=0.0, format="%.2f")
        preco_compra = st.number_input("Preço de Compra", min_value=0.0, format="%.2f")
        unidade = st.text_input("Unidade (ex: un, ml)", value="un")
        if st.button("Adicionar Produto"):
            if nome:
                cadastrar_produto(nome.strip(), float(preco_venda), float(preco_compra), unidade.strip() if unidade else "un")
                st.success("Produto cadastrado e registro de estoque criado.")
            else:
                st.warning("Nome é obrigatório.")
    with tab2:
        produtos = listar_produtos()
        df = pd.DataFrame(produtos, columns=["ID", "Nome", "Preço Venda", "Quantidade em Estoque"])
        st.dataframe(df)

# ---------------- Registrar Agendamento ----------------
elif choice == "Registrar Agendamento":
    st.subheader("✂️ Registrar Agendamento")
    # carrega clientes, serviços, funcionarios
    cursor.execute("SELECT id, nome FROM clientes ORDER BY nome")
    clientes = cursor.fetchall()
    clientes_dict = {f"{c[1]} (ID:{c[0]})": c[0] for c in clientes}

    cursor.execute("SELECT id, nome, preco, duracao_min FROM servicos WHERE ativo=1")
    servicos = cursor.fetchall()
    servicos_dict = {f"{s[1]} - R${s[2]} (ID:{s[0]})": (s[0], float(s[2]), s[3]) for s in servicos}

    funcionarios = listar_funcionarios()
    func_dict = {f"{f[1]} (ID:{f[0]})": f[0] for f in funcionarios}

    if not clientes:
        st.info("Nenhum cliente cadastrado. Vá em 'Criar Cliente'.")
    else:
        cliente_selecionado = st.selectbox("Cliente", list(clientes_dict.keys()))
        funcionario_selecionado = st.selectbox("Funcionário (opcional)", ["---"] + list(func_dict.keys()))
        servico_selecionados = st.multiselect("Serviços", list(servicos_dict.keys()))
        data = st.date_input("Data do Agendamento", min_value=date.today())
        hora = st.time_input("Hora do Agendamento", value=time(hour=9, minute=0))
        obs = st.text_area("Observações (opcional)")
        if st.button("Agendar"):
            cli_id = clientes_dict[cliente_selecionado]
            func_id = func_dict.get(funcionario_selecionado) if funcionario_selecionado != "---" else None
            ag_id = registrar_agendamento(cli_id, func_id, data.strftime("%Y-%m-%d"), hora.strftime("%H:%M:%S"), obs)
            total = 0
            for s_key in servico_selecionados:
                sid, preco, dur = servicos_dict[s_key]
                adicionar_item_agendamento(ag_id, sid, preco, dur)
                total += preco
            # atualiza total no agendamento
            cursor.execute("UPDATE agendamentos SET total=%s WHERE id=%s", (total, ag_id))
            conexao.commit()
            st.success(f"Agendamento {ag_id} registrado. Total R$ {total:.2f}")

# ---------------- Listar Agendamentos ----------------
elif choice == "Listar Agendamentos":
    st.subheader("🗓️ Agendamentos")
    col1, col2 = st.columns(2)
    with col1:
        inicio = st.date_input("Data inicial", value=date.today())
    with col2:
        fim = st.date_input("Data final", value=date.today())
    if st.button("Buscar agendamentos"):
        rows = listar_agendamentos(inicio.strftime("%Y-%m-%d"), fim.strftime("%Y-%m-%d"))
        df = pd.DataFrame(rows, columns=["ID", "Cliente", "Funcionário", "Data", "Hora", "Status", "Total"])
        st.dataframe(df)

# ---------------- Vendas / Pagamentos ----------------
elif choice == "Vendas / Pagamentos":
    st.subheader("💳 Registrar Venda / Pagamento")
    cursor.execute("""SELECT a.id, c.nome, a.data, a.hora, a.total 
                      FROM agendamentos a
                      LEFT JOIN clientes c ON a.cliente_id = c.id
                      WHERE a.data >= CURDATE()-INTERVAL 30 DAY
                      ORDER BY a.data DESC LIMIT 100""")
    arows = cursor.fetchall()
    ag_dict = {f"#{r[0]} {r[1]} {r[2]} {r[3]} (R${r[4]})": r[0] for r in arows}
    cursor.execute("SELECT id, nome FROM clientes")
    clients = cursor.fetchall()
    clients_dict = {f"{c[1]} (ID:{c[0]})": c[0] for c in clients}

    ag_sel = st.selectbox("Agendamento (opcional)", ["---"] + list(ag_dict.keys()))
    cliente_sel = st.selectbox("Cliente (se não for vinculado a agendamento)", ["---"] + list(clients_dict.keys()))
    valor = st.number_input("Valor total (R$)", min_value=0.0, format="%.2f")
    forma = st.selectbox("Forma de pagamento", ["dinheiro", "cartao", "pix", "parcelado", "outros"])
    if st.button("Registrar Venda"):
        ag_id = ag_dict.get(ag_sel) if ag_sel != "---" else None
        cli_id = None
        if ag_id:
            cursor.execute("SELECT cliente_id FROM agendamentos WHERE id=%s", (ag_id,))
            res = cursor.fetchone()
            cli_id = res[0] if res else None
        elif cliente_sel != "---":
            cli_id = clients_dict[cliente_sel]
        registrar_venda(ag_id, cli_id, float(valor), forma)
        st.success("Venda registrada.")

# ---------------- Promoções ----------------
elif choice == "Promoções":
    st.subheader("🏷️ Promoções")
    with st.form("promo_form"):
        titulo = st.text_input("Título")
        desconto = st.number_input("Desconto (%)", min_value=0.0, max_value=100.0, format="%.2f")
        inicio = st.date_input("Início", value=date.today())
        fim = st.date_input("Fim", value=date.today())
        descricao = st.text_area("Descrição")
        submitted = st.form_submit_button("Criar Promoção")
        if submitted:
            cadastrar_promocao(titulo, desconto, inicio.strftime("%Y-%m-%d"), fim.strftime("%Y-%m-%d"), descricao)
            st.success("Promoção criada.")

    cursor.execute("SELECT id, titulo, desconto_percent, data_inicio, data_fim, ativo FROM promocoes ORDER BY data_inicio DESC")
    promos = cursor.fetchall()
    df = pd.DataFrame(promos, columns=["ID", "Título", "Desconto %", "Início", "Fim", "Ativa"])
    st.dataframe(df)

# ---------------- Feedbacks ----------------
elif choice == "Feedbacks":
    st.subheader("⭐ Feedbacks e Avaliações")
    cursor.execute("SELECT id, nome FROM clientes")
    clients = cursor.fetchall()
    clients_dict = {f"{c[1]} (ID:{c[0]})": c[0] for c in clients}
    cliente_sel = st.selectbox("Cliente", list(clients_dict.keys()) if clients else ["---"])
    agendamento_id = st.text_input("Agendamento ID (opcional)")
    nota = st.slider("Nota (1 a 5)", 1, 5, 5)
    comentario = st.text_area("Comentário (opcional)")
    if st.button("Registrar Feedback"):
        if cliente_sel and cliente_sel != "---":
            cid = clients_dict[cliente_sel]
            agid = int(agendamento_id) if agendamento_id.strip().isdigit() else None
            registrar_feedback(cid, agid, int(nota), comentario)
            st.success("Feedback registrado.")
        else:
            st.warning("Selecione um cliente.")

    # listar últimos feedbacks
    cursor.execute("""SELECT f.id, c.nome, f.nota, f.comentario, f.criado_em 
                      FROM feedbacks f
                      LEFT JOIN clientes c ON f.cliente_id = c.id
                      ORDER BY f.criado_em DESC LIMIT 200""")
    fb = cursor.fetchall()
    df = pd.DataFrame(fb, columns=["ID", "Cliente", "Nota", "Comentário", "Data"])
    st.dataframe(df)

# ---------------- Dashboard ----------------
elif choice == "Dashboard":
    st.subheader("📊 Dashboard de Receita e Serviços (Mantido)")
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data inicial", value=date(2025,1,1))
    with col2:
        data_fim = st.date_input("Data final", value=date.today())

    if st.button("Gerar Dashboard"):
        sql = """
        SELECT s.nome, COUNT(ai.id) AS qtd, SUM(ai.preco_servico) AS receita
        FROM agendamento_itens ai
        JOIN servicos s ON ai.servico_id = s.id
        JOIN agendamentos a ON ai.agendamento_id = a.id
        WHERE a.data BETWEEN %s AND %s
        GROUP BY s.id
        ORDER BY receita DESC
        """
        cursor.execute(sql, (data_inicio.strftime("%Y-%m-%d"), data_fim.strftime("%Y-%m-%d")))
        resultados = cursor.fetchall()

        if resultados:
            servicos = [r[0] for r in resultados]
            qtd = [int(r[1]) for r in resultados]
            receita = [float(r[2]) for r in resultados]

            # gráfico quantidade
            fig1, ax1 = plt.subplots(figsize=(6,3))
            ax1.bar(servicos, qtd)
            ax1.set_title("📊 Serviços mais realizados", fontsize=12, fontweight="bold")
            ax1.set_ylabel("Quantidade")
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig1)

            # receita por serviço
            fig2, ax2 = plt.subplots(figsize=(6,3))
            ax2.bar(servicos, receita)
            ax2.set_title("💰 Receita por Serviço", fontsize=12, fontweight="bold")
            ax2.set_ylabel("R$ Receita")
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig2)

            # pizza percentual
            fig3, ax3 = plt.subplots(figsize=(5,5))
            ax3.pie(qtd, labels=servicos, autopct='%1.1f%%', startangle=90)
            ax3.set_title("📌 Participação de cada serviço", fontsize=12, fontweight="bold")
            st.pyplot(fig3)

            # receita total e média
            total_receita = sum(receita)
            st.metric("Receita total", f"R$ {total_receita:.2f}")
            st.write(f"Período: {data_inicio} — {data_fim}")
        else:
            st.info("Nenhum agendamento encontrado nesse período.")

# ---------------- default ----------------
else:
    st.write("Selecione uma opção no menu.")
