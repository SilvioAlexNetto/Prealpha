from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.services.cardapio_service import carregar_receitas

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "API HealthCare rodando"}

@app.get("/receitas")
def listar_receitas():
    return carregar_receitas()