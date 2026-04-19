from difflib import SequenceMatcher
from app.backend.services.bases import (
    proteinasKG, proteinasUN, carboidratos,
    carboidratosCF, frutas, legumes, cereais,
    massas, molhos, liquidos, farinhas
)

from app.backend.services.utils.base_dinamica import montar_base_dinamica
from app.backend.services.core.normalizacao import normalizar

def score_match(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def construir_vocabulario():
    base = montar_base_dinamica()

    vocab = {}

    for categoria, itens in base.items():
        for item in itens:
            vocab[normalizar(item)] = item, categoria

    return vocab

def resolver_categoria_final(nome: str):
    nome_norm = normalizar(nome)

    vocab = construir_vocabulario()

    melhor_match = None
    melhor_score = 0
    melhor_categoria = None
    melhor_original = None

    for key, (original, categoria) in vocab.items():
        score = score_match(nome_norm, key)

        if score > melhor_score:
            melhor_score = score
            melhor_match = key
            melhor_categoria = categoria
            melhor_original = original

    # 🔥 threshold de confiança
    if melhor_score >= 0.78:
        return {
            "nome_final": melhor_original,
            "categoria": melhor_categoria,
            "score": melhor_score
        }

    # fallback
    return {
        "nome_final": nome,
        "categoria": "desconhecido",
        "score": melhor_score
    }