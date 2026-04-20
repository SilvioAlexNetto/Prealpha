import httpx
import difflib
import re
from difflib import SequenceMatcher
from app.backend.services.core.normalizacao import limpar_nome_produto
from app.database.database import get_connection

TIMEOUT = 5


# =========================
# 🔥 CACHE LOCAL
# =========================
def buscar_cache():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT nome_original, nome_normalizado FROM aprendizado_produtos"
    )

    rows = cursor.fetchall()
    conn.close()

    return rows


def salvar_cache(nome_original: str, nome_normalizado: str):
    if not nome_normalizado or len(nome_normalizado) < 3:
        return  # 🔥 evita lixo no banco

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT OR IGNORE INTO aprendizado_produtos (nome_original, nome_normalizado)
            VALUES (?, ?)
            """,
            (nome_original.lower(), nome_normalizado.lower())
        )
        conn.commit()
    except:
        pass
    finally:
        conn.close()


def similaridade(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def melhor_match_api(nome_limpo: str, produtos: list):
    melhor = None
    melhor_score = 0

    for p in produtos:
        nome_api = p.get("product_name")

        if not nome_api:
            continue

        nome_api_limpo = limpar_nome_produto(nome_api)

        score = similaridade(nome_limpo, nome_api_limpo)

        if score > melhor_score:
            melhor_score = score
            melhor = nome_api_limpo

    if melhor and melhor_score >= 0.75:
        return melhor

    return None


# =========================
# 🧠 FUZZY MATCH
# =========================
def fuzzy_match(nome_normalizado: str, cache_rows):
    if not cache_rows:
        return None

    nomes_conhecidos = [row["nome_normalizado"] for row in cache_rows]

    match = difflib.get_close_matches(
        nome_normalizado,
        nomes_conhecidos,
        n=1,
        cutoff=0.7
    )

    if match:
        return match[0]

    return None


# =========================
# 🧹 REMOVE MARCA
# =========================
def remover_marca(nome: str, marca: str):
    if not nome or not marca:
        return nome

    nome = nome.lower().replace(marca.lower(), "")
    nome = re.sub(r"\s+", " ", nome).strip()

    return nome


# =========================
# 🌍 OPEN FOOD FACTS
# =========================
async def buscar_marca_openfoodfacts(nome: str):
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

        for p in produtos:
            marca = p.get("brands")
            if marca:
                return marca.split(",")[0].strip().lower()

        return None

    except:
        return None


async def buscar_openfoodfacts_raw(nome: str):
    try:
        url = "https://world.openfoodfacts.org/cgi/search.pl"

        params = {
            "search_terms": nome,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": 5
        }

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(url, params=params)

        if response.status_code != 200:
            return None

        return response.json()

    except:
        return None


async def buscar_openfoodfacts_por_ean(codigo: str):
    try:
        url = f"https://world.openfoodfacts.org/api/v0/product/{codigo}.json"

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(url)

        if response.status_code != 200:
            return None

        data = response.json()

        produto = data.get("product")
        if not produto:
            return None

        nome = produto.get("product_name")
        if not nome:
            return None

        return limpar_nome_produto(nome)

    except:
        return None


# =========================
# 🧠 RESOLVER NOME FINAL
# =========================
async def resolver_nome(nome_original: str):
    if not nome_original:
        return "produto"

    nome_original = nome_original.strip()
    nome_normalizado = limpar_nome_produto(nome_original)

    # =========================
    # CACHE
    # =========================
    cache_rows = buscar_cache()

    for row in cache_rows:
        if row["nome_original"] == nome_original.lower():
            return row["nome_normalizado"]

    fuzzy = fuzzy_match(nome_normalizado, cache_rows)
    if fuzzy:
        salvar_cache(nome_original, fuzzy)
        return fuzzy

    # =========================
    # API
    # =========================
    marca = await buscar_marca_openfoodfacts(nome_normalizado)

    nome_limpo = remover_marca(nome_normalizado, marca) if marca else nome_normalizado
    nome_limpo = re.sub(r"\b\d+[\.,]?\d*\s?(kg|g|mg|l|ml)\b", "", nome_limpo)
    nome_limpo = limpar_nome_produto(nome_limpo)

    data_api = await buscar_openfoodfacts_raw(nome_normalizado)

    nome_api_final = None
    if data_api:
        produtos = data_api.get("products", [])
        nome_api_final = melhor_match_api(nome_normalizado, produtos)

    # =========================
    # PRIORIDADE FINAL
    # =========================
    resultado_final = None

    if nome_api_final:
        resultado_final = nome_api_final
    elif nome_limpo and len(nome_limpo) > 3:
        resultado_final = nome_limpo
    else:
        resultado_final = nome_normalizado

    # =========================
    # SALVA APENAS SE VALIDO
    # =========================
    if resultado_final and len(resultado_final) > 3:
        salvar_cache(nome_original, resultado_final)

    return resultado_final