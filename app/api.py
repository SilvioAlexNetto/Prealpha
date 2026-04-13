from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.backend.services.FabricaReceitas import gerar_tudo
from app.backend.services.nota_fiscal_service import ler_nota_fiscal
from .backend.services.cardapio_service import (
    carregar_receitas,
    listar_ingredientes_e_unidades,
    carregar_sobras,
    montar_cardapio
)

from app.backend.services.utils.base_dinamica import categorias


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

        data = await request.json()

        ingredientes_custom = data.get("ingredientes_custom", {})

        estoque = listar_estoque_atual()

        print(f"📦 Estoque carregado: {len(estoque)} itens")

        if not estoque:
            print("⚠️ Estoque vazio")
            return {
                "cardapio": {},
                "estoque": []
            }

        # =========================
        # 🔥 PASSO 1: GERAR
        # =========================
        print("⚙️ Gerando receitas...")
        gerar_tudo(estoque, ingredientes_custom)
        print("✅ gerar_tudo OK")

        # =========================
        # 🔥 PASSO 2: CARREGAR
        # =========================
        print("📥 Carregando receitas...")
        receitas = carregar_receitas()
        sobras = carregar_sobras()

        print(f"🍽️ Receitas: {len(receitas)}")
        print(f"📦 Sobras: {len(sobras)}")

        # =========================
        # 🔥 PASSO 3: MONTAR
        # =========================
        print("📅 Montando cardápio...")
        cardapio = montar_cardapio(receitas)

        print("✅ Cardápio montado")
        print("🔥 ===== FIM CARDAPIO =====\n")

        return {
            "cardapio": cardapio,
            "estoque": sobras
        }

    except Exception as e:
        import traceback

        print("\n💥💥💥 ERRO NO BACKEND 💥💥💥")
        print("Erro:", str(e))
        traceback.print_exc()
        print("💥💥💥 FIM ERRO 💥💥💥\n")

        return {
            "erro": str(e),
            "tipo": type(e).__name__
        }
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
