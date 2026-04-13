from app.backend.services.bases import (
    proteinasUN, proteinasKG, legumes, carboidratos,
    folhas_saladas, massas, molhos, caldos, frutas,
    proteinasCF, carboidratosCF, liquidos, cereais,
    farinhas, fermentos, produtoBruto
)

from app.backend.services.core.normalizacao import normalizar


def montar_base_dinamica(ingredientes_custom=None):
    """
    Junta base padrão + ingredientes do usuário (sem duplicar)
    """

    # 🔥 BASE ORIGINAL
    categorias = {
        "proteinasKG": list(proteinasKG),
        "proteinasUN": list(proteinasUN),
        "proteinasCF": list(proteinasCF),
        "carboidratos": list(carboidratos),
        "carboidratosCF": list(carboidratosCF),
        "legumes": list(legumes),
        "folhas_saladas": list(folhas_saladas),
        "massas": list(massas),
        "molhos": list(molhos),
        "caldos": [c["nome"] for c in caldos],
        "frutas": list(frutas),
        "liquidos": list(liquidos),
        "cereais": list(cereais),
        "farinhas": list(farinhas),
        "fermentos": list(fermentos),
        "produtoBruto": list(produtoBruto)
    }

    # 🔥 SE NÃO VEIO CUSTOM → retorna base normal
    if not ingredientes_custom:
        return categorias

    # 🔥 NORMALIZA BASE (para evitar duplicação inteligente)
    categorias_normalizadas = {
        cat: [normalizar(i) for i in itens]
        for cat, itens in categorias.items()
    }

    # 🔥 INJETAR CUSTOM
    for categoria, itens in ingredientes_custom.items():

        if categoria not in categorias:
            continue

        for item in itens:
            item_norm = normalizar(item)

            if item_norm not in categorias_normalizadas[categoria]:
                categorias[categoria].append(item)
                categorias_normalizadas[categoria].append(item_norm)

    return categorias