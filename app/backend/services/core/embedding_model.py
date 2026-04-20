from sentence_transformers import SentenceTransformer
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"

model = SentenceTransformer(
    "all-MiniLM-L6-v2",
    device=device
)

print(f"[EMBEDDING MODEL] carregado em {device}")


def encode(texts):
    return model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)