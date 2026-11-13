import requests
from config import carregar_config

class LLMError(Exception):
    pass

def gerar_ficha(prompt):
    cfg = carregar_config()
    headers = {}
    if cfg["api_key"]:
        headers["Authorization"] = f"Bearer {cfg['api_key']}"

    payload = {
        "model": cfg["model"],
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }

    try:
        resp = requests.post(
            f"{cfg['base_url']}/api/chat",
            json=payload,
            headers=headers,
            timeout=cfg["timeout"],
            verify=cfg["verify_ssl"],
        )
    except requests.exceptions.Timeout:
        raise LLMError("O LLM demorou demais para responder (timeout).")
    except requests.exceptions.ConnectionError:
        raise LLMError("Não foi possível conectar ao LLM. Verifique a URL e a rede.")

    if resp.status_code in (401, 403):
        raise LLMError("Credencial ausente ou inválida.")
    if resp.status_code >= 500:
        raise LLMError("LLM indisponível no momento.")
    if resp.status_code != 200:
        raise LLMError(f"Erro inesperado do LLM (HTTP {resp.status_code}).")

    try:
        texto = resp.json()["message"]["content"].strip()
    except (ValueError, KeyError, TypeError):
        raise LLMError("Resposta do LLM em formato inesperado.")

    if not texto:
        raise LLMError("O LLM retornou uma resposta vazia.")
    return texto