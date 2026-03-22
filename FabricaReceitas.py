import random
import json

# =========================
# BASES
# =========================

proteinasKG = [
    "Peito de frango", "Coxa de frango", "Sobrecoxa de frango", "Frango inteiro",
    "Filé de frango", "Asa de frango", "Frango desfiado",

    "Patinho", "Acém", "Alcatra", "Músculo bovino", "Coxão mole",
    "Coxão duro", "Lagarto", "Fraldinha", "Picanha", "Contrafilé",
    "Maminha", "Filé mignon", "Costela bovina", "Cupim", "Acém moído",
    "Carne moída", "Carne de segunda",

    "Lombo suíno", "Pernil suíno", "Costelinha suína", "Bisteca suína",
    "Panceta", "Barriga suína", "Filé suíno",

    "Salmão", "Tilápia", "Bacalhau", "Merluza", "Sardinha",
    "Atum", "Truta", "Pescada", "Dourado", "Corvina",
    "Cação", "Anchova", "Linguado",

    "Frango caipira", "Fígado bovino", "Fígado de frango",
    "Moela de frango", "Coração de frango",

    "Carne suína moída", "Carne bovina moída magra",
    "Costela bovina", "Peixe branco",

    "Cordeiro", "Peru", "Peito de peru",
    "Linguiça toscana", "Linguiça calabresa",
    "Linguiça de frango", "Linguiça bovina",

    "Filé de peixe branco", "Peixe pescada amarela",
    "Peixe robalo", "Peixe namorado"
]

proteinasUN = [
    "Ovo", "Ovo caipira", "Ovo vermelho", "Ovo de codorna",
    "Gema de ovo",

    "Hambúrguer bovino", "Hambúrguer de frango", "Hambúrguer suíno",
    "Hambúrguer artesanal",

    "Salsicha", "Salsicha de frango", "Salsicha bovina",
    "Salsicha hot dog",

    "Nuggets de frango", "Empanado de frango",
    "Almôndega",

    "Tofu", "Tofu defumado", "Tempeh",

    "Queijo coalho", "Queijo muçarela",
    "Queijo prato",

    "Presunto", "Peito de peru",

    "Sardinha enlatada", "Atum enlatado",

    "Hambúrguer vegetal", "Proteína vegetal"
]

folhas_saladas = [
"Alface",
"Alface americana",
"Alface crespa",
"Alface lisa",
"Alface roxa",
"Alface mimosa",
"Alface frisée",
"Alface baby leaf",
"Alface romana",
"Alface iceberg",
"Rúcula",
"Rúcula selvagem",
"Agrião",
"Agrião da terra",
"Espinafre",
"Espinafre baby",
"Couve",
"Couve manteiga",
"Couve baby",
"Repolho",
"Repolho roxo",
"Repolho verde",
"Acelga",
"Acelga chinesa",
"Endívia",
"Endívia roxa",
"Almeirão",
"Chicória",
"Radicchio",
"Mostarda",
"Folha de mostarda",
"Folha de beterraba",
"Folha de cenoura",
"Folha de nabo",
"Folha de rabanete",
"Folha de brócolis",
"Folha de couve-flor",
"Escarola",
"Escarola crespa",
"Treviso",
"Baby rúcula",
"Mix de folhas verdes",
"Mix primavera",
"Mix mediterrâneo",
"Microgreens",
"Broto de alfafa",
"Broto de feijão",
"Broto de lentilha",
"Broto de ervilha",
"Broto de girassol",
"Broto de rúcula",
"Broto de beterraba",
"Broto de mostarda",
"Broto de trigo",
"Broto de milho",
"Broto de cebola",
"Broto de coentro",
"Broto de manjericão",
"Folha de manjericão",
"Manjericão roxo",
"Folha de hortelã",
"Hortelã pimenta",
"Folha de coentro",
"Folha de salsa",
"Salsinha crespa",
"Salsinha lisa",
"Folha de dill",
"Folha de erva-doce",
"Folha de funcho",
"Folha de cebola",
"Cebolinha verde",
"Folha de alho-poró",
"Folha de alho",
"Folha de louro fresco",
"Folha de taioba",
"Folha de ora-pro-nóbis",
"Folha de bertalha",
"Folha de beldroega",
"Folha de serralha",
"Folha de dente-de-leão",
"Folha de mostarda japonesa",
"Mizuna",
"Tatsoi",
"Pak choi",
"Bok choy",
"Komatsuna",
"Shiso",
"Perilla",
"Folha de uva",
"Folha de hibisco",
"Folha de amaranto",
"Folha de quinoa",
"Folha de espinafre selvagem",
"Folha de chicória roxa",
"Folha de rúcula baby roxa",
"Folha de alface baby mix"
]

