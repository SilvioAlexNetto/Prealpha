from app.backend.services.utils.base_dinamica import montar_base_dinamica
from app.backend.services.core.normalizacao import normalizar

def classificar_estoque(estoque, ingredientes_custom=None):
    bases = montar_base_dinamica(ingredientes_custom)

    estoque_classificado = []
    
    categorias = [
        ("proteinaCF", bases["proteinasCF"], "cafe"),
        ("carboCF", bases["carboidratosCF"], "cafe"),
        ("liquido", bases["liquidos"], "cafe"),
        ("proteina", bases["proteinasKG"] + bases["proteinasUN"], "ambos"),
        ("massa", bases["massas"], "ambos"),
        ("legume", bases["legumes"], "ambos"),
        ("carbo", bases["carboidratos"], "ambos"),
        ("folha", bases["folhas_saladas"], "ambos"),
        ("molho", bases["molhos"], "ambos"),
        ("fermento", bases["fermentos"], "ambos"),
        ("farinha", bases["farinhas"], "cafe"),
        ("cereal", bases["cereais"], "cafe"),
        ("caldo", bases["caldos"], "ambos"),
        ("fruta", bases["frutas"], "cafe"),
        ("bruto", bases["produtoBruto"], "ambos")
    ]

    def match_seguro(nome_item, termo):
        nome = normalizar(nome_item)
        termo = normalizar(termo)
        return termo in nome
    
    print("🔥 CUSTOM RECEBIDO:", ingredientes_custom)
    print("🔥 BASE FRUTAS:", bases["frutas"])

    for item in estoque:
        nome_original = item["nome"]
        nome = normalizar(nome_original)

        categorias_encontradas = []
        subcategorias_encontradas = []

        print("📦 ITEM:", nome_original)
        print("➡️ categorias:", categorias_encontradas)

        # 🔍 CLASSIFICAÇÃO
        for cat, lista, sub in categorias:
            if any(match_seguro(nome_original, x) for x in lista):
                if cat not in categorias_encontradas:
                    categorias_encontradas.append(cat)
                    subcategorias_encontradas.append(sub)

        # 🔥 FALLBACK
        if not categorias_encontradas:
            if any(x in nome for x in ["arroz", "feijao", "batata"]):
                categorias_encontradas.append("carbo")
                subcategorias_encontradas.append("ambos")
            elif any(x in nome for x in ["frango", "carne", "linguica", "ovo"]):
                categorias_encontradas.append("proteina")
                subcategorias_encontradas.append("ambos")
            elif "leite" in nome:
                categorias_encontradas.append("liquido")
                subcategorias_encontradas.append("cafe")

        # 🛡️ ANTI-CONFLITO
        if "massa" in categorias_encontradas and "fruta" in categorias_encontradas:
            idx = categorias_encontradas.index("fruta")
            categorias_encontradas.pop(idx)
            subcategorias_encontradas.pop(idx)

        if "massa" in categorias_encontradas and "carboCF" in categorias_encontradas:
            idx = categorias_encontradas.index("carboCF")
            categorias_encontradas.pop(idx)
            subcategorias_encontradas.pop(idx)

        # 📏 NORMALIZA UNIDADE
        if categorias_encontradas:
            unidade = str(item.get("unidade", "")).strip().lower()
            quantidade = float(item.get("quantidade", 0))

            if unidade in ["kg", "quilo", "quilos"]:
                quantidade *= 1000
                unidade = "g"
            elif unidade in ["l", "litro", "litros"]:
                quantidade *= 1000
                unidade = "ml"
            elif unidade in ["un", "unidade", "unidades"]:
                unidade = "unidade"
            elif unidade in ["fatia", "fatias"]:
                unidade = "fatia"

            estoque_classificado.append({
                "nome": nome_original,
                "quantidade": quantidade,
                "unidade": unidade,
                "categorias": categorias_encontradas,
                "subcategorias": subcategorias_encontradas
            })

    return estoque_classificado