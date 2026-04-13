from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.backend.services.FabricaReceitas import gerar_tudo
from app.backend.services.nota_fiscal_service import ler_nota_fiscal
from .backend.services.cardapio_service import (
    carregar_receitas,
    listar_ingredientes_e_unidades,
    carregar_sobras,
    montar_cardapio,
    carregar_consumidos
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
# CARDÁPIO (DEBUG MODE)
# =========================


@app.post("/cardapio")
async def gerar_cardapio_api(request: Request):
    try:
        print("\n🔥 ===== INICIO CARDAPIO =====")

        try:
            data = await request.json()
        except:
            data = {}

        ingredientes_custom = data.get("ingredientes_custom", {})

        estoque = listar_estoque_atual()

        print(f"📦 Estoque carregado: {len(estoque)} itens")

        if not estoque:
            return {"cardapio": {}, "estoque": []}

        print("⚙️ Gerando receitas...")
        gerar_tudo(estoque, ingredientes_custom)
        print("✅ gerar_tudo OK")

        receitas = carregar_receitas()
        sobras = carregar_sobras()
        consumidos = carregar_consumidos()

        cardapio = montar_cardapio(receitas)

        return {
            "cardapio": cardapio,
            "estoque": sobras,
            "consumidos": consumidos
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"erro": str(e)}
# =========================
# INGREDIENTES
# =========================
@app.get("/ingredientes")
def get_ingredientes():
    return listar_ingredientes_e_unidades()


@app.post("/nota-fiscal/ler")
async def ler_nota(request: Request):
    data = await request.json()
    url = data.get("url")

    if not url:
        return {"erro": "URL não enviada"}

    return await ler_nota_fiscal(url)
