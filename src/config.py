import os
from dotenv import load_dotenv

load_dotenv()


class ConfigError(Exception):
    pass


def _bool(nome, padrao="false"):
    return os.getenv(nome, padrao).lower() == "true"


def carregar_config():
    base_url = os.getenv("LLM_BASE_URL") or os.getenv("OLLAMA_HOST")
    if not base_url:
        raise ConfigError(
            "LLM_BASE_URL (ou OLLAMA_HOST) não configurada. Copie .env.example para .env."
        )

    try:
        timeout = float(os.getenv("LLM_TIMEOUT", "300"))
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
        max_tokens = int(os.getenv("LLM_MAX_TOKENS", "500"))
    except ValueError:
        raise ConfigError(
            "Valor inválido em LLM_TIMEOUT, LLM_TEMPERATURE ou LLM_MAX_TOKENS. "
            "Use apenas números."
        )

    return {
        "base_url": base_url.rstrip("/"),
        "model": os.getenv("LLM_MODEL", "qwen3.5:9b"),
        "api_key": os.getenv("LLM_API_KEY", ""),
        "timeout": timeout,
        "verify_ssl": _bool("LLM_VERIFY_SSL"),
        "temperature": temperature,
        "max_tokens": max_tokens,
        "think": _bool("LLM_THINK"),
        "diagnostico": _bool("LLM_DIAGNOSTICO"),
    }