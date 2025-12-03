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
