import streamlit as st
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
from datetime import date

# Conexão com MySQL
conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="admin",   # coloque sua senha
    database="barbearia"
)

cursor = conexao.cursor()

# ------------------------------
# Funções CRUD
# ------------------------------
def cadastrar_cliente(nome, telefone):
    sql = "INSERT INTO clientes (nome, telefone) VALUES (%s, %s)"
    cursor.execute(sql, (nome, telefone))
    conexao.commit()
    st.success(f"✅ Cliente {nome} cadastrado com sucesso!")

def agendar_servico(cliente_id, servico_id, data):
    sql = "INSERT INTO agendamentos (cliente_id, servico_id, data) VALUES (%s, %s, %s)"
    cursor.execute(sql, (cliente_id, servico_id, data))
    conexao.commit()
    st.success("📅 Agendamento realizado com sucesso!")

def dashboard_receita(data_inicio, data_fim):
    sql = """
    SELECT s.nome, COUNT(a.id) AS qtd, SUM(s.preco) AS receita
    FROM agendamentos a
    JOIN servicos s ON a.servico_id = s.id
    WHERE a.data BETWEEN %s AND %s
    GROUP BY s.id
    """
    cursor.execute(sql, (data_inicio, data_fim))
    resultados = cursor.fetchall()

    if resultados:
        servicos = [r[0] for r in resultados]
        qtd = [r[1] for r in resultados]
        receita = [float(r[2]) for r in resultados]

        # Estilo mais bonito
        plt.style.use("seaborn-v0_8")

        # Gráfico de quantidade de serviços
        fig1, ax1 = plt.subplots(figsize=(5,3))
        ax1.bar(servicos, qtd)
        ax1.set_title("📊 Serviços mais realizados", fontsize=12, fontweight="bold")
        ax1.set_ylabel("Quantidade")
        st.pyplot(fig1)

        # Gráfico de receita por serviço
        fig2, ax2 = plt.subplots(figsize=(5,3))
        ax2.bar(servicos, receita)
        ax2.set_title("💰 Receita por Serviço", fontsize=12, fontweight="bold")
        ax2.set_ylabel("R$ Receita")
        st.pyplot(fig2)

        # Gráfico de Pizza (percentual de serviços)
        fig3, ax3 = plt.subplots(figsize=(4,4))
        ax3.pie(qtd, labels=servicos, autopct='%1.1f%%', startangle=90)
        ax3.set_title("📌 Participação de cada serviço", fontsize=12, fontweight="bold")
        st.pyplot(fig3)

    else:
        st.info("Nenhum agendamento encontrado nesse período.")

# ------------------------------
# Layout da aplicação
# ------------------------------
st.set_page_config(page_title="Data-Barber CRM", layout="wide")
st.title("💈 Data-Barber - CRM para Barbearias")

menu = ["Criar Cliente", "Listar Clientes", "Registrar Serviço", "Dashboard"]
choice = st.sidebar.selectbox("Menu", menu)

# ------------------------------
# Criar Cliente
# ------------------------------
if choice == "Criar Cliente":
    st.subheader("🧑‍💼 Cadastrar Novo Cliente")
    nome = st.text_input("Nome")
    telefone = st.text_input("Telefone")
    if st.button("Criar"):
        if nome and telefone:
            cadastrar_cliente(nome, telefone)
        else:
            st.warning("Preencha todos os campos!")

# ------------------------------
# Listar Clientes
# ------------------------------
elif choice == "Listar Clientes":
    st.subheader("📋 Lista de Clientes")
    cursor.execute("SELECT id, nome, telefone FROM clientes")
    clientes = cursor.fetchall()
    df = pd.DataFrame(clientes, columns=["ID", "Nome", "Telefone"])
    st.dataframe(df)

# ------------------------------
# Registrar Serviço
# ------------------------------
elif choice == "Registrar Serviço":
    st.subheader("✂️ Registrar Agendamento")
    cursor.execute("SELECT id, nome FROM clientes")
    clientes = cursor.fetchall()
    clientes_dict = {f"{c[1]} (ID:{c[0]})": c[0] for c in clientes}

    cursor.execute("SELECT id, nome, preco FROM servicos")
    servicos = cursor.fetchall()
    servicos_dict = {f"{s[1]} - R${s[2]} (ID:{s[0]})": s[0] for s in servicos}

    cliente_selecionado = st.selectbox("Cliente", list(clientes_dict.keys()))
    servico_selecionado = st.selectbox("Serviço", list(servicos_dict.keys()))
    data = st.date_input("Data do Agendamento")

    if st.button("Agendar"):
        agendar_servico(clientes_dict[cliente_selecionado], servicos_dict[servico_selecionado], str(data))

# Dashboard
elif choice == "Dashboard":
    st.subheader("📊 Dashboard de Receita e Serviços")

    # Filtro de datas
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data inicial", value=date(2025,1,1))
    with col2:
        data_fim = st.date_input("Data final", value=date.today())

    if st.button("Gerar Dashboard"):
        dashboard_receita(str(data_inicio), str(data_fim))
