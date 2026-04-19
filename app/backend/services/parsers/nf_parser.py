from bs4 import BeautifulSoup
import re
from app.backend.services.core.normalizacao import extrair_embalagem_completa
from app.backend.services.core.produto_codigo_service import buscar_produto_por_codigo, salvar_produto_codigo
from app.backend.services.core.resolver_nome_produto import resolver_nome


pattern = re.compile(
    r"([A-Z0-9\s\.\-\/]+?)\s*\(Código:\s*(\d+)\s*\)\s*(.*?)\s*Vl\.?\s*Total\s*(\d+[\.,]\d{2})",
    re.IGNORECASE
)

# =========================
# 🔢 CÓDIGO DO PRODUTO
# =========================
def extrair_codigo_produto(texto: str):
    match = re.search(r"\(Código:\s*(\d+)\)", texto, re.I)
    if match:
        return match.group(1)
    return None


# =========================
# 🧠 NOME LIMPO
# =========================
def extrair_nome_produto(texto: str):
    # remove "(Código: xxx)"
    texto = re.sub(r"\(.*?c[oó]digo.*?\)", "", texto, flags=re.I)

    # corta antes de Qtde (sem destruir tudo)
    texto = re.split(r"Qtde\.:", texto, flags=re.I)[0]

    # remove preço
    texto = re.sub(r"R\$\s*\d+[\.,]\d{2}", "", texto)

    # remove Vl. Unit / Total
    texto = re.sub(r"Vl\.?\s*Unit\.\s*\d+[\.,]\d{2}", "", texto, flags=re.I)
    
    texto = re.sub(r"Vl\.?\s*Total\s*\d+[\.,]\d{2}", "", texto, flags=re.I)

    # remove números grandes (códigos)
    texto = re.sub(r"\b\d{4,14}\b", "", texto)

    # remove unidades
    texto = re.sub(
        r"\d+[\.,]?\d*\s?(kg|g|mg|l|ml|un|und)",
        "",
        texto,
        flags=re.I
    )

    # remove estados isolados no começo (SP, RJ, etc)
    texto = re.sub(r"^(sp|rj|mg|es)\s+", "", texto, flags=re.I)

    # remove lixo
    texto = re.sub(
        r"\b(cnpj|cpf|valor|total|item)\b",
        "",
        texto,
        flags=re.I
    )

    texto = re.sub(r"\s+", " ", texto).strip()

    return texto

# =========================
# 🧾 PARSER PRINCIPAL
# =========================

async def extrair_dados_nota(html: str):
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
            nome = None

            mercado = resultado.get("mercado") or "global"

            # 🔥 1. tenta buscar no banco
            if codigo:
                nome = buscar_produto_por_codigo(mercado, codigo)

            # 🔥 2. se não encontrou, processa
            if not nome:
                nome_pre = extrair_nome_produto(nome_bruto)
                nome = await resolver_nome(nome_pre)

                # 🔥 3. salva aprendizado
                if codigo and nome:
                    salvar_produto_codigo(mercado, codigo, nome)

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

            # 🔥 tenta extrair embalagem real
            qtd_emb, un_emb = extrair_embalagem_completa(nome_bruto)

            quantidade_final = quantidade
            unidade_final = unidade

            # 🔥 REGRA INTELIGENTE
            if unidade in ["un", "und"] and qtd_emb and un_emb:
                quantidade_final = quantidade * qtd_emb if quantidade else qtd_emb
                unidade_final = un_emb

            resultado["itens"].append({
                "nome": nome,
                "codigo": codigo,
                "quantidade": quantidade_final,
                "unidade": unidade_final,
                "preco_total": preco_total,
                "valor_kg": round(valor_kg, 2) if valor_kg else None
            })

        except Exception as e:
            print("[ERRO ITEM]", e)
            continue

    print(f"\n[DEBUG] 📦 TOTAL FINAL: {len(resultado['itens'])}")

    return resultado