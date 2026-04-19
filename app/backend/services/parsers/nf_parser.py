from bs4 import BeautifulSoup
import re


# =========================
# 🔢 CÓDIGO DO PRODUTO
# =========================
def extrair_codigo_produto(texto: str):
    texto_limpo = texto.replace(".", " ").replace(",", " ")

    candidatos = re.findall(r"\b\d{3,14}\b", texto_limpo)

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
    # remove trecho "(Código: xxx)"
    texto = re.sub(r"\(.*?c[oó]digo.*?\)", "", texto, flags=re.I)

    # remove Qtde e unidade
    texto = re.sub(r"Qtde\.:.*", "", texto, flags=re.I)

    # remove Vl. Unit e Vl. Total
    texto = re.sub(r"Vl\.?.*", "", texto, flags=re.I)

    return texto


# =========================
# 🧾 PARSER PRINCIPAL
# =========================

def extrair_dados_nota(html: str):
    print("[DEBUG] 🧾 Parser NÍVEL PRODUÇÃO iniciado")

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
        texto_full = soup.get_text(" ", strip=True)

        data_match = re.search(r"\d{2}/\d{2}/\d{4}", texto_full)
        if data_match:
            resultado["data"] = data_match.group()
    except:
        pass

    # =========================
    # 🧠 TEXTO LIMPO GLOBAL
    # =========================
    texto = soup.get_text(" ", strip=True)

    # remove espaços duplicados
    texto = re.sub(r"\s+", " ", texto)

    print("\n[DEBUG] 🧠 TEXTO NORMALIZADO:")
    print(texto[:500])

    # =========================
    # 🔥 ENCONTRAR TODOS OS PRODUTOS
    # =========================
    pattern = re.compile(
        r"(.*?)\(Código:\s*(\d+)\s*\)(.*?)Vl\.?\s*Total\s*(\d+[\.,]\d{2})",
        re.IGNORECASE
    )

    matches = list(pattern.finditer(texto))

    print(f"\n[DEBUG] 🔍 TOTAL MATCHES: {len(matches)}")

    for match in matches:
        try:
            nome_bruto = match.group(1).strip()
            codigo = match.group(2)
            trecho_meio = match.group(3)
            preco_str = match.group(4)

            # =========================
            # 🧠 LIMPEZA DO NOME
            # =========================
            nome = limpar_nome_produto(nome_bruto)

            # fallback se vier lixo
            if len(nome) < 3:
                nome = nome_bruto.strip()

            # =========================
            # 📦 QUANTIDADE
            # =========================
            qtd_match = re.search(
                r"Qtde\.:\s*(\d+[\.,]?\d*)",
                trecho_meio,
                re.IGNORECASE
            )

            quantidade = None
            if qtd_match:
                quantidade = float(qtd_match.group(1).replace(",", "."))

            # =========================
            # 📏 UNIDADE
            # =========================
            un_match = re.search(
                r"UN:\s*(kg|g|mg|l|ml|un|und)",
                trecho_meio,
                re.IGNORECASE
            )

            unidade = None
            if un_match:
                unidade = un_match.group(1).lower()

            # =========================
            # 💰 PREÇO
            # =========================
            preco_total = float(preco_str.replace(",", "."))

            # =========================
            # 💸 VALOR POR KG
            # =========================
            valor_kg = None

            if quantidade and unidade:
                try:
                    if unidade in ["kg", "l"]:
                        valor_kg = preco_total / quantidade
                    elif unidade in ["g", "ml"]:
                        valor_kg = preco_total / (quantidade / 1000)
                except:
                    pass

            print(f"[DEBUG] ✅ ITEM: {nome} | {codigo} | R$ {preco_total}")

            resultado["itens"].append({
                "nome": nome,
                "codigo": codigo,
                "quantidade": quantidade,
                "unidade": unidade,
                "preco_total": preco_total,
                "valor_kg": round(valor_kg, 2) if valor_kg else None
            })

        except Exception as e:
            print("[ERRO ITEM]", e)
            continue

    print(f"\n[DEBUG] 📦 TOTAL FINAL: {len(resultado['itens'])}")

    return resultado