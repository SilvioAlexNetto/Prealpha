import httpx

# Tempo máximo de espera (evita travar backend)
TIMEOUT = 10


async def buscar_url(url: str) -> str:
    """
    Faz GET em uma URL e retorna o HTML da página.

    Args:
        url (str): URL do QR Code da nota fiscal

    Returns:
        str: HTML da página

    Raises:
        Exception: se não conseguir acessar ou status != 200
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(url)

        if response.status_code != 200:
            raise Exception(f"Erro HTTP: {response.status_code}")

        return response.text

    except httpx.ReadTimeout:
        raise Exception("Tempo de requisição excedido")

    except httpx.RequestError as e:
        raise Exception(f"Erro na requisição: {str(e)}")


async def buscar_url_json(url: str) -> dict:
    """
    Faz GET e tenta retornar JSON (caso alguma SEFAZ futura suporte JSON).

    Args:
        url (str)

    Returns:
        dict
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(url)

        if response.status_code != 200:
            raise Exception(f"Erro HTTP: {response.status_code}")

        return response.json()

    except ValueError:
        raise Exception("Resposta não é JSON válido")

    except httpx.RequestError as e:
        raise Exception(f"Erro ao buscar JSON: {str(e)}")