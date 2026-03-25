import sqlite3
import json
import os

# =========================
# CAMINHOS BASE
# =========================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "healthcare.db")

# =========================
# CONEXÃO
# =========================

def get_connection():
    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    return conn

# =========================
# CRIAÇÃO DAS TABELAS
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
        nome TEXT NOT NULL,
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

    conn.commit()
    conn.close()

# =========================
# CONSULTAS
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
        except json.JSONDecodeError:
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

# =========================
# INSERÇÕES
# =========================

def adicionar_item_estoque_atual(nome, quantidade, unidade):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO estoque_atual (nome, quantidade, unidade)
        VALUES (?, ?, ?)
        """,
        (
            nome.strip().lower(),
            float(quantidade),
            unidade.strip().lower()
        )
    )

    conn.commit()
    conn.close()


def adicionar_item_estoque_andamento(nome, quantidade, unidade, data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO estoque_andamento (nome, quantidade, unidade, data)
        VALUES (?, ?, ?, ?)
        """,
        (
            nome.strip().lower(),
            float(quantidade),
            unidade.strip().lower(),
            data
        )
    )

    conn.commit()
    conn.close()

# =========================
# GARANTIA DE ESTRUTURA
# =========================

# criar_tabelas()