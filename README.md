# 🍔 iFood GenAI Agent POC (RAG & Tool Calling)

> **Prova de Conceito (POC)** de um agente autônomo para auxiliar na tomada de decisão de reembolsos e cancelamentos, combinando Inteligência Artificial Generativa com validações transacionais rígidas.

## 🎯 Objetivo do Projeto

Simular um agente de suporte interno capaz de:
1.  **Consultar Políticas (RAG):** Buscar regras oficiais em uma base de conhecimento (CSV) para responder dúvidas sobre prazos e elegibilidade.
2.  **Executar Ações Seguras:** Consultar status reais de pedidos e realizar cancelamentos apenas quando permitido pelas regras de negócio.
3.  **Prevenir Alucinações:** Utilizar uma camada de validação ("Guardrails") que impede a IA de cancelar pedidos já entregues ou realizar ações em cenários de fraude.

## 🏗️ Arquitetura Híbrida

O projeto utiliza uma abordagem **"Backend for Frontend" (BFF)** para IA:

1.  **Cérebro (Flowise):** Orquestrador No-Code rodando em Docker. Gerencia o fluxo da conversa, memória e decisão do LLM (OpenAI GPT-4o-mini).
2.  **Músculos (Middleware Python):** Uma API em **FastAPI** que expõe ferramentas locais para o Flowise consumir via HTTP:
    * `/tools/consultar-pedido`: Conecta ao sistema legado mockado.
    * `/tools/consultar-politicas`: Realiza busca semântica no **ChromaDB**.
    * `/tools/cancelar-pedido`: Executa a lógica transacional com validação de status.
3.  **Dados (Mock API):** Um servidor simulando o banco de dados transacional do iFood (Pedidos, Status, Itens).

##  Arquitetura de Segurança: Hard Logic vs Soft Logic

    O grande diferencial deste projeto é a separação clara entre a Intenção da IA e a Execução do Código. O agente não tem permissão direta de escrita no banco de dados; ele atua apenas como um orquestrador de intenções que são validadas por código determinístico.

**O Fluxo de "Double Check":**

    1. Soft Logic (LLM/Flowise):

        Analisa a conversa e o sentimento do usuário.

        Interpreta as políticas (RAG) para decidir se o pedido deveria ser cancelado.

        Exemplo: "O usuário está elegível para reembolso por atraso." -> Envia comando de cancelamento.

    2. Hard Logic (Python Middleware):

        Recebe a intenção de cancelamento da LLM.

        Validação Determinística: O código Python verifica o status real no banco de dados antes de agir.

        Bloqueio de Alucinação: Se a LLM tentar cancelar um pedido com status DELIVERED, a API rejeita a requisição e retorna um erro 400, independentemente da "vontade" da IA.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.11
* **Orquestração:** FlowiseAI (via Docker)
* **API Framework:** FastAPI (para o Middleware)
* **Vector Store:** ChromaDB (Local)
* **LLM Framework:** LangChain (para ingestão de dados)
* **Embeddings:** HuggingFace (`all-MiniLM-L6-v2`)

## 📂 Estrutura do Projeto

```bash
.
├── agente
│   ├── ferramentas.py   # Lógica das ferramentas (Tool Calling)
│   └── rag.py           # Ingestão e busca no ChromaDB
├── data
│   └── base_conhecimento.csv # Políticas de reembolso e fraude
├── mock_api
│   ├── main.py          # Simulação do Sistema Legado (SQL Mock)
│   └── schemas.py       # Contratos de dados (Pydantic)
├── middleware.py        # API que conecta o Flowise ao Python
├── requirements.txt     # Dependências Python
└── README.md
```

## 🚀 Como Executar

O projeto roda em 3 terminais simultâneos para simular a arquitetura de microsserviços.
Pré-requisitos

    Python 3.11+

    Docker (para o Flowise)

    Chave de API OpenAI (configurada no Flowise)

**Passo 1:** Iniciar o Sistema Legado (Mock API)

    Simula o banco de dados de pedidos do iFood.

    Bash
    uvicorn mock_api.main:app --reload --port 8000

**Passo 2:** Iniciar o Middleware de IA

    Expõe as ferramentas de RAG e Cancelamento para o orquestrador.

    Bash
    python middleware.py

    Roda na porta 8001

**Passo 3:** Iniciar o Orquestrador (Flowise)
    
    importe o arquivo flowise_flows/test_desafio_Ifood Chatflow no seu painel Flowise.

    Bash
    docker run -d --name flowise -p 3000:3000 flowiseai/flowise

    Acesse http://localhost:3000 e importe o fluxo do agente.


## ✅ Casos de Uso Validados

O agente foi submetido a testes de estresse para garantir conformidade:
    Recusa o cancelamento baseando-se no status DELIVERED retornado pela API.
    Identifica a política de Reembolso Automático e executa o cancelamento.
    Identifica padrão de múltiplos reembolsos e nega ação, sugerindo suporte humano.
    Responde "Não sei" para perguntas sobre as quais não possui nenhuma informação na base de dados (Fallback).


## Projeto desenvolvido como Prova de Conceito (POC) para portfólio de Engenharia de IA.