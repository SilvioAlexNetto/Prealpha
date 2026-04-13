from copy import deepcopy
from datetime import datetime
import calendar

from app.backend.services.core.classificador import classificar_estoque
from app.backend.services.geradores.cafe import gerar_cafe
from app.backend.services.geradores.almoco import gerar_almoco
from app.backend.services.geradores.jantar import gerar_janta

from app.backend.services.cardapio_service import salvar_resultado


def calcular_consumidos(inicial, sobras):
    sobra_map = {i["nome"]: i["quantidade"] for i in sobras}

    consumidos = []

    for item in inicial:
        nome = item["nome"]
        inicial_qtd = item["quantidade"]
        sobra_qtd = sobra_map.get(nome, 0)

        usado = inicial_qtd - sobra_qtd

        if usado > 0:
            consumidos.append({
                "nome": nome,
                "quantidade": usado,
                "unidade": item["unidade"]
            })

    return consumidos
    
def gerar_tudo(estoque_usuario, ingredientes_custom=None):

    hoje = datetime.now()
    total_dias = calendar.monthrange(hoje.year, hoje.month)[1]

    print("👉 Entrou no gerar_tudo", flush=True)

    estoque_copia = deepcopy(estoque_usuario)
    estoque_classificado = classificar_estoque(
    estoque_copia,
    ingredientes_custom
)

    # 🔥 ESTOQUE ÚNICO
    estoque_inicial = deepcopy(estoque_classificado)
    estoque_base = estoque_classificado

    print("☕ Gerando café...", flush=True)
    cafe = gerar_cafe(estoque_base, total_dias)

    print("🍽️ Gerando almoço...", flush=True)
    almoco = gerar_almoco(estoque_base, total_dias)

    print("🌙 Gerando jantar...", flush=True)
    janta = gerar_janta(estoque_base, total_dias)

    todas_receitas = cafe + almoco + janta

    print(f"📊 Total receitas geradas: {len(todas_receitas)}", flush=True)

    sobras = [i for i in estoque_base if i["quantidade"] > 0]

    consumidos = calcular_consumidos(estoque_inicial, sobras)

    resultado = {
        "receitas": todas_receitas,
        "sobras": sobras,
        "consumidos": consumidos
    }

    salvar_resultado(resultado)

    print("✅ gerar_tudo OK", flush=True)

    return resultado