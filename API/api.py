
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import mysql.connector
from datetime import datetime

app = FastAPI(title="Data-Barber API", version="1.0.0")

# ----------------------------
# ✅ CONFIGURAÇÃO DO BANCO
# ----------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "2110",
    "database": "barbearia",
    "auth_plugin": "mysql_native_password"
}


def get_db():
    return mysql.connector.connect(**DB_CONFIG)

# ----------------------------
# ✅ MODELOS Pydantic
# ----------------------------
class Cliente(BaseModel):
    nome: str
    telefone: Optional[str] = None
    email: Optional[str] = None

class Servico(BaseModel):
    nome: str
    preco: float

class Barbeiro(BaseModel):
    nome: str

class Agendamento(BaseModel):
    cliente_id: int
    barbeiro_id: int
    servico_id: int
    data_hora: str
    status: Optional[str] = "confirmado"

class Venda(BaseModel):
    cliente_id: int
    servicos: List[int]

# ----------------------------
# ✅ ENDPOINTS - CLIENTES
# ----------------------------
@app.get("/api/clientes")
def listar_clientes():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clientes")
    result = cursor.fetchall()
    db.close()
    return result


@app.get("/api/clientes/{cliente_id}")
def buscar_cliente(cliente_id: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clientes WHERE id = %s", (cliente_id,))
    cliente = cursor.fetchone()
    db.close()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente


@app.post("/api/clientes", status_code=201)
def criar_cliente(cliente: Cliente):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO clientes (nome, telefone, email, data_cadastro) VALUES (%s, %s, %s, %s)",
                   (cliente.nome, cliente.telefone, cliente.email, datetime.today().date()))
    db.commit()
    novo_id = cursor.lastrowid
    db.close()
    return {"id": novo_id, "mensagem": "Cliente cadastrado com sucesso"}


@app.put("/api/clientes/{cliente_id}")
def atualizar_cliente(cliente_id: int, cliente: Cliente):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE clientes SET nome=%s, telefone=%s, email=%s WHERE id=%s",
                   (cliente.nome, cliente.telefone, cliente.email, cliente_id))
    db.commit()
    db.close()
    return {"mensagem": "Cliente atualizado com sucesso"}


@app.delete("/api/clientes/{cliente_id}")
def deletar_cliente(cliente_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM clientes WHERE id=%s", (cliente_id,))
    db.commit()
    db.close()
    return {"mensagem": "Cliente removido com sucesso"}

# ----------------------------
# ✅ ENDPOINTS - SERVIÇOS
# ----------------------------
@app.get("/api/servicos")
def listar_servicos():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM servicos")
    result = cursor.fetchall()
    db.close()
    return result


@app.post("/api/servicos", status_code=201)
def criar_servico(servico: Servico):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO servicos (nome, preco) VALUES (%s, %s)", (servico.nome, servico.preco))
    db.commit()
    novo_id = cursor.lastrowid
    db.close()
    return {"id": novo_id, "mensagem": "Serviço cadastrado"}

# ----------------------------
# ✅ ENDPOINTS - BARBEIROS
# ----------------------------
@app.get("/api/barbeiros")
def listar_barbeiros():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM barbeiros")
    result = cursor.fetchall()
    db.close()
    return result


@app.post("/api/barbeiros", status_code=201)
def criar_barbeiro(barbeiro: Barbeiro):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO barbeiros (nome) VALUES (%s)", (barbeiro.nome,))
    db.commit()
    novo_id = cursor.lastrowid
    db.close()
    return {"id": novo_id, "mensagem": "Barbeiro cadastrado"}

# ----------------------------
# ✅ ENDPOINTS - AGENDAMENTOS
# ----------------------------
@app.get("/api/agendamentos")
def listar_agendamentos():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM agendamentos")
    result = cursor.fetchall()
    db.close()
    return result


@app.post("/api/agendamentos", status_code=201)
def criar_agendamento(ag: Agendamento):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO agendamentos (cliente_id, barbeiro_id, servico_id, data_hora, status) VALUES (%s, %s, %s, %s, %s)",
        (ag.cliente_id, ag.barbeiro_id, ag.servico_id, ag.data_hora, ag.status))
    db.commit()
    novo_id = cursor.lastrowid
    db.close()
    return {"id": novo_id, "mensagem": "Agendamento criado"}

# ----------------------------
# ✅ ENDPOINTS - VENDAS
# ----------------------------
@app.get("/api/vendas")
def listar_vendas():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vendas")
    result = cursor.fetchall()
    db.close()
    return result


@app.post("/api/vendas", status_code=201)
def criar_venda(venda: Venda):
    db = get_db()
    cursor = db.cursor()

    # Calcula total
    cursor.execute(f"SELECT SUM(preco) FROM servicos WHERE id IN ({','.join(['%s']*len(venda.servicos))})", venda.servicos)
    total = cursor.fetchone()[0]

    cursor.execute("INSERT INTO vendas (cliente_id, valor_total, data_venda) VALUES (%s, %s, %s)",
                   (venda.cliente_id, total, datetime.today().date()))
    db.commit()
    novo_id = cursor.lastrowid
    db.close()
    return {"id": novo_id, "valor_total": total, "mensagem": "Venda registrada"}

# ----------------------------
# ✅ ROTA RAIZ / STATUS
# ----------------------------
@app.get("/")
def home():
    return {"status": "API Data-Barber rodando ✅"}


# ----------------------------
# ✅ COMO RODAR
# ----------------------------
# uvicorn api:app --reload --port 8000