carboidratos = [
    "Quinoa", "Cuscuz", "Aveia", "Milho verde", "Milho",
    "Polenta", "Fubá", "Farofa",

    "Grão-de-bico", "Lentilha", "Feijão carioca",
    "Feijão preto", "Feijão branco", "Ervilha",

    "Batata baroa", "Mandioquinha", "Inhame",
    "Cará", "Tapioca", "Cuscuz nordestino", "Cuscuz"
    "Arroz branco",
"Arroz integral",
"Arroz parboilizado",
"Arroz basmati",
"Arroz jasmim",
"Arroz arbóreo",
"Arroz selvagem",
"Arroz cateto",
"Arroz vermelho",
"Arroz negro",

"Feijão carioca",
"Feijão preto",
"Feijão branco",
"Feijão fradinho",
"Feijão rosinha",
"Feijão jalo",
"Feijão manteiguinha",
"Feijão azuki",
"Feijão rajado",
"Feijão vermelho",

"Lentilha",
"Grão-de-bico",
"Ervilha seca",
"Ervilha verde",
"Fava",
"Soja em grão",
"Soja preta",
"Soja amarela",

"Milho verde",
"Milho seco",
"Milho para canjica",
"Canjica branca",
"Canjica amarela",

"Quinoa branca",
"Quinoa vermelha",
"Quinoa preta",

"Amaranto",
"Trigo em grão",
"Trigo para quibe",
"Trigo integral",
"Cevada",
"Centeio",
"Sorgo",
"Painço",
"Teff",
"Batata inglesa",
"Batata asterix",
"Batata bolinha",
"Batata doce branca",
"Batata doce roxa",
"Batata doce laranja",
"Batata yacon",
"Mandioca",
"Aipim",
"Macaxeira",
"Mandioca amarela",
"Mandioca branca",
"Inhame",
"Cará",
"Cará roxo",
"Cará branco",
"Mandioquinha",
"Batata baroa",
"Nabo",
"Rabanete",
"Beterraba",
"Cenoura",
"Abóbora japonesa",
"Abóbora moranga",
"Abóbora cabotiá",
"Abóbora paulista",
"Chuchu",
"Abobrinha",
"Fubá",
"Fubá mimoso",
"Fubá grosso",
"Polenta",
"Cuscuz de milho",
"Cuscuz de arroz",
"Arroz integral vermelho",
"Arroz integral negro",
"Milheto",
"Grão de cevada perlada",
"Batata doce japonesa",
"Batata doce biofortificada",
"Inhame chinês",
"Inhame africano",
"Cará-do-ar",
"Cará-de-espinho",
"Creme de arroz",
"Creme de milho",
"Semolina",
"Sêmola de trigo",
"Trigo sarraceno",
"Trigo para canjica",
"Grão de bico torrado",
"Lentilha vermelha",
"Lentilha verde",
"Lentilha marrom",
"Feijão mungo",
"Feijão branco gigante",
"Feijão manteiga",
"Milho roxo",
"Milho crioulo",
"Arroz cateto integral",
"Arroz agulhinha",
"Goma de tapioca fresca",
"Cuscuz marroquino",
"Cuscuz integral",
"Milho canjicado",
"Milho flocão",
"Sorgo em grão",
"Sorgo moído",
"Teff branco",
"Teff escuro"
]

massas = [
    "Macarrão Espaguete", "Macarrão Penne", "Macarrão Fusilli", "Macarrão Rigatoni", "Macarrão Linguine",
    "Macarrão Talharim", "Macarrão Tagliatelle", "Macarrão Farfalle", "Macarrão Parafuso",
    "Nhoque", "Ravioli", "Capeletti", "Tortellini",
    "Canelone",

    "Macarrão integral", "Macarrão de arroz",
    "Macarrão de grão duro",
    
]

molhos = [
    "Molho de tomate", "Molho de tomate rústico",
    "Molho de tomate caseiro", "Molho de tomate com manjericão",

    "Molho branco", "Molho branco cremoso",
    "Molho quatro queijos", "Molho cheddar",

    "Molho pesto", "Molho de ervas",
    "Molho de manjericão", "Molho de salsinha",

    "Molho de alho e azeite", "Molho de alho cremoso",
    "Molho de mostarda", "Molho de mostarda e mel",

    "Molho barbecue", "Molho agridoce",
    "Molho picante", "Molho chipotle",

    "Molho de cogumelos", "Molho funghi",
    "Molho madeira", "Molho bolonhesa",

    "Molho rosé","Molho de iogurte", "Molho de limão",

    "Molho de queijo", "Molho parmesão"
]

