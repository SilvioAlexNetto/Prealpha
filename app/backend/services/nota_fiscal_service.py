from app.backend.services.utils.http_client import buscar_url
from app.backend.services.parsers.nf_parser import extrair_dados_nota
from app.backend.services.core.resolver_nome_produto import resolver_nome


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
        data = dados.get("data")
        itens = dados.get("itens", [])

        itens_normalizados = []

        for item in itens:
            nome = item.get("nome")

            if not nome:
                continue

            nome_original = nome

            nome_resolvido = await resolver_nome(nome_original)

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