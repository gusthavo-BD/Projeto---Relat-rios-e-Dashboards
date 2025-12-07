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
