from app.backend.services.utils.http_client import buscar_url
from app.backend.services.parsers.nf_parser import extrair_dados_nota
from app.backend.services.core.resolver_nome_produto import resolver_nome, buscar_openfoodfacts_por_ean
from app.backend.services.core.produto_codigo_service import (
    buscar_produto_por_codigo,
    salvar_produto_codigo,
    is_ean
)



async def ler_nota_fiscal(url: str):
    try:
        # =========================
        # 🌐 1. BAIXAR HTML
        # =========================
        html = await buscar_url(url)

        # =========================
        # 🧾 2. PARSEAR NOTA
        # =========================
        dados = extrair_dados_nota(html)

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
            nome = item.get("nome")

            if not nome:
                continue

            nome_original = nome

            codigo = item.get("codigo")

            nome_resolvido = None

            # =========================
            # 1. CACHE LOCAL POR CÓDIGO
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
            # 3. FALLBACK → NOME
            # =========================
            if not nome_resolvido:
                nome_resolvido = await resolver_nome(nome_original)

            # =========================
            # 4. SALVAR APRENDIZADO
            # =========================
            if codigo and nome_resolvido:
                salvar_produto_codigo(mercado, codigo, nome_resolvido)

            itens_normalizados.append({
                "nome": nome_original,            # UI
                "nome_resolvido": nome_resolvido, # 🔥 NOVO INTELIGENTE
                "quantidade": item.get("quantidade"),
                "unidade": item.get("unidade"),
                "valor_kg": item.get("valor_kg", None),
                "preco_total": item.get("preco_total")
            })

        # =========================
        # 📤 4. RETORNO FINAL
        # =========================
        return {
            "mercado": mercado,
            "data": data,
            "itens": itens_normalizados
        }

    except Exception as e:
        return {
            "erro": str(e)
        }