caldos = [
    {"nome": "Caldo de legumes", "forma": "liquido"},
    {"nome": "Caldo de frango", "forma": "liquido"},
    {"nome": "Caldo de carne", "forma": "liquido"},

    {"nome": "Tablete de caldo de legumes", "forma": "tablete"},
    {"nome": "Tablete de caldo de frango", "forma": "tablete"},
    {"nome": "Tablete de caldo de carne", "forma": "tablete"},

    {"nome": "Caldo em pó de legumes", "forma": "po"},
    {"nome": "Caldo em pó de frango", "forma": "po"},
    {"nome": "Caldo em pó de carne", "forma": "po"}
]

proteinas_proibidas_sopa = [
    "Ovo"
]

vegetais = [
    "Brócolis", "Cenoura", "Abobrinha", "Couve-flor",
    "Beterraba", "Vagem", "Espinafre", "Couve",
    "Repolho", "Tomate", "Pimentão", "Berinjela",
    "Abóbora", "Ervilha", "Chuchu", "Alface",
    "Rúcula", "Agrião", "Alho-poró", "Salsão",

    "Cebola", "Alho", "Cebolinha", "Salsa",
    "Coentro", "Milho verde", "Palmito",

    "Pepino", "Nabo", "Rabanete",
    "Acelga", "Endívia", "Almeirão",

    "Quiabo", "Jiló", "Maxixe",
    "Batata salsa", "Inhame", "Cará"
]

tecnicas_proteina = [
    "grelhe",
    "refogue",
    "asse",
    "cozinhe",
    "doure",
    "sele",
    "frite levemente"
]

def adicionar_salada():
    return random.random() < 0.5  # 50% dos pratos terão salada

# =========================
# LEGUMES INTELIGENTES
# =========================

def preparar_legume(legume):
    tecnicas = [
        f"Cozinhe {legume.lower()} no vapor até ficar macio",
        f"Salteie {legume.lower()} em fogo médio com temperos naturais",
        f"Cozinhe rapidamente {legume.lower()} em água fervente e finalize com azeite"
    ]
    return random.choice(tecnicas)

# =========================
# NOVA REGRA: PROTEÍNA KG vs UN
# =========================
def escolher_carbo_compativel(proteina_nome):

    if "peixe" in proteina_nome.lower() or "salmão" in proteina_nome.lower():
        return random.choice(["Arroz integral", "Quinoa", "Legumes cozidos"])

    if "bovina" in proteina_nome.lower() or "patinho" in proteina_nome.lower():
        return random.choice(["Arroz branco", "Feijão", "Batata", "Mandioca"])

    return random.choice(carboidratos)


def escolher_proteina():
    tipo = random.choice(["KG", "UN"])

    if tipo == "KG":
        return {
            "nome": random.choice(proteinasKG),
            "quantidade": 120,
            "unidade": "g"
        }

    return {
        "nome": random.choice(proteinasUN),
        "quantidade": 2,
        "unidade": "unidade"
    }

def preparar_proteina(proteina):

    nome = proteina.lower()

    # Regras inteligentes por tipo
    if any(p in nome for p in ["frango", "peito de frango", "coxa"]):
        metodo = random.choice(["grelhe", "asse", "refogue"])
        texto = f"{metodo.capitalize()} o {nome} até dourar bem por fora e cozinhar completamente por dentro."

    elif any(p in nome for p in ["patinho", "alcatra", "carne", "bovina"]):
        metodo = random.choice(["grelhe", "sele", "refogue"])
        texto = f"{metodo.capitalize()} a {nome} em fogo alto até dourar e manter suculenta."

    elif any(p in nome for p in ["salmão", "tilápia", "peixe", "pescada", "linguado"]):
        metodo = random.choice(["grelhe", "asse"])
        texto = f"{metodo.capitalize()} o {nome} por poucos minutos de cada lado até ficar macio."

    elif any(p in nome for p in ["ovo"]):
        metodo = random.choice(["mexa", "refogue"])
        texto = f"{metodo.capitalize()} o {nome} mexendo até ficar completamente cozido."

    elif any(p in nome for p in ["linguiça", "salsicha"]):
        metodo = random.choice(["frite levemente", "asse"])
        texto = f"{metodo.capitalize()} a {nome} até dourar por fora."

    elif any(p in nome for p in ["tofu", "tempeh"]):
        metodo = random.choice(["grelhe", "refogue"])
        texto = f"{metodo.capitalize()} o {nome} até dourar levemente."

    else:
        metodo = random.choice(["grelhe", "refogue", "cozinhe"])
        texto = f"{metodo.capitalize()} o {nome} por cerca de 5 a 10 minutos até dourar."

    return {
        "texto": texto,
        "metodo": metodo
    }

