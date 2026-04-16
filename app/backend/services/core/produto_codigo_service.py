import re
from app.database.database import get_connection


def is_ean(codigo: str):
    return codigo and codigo.isdigit() and len(codigo) in [8, 12, 13, 14]


def buscar_produto_por_codigo(mercado: str, codigo: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nome_normalizado 
        FROM produtos_codigo 
        WHERE mercado = ? AND codigo = ?
    """, (mercado.lower(), codigo))

    row = cursor.fetchone()
    conn.close()

    if row:
        return row["nome_normalizado"]

    return None


def salvar_produto_codigo(mercado: str, codigo: str, nome: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT OR REPLACE INTO produtos_codigo 
            (mercado, codigo, nome_normalizado)
            VALUES (?, ?, ?)
        """, (mercado.lower(), codigo, nome.lower()))
        conn.commit()
    except:
        pass
    finally:
        conn.close()