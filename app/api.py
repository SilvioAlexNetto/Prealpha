from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from .backend.services.cardapio_service import (
    carregar_receitas,
    gerar_cardapio,
    listar_ingredientes_e_unidades
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
def salvar_estoque(itens: list[dict]):
    # limpa estoque antes
    conn = get_connection()
    conn.execute("DELETE FROM estoque_atual")
    conn.commit()
    conn.close()

    for item in itens:
        adicionar_item_estoque_atual(
            item["nome"],                 # ✅ nome preservado
            float(item["quantidade"]),
            item["unidade"]
        )

    return {"status": "ok"}

# =========================
# CARDÁPIO
# =========================
@app.post("/cardapio")
def gerar_cardapio_api():
    estoque = listar_estoque_atual()

    # 🔒 proteção básica
    if not estoque:
        return {
            "cardapio": {},
            "estoque": []
        }

    cardapio, estoque_atualizado = gerar_cardapio(estoque)

    return {
        "cardapio": cardapio,
        "estoque": estoque_atualizado
    }

# =========================
# INGREDIENTES
# =========================
@app.get("/ingredientes")
def get_ingredientes():
    return listar_ingredientes_e_unidades()

