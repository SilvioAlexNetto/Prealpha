import random

def gerar_preparo_cafe(base, ingredientes=None, bebida=None):
    preparo = []
    base_lower = base.lower()

    def escolher(opcoes):
        return random.choice(opcoes)

    ingredientes = ingredientes or []

    # separa alguns tipos automaticamente (leve inteligência)
    fruta = next((i for i in ingredientes if "banana" in i.lower() or "maçã" in i.lower()), None)
    liquido = bebida
    proteina = next((i for i in ingredientes if "ovo" in i.lower() or "queijo" in i.lower()), None)

    # =========================
    # 🥞 PANQUECA
    # =========================
    if "panqueca" in base_lower:

        preparo.append(escolher([
            f"Misture os ingredientes com {liquido or 'líquido'} até formar uma massa.",
            "Combine os ingredientes até obter uma massa homogênea.",
        ]))

        preparo.append(escolher([
            "Aqueça uma frigideira antiaderente.",
            "Leve uma frigideira ao fogo médio.",
        ]))

        preparo.append(escolher([
            "Despeje porções da massa e cozinhe até dourar.",
            "Coloque a massa na frigideira e deixe dourar dos dois lados.",
        ]))

        if fruta:
            preparo.append(f"Sirva com {fruta}.")

        preparo.append("Sirva quente.")

    # =========================
    # 🥣 MINGAU
    # =========================
    elif "mingau" in base_lower:

        preparo.append(escolher([
            f"Aqueça {liquido or 'líquido'} em fogo médio.",
            f"Leve {liquido or 'líquido'} ao fogo.",
        ]))

        preparo.append(escolher([
            "Adicione os ingredientes e mexa bem.",
            "Incorpore os ingredientes mexendo sempre.",
        ]))

        preparo.append(escolher([
            "Cozinhe até engrossar.",
            "Mexa até atingir textura cremosa.",
        ]))

        if fruta:
            preparo.append(f"Finalize com {fruta}.")

        preparo.append("Sirva quente.")

    # =========================
    # 🥤 VITAMINA
    # =========================
    elif "vitamina" in base_lower:

        preparo.append(escolher([
            f"Adicione {liquido or 'líquido'} no liquidificador.",
            "Coloque os ingredientes no liquidificador.",
        ]))

        preparo.append("Bata até ficar homogêneo.")

        preparo.append(escolher([
            "Sirva gelado.",
            "Sirva imediatamente.",
        ]))

    # =========================
    # 🍞 SIMPLES
    # =========================
    elif "simples" in base_lower:

        preparo.append(escolher([
            "Organize os ingredientes em um prato.",
            "Disponha os alimentos para consumo.",
        ]))

        if fruta:
            preparo.append(f"Prepare {fruta} para consumo.")

        if bebida:
            preparo.append(f"Sirva com {bebida}.")

        preparo.append("Pronto para consumo.")

    # =========================
    # 🔥 FALLBACK
    # =========================
    else:
        preparo.append(f"Prepare {base}.")
        if bebida:
            preparo.append(f"Acompanhe com {bebida}.")
        preparo.append("Sirva.")

    return [p for p in preparo if p]