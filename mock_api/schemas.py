from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

# Enum para garantir que o status seja sempre consistente
class OrderStatus(str, Enum):
    PREPARING = "PREPARANDO"
    IN_TRANSIT = "EM_ROTA"
    DELIVERED = "ENTREGUE"
    CANCELLED = "CANCELADO"

# Modelo de um item do pedido (ex: Hamburguer, Refri)
class OrderItem(BaseModel):
    item_name: str
    quantity: int
    price: float

# O Modelo principal do Pedido
class OrderResponse(BaseModel):
    order_id: str
    customer_name: str
    status: OrderStatus
    items: List[OrderItem]
    total_value: float
    created_at: datetime
    # Campo opcional: simular atraso pode ser útil para o agente pedir desculpas
    estimated_delivery: datetime

class CancelResponse(BaseModel):
    order_id: str
    status: str
    message: str