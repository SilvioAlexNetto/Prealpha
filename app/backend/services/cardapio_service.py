import os
import sys
import json
import random
import unicodedata
from copy import deepcopy


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.append(BASE_DIR)

from FabricaReceitas import proteinasKG, proteinasUN, carboidratos, vegetais

# =========================
# PATH DO JSON DE RECEITAS
# =========================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RECEITAS_PATH = os.path.join(BASE_DIR, "database", "BancoReceitas.json")

# =========================
# FUNÇÕES DE NORMALIZAÇÃO
# =========================
def remover_acentos(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

def singularizar(texto):
    texto = texto.strip().lower()
    texto = remover_acentos(texto)
    if texto.endswith("s") and len(texto) > 1:
        texto = texto[:-1]
    return texto

def normalizar_ingrediente(texto):
    return singularizar(texto)

# =========================
# CONVERTER PARA MENOR UNIDADE
# =========================
def para_menor_unidade(quantidade, unidade):
    unidade = unidade.lower()
    if unidade in ["kg", "quilograma", "quilo"]:
        return quantidade * 1000, "g"
    if unidade in ["l", "litro", "litros"]:
        return quantidade * 1000, "ml"
    return quantidade, unidade

# =========================
# CARREGAR RECEITAS
# =========================
def carregar_receitas():
    if not os.path.exists(RECEITAS_PATH):
        raise FileNotFoundError(f"O arquivo JSON de receitas não foi encontrado: {RECEITAS_PATH}")

    with open(RECEITAS_PATH, "r", encoding="utf-8") as f:
        receitas = json.load(f)
        
    for receita in receitas:
        # dentro de carregar_receitas()
        receita["categoria"] = normalizar_ingrediente(receita["categoria"])
        for ing in receita["ingredientes"]:
            ing["nome"] = normalizar_ingrediente(ing["nome"])
            ing["unidade"] = normalizar_ingrediente(ing["unidade"])

    return receitas

# =========================
# BUSCAR RECEITAS POR TIPO
# =========================
def buscar_receitas_por_tipo(tipo, receitas=None):
    if receitas is None:
        receitas = carregar_receitas()
    return [r for r in receitas if r["categoria"] == tipo]

# =========================
# VERIFICAR DISPONIBILIDADE
# =========================
def receita_disponivel(receita, estoque):
    estoque_dict = {}

    for item in estoque:
        # 🔧 UPGRADE: proteção contra dados inválidos
        nome_bruto = item.get("nome") or item.get("item")
        if not nome_bruto:
            continue

        nome = normalizar_ingrediente(nome_bruto)
        qtd, unid = para_menor_unidade(item["quantidade"], item["unidade"])
        estoque_dict[nome] = {"quantidade": qtd, "unidade": unid}

    for ing in receita["ingredientes"]:
        # 🔧 UPGRADE: proteção extra
        if "nome" not in ing:
            continue

        nome = normalizar_ingrediente(ing["nome"])
        qtd_necessaria, unid_necessaria = para_menor_unidade(
            ing["quantidade"], ing["unidade"]
        )

        if nome not in estoque_dict:
            return False
        if estoque_dict[nome]["unidade"] != unid_necessaria:
            return False
        if estoque_dict[nome]["quantidade"] < qtd_necessaria:
            return False

    return True

# =========================
# ABATER ESTOQUE
# =========================
def abater_estoque(receita, estoque):
    estoque_dict = {}

    # 🔹 Mapeia estoque preservando nome original (ROBUSTO)
    for item in estoque:
        nome_original = item.get("nome") or item.get("item")
        if not nome_original:
            continue

        nome_norm = normalizar_ingrediente(nome_original)
        qtd, unid = para_menor_unidade(item["quantidade"], item["unidade"])

        estoque_dict[nome_norm] = {
            "nome": nome_original,   # ✅ nome garantido
            "quantidade": qtd,
            "unidade": unid
        }

    # 🔹 Abate ingredientes
    for ing in receita["ingredientes"]:
        nome_norm = normalizar_ingrediente(ing["nome"])
        qtd_necessaria, _ = para_menor_unidade(
            ing["quantidade"], ing["unidade"]
        )

        if nome_norm in estoque_dict:
            estoque_dict[nome_norm]["quantidade"] -= qtd_necessaria

            if estoque_dict[nome_norm]["quantidade"] <= 0:
                del estoque_dict[nome_norm]

    # 🔹 Reconstrói estoque final (histórico)
    estoque_atualizado = []
    for dados in estoque_dict.values():
        estoque_atualizado.append({
            "nome": dados["nome"],
            "quantidade": dados["quantidade"],
            "unidade": dados["unidade"]
        })

    return estoque_atualizado

def normalizar_estoque(estoque):
    estoque_corrigido = []

    for item in estoque:
        nome = item.get("nome") or item.get("item")
        if not nome:
            continue  # ignora lixo

        estoque_corrigido.append({
            "nome": nome,
            "quantidade": item["quantidade"],
            "unidade": item["unidade"]
        })

    return estoque_corrigido

# =========================
# MUDANÇAS
# =========================

estoque = [
    {"nome": "Peito de frango", "quantidade": 500, "unidade": "g"},
    {"nome": "arroz branco", "quantidade": 200, "unidade": "g"},
]

def classificar_estoque(estoque):
    categorias = {
        "proteina": [],
        "carbo": [],
        "vegetal": []
    }

    for item in estoque:
        nome = item["nome"].lower()

        if any(nome in p.lower() for p in proteinasKG + proteinasUN):
            categorias["proteina"].append(item)

        elif any(nome in c.lower() for c in carboidratos):
            categorias["carbo"].append(item)

        elif any(nome in v.lower() for v in vegetais):
            categorias["vegetal"].append(item)

    return categorias

import random

def gerar_receita_com_estoque(estoque):
    cat = classificar_estoque(estoque)

    if not cat["proteina"] or not cat["carbo"]:
        return None

    proteina = random.choice(cat["proteina"])
    carbo = random.choice(cat["carbo"])

    vegetais = []
    if cat["vegetal"]:
        vegetais = random.sample(cat["vegetal"], min(2, len(cat["vegetal"])))

    ingredientes = [proteina, carbo] + vegetais

    return {
        "nome": f"{proteina['nome']} com {carbo['nome']}",
        "categoria": "almoco",
        "ingredientes": ingredientes,
        "modo_preparo": ["Prepare os ingredientes e cozinhe."],
        "tempo_preparo": "30 min",
        "Porcao": "1"
    }




def gerar_cardapio(estoque, receitas=None):
    from datetime import datetime
    import calendar
    import random
    from copy import deepcopy

    tipos = ["cafe", "almoco", "jantar"]

    # ✅ ESTOQUE DE TRABALHO
    estoque_atual = normalizar_estoque(deepcopy(estoque))

    cardapio = {}

    hoje = datetime.now()
    mes = hoje.month
    ano = hoje.year
    total_dias = calendar.monthrange(ano, mes)[1]

    if receitas is None:
        receitas = carregar_receitas()

    for dia in range(1, total_dias + 1):
        cardapio[dia] = {}

        for tipo in tipos:
            receita_escolhida = None

            # =========================
            # 🔥 1. TENTA GERAR DINÂMICO
            # =========================
            for tentativa in range(5):
                receita = gerar_receita_com_estoque(estoque_atual)

                if receita:
                    receita_escolhida = receita
                    estoque_atual = abater_estoque(receita, estoque_atual)
                    break

            # =========================
            # 🛟 2. FALLBACK → JSON
            # =========================
            if not receita_escolhida:
                receitas_disponiveis = [
                    r for r in receitas if r["categoria"] == tipo
                ]
                random.shuffle(receitas_disponiveis)

                for r in receitas_disponiveis:
                    if receita_disponivel(r, estoque_atual):
                        receita_escolhida = r
                        estoque_atual = abater_estoque(r, estoque_atual)
                        break

            # =========================
            # ✅ GARANTE ESTRUTURA
            # =========================
            cardapio[dia][tipo] = receita_escolhida if receita_escolhida else {}

    return cardapio, estoque_atual

def listar_ingredientes_e_unidades():
    receitas = carregar_receitas()

    ingredientes = {}
    unidades = set()

    for receita in receitas:
        for item in receita.get("ingredientes", []):
            nome = item["nome"].strip().lower()
            unidade = item["unidade"].strip().lower()

            ingredientes[nome] = True
            unidades.add(unidade)

    return {
        "ingredientes": sorted(ingredientes.keys()),
        "unidades": sorted(unidades)
    }

if __name__ == "__main__":
    estoque = [
        {"nome": "frango", "quantidade": 500, "unidade": "g"},
        {"nome": "arroz", "quantidade": 200, "unidade": "g"},
        {"nome": "cenoura", "quantidade": 100, "unidade": "g"}
    ]

    print(gerar_receita_com_estoque(estoque))