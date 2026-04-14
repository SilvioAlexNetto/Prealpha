import unicodedata
import re

# =========================
# 🔤 NORMALIZA TEXTO SIMPLES
# =========================
def normalizar(texto):
    if texto is None:
        return ""

    return unicodedata.normalize("NFD", str(texto).lower()) \
        .encode("ascii", "ignore") \
        .decode("utf-8") \
        .strip()


# =========================
# 🧠 LIMPA NOME DE PRODUTO
# =========================
def limpar_nome_produto(nome):
    nome = normalizar(nome)

    # remove números + unidades
    nome = re.sub(r"\b\d+[\.,]?\d*\s?(kg|g|mg|l|ml|un|und)\b", "", nome)

    # remove números soltos
    nome = re.sub(r"\b\d+\b", "", nome)

    # remove marcas comuns (expandível)
    blacklist = [
        "italac", "piracanjuba", "nestle", "itambe", "tirol", "batavo",
        "garoto", "lacta", "hersheys", "arcor",
        "marilan", "piraque", "bauducco",
        "sadia", "perdigao", "seara",
        "coca", "cocacola", "pepsi", "fanta", "sprite",
        "quaker", "yoki", "camil",
        "hemmer", "quero", "fugini",
        "pilao", "melitta", "trescoracoes",
        "tradicional", "original"
    ]

    palavras = nome.split()

    palavras = [
        p for p in palavras
        if p not in blacklist and len(p) > 2
    ]

    if not palavras:
        return "produto"

    # pega no máximo 3 palavras
    nome_final = " ".join(palavras[:3])

    return nome_final.strip()


# =========================
# 🔄 CONVERSÃO DE UNIDADE
# =========================
def normalizar_unidade(quantidade, unidade):
    unidade = normalizar(unidade)

    if quantidade is None:
        return None, unidade

    try:
        quantidade = float(quantidade)
    except:
        return None, unidade

    # 🔥 PADRÃO: TUDO PARA BASE (g / ml / un)

    if unidade == "kg":
        return quantidade * 1000, "g"

    if unidade == "l":
        return quantidade * 1000, "ml"

    if unidade in ["g", "ml", "un", "und"]:
        return quantidade, "g" if unidade == "g" else ("ml" if unidade == "ml" else "un")

    return quantidade, unidade


# =========================
# 💰 CALCULA VALOR UNITÁRIO
# =========================
def calcular_valor_unitario(quantidade, preco_total):
    try:
        if quantidade and preco_total:
            valor = float(preco_total) / float(quantidade)
            return round(valor, 2)
    except:
        pass

    return None


# =========================
# 🧾 NORMALIZA ITEM COMPLETO
# =========================
def normalizar_item(item):
    nome = limpar_nome_produto(item.get("nome"))

    quantidade = item.get("quantidade")
    unidade = item.get("unidade")
    preco_total = item.get("preco_total")

    quantidade, unidade = normalizar_unidade(quantidade, unidade)

    valor_unitario = calcular_valor_unitario(quantidade, preco_total)

    return {
        "nome": nome,
        "quantidade": quantidade,
        "unidade": unidade,
        "valor_unitario": valor_unitario
    }