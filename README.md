# Gerador de Ficha de Produção para Pedidos de Acrílico

Aplicação em Python, executada no terminal, que usa um LLM para transformar o pedido de um cliente, escrito em linguagem livre, em uma ficha de produção padronizada para placas de acrílico.

## Problema

Um funcionário responsável por receber pedidos de placas de acrílico precisa transformar mensagens escritas pelos clientes em fichas padronizadas de produção, porque atualmente as informações chegam em formatos diferentes e exigem interpretação manual.

## Público-alvo

Funcionários responsáveis pelo atendimento e preparação de pedidos.

## Justificativa para uso de LLM

Os clientes escrevem seus pedidos em linguagem natural, sem um formato padronizado. Um modelo de linguagem consegue interpretar diferentes formas de escrita e extrair informações relevantes para uma ficha de produção.

## Entrada e saída

- **Entrada:** texto livre com o pedido do cliente, digitado no terminal.
- **Saída:** ficha de produção em texto, com campos como empresa, produto, material, dimensões, prazo e observações.

### Exemplo

Entrada:

```
Preciso de uma placa de acrílico 60x40 para a empresa Alfa, entrega até sexta.
```

Saída (exemplo ilustrativo):

```
EMPRESA: Alfa
PRODUTO: Placa
MATERIAL: Acrílico
DIMENSÕES: 60x40
PRAZO: Sexta-feira
OBSERVAÇÕES: Nenhuma
```

## Requisitos

- Python 3.15.2 (testado com esta versão; o curso pede 3.10 ou superior)
- Bibliotecas: `requests`, `python-dotenv`, `pytest`, `requests-mock`
- Acesso ao LLM institucional (modelo `qwen3.5:9b`, API compatível com Ollama)

## Instalação

```bash
git clone https://github.com/dbenass/p0-basico.git
cd p0-basico
python -m venv .venv
.venv\Scripts\activate        # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

## Configuração

Copie o arquivo de exemplo e ajuste os valores:

```bash
copy .env.example .env        # Linux/macOS: cp .env.example .env
```

| Variável | Descrição | Padrão |
|---|---|---|
| `LLM_BASE_URL` | Endereço do servidor do LLM | (obrigatória) |
| `LLM_MODEL` | Nome do modelo | `qwen3.5:9b` |
| `LLM_API_KEY` | Credencial, se o serviço exigir | vazio |
| `LLM_TIMEOUT` | Tempo máximo de espera, em segundos | `300` |
| `LLM_VERIFY_SSL` | Verificar o certificado SSL | `false` |
| `LLM_TEMPERATURE` | Variação das respostas | `0.2` |
| `LLM_MAX_TOKENS` | Limite de tokens da resposta | `800` |
| `LLM_THINK` | Ativa o raciocínio interno do modelo (gasta tokens) | `false` |

O arquivo `.env` contém dados de acesso e **não** é versionado. Nunca coloque credenciais reais no `.env.example`.

O servidor `llm-internal.softex:9001` usa certificado autoassinado, por isso a verificação SSL fica desabilitada (`LLM_VERIFY_SSL=false`). Ele só é acessível por aplicações executadas dentro do ambiente da plataforma, não pela máquina local.

## Execução

```bash
python src/app.py
```

## Testes

```bash
python -m pytest -v
```

Os testes **não** fazem chamada real ao LLM e não consomem tokens. Eles usam integração simulada (`requests_mock`) e cobrem: resposta de sucesso, credencial inválida, LLM indisponível, timeout, resposta vazia, validação de pedido vazio, montagem do prompt e carregamento da configuração.

A chamada **real** ao LLM só foi demonstrada [descreva onde e quando, por exemplo: "executando o container na plataforma Devel LLM Portal"].

## Tratamento de erros

O programa mostra mensagens claras, sem traceback, para: pedido vazio, configuração ausente ou inválida, credencial ausente ou inválida, LLM indisponível, falha de comunicação, timeout e resposta vazia ou em formato inesperado.

## Logs

A execução é registrada em `logs/app.log`. O log guarda apenas o resultado da execução (sucesso ou falha). Ele **não** registra chaves, credenciais, o pedido do cliente nem o conteúdo da ficha.

## Estrutura

```
src/app.py          entrada, prompt e apresentação
src/config.py       carregamento da configuração
src/llm_client.py   cliente HTTP do LLM
tests/              testes automatizados
```

## Validação em ambiente limpo

[Clonei o repositório em uma pasta nova, fora do projeto original, e segui apenas as instruções deste README: criei um novo `.venv`, instalei as dependências, copiei o `.env.example` para `.env` e executei `python -m pytest -v`.

- Sistema: Windows [11]
- Python: [saída de `python --3.15.2`]
- Resultado: 16 testes passaram.
- Problemas encontrados: nenhum.]

## Uso de IA no desenvolvimento

[Usei o Claude para orientar a estrutura do projeto, revisar o código e gerar rascunhos de testes e documentação. Todo o código foi executado, testado e revisado por mim.]