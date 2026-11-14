import pytest
from config import carregar_config, ConfigError


def test_config_sem_url(monkeypatch):
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    with pytest.raises(ConfigError):
        carregar_config()


def test_config_parametros(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "https://x:1")
    monkeypatch.setenv("LLM_MAX_TOKENS", "300")
    assert carregar_config()["max_tokens"] == 300


def test_config_valor_invalido(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "https://x:1")
    monkeypatch.setenv("LLM_MAX_TOKENS", "abc")
    with pytest.raises(ConfigError):
        carregar_config()


def test_config_aceita_ollama_host(monkeypatch):
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.setenv("OLLAMA_HOST", "https://x:1/")
    assert carregar_config()["base_url"] == "https://x:1"


def test_config_diagnostico_desligado_por_padrao(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "https://x:1")
    monkeypatch.delenv("LLM_DIAGNOSTICO", raising=False)
    assert carregar_config()["diagnostico"] is False