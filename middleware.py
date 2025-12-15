# Arquivo: middleware.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager

# Importando suas ferramentas existentes
from agente.ferramentas import consultar_pedido, cancelar_pedido, consultar_politicas
from agente.rag import get_embeddings_model

# --- Configuração de Ciclo de Vida ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Inicializando Middleware de IA...")
    # Garante que o modelo de embeddings esteja na memória
    get_embeddings_model()
    yield
    print("🛑 Desligando Middleware...")

app = FastAPI(title="Middleware iFood AI Tools", lifespan=lifespan)

# --- Modelos de Entrada ---
class PedidoInput(BaseModel):
    order_id: str

class PoliticaInput(BaseModel):
    duvida: str

# --- Endpoints ---

@app.get("/")
def health_check():
    return {"status": "online", "service": "Middleware AI Tools"}

@app.post("/tools/consultar-pedido")
def endpoint_consultar_pedido(dados: PedidoInput):
    """
    Wrapper para consultar_pedido.
    Usa .invoke() pois é uma LangChain Tool.
    """
    resultado = consultar_pedido.invoke({"order_id": dados.order_id})
    return resultado

@app.post("/tools/cancelar-pedido")
def endpoint_cancelar_pedido(dados: PedidoInput):
    """
    Wrapper para cancelar_pedido.
    """
    resultado = cancelar_pedido.invoke({"order_id": dados.order_id})
    return resultado

@app.post("/tools/consultar-politicas")
def endpoint_consultar_politicas(dados: PoliticaInput):
    """
    Wrapper para o RAG.
    """
    # O nome da chave "duvida" deve bater com o argumento na função em ferramentas.py
    resposta_texto = consultar_politicas.invoke({"duvida": dados.duvida})
    
    return {
        "contexto_encontrado": resposta_texto
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)