from collections import defaultdict


def criar_tracker():
    """
    Estrutura central de consumo.
    Guarda tudo que foi usado durante a geração das receitas.
    """
    return defaultdict(lambda: {"nome": "", "quantidade": 0, "unidade": ""})


def registrar_consumo(tracker, nome, quantidade, unidade):
    key = f"{nome}|{unidade}"

    if key not in tracker:
        tracker[key] = {
            "nome": nome,
            "quantidade": 0,
            "unidade": unidade
        }

    tracker[key]["quantidade"] += quantidade