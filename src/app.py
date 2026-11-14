import logging
import os
import sys
import threading
from logging.handlers import RotatingFileHandler

from config import ConfigError, carregar_config
from llm_client import LLMError, gerar_ficha, listar_modelos_disponiveis


def configurar_logs():
    handlers = [logging.StreamHandler(sys.stdout)]
    log_dir = os.getenv("LOG_DIR", "logs")
    try:
        os.makedirs(log_dir, exist_ok=True)
        handlers.append(
            RotatingFileHandler(
                os.path.join(log_dir, "app.log"),
                maxBytes=200_000,
                backupCount=2,
                encoding="utf-8",
            )
        )
    except OSError as e:
        print(f"Aviso: não foi possível gravar o log em arquivo ({e}).", flush=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=handlers,
    )


def criar_prompt(pedido):
    return f"""Você é um assistente especializado em produção de placas de acrílico.

Analise o pedido e gere uma ficha estruturada. Responda apenas com a ficha, sem explicações, neste formato:

EMPRESA:
PRODUTO:
MATERIAL:
DIMENSÕES:
PRAZO:
OBSERVAÇÕES:

Se alguma informação não estiver no pedido, escreva "não informado".

Pedido:
{pedido}
"""


def validar_pedido(pedido):
    pedido = pedido.strip()
    if not pedido:
        raise ValueError("O pedido não pode estar vazio.")
    return pedido


def obter_pedido():
    pedido = os.getenv("PEDIDO")
    if pedido is None:
        pedido = input("Digite o pedido do cliente:\n")
    return validar_pedido(pedido)


def _acompanhar_espera(parar, intervalo=30):
    segundos = 0
    while not parar.wait(intervalo):
        segundos += intervalo
        logging.info("Aguardando resposta do LLM... %ds", segundos)


def main():
    configurar_logs()
    logging.info("Aplicação iniciada")

    try:
        cfg = carregar_config()
    except ConfigError as e:
        logging.error("Configuração inválida: %s", e)
        print(f"\nErro: {e}", flush=True)
        sys.exit(1)

    try:
        pedido = obter_pedido()
    except ValueError as e:
        logging.error("Pedido inválido: %s", e)
        print(f"\nErro: {e}", flush=True)
        sys.exit(1)

    if cfg["diagnostico"]:
        modelos = listar_modelos_disponiveis()
        if modelos:
            logging.info("Servidor respondeu. Modelos: %s", ", ".join(modelos))
        else:
            logging.warning("Servidor não listou modelos")

    prompt = criar_prompt(pedido)

    logging.info("Enviando pedido ao LLM")
    parar = threading.Event()
    threading.Thread(target=_acompanhar_espera, args=(parar,), daemon=True).start()
    try:
        resultado = gerar_ficha(prompt)
    except (ConfigError, LLMError) as e:
        logging.error("Falha ao gerar ficha: %s", e)
        print(f"\nErro: {e}", flush=True)
        sys.exit(1)
    finally:
        parar.set()

    logging.info("Ficha gerada com sucesso (%d caracteres)", len(resultado))
    print("\n===== FICHA GERADA =====", flush=True)
    print(resultado, flush=True)


if __name__ == "__main__":
    main()