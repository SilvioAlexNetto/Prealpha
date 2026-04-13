from copy import deepcopy
from datetime import datetime
import calendar

from app.backend.services.core.classificador import classificar_estoque
from app.backend.services.geradores.cafe import gerar_cafe
from app.backend.services.geradores.almoco import gerar_almoco
from app.backend.services.geradores.jantar import gerar_janta

from app.backend.services.cardapio_service import salvar_resultado


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

    resultado = {
        "receitas": todas_receitas,
        "sobras": sobras
    }

    salvar_resultado(resultado)

    print("✅ gerar_tudo OK", flush=True)

    return resultado