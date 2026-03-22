import random
import json

# =========================
# BASES
# =========================

proteinasKG = [
    "Peito de frango","Coxa de frango","Sobrecoxa de frango","Frango inteiro","Filé de frango","Asa de frango","Frango desfiado",
    "Patinho","Acém","Alcatra","Músculo bovino","Coxão mole","Coxão duro","Lagarto","Fraldinha","Picanha","Contrafilé","Maminha","Filé mignon","Costela bovina","Cupim","Acém moído","Carne moída","Carne de segunda",
    "Lombo suíno","Pernil suíno","Costelinha suína","Bisteca suína","Panceta","Barriga suína","Filé suíno",
    "Salmão","Tilápia","Bacalhau","Merluza","Sardinha","Atum","Truta","Pescada","Dourado","Corvina","Cação","Anchova","Linguado",
    "Frango caipira","Fígado bovino","Fígado de frango","Moela de frango","Coração de frango",
    "Carne suína moída","Carne bovina moída magra","Costela bovina","Peixe branco",
    "Cordeiro","Peru","Peito de peru","Linguiça toscana","Linguiça calabresa","Linguiça de frango","Linguiça bovina",
    "Filé de peixe branco","Peixe pescada amarela","Peixe robalo","Peixe namorado"
]

proteinasUN = [
    "Ovo","Ovo caipira","Ovo vermelho","Ovo de codorna","Gema de ovo",
    "Hambúrguer bovino","Hambúrguer de frango","Hambúrguer suíno","Hambúrguer artesanal",
    "Salsicha","Salsicha de frango","Salsicha bovina","Salsicha hot dog",
    "Nuggets de frango","Empanado de frango","Almôndega",
    "Tofu","Tofu defumado","Tempeh",
    "Queijo coalho","Queijo muçarela","Queijo prato",
    "Presunto","Peito de peru",
    "Sardinha enlatada","Atum enlatado",
    "Hambúrguer vegetal","Proteína vegetal"
]

folhas_saladas = ["Alface","Rúcula","Agrião","Espinafre","Couve","Repolho"]

# ✅ CORRIGIDO (vírgula)
carboidratos = [
    "Quinoa","Cuscuz","Aveia","Milho verde","Milho","Polenta","Fubá","Farofa",
    "Grão-de-bico","Lentilha","Feijão carioca","Feijão preto","Feijão branco","Ervilha",
    "Batata baroa","Mandioquinha","Inhame","Cará","Tapioca","Cuscuz nordestino","Cuscuz",
    "Arroz branco","Arroz integral"
]

massas = ["Macarrão Espaguete","Macarrão Penne","Macarrão Fusilli"]

molhos = ["Molho de tomate","Molho branco","Molho pesto"]

caldos = [
    {"nome":"Caldo de legumes","forma":"liquido"},
    {"nome":"Tablete de caldo de legumes","forma":"tablete"}
]

proteinas_proibidas_sopa = ["Ovo"]

vegetais = [
    "Brócolis","Cenoura","Abobrinha","Couve-flor","Beterraba","Vagem","Espinafre","Couve",
    "Repolho","Tomate","Pimentão","Berinjela","Abóbora","Ervilha","Chuchu"
]

def adicionar_salada():
    return random.random() < 0.5

def escolher_carbo_compativel(proteina_nome):
    return random.choice(carboidratos)

def escolher_proteina():
    if random.random() < 0.5:
        return {"nome": random.choice(proteinasKG),"quantidade":120,"unidade":"g"}
    return {"nome": random.choice(proteinasUN),"quantidade":2,"unidade":"unidade"}

def preparar_proteina(proteina):
    return {"texto":f"Grelhe o {proteina.lower()}","metodo":"grelhe"}

def metodo_para_nome(metodo):
    return "grelhado"

def escolher_tipo():
    r = random.random()
    if r < 0.5:
        return "pf"
    elif r < 0.8:
        return "massa"
    return "sopa"

def gerar_pf():
    proteina = escolher_proteina()
    carbo = escolher_carbo_compativel(proteina["nome"])

    if len(vegetais) < 1:
        raise Exception("Sem vegetais")

    vegs = random.sample(vegetais, min(2, len(vegetais)))

    ingredientes = [
        {"nome":proteina["nome"],"quantidade":proteina["quantidade"],"unidade":proteina["unidade"]},
        {"nome":carbo,"quantidade":90,"unidade":"g"}
    ]

    for v in vegs:
        ingredientes.append({"nome":v,"quantidade":80,"unidade":"g"})

    return {
        "nome":f"{proteina['nome']} com {carbo}",
        "tipo":"pf",
        "categoria":"almoco",
        "ingredientes":ingredientes
    }

# ✅ PROTEÇÃO CONTRA LOOP INFINITO
def escolher_proteina_sopa():
    for _ in range(20):
        p = escolher_proteina()
        if p["nome"] not in proteinas_proibidas_sopa:
            return p
    raise Exception("Não encontrou proteína válida para sopa")

def gerar_massa():
    return gerar_pf()

def gerar_sopa():
    proteina = escolher_proteina_sopa()
    legumes = random.sample(vegetais, min(3, len(vegetais)))

    return {
        "nome":f"Sopa de {proteina['nome']}",
        "tipo":"sopa",
        "categoria":"prato único",
        "ingredientes":[
            {"nome":proteina["nome"],"quantidade":proteina["quantidade"],"unidade":proteina["unidade"]}
        ]
    }

def gerar_receita():
    tipo = escolher_tipo()
    if tipo == "pf":
        return gerar_pf()
    elif tipo == "massa":
        return gerar_massa()
    else:
        return gerar_sopa()

def gerar_lote(qtd=5000):
    return [gerar_receita() for _ in range(qtd)]

if __name__ == "__main__":
    receitas = gerar_lote(5000)
    with open("receitas_almoco.json","w",encoding="utf-8") as f:
        json.dump(receitas,f,ensure_ascii=False,indent=4)
    print("receitas_almoco.json finalizado!")