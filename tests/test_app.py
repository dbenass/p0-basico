import pytest
from app import criar_prompt, validar_pedido


def test_pedido_vazio():
    with pytest.raises(ValueError):
        validar_pedido("   ")


def test_prompt_contem_pedido():
    assert "placa 60x40" in criar_prompt("placa 60x40")