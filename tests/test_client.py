import pytest
import requests
from llm_client import gerar_ficha, LLMError

URL = "https://llm.teste:9001/api/chat"

@pytest.fixture(autouse=True)
def env(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "https://llm.teste:9001")
    monkeypatch.setenv("LLM_MODEL", "qwen3.5")

def test_sucesso(requests_mock):
    requests_mock.post(URL, json={"message": {"content": "EMPRESA: X"}})
    assert gerar_ficha("pedido") == "EMPRESA: X"

def test_credencial_invalida(requests_mock):
    requests_mock.post(URL, status_code=401)
    with pytest.raises(LLMError, match="Credencial"):
        gerar_ficha("pedido")

def test_indisponivel(requests_mock):
    requests_mock.post(URL, status_code=503)
    with pytest.raises(LLMError, match="indisponível"):
        gerar_ficha("pedido")

def test_timeout(requests_mock):
    requests_mock.post(URL, exc=requests.exceptions.Timeout)
    with pytest.raises(LLMError, match="timeout"):
        gerar_ficha("pedido")

def test_resposta_vazia(requests_mock):
    requests_mock.post(URL, json={"message": {"content": ""}})
    with pytest.raises(LLMError, match="vazia"):
        gerar_ficha("pedido")