def metodo_para_nome(metodo):

    mapa = {
        "grelhe": "grelhado",
        "refogue": "refogado",
        "asse": "assado",
        "cozinhe": "cozido",
        "mexa": "mexido"
    }

    return mapa.get(metodo, "preparado")


def extrair_metodo(preparo):

    texto = preparo.lower()

    if "grelhe" in texto:
        return "grelhado"
    if "refogue" in texto:
        return "refogado"
    if "asse" in texto:
        return "assado"
    if "cozinhe" in texto:
        return "cozido"
    if "mexa" in texto or "mexido" in texto:
        return "mexido"

    return "preparado"

# =========================
# TIPOS DE PRATO
# =========================

def escolher_tipo():
    r = random.random()
    if r < 0.5:
        return "pf"
    elif r < 0.8:
        return "massa"
    else:
        return "sopa"

# =========================
# PF (PRATO FEITO)
# =========================

def gerar_salada():
    folhas = random.sample(folhas_saladas, 2)

    return {
        "ingredientes": [
            {"nome": folhas[0], "quantidade": 50, "unidade": "g"},
            {"nome": folhas[1], "quantidade": 50, "unidade": "g"}
        ],
        "descricao": f"Sirva com salada de {folhas[0].lower()} e {folhas[1].lower()}."
    }


def gerar_pf():
    proteina = escolher_proteina()
    carbo = escolher_carbo_compativel(proteina["nome"])
    veg1, veg2 = random.sample(vegetais, 2)

    prep = preparar_proteina(proteina["nome"])
    metodo = metodo_para_nome(prep["metodo"])

    tem_salada = adicionar_salada()

    ingredientes = [
        {
            "nome": proteina["nome"],
            "quantidade": proteina["quantidade"],
            "unidade": proteina["unidade"]
        },
        {
            "nome": carbo,
            "quantidade": 90,
            "unidade": "g"
        },
        {
            "nome": veg1,
            "quantidade": 80,
            "unidade": "g"
        },
        {
            "nome": veg2,
            "quantidade": 80,
            "unidade": "g"
        }
    ]

    modo = [
    f"1. Tempere a {proteina['nome'].lower()} com sal e temperos naturais a gosto.",

    f"2. Em uma frigideira, aqueça um fio de azeite ou óleo e {prep['texto'].lower()}",

    f"3. Em uma panela, cozinhe o {carbo.lower()} em água com uma pitada de sal até ficar macio. Escorra e reserve.",

    f"4. Prepare {veg1.lower()} cozinhando no vapor ou salteando levemente até ficar macio.",

    f"5. Prepare {veg2.lower()} da mesma forma, mantendo leve crocância.",

    "6. Monte o prato distribuindo o carboidrato como base.",

    f"7. Adicione a {proteina['nome'].lower()} preparada por cima.",

    f"8. Acrescente {veg1.lower()} e {veg2.lower()} ao lado ou sobre o prato.",

    ]

    nome = f"{proteina['nome']} {metodo} com {carbo} e legumes"

    if tem_salada:
        salada = gerar_salada()
        ingredientes.extend(salada["ingredientes"])

        modo.append(f"9. {salada['descricao']}")
        nome += " com salada"

        modo.extend([
        "10. Finalize com um fio de azeite ou ervas frescas, se desejar.",
        "11. Sirva quente."
        ])

    return {
        "nome": nome,
        "tipo": "pf",
        "categoria": "almoco",
        "ingredientes": ingredientes,
        "modo_preparo": modo,
        "tempo_preparo": f"{random.randint(25, 50)} min",
        "Porcao": "1"
    }

# =========================
# MASSA (PRATO ÚNICO)
# =========================
def escolher_proteina_sopa():

    while True:
        proteina = escolher_proteina()

        if proteina["nome"] not in proteinas_proibidas_sopa:
            return proteina
        
