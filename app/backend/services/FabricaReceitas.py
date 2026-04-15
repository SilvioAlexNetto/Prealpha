from copy import deepcopy
from datetime import datetime
import calendar

from app.backend.services.utils.tracker import criar_tracker
from app.backend.services.core.classificador import classificar_estoque
from app.backend.services.geradores.cafe import gerar_cafe
from app.backend.services.geradores.almoco import gerar_almoco
from app.backend.services.geradores.jantar import gerar_janta
from app.backend.services.cardapio_service import salvar_resultado


def gerar_tudo(estoque_usuario, ingredientes_custom=None):

    hoje = datetime.now()
    total_dias = calendar.monthrange(hoje.year, hoje.month)[1]

    estoque_copia = deepcopy(estoque_usuario)

    estoque_classificado = classificar_estoque(
        estoque_copia,
        ingredientes_custom
    )

    estoque_base = deepcopy(estoque_classificado)

    tracker_consumo = criar_tracker()

    cafe = gerar_cafe(estoque_base, total_dias, tracker_consumo)
    almoco = gerar_almoco(estoque_base, total_dias, tracker_consumo)
    janta = gerar_janta(estoque_base, total_dias, tracker_consumo)

    todas_receitas = cafe + almoco + janta

    sobras = [
        {
            "nome": item["nome"],
            "quantidade": item["quantidade"],
            "unidade": item["unidade"]
        }
        for item in estoque_base
        if item["quantidade"] > 0
    ]

    consumidos = list(tracker_consumo.values())

    resultado = {
        "receitas": todas_receitas,
        "sobras": sobras,
        "consumidos": list(tracker_consumo.values())
    }


    print("\n📊 TRACKER FINAL:")
    for k, v in tracker_consumo.items():
        print(k, v)

    print("\n📦 SOBRAS:")
    for s in sobras[:5]:
        print(s)

    print("\n🔥 CONSUMIDOS:")
    for c in consumidos[:5]:
        print(c)

    salvar_resultado(resultado)

    return resultado