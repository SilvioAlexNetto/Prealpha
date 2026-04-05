from bs4 import BeautifulSoup
import re


def extrair_dados_nota(html: str):
    soup = BeautifulSoup(html, "html.parser")

    resultado = {
        "mercado": None,
        "data": None,
        "itens": []
    }

    # =========================
    # 🏪 MERCADO
    # =========================
    try:
        topo = soup.find("div", {"class": "txtTopo"})
        if topo:
            resultado["mercado"] = topo.get_text(" ", strip=True)
        else:
            # fallback mais genérico
            strong = soup.find("strong")
            if strong:
                resultado["mercado"] = strong.get_text(strip=True)
    except:
        pass

    # =========================
    # 📅 DATA
    # =========================
    try:
        data_match = soup.find(string=re.compile(r"\d{2}/\d{2}/\d{4}"))
        if data_match:
            resultado["data"] = data_match.strip()
    except:
        pass

    # =========================
    # 🧾 ITENS
    # =========================
    itens_html = soup.find_all("tr")

    for item in itens_html:
        texto = item.get_text(" ", strip=True)

        # ignora linhas inúteis
        if len(texto) < 5:
            continue

        # =========================
        # 🧠 NOME DO PRODUTO
        # =========================
        nome_match = re.match(r"^[A-Za-zÀ-ÿ].+", texto)
        if not nome_match:
            continue

        nome = nome_match.group(0)

        # =========================
        # 📦 QUANTIDADE + UNIDADE
        # =========================
        qtd_match = re.search(
            r"(\d+[\.,]?\d*)\s?(kg|g|mg|l|ml|un|und)",
            texto,
            re.I
        )

        quantidade = None
        unidade = None

        if qtd_match:
            quantidade = float(qtd_match.group(1).replace(",", "."))
            unidade = qtd_match.group(2).lower()

        # =========================
        # 💰 PREÇO TOTAL
        # =========================
        precos = re.findall(r"\d+[\.,]\d{2}", texto)
        preco_total = None

        if precos:
            preco_total = float(precos[-1].replace(",", "."))

        # =========================
        # 💸 VALOR POR KG / LITRO
        # =========================
        valor_kg = None

        # tenta pegar explicitamente (algumas notas têm isso)
        match_kg = re.search(
            r"(?:R\$)?\s*(\d+[\.,]\d{2})\s*/\s*(kg|l)",
            texto,
            re.I
        )

        if match_kg:
            valor_kg = float(match_kg.group(1).replace(",", "."))

        # fallback: calcular se não veio
        elif preco_total and quantidade and unidade:
            try:
                if unidade in ["kg", "l"]:
                    valor_kg = preco_total / quantidade

                elif unidade == "g":
                    valor_kg = preco_total / (quantidade / 1000)

                elif unidade == "ml":
                    valor_kg = preco_total / (quantidade / 1000)

                else:
                    valor_kg = None
            except:
                valor_kg = None

        # =========================
        # 🚫 FILTRO DE RUÍDO
        # =========================
        if not nome or len(nome) < 3:
            continue

        if not preco_total:
            continue

        # =========================
        # 📦 ADD ITEM
        # =========================
        resultado["itens"].append({
            "nome": nome,
            "quantidade": quantidade,
            "unidade": unidade,
            "preco_total": preco_total,
            "valor_kg": round(valor_kg, 2) if valor_kg else None
        })

    return resultado