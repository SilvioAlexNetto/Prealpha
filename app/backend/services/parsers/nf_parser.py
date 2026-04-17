from bs4 import BeautifulSoup
import re


# =========================
# 🔢 CÓDIGO DO PRODUTO
# =========================
def extrair_codigo_produto(texto: str):
    texto_limpo = texto.replace(".", " ").replace(",", " ")

    candidatos = re.findall(r"\b\d{4,14}\b", texto_limpo)

    for codigo in candidatos:
        # ignora se tiver data no texto (linha administrativa)
        if re.search(r"\d{2}/\d{2}/\d{4}", texto):
            continue

        # ignora anos tipo 2023
        if len(codigo) == 4 and codigo.startswith("20"):
            continue

        # ignora códigos inválidos
        if codigo.startswith("000"):
            continue

        return codigo

    return None


# =========================
# 🧠 NOME LIMPO
# =========================
def extrair_nome_produto(texto: str):
    # remove preço
    texto = re.sub(r"R\$\s*\d+[\.,]\d{2}", "", texto)

    # remove quantidade/unidade
    texto = re.sub(
        r"\d+[\.,]?\d*\s?(kg|g|mg|l|ml|un|und)",
        "",
        texto,
        flags=re.I
    )

    # remove códigos grandes
    texto = re.sub(r"\b\d{4,14}\b", "", texto)

    # remove palavras lixo
    texto = re.sub(
        r"\b(cnpj|cpf|cod|codigo|valor|total|item)\b",
        "",
        texto,
        flags=re.I
    )

    # limpa espaços
    texto = re.sub(r"\s+", " ", texto).strip()

    return texto


# =========================
# 🧾 PARSER PRINCIPAL
# =========================
def extrair_dados_nota(html: str):
    print("[DEBUG] 🧾 Iniciando parser")

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
    itens_html = soup.find_all(["tr", "div"])

    print(f"[DEBUG] 🔍 Total de elementos encontrados: {len(itens_html)}")

    for item in itens_html:
        texto = item.get_text(" ", strip=True)

        print(f"\n[DEBUG] 🔹 TEXTO BRUTO: {texto}")

        # =========================
        # 🚫 FILTROS INTELIGENTES
        # =========================
        if len(texto) < 10:
            continue

        if "R$" not in texto:
            continue

        if re.search(
            r"(cnpj|cpf|total|pagamento|forma|troco|valor total)",
            texto,
            re.I
        ):
            continue

        # precisa ter letras (nome de produto)
        if not any(c.isalpha() for c in texto):
            continue

        # =========================
        # EXTRAÇÕES
        # =========================
        codigo = extrair_codigo_produto(texto)
        nome = extrair_nome_produto(texto)

        # =========================
        # 📦 QUANTIDADE
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
        # 💰 PREÇO
        # =========================
        preco_match = re.search(r"R\$\s*(\d+[\.,]\d{2})", texto)
        preco_total = None

        if preco_match:
            preco_total = float(preco_match.group(1).replace(",", "."))

        # =========================
        # 💸 VALOR POR KG
        # =========================
        valor_kg = None

        match_kg = re.search(
            r"(?:R\$)?\s*(\d+[\.,]\d{2})\s*/\s*(kg|l)",
            texto,
            re.I
        )

        if match_kg:
            valor_kg = float(match_kg.group(1).replace(",", "."))

        elif preco_total and quantidade and unidade:
            try:
                if unidade in ["kg", "l"]:
                    valor_kg = preco_total / quantidade

                elif unidade in ["g", "ml"]:
                    valor_kg = preco_total / (quantidade / 1000)
            except:
                valor_kg = None

        # =========================
        # 🚫 VALIDAÇÃO FINAL
        # =========================
        if not nome or len(nome) < 3:
            continue

        if not preco_total:
            continue

        print(f"[DEBUG] ✅ ITEM EXTRAÍDO: nome={nome} | codigo={codigo} | preco={preco_total}")

        resultado["itens"].append({
            "nome": nome,
            "codigo": codigo,
            "quantidade": quantidade,
            "unidade": unidade,
            "preco_total": preco_total,
            "valor_kg": round(valor_kg, 2) if valor_kg else None
        })

    print(f"\n[DEBUG] 📦 TOTAL FINAL DE ITENS: {len(resultado['itens'])}")

    return resultado