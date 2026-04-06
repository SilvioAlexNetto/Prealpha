import sqlite3
import httpx
import difflib

from app.backend.services.core.normalizacao import limpar_nome_produto
from app.database.database import get_connection

TIMEOUT = 5


# =========================
# 🔥 CACHE LOCAL
# =========================
def buscar_cache(nome_sujo: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT nome_limpo FROM aprendizado_produtos"
    )

    rows = cursor.fetchall()
    conn.close()

    return rows


def salvar_cache(nome_sujo: str, nome_limpo: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT OR IGNORE INTO aprendizado_produtos (nome_sujo, nome_limpo)
            VALUES (?, ?)
            """,
            (nome_sujo.lower(), nome_limpo.lower())
        )
        conn.commit()
    except:
        pass
    finally:
        conn.close()


# =========================
# 🧠 FUZZY MATCH
# =========================
def fuzzy_match(nome_limpo: str, cache_rows):
    if not cache_rows:
        return None

    nomes_conhecidos = [row["nome_limpo"] for row in cache_rows]

    match = difflib.get_close_matches(
        nome_limpo,
        nomes_conhecidos,
        n=1,
        cutoff=0.7  # 🔥 sensibilidade
    )

    if match:
        return match[0]

    return None


# =========================
# 🌍 OPEN FOOD FACTS
# =========================
async def buscar_openfoodfacts(nome: str):
    try:
        url = "https://world.openfoodfacts.org/cgi/search.pl"

        params = {
            "search_terms": nome,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": 3
        }

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(url, params=params)

        if response.status_code != 200:
            return None

        data = response.json()

        produtos = data.get("products", [])
        if not produtos:
            return None

        produto = produtos[0]

        nome_api = produto.get("product_name")
        if not nome_api:
            return None

        return limpar_nome_produto(nome_api)

    except:
        return None


# =========================
# 🧠 RESOLVER NOME FINAL
# =========================
async def resolver_nome(nome_sujo: str):
    if not nome_sujo:
        return "produto"

    nome_sujo = nome_sujo.strip()

    # =========================
    # 1. LIMPEZA BASE
    # =========================
    nome_limpo = limpar_nome_produto(nome_sujo)

    # =========================
    # 2. CACHE + FUZZY
    # =========================
    cache_rows = buscar_cache(nome_sujo)

    # match exato já existente
    for row in cache_rows:
        if row["nome_sujo"] == nome_sujo.lower():
            return row["nome_limpo"]

    # fuzzy match
    fuzzy = fuzzy_match(nome_limpo, cache_rows)
    if fuzzy:
        salvar_cache(nome_sujo, fuzzy)
        return fuzzy

    # =========================
    # 3. API EXTERNA
    # =========================
    nome_api = await buscar_openfoodfacts(nome_limpo)

    if nome_api:
        salvar_cache(nome_sujo, nome_api)
        return nome_api

    # =========================
    # 4. FALLBACK FINAL
    # =========================
    salvar_cache(nome_sujo, nome_limpo)
    return nome_limpo