from app.backend.services.utils.http_client import buscar_url
from app.backend.services.parsers.nf_parser import extrair_dados_nota
from app.backend.services.core.resolver_nome_produto import resolver_nome, buscar_openfoodfacts_por_ean
from app.backend.services.core.produto_codigo_service import (
    buscar_produto_por_codigo,
    salvar_produto_codigo,
    is_ean
)

def extrair_nome_string(nome):
    if isinstance(nome, dict):
        return nome.get("nome_final")
    return nome


async def ler_nota_fiscal(url: str):
    try:
        # =========================
        # 🌐 1. BAIXAR HTML
        # =========================
        html = await buscar_url(url)

        # =========================
        # 🧾 2. PARSEAR NOTA
        # =========================
        dados = await extrair_dados_nota(html)

        # =========================
        # 🧠 3. NORMALIZAR DADOS
        # =========================
        mercado = dados.get("mercado")

        if mercado:
            mercado = mercado.lower().strip()
        data = dados.get("data")
        itens = dados.get("itens", [])

        itens_normalizados = []

        for item in itens:
            nome_original = extrair_nome_string(item.get("nome"))

            if not nome_original:
                continue

            codigo = item.get("codigo")
            nome_resolvido = None

            # =========================
            # 1. CACHE LOCAL
            # =========================
            if codigo:
                nome_cache = buscar_produto_por_codigo(mercado, codigo)
                if nome_cache:
                    nome_resolvido = nome_cache

            # =========================
            # 2. EAN → API
            # =========================
            if not nome_resolvido and codigo and is_ean(codigo):
                nome_api = await buscar_openfoodfacts_por_ean(codigo)
                if nome_api:
                    nome_resolvido = nome_api

            # =========================
            # 3. FALLBACK
            # =========================
            if not nome_resolvido:
                nome_resolvido = resolver_nome(nome_original)

            # garante string
            if isinstance(nome_resolvido, dict):
                nome_resolvido = nome_resolvido.get("nome_final")

            itens_normalizados.append({
                "nome": nome_original,
                "nome_resolvido": nome_resolvido,
                "quantidade": item.get("quantidade"),
                "unidade": item.get("unidade"),
                "valor_kg": item.get("valor_kg"),
                "preco_total": item.get("preco_total")
            })

        # =========================
        # 📤 4. RETORNO FINAL
        # =========================
        print("ITENS NORMALIZADOS:", len(itens_normalizados))

        return {
            "mercado": mercado,
            "data": data,
            "itens": itens_normalizados
        }

    except Exception as e:
        print("ERRO INTERNO:", e)
    return {
        "mercado": None,
        "data": None,
        "itens": []
    }