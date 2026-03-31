import random

def gerar_preparo_cafe(base, proteina=None, liquido=None, fruta=None, recheio=None, fermento=None):
    preparo = []
    base_lower = base.lower()

    def escolher(opcoes):
        return random.choice(opcoes)

    # =========================
    # 🔹 PANQUECA
    # =========================
    if "panqueca" in base_lower:
        preparo.append(escolher([
            f"Em uma tigela, misture os ingredientes com {liquido} e {proteina}.",
            f"Combine a base com {liquido} e {proteina} até formar uma massa.",
        ]))

        if fermento:
            preparo.append(escolher([
                f"Adicione {fermento} e misture delicadamente.",
                f"Incorpore {fermento} para deixar a massa mais leve.",
            ]))

        preparo.append(escolher([
            "Mexa até obter uma massa lisa e homogênea.",
            "Misture bem até a massa ficar uniforme.",
        ]))

        preparo.append(escolher([
            "Aqueça uma frigideira antiaderente em fogo médio.",
            "Leve uma frigideira ao fogo médio e unte levemente se necessário.",
        ]))

        preparo.append(escolher([
            "Despeje pequenas porções da massa e cozinhe até formar bolhas.",
            "Coloque porções da massa na frigideira e aguarde dourar a base.",
        ]))

        preparo.append(escolher([
            "Vire e doure o outro lado.",
            "Vire a panqueca e deixe dourar levemente.",
        ]))

        if recheio:
            preparo.append(escolher([
                f"Recheie com {recheio} antes de servir.",
                f"Finalize com recheio de {recheio}.",
            ]))

        if fruta:
            preparo.append(escolher([
                f"Sirva com {fruta} por cima.",
                f"Acompanhe com {fruta}.",
            ]))

        preparo.append(escolher([
            "Sirva ainda quente.",
            "Finalize e sirva na sequência.",
        ]))

    # =========================
    # 🔹 CREPIOCA
    # =========================
    elif "crepioca" in base_lower:
        preparo.append(escolher([
            f"Misture a base com {proteina} até formar uma massa homogênea.",
            f"Em uma tigela, combine os ingredientes com {proteina}.",
        ]))

        if liquido:
            preparo.append(escolher([
                f"Adicione {liquido} aos poucos para ajustar a textura.",
                f"Se necessário, acrescente {liquido} para deixar a massa mais leve.",
            ]))

        preparo.append(escolher([
            "Misture bem até ficar uniforme.",
            "Mexa até obter uma massa lisa.",
        ]))

        preparo.append(escolher([
            "Aqueça uma frigideira antiaderente.",
            "Leve uma frigideira ao fogo médio.",
        ]))

        preparo.append(escolher([
            "Espalhe a massa formando uma camada fina.",
            "Despeje a massa e espalhe bem pela superfície.",
        ]))

        preparo.append(escolher([
            "Cozinhe até firmar e vire para dourar o outro lado.",
            "Quando firmar, vire e deixe dourar levemente.",
        ]))

        if recheio:
            preparo.append(escolher([
                f"Adicione {recheio} antes de dobrar.",
                f"Recheie com {recheio} e feche ao meio.",
            ]))

        if fruta:
            preparo.append(escolher([
                f"Sirva com {fruta}.",
                f"Acompanhe com {fruta}.",
            ]))

        preparo.append(escolher([
            "Sirva na sequência.",
            "Finalize e sirva quente.",
        ]))

    # =========================
    # 🔹 MINGAU
    # =========================
    elif "mingau" in base_lower:
        preparo.append(escolher([
            f"Aqueça {liquido} em fogo médio.",
            f"Leve {liquido} ao fogo até começar a aquecer.",
        ]))

        preparo.append(escolher([
            "Adicione a base aos poucos, mexendo sempre.",
            "Incorpore a base gradualmente, mexendo sem parar.",
        ]))

        preparo.append(escolher([
            "Cozinhe até engrossar e ficar cremoso.",
            "Mexa até atingir uma textura cremosa.",
        ]))

        if fruta:
            preparo.append(escolher([
                f"Finalize com {fruta} por cima.",
                f"Sirva com {fruta}.",
            ]))

        if proteina:
            preparo.append(escolher([
                f"Acompanhe com {proteina}.",
                f"Sirva junto com {proteina}.",
            ]))

        preparo.append(escolher([
            "Sirva quente.",
            "Finalize e sirva imediatamente.",
        ]))

    # =========================
    # 🔹 VITAMINA (NOVO 🔥)
    # =========================
    elif "vitamina" in base_lower:
        preparo.append(escolher([
            f"Adicione {liquido} no liquidificador.",
            f"Coloque {liquido} no liquidificador.",
        ]))

        if fruta:
            preparo.append(escolher([
                f"Acrescente {fruta}.",
                f"Adicione {fruta} ao liquidificador.",
            ]))

        preparo.append(escolher([
            "Bata até obter uma mistura homogênea.",
            "Bata bem até ficar cremoso.",
        ]))

        preparo.append(escolher([
            "Sirva gelado.",
            "Sirva imediatamente após o preparo.",
        ]))

    # =========================
    # 🔹 SIMPLES
    # =========================
    elif "simples" in base_lower:
        preparo.append(escolher([
            "Organize os ingredientes em um prato ou tigela.",
            "Disponha os ingredientes de forma prática para consumo.",
        ]))

        if proteina:
            preparo.append(escolher([
                f"Separe {proteina} para acompanhar.",
                f"Inclua {proteina} como acompanhamento.",
            ]))

        if fruta:
            preparo.append(escolher([
                f"Corte {fruta} e adicione ao prato.",
                f"Adicione {fruta} já cortada.",
            ]))

        if liquido:
            preparo.append(escolher([
                f"Sirva com {liquido}.",
                f"Acompanhe com {liquido}.",
            ]))

        preparo.append(escolher([
            "Finalize e sirva.",
            "Pronto para consumo.",
        ]))

    # =========================
    # 🔹 FALLBACK
    # =========================
    else:
        preparo.append(f"Prepare {base}.")
        if fruta:
            preparo.append(f"Sirva com {fruta}.")
        preparo.append("Finalize e sirva.")

    return [p for p in preparo if p]