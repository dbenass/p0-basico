import os
from dotenv import load_dotenv

load_dotenv()

class ConfigError(Exception):
    pass

def carregar_config():
    base_url = os.getenv("LLM_BASE_URL")
    if not base_url:
        raise ConfigError("LLM_BASE_URL não configurada. Copie .env.example para .env.")
    return {
        "base_url": base_url.rstrip("/"),
        "model": os.getenv("LLM_MODEL", "qwen3.5"),
        "api_key": os.getenv("LLM_API_KEY", ""),
        "timeout": float(os.getenv("LLM_TIMEOUT", "60")),
        "verify_ssl": os.getenv("LLM_VERIFY_SSL", "false").lower() == "true",
    }