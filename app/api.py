from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.database import (
    salvar_cardapio,
    buscar_cardapio
)

from backend.engine.engine import gerar_receita

from backend.services.cardapio_service import (
    carregar_receitas,
    gerar_cardapio,
    listar_ingredientes_e_unidades
)

from backend.database.database import (
    listar_estoque_atual,
    adicionar_item_estoque_atual,
    get_connection
)


app = FastAPI()


# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_credentials=True,
    allow_headers=["*"],
)


# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def root():
    return {"status": "API HealthCare rodando"}


# =========================
# ENGINE (NOVA ROTA IMPORTANTE)
# =========================
@app.get("/gerar-receita")
def api_gerar_receita():
    return gerar_receita()


# =========================
# RECEITAS (BANCO)
# =========================
@app.get("/receitas")
def get_receitas():
    return carregar_receitas()


# =========================
# ESTOQUE
# =========================
@app.get("/estoque")
def get_estoque():
    return listar_estoque_atual()


@app.post("/estoque")
def salvar_estoque(itens: list[dict]):

    conn = get_connection()
    conn.execute("DELETE FROM estoque_atual")
    conn.commit()
    conn.close()

    for item in itens:
        adicionar_item_estoque_atual(
            item["nome"],
            float(item["quantidade"]),
            item["unidade"]
        )

    return {"status": "ok"}

@app.post("/cardapio/gerar")
def gerar_cardapio_api(mes: int, ano: int):

    # 🔥 se já existe, NÃO gera de novo
    existente = buscar_cardapio(mes, ano)
    if existente:
        return {
            "status": "já existe",
            "cardapio": existente
        }

    estoque = listar_estoque_atual()

    if not estoque:
        return {"erro": "sem estoque"}

    cardapio, estoque_final = gerar_cardapio(estoque)

    salvar_cardapio(mes, ano, cardapio, estoque_final)

    return {
        "status": "gerado",
        "cardapio": cardapio
    }

@app.get("/cardapio")
def get_cardapio(mes: int, ano: int):

    data = buscar_cardapio(mes, ano)

    if not data:
        return {
            "status": "não existe",
            "cardapio": None
        }

    return data


# =========================
# INGREDIENTES
# =========================
@app.get("/ingredientes")
def get_ingredientes():
    return listar_ingredientes_e_unidades()