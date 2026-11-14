# Gerador de Ficha de Produção para Pedidos de Acrílico

Aplicação em Python, executada no terminal, que usa um LLM para transformar o pedido de um cliente, escrito em linguagem livre, em uma ficha de produção padronizada para placas de acrílico.

## Problema

Um funcionário responsável por receber pedidos de placas de acrílico precisa transformar mensagens escritas pelos clientes em fichas padronizadas de produção, porque atualmente as informações chegam em formatos diferentes e exigem interpretação manual.

## Público-alvo

Funcionários responsáveis pelo atendimento e preparação de pedidos.

## Por que usar um LLM

Os clientes escrevem seus pedidos em linguagem natural, sem formato padronizado. Um modelo de linguagem consegue interpretar diferentes formas de escrita e extrair as informações relevantes para a ficha.

## Entrada e saída

- **Entrada:** texto livre com o pedido do cliente.
- **Saída:** ficha de produção em texto, com seis campos fixos: empresa, produto, material, dimensões, prazo e observações.

### Como o pedido é informado

- **Execução local:** o programa pede o pedido pelo terminal.
- **Plataforma (container):** o Devel LLM Portal não oferece terminal interativo, então o pedido é informado pela variável de ambiente `PEDIDO`, e o resultado é lido no botão **Logs**.

Se `PEDIDO` estiver definida (inclusive no `.env`), o programa não pede a digitação.

### Exemplo real

Entrada (pedido fictício):

```
Placa de acrilico 60x40 para a empresa Alfa, entrega sexta
```

Saída, obtida na execução real em 13/11/2026:

```
EMPRESA: Alfa
PRODUTO: Placa de acrílico
MATERIAL: Acrílico
DIMENSÕES: 60x40
PRAZO: Sexta-feira
OBSERVAÇÕES: não informado
```

## Requisitos

- Python 3.15.2 (desenvolvimento local). A imagem Docker usa Python 3.12.
- Bibliotecas, com versões fixadas em `requirements.txt`: `requests` (chamada HTTP), `python-dotenv` (leitura do `.env`), `pytest` e `requests-mock` (testes).
- Acesso ao LLM institucional: modelo `qwen3.5:9b`, API REST compatível com Ollama.

## Instalação

