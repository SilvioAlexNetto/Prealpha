import sqlite3
import json
import os

# =========================
# CAMINHO DO BANCO
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "healthcare.db")


# =========================
# CONEXÃO
# =========================
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# =========================
# CRIAR TABELAS
# =========================
def criar_tabelas():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS receitas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        tipo TEXT NOT NULL,
        ingredientes TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estoque_atual (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL,
        quantidade REAL NOT NULL,
        unidade TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estoque_andamento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        quantidade REAL NOT NULL,
        unidade TEXT NOT NULL,
        data TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cardapio_mensal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mes INTEGER NOT NULL,
        ano INTEGER NOT NULL,
        cardapio TEXT NOT NULL,
        estoque_final TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


# =========================
# LISTAR
# =========================
def listar_receitas():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM receitas")
    rows = cursor.fetchall()

    receitas = []
    for row in rows:
        try:
            ingredientes = json.loads(row["ingredientes"]) if row["ingredientes"] else []
        except:
            ingredientes = []

        receitas.append({
            "id": row["id"],
            "nome": row["nome"],
            "tipo": row["tipo"],
            "ingredientes": ingredientes
        })

    conn.close()
    return receitas


def listar_estoque_atual():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM estoque_atual")
    rows = cursor.fetchall()

    estoque = [
        {
            "id": row["id"],
            "nome": row["nome"],
            "quantidade": row["quantidade"],
            "unidade": row["unidade"]
        }
        for row in rows
    ]

    conn.close()
    return estoque


def listar_estoque_andamento():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM estoque_andamento")
    rows = cursor.fetchall()

    andamento = [
        {
            "id": row["id"],
            "nome": row["nome"],
            "quantidade": row["quantidade"],
            "unidade": row["unidade"],
            "data": row["data"]
        }
        for row in rows
    ]

    conn.close()
    return andamento

def salvar_cardapio(mes, ano, cardapio, estoque_final):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO cardapio_mensal (mes, ano, cardapio, estoque_final)
        VALUES (?, ?, ?, ?)
    """, (
        mes,
        ano,
        json.dumps(cardapio),
        json.dumps(estoque_final)
    ))

    conn.commit()
    conn.close()


def buscar_cardapio(mes, ano):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM cardapio_mensal
        WHERE mes = ? AND ano = ?
    """, (mes, ano))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "mes": row["mes"],
        "ano": row["ano"],
        "cardapio": json.loads(row["cardapio"]),
        "estoque_final": json.loads(row["estoque_final"])
    }


# =========================
# INSERIR / ATUALIZAR ESTOQUE (INTELIGENTE)
# =========================
def adicionar_item_estoque_atual(nome, quantidade, unidade):
    conn = get_connection()
    cursor = conn.cursor()

    nome = nome.strip().lower()
    unidade = unidade.strip().lower()

    # 🔥 se já existe, soma quantidade
    cursor.execute("""
        SELECT quantidade FROM estoque_atual WHERE nome = ?
    """, (nome,))

    result = cursor.fetchone()

    if result:
        nova_qtd = result["quantidade"] + float(quantidade)

        cursor.execute("""
            UPDATE estoque_atual
            SET quantidade = ?, unidade = ?
            WHERE nome = ?
        """, (nova_qtd, unidade, nome))

    else:
        cursor.execute("""
            INSERT INTO estoque_atual (nome, quantidade, unidade)
            VALUES (?, ?, ?)
        """, (nome, float(quantidade), unidade))

    conn.commit()
    conn.close()


# =========================
# UPDATE DIRETO (ENGINE USA ISSO)
# =========================
def atualizar_item_estoque(nome, quantidade, unidade):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE estoque_atual
        SET quantidade = ?, unidade = ?
        WHERE nome = ?
    """, (float(quantidade), unidade.lower(), nome.lower()))

    conn.commit()
    conn.close()


# =========================
# REMOVER ITEM
# =========================
def remover_item_estoque(nome):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM estoque_atual
        WHERE nome = ?
    """, (nome.lower(),))

    conn.commit()
    conn.close()


# =========================
# ESTOQUE ANDAMENTO
# =========================
def adicionar_item_estoque_andamento(nome, quantidade, unidade, data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO estoque_andamento (nome, quantidade, unidade, data)
        VALUES (?, ?, ?, ?)
    """, (
        nome.strip().lower(),
        float(quantidade),
        unidade.strip().lower(),
        data
    ))

    conn.commit()
    conn.close()


# =========================
# GARANTIA DE ESTRUTURA
# =========================
# criar_tabelas()