import logging

import requests
import urllib3

from config import carregar_config


class LLMError(Exception):
    pass


def _montar_headers(cfg):
    headers = {}
    if cfg["api_key"]:
        headers["Authorization"] = f"Bearer {cfg['api_key']}"
    return headers


def montar_payload(prompt, cfg):
    return {
        "model": cfg["model"],
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "think": cfg["think"],
        "options": {
            "temperature": cfg["temperature"],
            "num_predict": cfg["max_tokens"],
        },
    }


def _chamar_llm(payload, cfg, headers):
    try:
        return requests.post(
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
    except requests.exceptions.RequestException:
        raise LLMError("Falha na comunicação com o LLM. Verifique LLM_BASE_URL.")


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
            timeout=min(cfg["timeout"], 15),
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


def _validar_status(resp, cfg, headers):
    if resp.status_code == 200:
        return
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
    raise LLMError(f"Erro inesperado do LLM (HTTP {resp.status_code}).")


def _registrar_tempos(resp):
    try:
        d = resp.json()
        logging.info(
            "Tempos do LLM: total=%.1fs carga_modelo=%.1fs leitura_prompt=%.1fs "
            "geracao=%.1fs tokens_gerados=%s",
            d.get("total_duration", 0) / 1e9,
            d.get("load_duration", 0) / 1e9,
            d.get("prompt_eval_duration", 0) / 1e9,
            d.get("eval_duration", 0) / 1e9,
            d.get("eval_count", "?"),
        )
    except (ValueError, AttributeError, TypeError):
        pass


def _extrair_texto(resp):
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


def _preparar_ambiente(cfg):
    if not cfg["verify_ssl"]:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def listar_modelos_disponiveis():
    cfg = carregar_config()
    _preparar_ambiente(cfg)
    return _listar_modelos(cfg, _montar_headers(cfg))


def gerar_ficha(prompt):
    cfg = carregar_config()
    _preparar_ambiente(cfg)
    headers = _montar_headers(cfg)
    payload = montar_payload(prompt, cfg)

    resp = _chamar_llm(payload, cfg, headers)
    _validar_status(resp, cfg, headers)
    _registrar_tempos(resp)
    return _extrair_texto(resp)