```bash
git clone https://github.com/dbenass/p0-basico.git
cd p0-basico
python -m venv .venv
.venv\Scripts\activate        # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

## Configuração

Copie o arquivo de exemplo:

```bash
copy .env.example .env        # Linux/macOS: cp .env.example .env
```

| Variável | Descrição | Padrão |
|---|---|---|
| `LLM_BASE_URL` | Endereço do servidor do LLM (aceita também `OLLAMA_HOST`) | obrigatória |
| `LLM_MODEL` | Nome exato do modelo | `qwen3.5:9b` |
| `LLM_API_KEY` | Credencial, se o serviço exigir | vazio |
| `LLM_TIMEOUT` | Tempo máximo de espera, em segundos | `300` |
| `LLM_VERIFY_SSL` | Verificar o certificado SSL | `false` |
| `LLM_TEMPERATURE` | Variação das respostas | `0.2` |
| `LLM_MAX_TOKENS` | Limite de tokens da resposta | `500` |
| `LLM_THINK` | Ativa o raciocínio interno do modelo (gasta tokens) | `false` |
| `LLM_DIAGNOSTICO` | Lista os modelos do servidor ao iniciar | `false` |
| `LOG_DIR` | Pasta do arquivo de log | `logs` |
| `PEDIDO` | Pedido informado sem digitação (usado no container) | vazio |

O `.env` contém dados de acesso e **não** é versionado. O `.env.example` não tem credenciais.

## Onde a aplicação funciona

O servidor do LLM (`llm-internal.softex:9001`) usa certificado autoassinado, por isso a verificação SSL fica desabilitada. Ele só é acessível por aplicações executadas dentro do ambiente da plataforma Devel LLM Portal. Na máquina local, a aplicação exibe uma mensagem de erro de conexão (comportamento esperado), e os testes usam integração simulada.

## Execução

Local (mostra o tratamento de erro, pois o servidor não é alcançável):

```bash
python src/app.py
```

Na plataforma (chamada real): gere a imagem, salve em `.tar` e envie pelo portal.

```bash
docker build -t seu-identificador:latest .
docker save --output seu-identificador.tar seu-identificador:latest
```

Variáveis informadas no portal:

```
LLM_BASE_URL=https://llm-internal.softex:9001
LLM_MODEL=qwen3.5:9b
LLM_VERIFY_SSL=false
LLM_TIMEOUT=300
LLM_MAX_TOKENS=500
LLM_THINK=false
LOG_DIR=/persistent/logs
PEDIDO=Placa de acrilico 60x40 para a empresa Alfa, entrega sexta
```

Como o aplicativo é de terminal, o container executa uma vez e termina (estado "Parado"). O resultado fica no botão **Logs**, que é apagado a cada novo início. Alterações de variáveis só valem depois de parar e iniciar o container.

## Testes

```bash
python -m pytest -v
```

| Tipo | O que cobre | Chamada ao LLM |
|---|---|---|
| **Simulados** (`requests-mock`) | sucesso, credencial inválida, credencial não exposta no erro, LLM indisponível, timeout, falha genérica de rede, resposta vazia, resposta só com raciocínio, modelo não encontrado (404), parâmetros enviados | não, sem custo de tokens |
| **Lógica local** | validação de pedido vazio, montagem do prompt com formato fixo, carregamento e validação da configuração | não |
| **Real** | execução do container na plataforma | sim, descrita abaixo |

## Tratamento de erros

O programa mostra mensagens claras, sem traceback, para: pedido vazio, configuração ausente ou inválida, credencial ausente ou inválida, LLM indisponível, falha de comunicação, timeout, resposta vazia ou em formato inesperado.

## Logs

O log vai para o terminal e para um arquivo com rotação (`LOG_DIR`, `/persistent/logs` na plataforma, único diretório que mantém dados quando o container para). Registra apenas eventos de execução e tempos informados pelo servidor. **Não** registra chaves, credenciais, o pedido do cliente nem o conteúdo da ficha.

## Execução real na plataforma

Em 13/11/2026, executei a aplicação como container no Devel LLM Portal, com o modelo `qwen3.5:9b` e um pedido fictício. O log registrou a ficha gerada com sucesso (122 caracteres). A chamada ao modelo levou cerca de 100 segundos, e a execução completa cerca de 2 minutos.

Problemas encontrados durante a execução real e correções:

| Problema | Causa | Correção |
|---|---|---|
| HTTP 404 | nome do modelo incompleto (`qwen3.5`) | usar o nome exato `qwen3.5:9b`; a mensagem de erro passou a listar os modelos disponíveis |
| Resposta vazia | o modelo gastava os tokens raciocinando | enviar `think: false` e tratar resposta só com raciocínio |
| Ficha fora do formato | prompt sem formato definido | prompt com os seis campos fixos e teste automatizado |
| Log vazio no portal | log gravado só em arquivo | log também no terminal, com aviso periódico de espera |

## Decisões de projeto

- **Chamada HTTP direta (`requests`)**, isolada em `llm_client.py`, para o código ficar simples e fácil de testar sem consumir tokens.
- **Etapas separadas:** captura da entrada, configuração, montagem da solicitação, chamada, tratamento da resposta e apresentação ficam em funções distintas.
- **Configuração por variáveis de ambiente**, para trocar modelo, tempo limite e parâmetros sem alterar o código.
- **Verificação SSL desabilitada** por exigência da plataforma (certificado autoassinado).
- **Raciocínio do modelo desligado**, porque consumia tokens e deixava a resposta vazia.
- **Logs sem o conteúdo do pedido**, por privacidade e conformidade com a LGPD.

## Estrutura

```
src/app.py          entrada, prompt e apresentação
src/config.py       carregamento da configuração
src/llm_client.py   cliente HTTP do LLM
tests/              testes automatizados
Dockerfile          imagem para a plataforma
```

## Uso de IA no desenvolvimento

Utilizei o Claude (Anthropic) como apoio durante o desenvolvimento: orientação sobre a estrutura do projeto, revisão e correção de código, rascunhos de testes e da documentação. Todo o código foi executado, testado e revisado por mim, e as decisões sobre o problema, o escopo e os testes foram minhas.