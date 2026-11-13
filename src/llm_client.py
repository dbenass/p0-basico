import requests
import urllib3

from config import carregar_config


class LLMError(Exception):
    pass


def _detalhe_erro(resp):
    try:
        return str(resp.json().get("error", ""))[:200]
    except (ValueError, AttributeError):
        return ""


def _listar_modelos(cfg, headers):
    try:
        resp = requests.get(
            f"{cfg['base_url']}/api/tags",
            headers=headers,
            timeout=cfg["timeout"],
            verify=cfg["verify_ssl"],
        )
        return [m["name"] for m in resp.json().get("models", [])]
    except (
        requests.exceptions.RequestException,
        ValueError,
        KeyError,
        TypeError,
        AttributeError,
    ):
        return []


def gerar_ficha(prompt):
    cfg = carregar_config()

    if not cfg["verify_ssl"]:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    headers = {}
    if cfg["api_key"]:
        headers["Authorization"] = f"Bearer {cfg['api_key']}"

    payload = {
        "model": cfg["model"],
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "think": cfg["think"],
        "options": {
            "temperature": cfg["temperature"],
            "num_predict": cfg["max_tokens"],
        },
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
    if resp.status_code == 404:
        msg = (
            f"Modelo ou endpoint não encontrado (HTTP 404). "
            f"Verifique LLM_MODEL ('{cfg['model']}') e LLM_BASE_URL."
        )
        detalhe = _detalhe_erro(resp)
        if detalhe:
            msg += f" Resposta do servidor: {detalhe}"
        modelos = _listar_modelos(cfg, headers)
        if modelos:
            msg += f" Modelos disponíveis: {', '.join(modelos)}."
        raise LLMError(msg)
    if resp.status_code >= 500:
        raise LLMError("LLM indisponível no momento.")
    if resp.status_code != 200:
        raise LLMError(f"Erro inesperado do LLM (HTTP {resp.status_code}).")

    try:
        mensagem = resp.json()["message"]
        texto = (mensagem.get("content") or "").strip()
    except (ValueError, KeyError, TypeError, AttributeError):
        raise LLMError("Resposta do LLM em formato inesperado.")

    if not texto:
        if mensagem.get("thinking"):
            raise LLMError(
                "O LLM gastou o limite de tokens raciocinando e não gerou a ficha. "
                "Aumente LLM_MAX_TOKENS ou mantenha LLM_THINK=false."
            )
        raise LLMError("O LLM retornou uma resposta vazia.")
    return texto