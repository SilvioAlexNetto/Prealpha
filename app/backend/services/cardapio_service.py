import os
import sys
import json
import random
import unicodedata
from copy import deepcopy

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.append(BASE_DIR)

from FabricaReceitas import (
    proteinasKG, proteinasUN, carboidratos, vegetais,
    massas, molhos, folhas_saladas, caldos,
    gerar_receita
)

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
        nome_bruto = item.get("nome") or item.get("item")
        if not nome_bruto:
            continue

        nome = normalizar_ingrediente(nome_bruto)
        qtd, unid = para_menor_unidade(item["quantidade"], item["unidade"])
        estoque_dict[nome] = {"quantidade": qtd, "unidade": unid}

    for ing in receita["ingredientes"]:
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

    for item in estoque:
        nome_original = item.get("nome") or item.get("item")
        if not nome_original:
            continue

        nome_norm = normalizar_ingrediente(nome_original)
        qtd, unid = para_menor_unidade(item["quantidade"], item["unidade"])

        estoque_dict[nome_norm] = {
            "nome": nome_original,
            "quantidade": qtd,
            "unidade": unid
        }

    for ing in receita["ingredientes"]:
        nome_norm = normalizar_ingrediente(ing["nome"])
        qtd_necessaria, _ = para_menor_unidade(
            ing["quantidade"], ing["unidade"]
        )

        if nome_norm in estoque_dict:
            estoque_dict[nome_norm]["quantidade"] -= qtd_necessaria

            if estoque_dict[nome_norm]["quantidade"] <= 0:
                del estoque_dict[nome_norm]

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
            continue

        estoque_corrigido.append({
            "nome": nome,
            "quantidade": item["quantidade"],
            "unidade": item["unidade"]
        })

    return estoque_corrigido

# =========================
# CLASSIFICAR ESTOQUE
# =========================
def classificar_estoque(estoque):
    categorias = {
        "proteinasKG": [],
        "proteinasUN": [],
        "carboidratos": [],
        "vegetais": [],
        "massas": [],
        "molhos": [],
        "caldos": [],
        "folhas_saladas": []
    }

    for item in estoque:
        nome = normalizar_ingrediente(item["nome"])

        if any(nome in normalizar_ingrediente(p) for p in proteinasKG):
            categorias["proteinasKG"].append(item)

        elif any(nome in normalizar_ingrediente(p) for p in proteinasUN):
            categorias["proteinasUN"].append(item)

        elif any(nome in normalizar_ingrediente(c) for c in carboidratos):
            categorias["carboidratos"].append(item)

        elif any(nome in normalizar_ingrediente(v) for v in vegetais):
            categorias["vegetais"].append(item)

        elif any(nome in normalizar_ingrediente(m) for m in massas):
            categorias["massas"].append(item)

        elif any(nome in normalizar_ingrediente(m) for m in molhos):
            categorias["molhos"].append(item)

        elif any(nome in normalizar_ingrediente(c["nome"]) for c in caldos):
            categorias["caldos"].append(item)

        elif any(nome in normalizar_ingrediente(f) for f in folhas_saladas):
            categorias["folhas_saladas"].append(item)

    return categorias

# =========================
# GERAR RECEITA CUSTOM (SEM GLOBAL)
# =========================
def gerar_receita_custom(categorias):

    def escolher_proteina_local():
        if categorias["proteinasKG"]:
            nome = random.choice(categorias["proteinasKG"])["nome"]
            return {"nome": nome, "quantidade": 120, "unidade": "g"}
        if categorias["proteinasUN"]:
            nome = random.choice(categorias["proteinasUN"])["nome"]
            return {"nome": nome, "quantidade": 2, "unidade": "unidade"}
        raise Exception("Sem proteína")

    def escolher_item(lista, erro):
        if not lista:
            raise Exception(erro)
        return random.choice(lista)["nome"]

    proteina = escolher_proteina_local()
    carbo = escolher_item(categorias["carboidratos"], "Sem carboidrato")

    if len(categorias["vegetais"]) < 2:
        raise Exception("Sem vegetais suficientes")

    vegs = random.sample(categorias["vegetais"], 2)

    return {
        "nome": f"{proteina['nome']} com {carbo}",
        "categoria": random.choice(["cafe", "almoco", "jantar"]),
        "ingredientes": [
            proteina,
            {"nome": carbo, "quantidade": 90, "unidade": "g"},
            {"nome": vegs[0]["nome"], "quantidade": 80, "unidade": "g"},
            {"nome": vegs[1]["nome"], "quantidade": 80, "unidade": "g"}
        ]
    }

# =========================
# GERAR CARDÁPIO (FIXADO)
# =========================
def gerar_cardapio(estoque, receitas=None):
    from datetime import datetime
    import calendar

    tipos = ["cafe", "almoco", "jantar"]

    estoque_atual = normalizar_estoque(deepcopy(estoque))

    cardapio = {}

    hoje = datetime.now()
    mes = hoje.month
    ano = hoje.year
    total_dias = calendar.monthrange(ano, mes)[1]

    for dia in range(1, total_dias + 1):
        cardapio[dia] = {}

        for tipo in tipos:
            receita_escolhida = None

            for _ in range(50):
                try:
                    categorias = classificar_estoque(estoque_atual)
                    receita = gerar_receita_custom(categorias)
                    receita["categoria"] = tipo

                    if receita_disponivel(receita, estoque_atual):
                        receita_escolhida = receita
                        estoque_atual = abater_estoque(receita, estoque_atual)
                        break

                except:
                    continue

            cardapio[dia][tipo] = receita_escolhida if receita_escolhida else {}

    return cardapio, estoque_atual

# =========================
# UTILIDADES
# =========================
def listar_ingredientes_e_unidades():
    ingredientes = set()
    unidades = set()

    listas = [
        proteinasKG, proteinasUN, carboidratos,
        vegetais, massas, molhos, folhas_saladas
    ]

    for lista in listas:
        for item in lista:
            if isinstance(item, dict):
                nome = item.get("nome")
                if nome:
                    ingredientes.add(nome.lower())
            else:
                ingredientes.add(str(item).lower())

    unidades.update(["g", "kg", "ml", "l", "unidade", "fatia"])

    return {
        "ingredientes": sorted(ingredientes),
        "unidades": sorted(unidades)
    }

def salvar_receitas_dinamicas(receitas):
    with open(RECEITAS_PATH, "w", encoding="utf-8") as f:
        json.dump(receitas, f, ensure_ascii=False, indent=4)