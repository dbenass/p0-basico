import os
from dotenv import load_dotenv

load_dotenv()


class ConfigError(Exception):
    pass


def carregar_config():
    base_url = os.getenv("LLM_BASE_URL")
    if not base_url:
        raise ConfigError("LLM_BASE_URL não configurada. Copie .env.example para .env.")

    try:
        timeout = float(os.getenv("LLM_TIMEOUT", "60"))
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
        max_tokens = int(os.getenv("LLM_MAX_TOKENS", "1000"))
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
        "verify_ssl": os.getenv("LLM_VERIFY_SSL", "false").lower() == "true",
        "temperature": temperature,
        "max_tokens": max_tokens,
        "think": os.getenv("LLM_THINK", "false").lower() == "true",
    }