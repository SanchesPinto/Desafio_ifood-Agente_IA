import requests
from langchain_core.tools import tool
from agente.rag import get_retriever

# URL da nossa API Mockada (Fase 1)
API_BASE_URL = "http://127.0.0.1:8000"

@tool
def consultar_pedido(order_id: str):
    """
    Consulta os detalhes técnicos de um pedido (status, itens, valor) no sistema legado.
    Use esta ferramenta SEMPRE que precisar saber o status ou dados de um pedido.
    """
    try:
        response = requests.get(f"{API_BASE_URL}/orders/{order_id}")
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {"erro": "Pedido não encontrado no sistema."}
        else:
            return {"erro": f"Erro técnico na API: {response.status_code}"}
    except Exception as e:
        return {"erro": f"Falha de conexão com o sistema de pedidos: {str(e)}"}

@tool
def cancelar_pedido(order_id: str):
    """
    Realiza o cancelamento efetivo de um pedido no sistema.
    Use esta ferramenta APENAS quando o cliente solicitar explicitamente o cancelamento
    E você já tiver verificado nas políticas que é permitido.
    """
    try:
        response = requests.post(f"{API_BASE_URL}/orders/{order_id}/cancel")
        if response.status_code == 200:
            return response.json()
        else:
            # Retorna o erro da API (ex: "Não pode cancelar pedido entregue")
            return response.json() 
    except Exception as e:
        return {"erro": f"Falha ao tentar cancelar: {str(e)}"}

@tool
def consultar_politicas(duvida: str):
    """
    Pesquisa na Base de Conhecimento (Políticas de Reembolso e Cancelamento).
    Use esta ferramenta para saber SE um reembolso é permitido ou quais são as regras.
    """
    retriever = get_retriever()
    # O retriever retorna documentos, vamos converter para texto simples para o LLM ler
    docs = retriever.invoke(duvida)
    contexto = "\n\n".join([doc.page_content for doc in docs])
    
    if not contexto:
        return "Não encontrei políticas específicas sobre isso."
    
    return contexto