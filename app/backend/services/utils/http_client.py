import httpx
import asyncio

# Tempo máximo de espera
TIMEOUT = 10

# Quantidade de tentativas (anti-instabilidade SEFAZ)
MAX_RETRIES = 3


# =========================
# 🌐 HEADERS (ANTI-BLOQUEIO)
# =========================
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
}


# =========================
# 🔗 BUSCAR HTML
# =========================
async def buscar_url(url: str) -> str:
    try:
        print(f"[DEBUG] 🔗 Buscando URL: {url}")

        for tentativa in range(1, MAX_RETRIES + 1):
            try:
                async with httpx.AsyncClient(
                    timeout=TIMEOUT,
                    follow_redirects=True,  # 🔥 ESSENCIAL (resolve 302)
                ) as client:

                    response = await client.get(
                        url,
                        headers=DEFAULT_HEADERS
                    )

                print(f"[DEBUG] 🌐 Status HTTP: {response.status_code} (tentativa {tentativa})")

                # sucesso
                if response.status_code == 200 and response.text:
                    print(f"[DEBUG] 📄 HTML tamanho: {len(response.text)}")
                    return response.text

                # retry se não for 200
                if tentativa < MAX_RETRIES:
                    await asyncio.sleep(1)
                    continue

                raise Exception(f"Erro HTTP: {response.status_code}")

            except httpx.ReadTimeout:
                print(f"[WARN] Timeout na tentativa {tentativa}")

                if tentativa < MAX_RETRIES:
                    await asyncio.sleep(1)
                    continue

                raise Exception("Tempo de requisição excedido")

            except httpx.RequestError as e:
                print(f"[WARN] Erro de conexão: {e}")

                if tentativa < MAX_RETRIES:
                    await asyncio.sleep(1)
                    continue

                raise Exception(f"Erro na requisição: {str(e)}")

    except Exception as e:
        print(f"[ERRO FINAL buscar_url] {e}")
        raise e


# =========================
# 🌐 BUSCAR JSON
# =========================
async def buscar_url_json(url: str) -> dict:
    try:
        for tentativa in range(1, MAX_RETRIES + 1):
            try:
                async with httpx.AsyncClient(
                    timeout=TIMEOUT,
                    follow_redirects=True
                ) as client:

                    response = await client.get(
                        url,
                        headers=DEFAULT_HEADERS
                    )

                if response.status_code == 200:
                    return response.json()

                if tentativa < MAX_RETRIES:
                    await asyncio.sleep(1)
                    continue

                raise Exception(f"Erro HTTP: {response.status_code}")

            except ValueError:
                raise Exception("Resposta não é JSON válido")

            except httpx.RequestError as e:
                if tentativa < MAX_RETRIES:
                    await asyncio.sleep(1)
                    continue

                raise Exception(f"Erro ao buscar JSON: {str(e)}")

    except Exception as e:
        print(f"[ERRO FINAL buscar_url_json] {e}")
        raise e