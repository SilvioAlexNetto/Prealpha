import requests

# Tempo máximo de espera (evita travar backend)
TIMEOUT = 10


def buscar_url(url: str) -> str:
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
        response = requests.get(url, timeout=TIMEOUT)

        if response.status_code != 200:
            raise Exception(f"Erro HTTP: {response.status_code}")

        return response.text

    except requests.exceptions.Timeout:
        raise Exception("Tempo de requisição excedido")

    except requests.exceptions.RequestException as e:
        raise Exception(f"Erro na requisição: {str(e)}")


def buscar_url_json(url: str) -> dict:
    """
    Faz GET e tenta retornar JSON (caso alguma SEFAZ futura suporte JSON).

    Args:
        url (str)

    Returns:
        dict
    """
    try:
        response = requests.get(url, timeout=TIMEOUT)

        if response.status_code != 200:
            raise Exception(f"Erro HTTP: {response.status_code}")

        return response.json()

    except ValueError:
        raise Exception("Resposta não é JSON válido")

    except Exception as e:
        raise Exception(f"Erro ao buscar JSON: {str(e)}")