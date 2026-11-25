# Relatório de Execução — P0

**Projeto:** Gerador de Ficha de Produção para Pedidos de Acrílico
**Autor:** Derick Benasse
**Repositório:** https://github.com/dbenass/p0-basico
**Modelo utilizado:** `qwen3.5:9b` (LLM institucional, API REST compatível com Ollama)
**Python:** 3.15.2 (desenvolvimento local) e 3.12 (imagem Docker)

## Evolução por nível

**Básico** (tag `p0-basico`): aplicação em Python, executada no terminal, que recebe o pedido de um cliente, monta um prompt, envia ao LLM por chamada HTTP e exibe a ficha de produção. Endereço e parâmetros de acesso ficam em variáveis de ambiente (`.env`), as dependências estão em `requirements.txt` e o repositório é público.

**Intermediário** (tag `p0-intermediario`): código dividido em etapas (`app.py` para entrada e apresentação, `config.py` para configuração, `llm_client.py` para montagem da solicitação, chamada e tratamento da resposta). Foram acrescentados: bloqueio de pedido vazio; tratamento de configuração ausente ou inválida, credencial ausente ou inválida, indisponibilidade, falha de comunicação, timeout e resposta vazia ou inesperada; testes com integração simulada; `.env.example`, `.gitignore` e README; e a integração da branch `dev` na `main` por Pull Request (#1 e #2).

**Avançado** (tag `p0-avancado`): parâmetros do LLM configuráveis sem alterar o código (modelo, timeout, temperatura, limite de tokens, raciocínio do modelo, pasta de log); logs com rotação, sem credenciais nem conteúdo do pedido; versões do Python e das bibliotecas documentadas; 19 testes da lógica local; Dockerfile e execução real no Devel LLM Portal; validação em ambiente limpo registrada no README.

As tags foram criadas depois do desenvolvimento, sobre os commits que reúnem as entregas de cada nível. O histórico de commits é a evidência da construção.

## Decisões principais

| Decisão | Alternativa considerada | Justificativa |
|---|---|---|
| Chamada HTTP direta com `requests`, isolada em `llm_client.py` | Usar uma biblioteca cliente específica do servidor do LLM | O curso pede cliente HTTP isolado; o código fica simples e a chamada pode ser simulada nos testes |
| Testes com integração simulada (`requests-mock`) | Chamar o LLM real nos testes | Sem custo de tokens, repetível, e o LLM não é acessível fora da plataforma |
| Executar a chamada real como container no portal, com o pedido na variável `PEDIDO` | Rodar apenas localmente, com `input()` | O servidor do LLM só responde dentro do ambiente da plataforma, e o portal não oferece terminal interativo |
| Enviar `think: false` na requisição | Apenas aumentar `LLM_MAX_TOKENS` | O raciocínio do modelo consome tokens e tempo sem ser necessário para preencher seis campos |

## Testes e resultados

Os 19 testes automatizados (`python -m pytest -v`) usam integração simulada. As três últimas linhas são execuções reais.

| Teste | Entrada ou situação | Resultado esperado | Resultado obtido |
|---|---|---|---|
| Sucesso | LLM responde HTTP 200 com o texto da ficha | Retorna a ficha | Passou |
| Pedido vazio | Pedido só com espaços | Erro "O pedido não pode estar vazio." | Passou |
| Credencial inválida | HTTP 401 | Mensagem de credencial ausente ou inválida | Passou |
| Segredo no erro | Chave configurada e HTTP 401 | A chave não aparece na mensagem | Passou |
| LLM indisponível | HTTP 503 | Mensagem de indisponibilidade | Passou |
| Timeout | Requisição excede o tempo limite | Mensagem de timeout | Passou |
| Falha de comunicação | Exceção genérica de rede | Mensagem de falha de comunicação | Passou |
| Resposta vazia | Conteúdo vazio, com ou sem campo de raciocínio | Mensagem específica, sem traceback | Passou |
| Modelo não encontrado | HTTP 404 | Mensagem com o modelo e a lista de modelos do servidor | Passou |
| Configuração inválida | Sem `LLM_BASE_URL`; `LLM_MAX_TOKENS=abc` | Erro de configuração com mensagem clara | Passou |
| Prompt com formato fixo | `criar_prompt(pedido)` | Contém os seis campos da ficha | Passou |
| Execução local, sem acesso ao LLM | Endereço de exemplo | Erro claro, sem traceback | "Falha na comunicação com o LLM. Verifique LLM_BASE_URL." |
| Execução real no portal | "Placa de acrilico 60x40 para a empresa Alfa, entrega sexta" | Ficha com seis campos | Ficha gerada (122 caracteres, 101,1 s) |
| Ambiente limpo | ZIP da branch `dev`, novo `.venv`, `pytest` | Todos os testes passam | 19 passaram em 0,45 s |

## Falhas e limitações

| Problema | Como foi identificado | Como foi tratado | Situação |
|---|---|---|---|
| HTTP 404 na primeira chamada real | Log do portal: "Erro inesperado do LLM (HTTP 404)" | Uso do nome exato `qwen3.5:9b`; a mensagem de erro passou a listar os modelos do servidor | Corrigido |
| Resposta vazia | Log do portal: "O LLM retornou uma resposta vazia" | `think: false`, prompt com formato definido e tratamento específico | Corrigido; não isolei qual das alterações resolveu |
| Log sem informação durante a espera | Log do portal com apenas duas linhas | Log também no terminal, aviso a cada 30 s e registro dos tempos informados pelo servidor | Corrigido |
| Lentidão da primeira chamada | Tempos no log: 101,1 s no total, 98,6 s só de carga do modelo, 1,3 s de geração | Timeout de 300 s e consulta de modelos opcional (economiza cerca de 15 s) | **Permanece:** a carga do modelo depende do servidor compartilhado |
| Limitações de escopo | — | — | **Permanecem:** o LLM só é acessível dentro da plataforma; credencial ausente e inválida foram demonstradas apenas com integração simulada, pois o serviço institucional não exigiu credencial; a validação em ambiente limpo foi feita por mim, e não por outra pessoa |

## Uso de IA no desenvolvimento

**Ferramenta:** Claude (Anthropic), em conversa de chat.

| Tarefa delegada | Resultado aproveitado | Correções ou alterações | Verificação |
|---|---|---|---|
| Estrutura do projeto, cliente HTTP, configuração e tratamento de erros | Base de `config.py`, `llm_client.py` e `app.py` | Um bloco colado ficou com indentação errada e o `payload` não era criado; corrigi substituindo o arquivo inteiro. Ajustei o nome do modelo para `qwen3.5:9b` e troquei o endereço real por um valor genérico no README e no `.env.example` | `pytest` e execução real |
| Testes com `requests-mock` | Os 19 testes | Casos adicionados depois das falhas reais (404, resposta vazia) | `pytest` e validação em ambiente limpo |
| Diagnóstico de falhas a partir dos logs do portal | Hipóteses (nome do modelo, raciocínio, carga do modelo) e instrumentação (tempos e aviso de espera) | Confirmei pelos tempos registrados no log da execução real | Execução no portal |
| Dockerfile e fluxo Git (branches, Pull Requests, tags, releases) | Comandos e modelos de texto | Escolhi os commits de cada tag conforme o histórico real; as tags foram criadas depois do desenvolvimento | `git log`, página de releases |
| README e este relatório | Rascunhos | Revisei e completei com dados reais de logs e prints | Conferência com logs, prints e histórico do Git |

## Reflexão final

**Principal aprendizado:** separar a chamada ao LLM da lógica do programa permite testar erros e respostas sem custo e sem acesso ao servidor, e os logs da execução real mostraram problemas (nome do modelo, resposta vazia, tempo de carga) que os testes simulados não mostrariam.

**Competência mais desenvolvida:** C03, integração com o serviço de LLM com tratamento de erros de comunicação, autenticação e resposta, sem expor informações sensíveis.

**Ponto a aprimorar:** autonomia no uso do terminal e do Git, e commitar e marcar as tags ao fim de cada nível, em vez de fazê-lo depois do desenvolvimento, para o histórico refletir melhor a evolução.
