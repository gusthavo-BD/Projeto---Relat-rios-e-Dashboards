import streamlit as st
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="minhasenha",   # coloque sua senha
    database="barbearia"
)

cursor = conexao.cursor()
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
def dashboard_receita():
    sql = """
    SELECT s.nome, COUNT(a.id) AS qtd, SUM(s.preco) AS receita
    FROM agendamentos a
    JOIN servicos s ON a.servico_id = s.id
    GROUP BY s.id
    """
    cursor.execute(sql)
    resultados = cursor.fetchall()

    if  resultados:
        servicos = [r[0] for r in resultados]
        qtd = [r[1] for r in resultados]
        receita = [float(r[2]) for r in resultados]

        # Gráfico de quantidade de serviços
        fig1, ax1 = plt.subplots()
        ax1.bar(servicos, qtd, color="skyblue")
        ax1.set_title("📊 Serviços mais realizados")
        ax1.set_ylabel("Quantidade")
        st.pyplot(fig1)

        # Gráfico de receita por serviço
        fig2, ax2 = plt.subplots()
        ax2.bar(servicos, receita, color="green")
        ax2.set_title("💰 Receita por Serviço")
        ax2.set_ylabel("R$ Receita")
        st.pyplot(fig2)
    else:
        st.info("Nenhum agendamento encontrado para gerar dashboard.")

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

# ------------------------------
# Dashboard
# ------------------------------
elif choice == "Dashboard":
    st.subheader("📊 Dashboard de Receita e Serviços")
    dashboard_receita()
   

