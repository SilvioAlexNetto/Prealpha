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
    print("[DEBUG] 🧾 Parser ROBUSTO iniciado")

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
    # 🔥 TEXTO COMPLETO (CHAVE)
    # =========================
    texto = soup.get_text(" ", strip=True)

    # normalização pesada
    texto = re.sub(r"\s+", " ", texto)

    print("\n[DEBUG] 🧠 TEXTO NORMALIZADO:")
    print(texto[:1000])  # preview

    # =========================
    # 🧾 SPLIT POR PRODUTOS
    # =========================
    blocos = re.split(r"\(Código:\s*\d+\s*\)", texto)

    print(f"\n[DEBUG] 📦 TOTAL DE BLOCOS: {len(blocos)}")

    for bloco in blocos:
        bloco = bloco.strip()

        if len(bloco) < 20:
            continue

        # ignora partes irrelevantes
        if re.search(
            r"(valor a pagar|forma de pagamento|troco|cpf|cnpj|qtd\. total)",
            bloco,
            re.I
        ):
            continue

        print(f"\n[DEBUG] 🔹 BLOCO:")
        print(bloco)

        # =========================
        # 🧠 NOME
        # =========================
        nome_match = re.match(r"([A-Z0-9\s\-\.,]+)", bloco)

        nome = nome_match.group(1).strip() if nome_match else None

        # limpeza básica
        if nome:
            nome = re.sub(r"\s+", " ", nome)

        # =========================
        # 📦 QUANTIDADE
        # =========================
        qtd_match = re.search(
            r"(\d+[\.,]?\d*)\s?(kg|g|mg|l|ml|un|und)",
            bloco,
            re.I
        )

        quantidade = None
        unidade = None

        if qtd_match:
            quantidade = float(qtd_match.group(1).replace(",", "."))
            unidade = qtd_match.group(2).lower()

        # =========================
        # 💰 PREÇO TOTAL (ROBUSTO)
        # =========================
        preco_match = re.search(
            r"Vl\.?\s*Total\s*(\d+[\.,]\d{2})",
            bloco,
            re.I
        )

        if not preco_match:
            preco_match = re.search(
                r"(\d+[\.,]\d{2})",
                bloco
            )

        preco_total = None

        if preco_match:
            preco_total = float(preco_match.group(1).replace(",", "."))

        # =========================
        # 🚫 VALIDAÇÃO
        # =========================
        if not nome or len(nome) < 3:
            continue

        if not preco_total:
            continue

        print(f"[DEBUG] ✅ ITEM: {nome} | R$ {preco_total}")

        resultado["itens"].append({
            "nome": nome,
            "codigo": None,  # opcional depois melhorar
            "quantidade": quantidade,
            "unidade": unidade,
            "preco_total": preco_total,
            "valor_kg": None
        })

    print(f"\n[DEBUG] 📦 TOTAL FINAL DE ITENS: {len(resultado['itens'])}")

    return resultado