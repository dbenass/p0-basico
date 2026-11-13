import pytest
import requests
from llm_client import gerar_ficha, LLMError

URL = "https://llm.teste:9001/api/chat"


@pytest.fixture(autouse=True)
def env(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "https://llm.teste:9001")
    monkeypatch.setenv("LLM_MODEL", "qwen3.5:9b")


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


def test_modelo_nao_encontrado(requests_mock):
    requests_mock.post(URL, status_code=404, json={"error": "model not found"})
    requests_mock.get(
        "https://llm.teste:9001/api/tags",
        json={"models": [{"name": "qwen3.5:9b"}]},
    )
    with pytest.raises(LLMError, match="qwen3.5:9b"):
        gerar_ficha("pedido")


def test_envia_think_desligado(requests_mock):
    mock = requests_mock.post(URL, json={"message": {"content": "EMPRESA: X"}})
    gerar_ficha("pedido")
    assert mock.last_request.json()["think"] is False


def test_so_raciocinio_sem_resposta(requests_mock):
    requests_mock.post(
        URL, json={"message": {"content": "", "thinking": "analisando..."}}
    )
    with pytest.raises(LLMError, match="raciocinando"):
        gerar_ficha("pedido")