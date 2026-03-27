from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.backend.services.FabricaReceitas import gerar_tudo

from .backend.services.cardapio_service import (
    carregar_receitas,
    obter_cardapio,
    listar_ingredientes_e_unidades,
    carregar_sobras,
    montar_cardapio
)


from .database.database import (
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
# ROTAS BÁSICAS
# =========================
@app.get("/")
def root():
    return {"status": "API HealthCare rodando"}

# =========================
# RECEITAS
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
async def salvar_estoque(request: Request):
    payload = await request.json()

    if isinstance(payload, list):
        itens = payload
    elif isinstance(payload, dict):
        itens = payload.get("estoque", [])
    else:
        itens = []

    if not isinstance(itens, list):
        itens = []

    conn = get_connection()
    conn.execute("DELETE FROM estoque_atual")
    conn.commit()
    conn.close()

    for item in itens:
        nome = item.get("nome")
        quantidade = item.get("quantidade")
        unidade = item.get("unidade")

        if not nome or not quantidade or not unidade:
            continue

        try:
            quantidade = float(quantidade)
        except:
            continue

        adicionar_item_estoque_atual(
            nome,
            quantidade,
            unidade
        )

    return {"status": "ok"}

# =========================
# CARDÁPIO
# =========================
@app.post("/cardapio")
def gerar_cardapio_api():
    estoque = listar_estoque_atual()

    if not estoque:
        return {
            "cardapio": {},
            "estoque": []
        }

    # 🔥 PASSO 1: gerar receitas com base no estoque
    gerar_tudo(estoque)

    # 🔥 PASSO 2: carregar receitas recém-geradas
    receitas = carregar_receitas()
    sobras = carregar_sobras()

    # 🔥 PASSO 3: montar cardápio
    cardapio = montar_cardapio(receitas)

    return {
        "cardapio": cardapio,
        "estoque": sobras
    }

# =========================
# INGREDIENTES
# =========================
@app.get("/ingredientes")
def get_ingredientes():
    return listar_ingredientes_e_unidades()

