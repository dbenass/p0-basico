import logging
import sys

from config import ConfigError
from llm_client import LLMError, gerar_ficha

logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def criar_prompt(pedido):
    return f"""
Você é um assistente especializado em produção de placas de acrílico.

Analise o pedido e gere uma ficha estruturada.

Pedido:

{pedido}
"""


def validar_pedido(pedido):
    pedido = pedido.strip()
    if not pedido:
        raise ValueError("O pedido não pode estar vazio.")
    return pedido


def main():
    try:
        pedido = validar_pedido(input("Digite o pedido do cliente:\n"))
    except ValueError as e:
        print(f"\nErro: {e}")
        sys.exit(1)

    prompt = criar_prompt(pedido)

    try:
        resultado = gerar_ficha(prompt)
    except (ConfigError, LLMError) as e:
        logging.error("Falha ao gerar ficha: %s", e)
        print(f"\nErro: {e}")
        sys.exit(1)

    logging.info("Ficha gerada com sucesso (%d caracteres)", len(resultado))
    print("\n===== FICHA GERADA =====")
    print(resultado)


if __name__ == "__main__":
    main()