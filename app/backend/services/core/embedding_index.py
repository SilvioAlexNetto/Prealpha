import numpy as np
import faiss
from app.backend.services.utils.base_dinamica import montar_base_dinamica
from app.backend.services.core.normalizacao import normalizar
from app.backend.services.core.embedding_model import model

index = None
mapeamento = []


def construir_index():
    global index, mapeamento

    base = montar_base_dinamica()

    textos = []
    mapeamento = []

    for categoria, itens in base.items():
        for item in itens:
            item_norm = item.lower()

            textos.append(item_norm)
            mapeamento.append((item, categoria))

    embeddings = model.encode(textos)

    dim = embeddings.shape[1]

    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype("float32"))

    print("[EMBEDDING] índice carregado:", len(textos))


def buscar_similar(nome: str, top_k=1):
    global index, mapeamento

    if index is None:
        construir_index()

    nome_norm = normalizar(nome)

    vec = model.encode([nome_norm])
    vec = np.array(vec).astype("float32")

    distancias, indices = index.search(vec, top_k)

    idx = indices[0][0]

    item, categoria = mapeamento[idx]

    # 🔥 converter distância L2 em score intuitivo
    distance = float(distancias[0][0])
    score = 1 / (1 + distance)

    return {
        "nome": item,
        "categoria": categoria,
        "score": score
    }

def atualizar_modelo():
    global index, mapeamento
    index = None
    mapeamento = []
    construir_index()