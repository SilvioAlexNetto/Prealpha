def receita_valida(*args):
    return all(arg is not None for arg in args)
