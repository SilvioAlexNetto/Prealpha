from app.backend.services.http_client import buscar_url
from app.backend.services.parser_nfe import extrair_dados_nota
from app.backend.services.normalizar import normalizar


async def ler_nota_fiscal(url: str):
    try:
        # =========================
        # 🌐 1. BAIXAR HTML
        # =========================
        html = buscar_url(url)

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

            nome_limpo = normalizar(nome)

            itens_normalizados.append({
                "nome": nome_limpo,
                "quantidade": item.get("quantidade"),
                "unidade": item.get("unidade"),
                "valor_kg": item.get("valor_kg"),
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