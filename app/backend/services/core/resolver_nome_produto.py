import httpx
import difflib
import re
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
# 🧹 REMOVE MARCA DO NOME
# =========================
def remover_marca(nome: str, marca: str):
    if not nome or not marca:
        return nome

    nome = nome.lower()
    marca = marca.lower()

    # remove marca exata
    nome = nome.replace(marca, "")

    # limpa espaços
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
                # pega primeira marca
                return marca.split(",")[0].strip().lower()

        return None

    except:
        return None
    
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

    # =========================
    # 1. LIMPEZA BASE
    # =========================
    nome_normalizado = limpar_nome_produto(nome_original)

    # =========================
    # 2. CACHE + FUZZY
    # =========================
    cache_rows = buscar_cache()

    # match exato
    for row in cache_rows:
        if row["nome_original"] == nome_original.lower():
            return row["nome_normalizado"]

    # fuzzy match
    fuzzy = fuzzy_match(nome_normalizado, cache_rows)
    if fuzzy:
        salvar_cache(nome_original, fuzzy)
        return fuzzy

    # =========================
    # 3. API EXTERNA
    # =========================

    # 🔥 tenta buscar marca primeiro
    marca = await buscar_marca_openfoodfacts(nome_normalizado)

    nome_sem_marca = nome_normalizado

    # remove marca
    if marca:
        nome_sem_marca = remover_marca(nome_normalizado, marca)
    else:
        nome_sem_marca = nome_normalizado

    # remove unidade
    nome_sem_marca = re.sub(
        r"\b\d+[\.,]?\d*\s?(kg|g|mg|l|ml)\b",
        "",
        nome_sem_marca
    )

    # limpa final
    nome_sem_marca = limpar_nome_produto(nome_sem_marca)

    # fallback: ainda tenta nome da API
    nome_api = await buscar_openfoodfacts(nome_normalizado)

    # prioridade: API se for melhor
    if nome_api and len(nome_api) > len(nome_sem_marca):
        salvar_cache(nome_original, nome_api)
        return nome_api
    
    nome_sem_marca = re.sub(r"\b\d+[\.,]?\d*\s?(kg|g|mg|l|ml)\b", "", nome_sem_marca)

    if nome_sem_marca and len(nome_sem_marca) > 3:
        salvar_cache(nome_original, nome_sem_marca)
        return nome_sem_marca

    # =========================
    # 4. FALLBACK FINAL
    # =========================
    salvar_cache(nome_original, nome_normalizado)
    return nome_normalizado