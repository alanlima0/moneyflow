from datetime import date as _date
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum
from app.schemas.account_schema import AccountSimpleResponse
from app.schemas.category_schema import CategoryResponse

class TransactionType(str, Enum):
    """Tipo da transação (receita/despesa)"""
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"

class TransactionBase(BaseModel):
    """Campos básicos para transações"""
    amount: Decimal = Field(..., gt=0, description="Valor positivo (será convertido conforme tipo)")
    date: _date = Field(default_factory=_date.today)
    description: str = Field(..., max_length=100)
    account_id: int = Field(..., description="ID da conta vinculada")
    category_id: Optional[int] = None

    @validator('amount')
    def validate_amount(cls, v):
        """Garante valor absoluto na validação"""
        return abs(v)

class TransactionCreate(TransactionBase):
    """Dados para criar transação (com tipo explícito)"""
    transaction_type: TransactionType

    @validator('amount')
    def validate_amount_based_on_type(cls, v, values):
        """Ajusta sinal conforme tipo: negativo para despesas"""
        if 'type' in values and values['type'] == TransactionType.EXPENSE:
            return -abs(v)
        return abs(v)

class TransactionUpdate(BaseModel):
    """Dados parciais para atualizar transação"""
    amount: Optional[Decimal] = None
    date: Optional[_date] = None
    description: Optional[str] = None
    category_id: Optional[int] = None

class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    transaction_type: TransactionType  # Nome consistente
    account: AccountSimpleResponse
    category: Optional[CategoryResponse] = None

    class Config:
        from_attributes = True  # Permite conversão de ORM

# Resolve referências
TransactionResponse.update_forward_refs()