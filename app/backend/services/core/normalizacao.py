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
async def limpar_nome_produto(nome):
    if not nome:
        return "produto"

    nome = normalizar(nome)

    # =========================
    # 🧾 REMOVE CÓDIGO DA NOTA
    # =========================
    nome = re.sub(r"\(.*?c[oó]digo.*?\)", "", nome)

    # =========================
    # 💰 REMOVE PREÇOS
    # =========================
    nome = re.sub(r"r\$\s*\d+[\.,]\d{2}", "", nome)

    # =========================
    # 📦 REMOVE PESO / VOLUME DO NOME
    # (400g, 1kg, 1l, 500 ml etc)
    # =========================
    nome = re.sub(r"\b\d+[\.,]?\d*\s?(kg|g|mg|l|ml)\b", "", nome)

    # =========================
    # 🔢 REMOVE CÓDIGOS NUMÉRICOS GRANDES
    # =========================
    nome = re.sub(r"\b\d{4,}\b", "", nome)

    # =========================
    # 🧾 REMOVE UNIDADES SOLTAS
    # =========================
    nome = re.sub(r"\b(un|und|cx|pct|lt|emb|pack)\b", "", nome)

    # =========================
    # 🏷️ REMOÇÃO FORTE DE MARCAS (CORE MARKETPLACE)
    # =========================
    MARCAS = {
        "piracanjuba", "nestle", "italac", "itambe", "tirol",
        "batavo", "visconti", "bauducco", "marilan", "piraque",
        "sadia", "perdigao", "seara", "aurora",
        "coca", "cocacola", "pepsi", "fanta", "sprite",
        "garoto", "lacta", "hersheys",
        "yoki", "camil", "quaker",
        "melitta", "pilao", "3coracoes", "trescoracoes",
        "fugini", "quero", "hemmer"
    }

    palavras = nome.split()

    palavras_filtradas = []
    for p in palavras:
        if p in MARCAS:
            continue
        if len(p) <= 2:
            continue
        palavras_filtradas.append(p)

    if not palavras_filtradas:
        return nome.strip()[:30] or "produto"

    # =========================
    # ✂️ LIMITE DE TOKENS (estilo marketplace)
    # =========================
    return " ".join(palavras_filtradas[:5]).strip()



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

    # 🔥 base padrão

    if unidade == "kg":
        return quantidade * 1000, "g"

    if unidade == "l":
        return quantidade * 1000, "ml"

    if unidade in ["g", "ml"]:
        return quantidade, unidade

    if unidade in ["un", "und"]:
        return quantidade, "un"

    return quantidade, unidade


# =========================
# 📦 EXTRAÇÃO SIMPLES
# =========================
def extrair_medida_embalagem(nome: str):
    nome = normalizar(nome)

    match = re.search(r"(\d+[\.,]?\d*)\s?(kg|g|mg|l|ml)", nome)

    if not match:
        return None, None

    qtd = float(match.group(1).replace(",", "."))
    unidade = match.group(2)

    return qtd, unidade


# =========================
# 🔥 EXTRAÇÃO AVANÇADA
# =========================
def extrair_embalagem_completa(nome: str):
    nome = normalizar(nome)

    # 🔥 multipack (6x200ml)
    match_multi = re.search(
        r"(\d+)\s*[xX]\s*(\d+[\.,]?\d*)\s?(kg|g|mg|l|ml)",
        nome
    )

    if match_multi:
        qtd_packs = int(match_multi.group(1))
        qtd_unit = float(match_multi.group(2).replace(",", "."))
        unidade = match_multi.group(3)

        return qtd_packs * qtd_unit, unidade

    # 🔥 c/12 ou 12un
    match_un = re.search(r"(?:c\/)?\s*(\d+)\s*(un|und)", nome)
    if match_un:
        return float(match_un.group(1)), "un"

    # 🔥 padrão simples
    return extrair_medida_embalagem(nome)


# =========================
# 💰 CALCULA VALOR UNITÁRIO
# =========================
def calcular_valor_unitario(quantidade, preco_total):
    try:
        if quantidade and preco_total:
            valor = float(preco_total) / float(quantidade)
            return round(valor, 4)
    except:
        pass

    return None


# =========================
# 🧠 NOVO: IDENTIFICA FRACIONADO
# =========================
def eh_fracionado(unidade):
    unidade = normalizar(unidade)
    return unidade in ["kg", "g", "mg", "l", "ml"]


# =========================
# 🧾 NORMALIZA ITEM COMPLETO
# =========================
def normalizar_item(item):
    nome_original = item.get("nome")

    # 🔥 extrai embalagem ANTES de limpar nome
    qtd_emb, un_emb = extrair_embalagem_completa(nome_original)

    nome = limpar_nome_produto(nome_original)

    quantidade_compra = item.get("quantidade")
    unidade_compra = item.get("unidade")
    preco_total = item.get("preco_total")

    try:
        quantidade_compra = float(quantidade_compra)
    except:
        quantidade_compra = None

    # =========================
    # 🔥 NOVA REGRA INTELIGENTE
    # =========================
    if unidade_compra and eh_fracionado(unidade_compra):
        # ✅ produto por peso/volume (já é consumo real)
        quantidade_final = quantidade_compra
        unidade_final = unidade_compra

    elif qtd_emb and un_emb and quantidade_compra:
        # ✅ produto unitário com embalagem
        quantidade_final = quantidade_compra * qtd_emb
        unidade_final = un_emb

    else:
        # fallback
        quantidade_final = quantidade_compra
        unidade_final = unidade_compra

    quantidade_final, unidade_final = normalizar_unidade(
        quantidade_final,
        unidade_final
    )

    valor_unitario = calcular_valor_unitario(
        quantidade_final,
        preco_total
    )

    return {
        "nome": nome,
        "quantidade": quantidade_final,
        "unidade": unidade_final,
        "valor_unitario": valor_unitario
    }