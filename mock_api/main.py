from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta
from typing import Dict

# Importando nossos schemas
from mock_api.schemas import OrderResponse, OrderStatus, OrderItem, CancelResponse

app = FastAPI(title="iFood Legacy System Mock", version="1.0.0")

# --- BANCO DE DADOS MOCKADO (Simula o DB do iFood) ---
# Pedido 1: Tudo certo, entregue.
# Pedido 2: Atrasado e ainda preparando (cenário de reclamação).
# Pedido 3: Cancelado.

MOCK_DB: Dict[str, OrderResponse] = {
    "12345": OrderResponse(
        order_id="12345",
        customer_name="João da Silva",
        status=OrderStatus.DELIVERED,
        items=[
            OrderItem(item_name="Hambúrguer X-Tudo", quantity=1, price=35.90),
            OrderItem(item_name="Refrigerante", quantity=1, price=6.00)
        ],
        total_value=41.90,
        created_at=datetime.now() - timedelta(hours=2), # Pedido feito 2h atrás
        estimated_delivery=datetime.now() - timedelta(hours=1)
    ),
    "67890": OrderResponse(
        order_id="67890",
        customer_name="Maria Oliveira",
        status=OrderStatus.PREPARING, # Status problematico: Preparando há muito tempo
        items=[
            OrderItem(item_name="Pizza Calabresa", quantity=1, price=65.00)
        ],
        total_value=65.00,
        created_at=datetime.now() - timedelta(minutes=90), # Pedido feito 90min atrás
        estimated_delivery=datetime.now() - timedelta(minutes=30) # Atrasado
    )
}

@app.get("/")
def read_root():
    return {"message": "API do Sistema Legado iFood está online"}

# Endpoint que o Agente vai consultar
@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order_details(order_id: str):
    """
    Retorna os detalhes de um pedido específico.
    Simula uma consulta ao banco de dados SQL do sistema legado.
    """
    order = MOCK_DB.get(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    return order

@app.post("/orders/{order_id}/cancel", response_model=CancelResponse)
def cancel_order(order_id: str):
    """
    Simula o cancelamento. 
    O Agente vai usar essa função quando o cliente pedir para cancelar.
    """
    # 1. Busca o pedido na "memória"
    order = MOCK_DB.get(order_id)
    
    # 2. Se não existir, erro 404
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    # 3. REGRA DE NEGÓCIO: Não cancelamos pedido entregue!
    # Se tentarem, devolvemos erro 400 (Bad Request)
    if order.status == OrderStatus.DELIVERED:
        raise HTTPException(
            status_code=400, 
            detail="Não é possível cancelar. O pedido já foi entregue."
        )
    
    # 4. Se passou pelas regras, aplica a mudança de estado
    order.status = OrderStatus.CANCELLED
    
    # 5. Retorna a confirmação bonitinha
    return CancelResponse(
        order_id=order.order_id,
        status=order.status,
        message="Pedido cancelado com sucesso."
    )