def gerar_massa():

    massa = random.choice(massas)
    proteina = escolher_proteina()
    legumes = random.sample(vegetais, 2)
    molho = random.choice(molhos)

    return {
        "nome": f"{massa} com {proteina['nome'].lower()} e legumes",

        "tipo": "massa",
        "categoria": "prato único",

        "ingredientes": [
            {
                "nome": massa,
                "quantidade": 100,
                "unidade": "g"
            },

            {
                "nome": proteina["nome"],
                "quantidade": proteina["quantidade"],
                "unidade": proteina["unidade"]
            },

            {
                "nome": molho,
                "quantidade": 150,
                "unidade": "ml"
            },

            {
                "nome": legumes[0],
                "quantidade": 70,
                "unidade": "g"
            },
            {
                "nome": legumes[1],
                "quantidade": 70,
                "unidade": "g"
            }
        ],

       "modo_preparo": [
    f"1. Em uma panela com água fervente e uma pitada de sal, cozinhe o {massa.lower()} até ficar al dente (cerca de 8 a 12 minutos). Escorra e reserve.",

    f"2. Tempere a {proteina['nome'].lower()} com sal e temperos a gosto.",

    f"3. Em uma frigideira, aqueça um fio de azeite ou óleo e prepare a {proteina['nome'].lower()} até dourar ou atingir o ponto desejado. Reserve.",

    f"4. Na mesma panela ou frigideira, adicione o {molho.lower()} e aqueça em fogo médio até começar a engrossar.",

    f"5. Acrescente a proteína ao molho e misture bem para incorporar os sabores.",

    f"6. Cozinhe {legumes[0].lower()} e {legumes[1].lower()} rapidamente (no vapor ou na água) por 3 a 5 minutos para manter a textura.",

    f"7. Misture o {massa.lower()} já cozido ao molho com a proteína.",

    f"8. Adicione os legumes e misture delicadamente.",

    "9. Ajuste o sal e finalize com um fio de azeite ou ervas frescas, se desejar.",

    "10. Sirva quente."
],

        "tempo_preparo": f"{random.randint(20, 40)} min",
        "Porcao": "1"
    }

# =========================
# SOPA (PRATO ÚNICO)
# =========================

def definir_caldo(caldo):

    if caldo["forma"] == "liquido":
        return {
            "nome": caldo["nome"],
            "quantidade": 500,
            "unidade": "ml"
        }

    if caldo["forma"] == "tablete":
        return {
            "nome": caldo["nome"],
            "quantidade": 1,
            "unidade": "unidade"
        }

    if caldo["forma"] == "po":
        return {
            "nome": caldo["nome"],
            "quantidade": 10,
            "unidade": "g"
        }

def gerar_sopa():

    proteina = escolher_proteina_sopa()
    legumes = random.sample(vegetais, 3)
    caldo_escolhido = definir_caldo(random.choice(caldos))

    legume_base = legumes[0]   # vai para creme
    legume_textura = legumes[1]
    legume_final = legumes[2]

    return {
        "nome": f"Sopa de {proteina['nome'].lower()} com legumes",

        "tipo": "sopa",
        "categoria": "prato único",

        "ingredientes": [
            {
                "nome": proteina["nome"],
                "quantidade": proteina["quantidade"],
                "unidade": proteina["unidade"]
            },

            caldo_escolhido,

            {
                "nome": legume_base,
                "quantidade": 2,
                "unidade": "unidade"
            },
            {
                "nome": legume_textura,
                "quantidade": 1,
                "unidade": "unidade"
            },
            {
                "nome": legume_final,
                "quantidade": 80,
                "unidade": "g"
            },
        ],

        "modo_preparo": [
            f"Cozinhe a {proteina['nome'].lower()} até ficar macia e desfie.",

            f"Corte {legume_base}, {legume_textura} e {legume_final} em pedaços pequenos.",

            f"Cozinhe {legume_base} até ficar bem macio e reserve parte para bater.",

            f"Bata o {legume_base} com o {caldo_escolhido['nome'].lower()} no liquidificador até formar um creme.",

            "Refogue alho e cebola até dourar levemente.",

            f"Adicione a proteína desfiada ao refogado.",

            f"Incorpore o creme e adicione {legume_textura} e {legume_final}.",

            "Cozinhe em fogo baixo até tudo ficar bem incorporado.",

            "Ajuste o sal e finalize com cheiro-verde.",

            "Sirva quente."
        ],

        "tempo_preparo": f"{random.randint(35, 60)} min",
        "Porcao": "1"
    }

# =========================
# GERADOR PRINCIPAL
# =========================

def gerar_receita():
    tipo = escolher_tipo()

    if tipo == "pf":
        return gerar_pf()
    elif tipo == "massa":
        return gerar_massa()
    else:
        return gerar_sopa()

# =========================
# LOTE
# =========================

def gerar_lote(qtd=5000):
    return [gerar_receita() for _ in range(qtd)]

if __name__ == "__main__":
    receitas = gerar_lote(5000)

    with open("receitas_almoco.json", "w", encoding="utf-8") as f:
        json.dump(receitas, f, ensure_ascii=False, indent=4)

    print("receitas_almoco.json finalizado!")