from config.paths import RECEITAS_PATH, SOBRAS_PATH
from copy import deepcopy

from core.classificador import classificar_estoque
from geradores.cafe import gerar_cafe_com_copia
from geradores.almoco import gerar_almoco
from geradores.jantar import gerar_janta

def gerar_tudo(estoque_usuario):

    estoque_copia = deepcopy(estoque_usuario)

    estoque_classificado = classificar_estoque(estoque_copia)

    cafe = gerar_cafe_com_copia(estoque_classificado)
    almoco = gerar_almoco(estoque_classificado)
    janta = gerar_janta(estoque_classificado)

    todas_receitas = cafe + almoco + janta
    sobras = [i for i in estoque_classificado if i["quantidade"] > 0]

    return {
        "receitas": todas_receitas,
        "sobras": sobras
    }