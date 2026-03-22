import os
import sys
import json
import random
import unicodedata
from copy import deepcopy


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.append(BASE_DIR)

from FabricaReceitas import proteinasKG, proteinasUN, carboidratos, vegetais, massas, molhos, folhas_saladas, caldos, gerar_receita

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

def aplicar_estoque_no_fabrica(categorias):
    # limpa listas
    proteinasKG.clear()
    proteinasUN.clear()
    carboidratos.clear()
    vegetais.clear()
    massas.clear()
    molhos.clear()
    folhas_saladas.clear()

    # injeta apenas o que o usuário tem
    proteinasKG.extend([i["nome"] for i in categorias["proteinasKG"]])
    proteinasUN.extend([i["nome"] for i in categorias["proteinasUN"]])
    carboidratos.extend([i["nome"] for i in categorias["carboidratos"]])
    vegetais.extend([i["nome"] for i in categorias["vegetais"]])
    massas.extend([i["nome"] for i in categorias["massas"]])
    molhos.extend([i["nome"] for i in categorias["molhos"]])
    folhas_saladas.extend([i["nome"] for i in categorias["folhas_saladas"]])

def gerar_receitas_do_estoque(estoque, qtd=50):
    categorias = classificar_estoque(estoque)
    print("CATEGORIAS:", categorias)
    aplicar_estoque_no_fabrica(categorias)

    receitas = []

    for _ in range(qtd):
        try:
            receita = gerar_receita()
            # 🔧 normaliza categoria
            receita["categoria"] = random.choice(["cafe", "almoco", "jantar"])

            receitas.append(receita)
        except:
            continue

    return receitas




def gerar_cardapio(estoque, receitas=None):
    from datetime import datetime
    import calendar
    import random
    from copy import deepcopy

    tipos = ["cafe", "almoco", "jantar"]

    estoque_atual = normalizar_estoque(deepcopy(estoque))

    # 🔥 1. GERA RECEITAS DINÂMICAS
    receitas = gerar_receitas_do_estoque(estoque_atual, qtd=100)

    # 🔥 2. SALVA NO JSON
    salvar_receitas_dinamicas(receitas)

    # 🔥 3. RECARREGA
    receitas = carregar_receitas()

    cardapio = {}

    hoje = datetime.now()
    mes = hoje.month
    ano = hoje.year
    total_dias = calendar.monthrange(ano, mes)[1]

    for dia in range(1, total_dias + 1):
        cardapio[dia] = {}

        for tipo in tipos:
            receitas_disponiveis = [
                r for r in receitas if r["categoria"] == tipo
            ]

            random.shuffle(receitas_disponiveis)

            receita_escolhida = None

            for r in receitas_disponiveis:
                if receita_disponivel(r, estoque_atual):
                    receita_escolhida = r
                    estoque_atual = abater_estoque(r, estoque_atual)
                    break

            cardapio[dia][tipo] = receita_escolhida if receita_escolhida else {}

    return cardapio, estoque_atual

def listar_ingredientes_e_unidades():
    ingredientes = set()
    unidades = set()

    # 🔥 TODAS AS LISTAS DO FABRICA
    listas = [
        proteinasKG,
        proteinasUN,
        carboidratos,
        vegetais,
        massas,
        molhos,
        folhas_saladas
    ]

    for lista in listas:
        for item in lista:
            if isinstance(item, dict):
                nome = item.get("nome")
                if nome:
                    ingredientes.add(nome.lower())
            else:
                ingredientes.add(str(item).lower())

    # 🔥 UNIDADES PADRÃO DO SISTEMA
    unidades.update(["g", "kg", "ml", "l", "unidade", "fatia"])

    return {
        "ingredientes": sorted(ingredientes),
        "unidades": sorted(unidades)
    }

def salvar_receitas_dinamicas(receitas):
    with open(RECEITAS_PATH, "w", encoding="utf-8") as f:
        json.dump(receitas, f, ensure_ascii=False, indent=4)