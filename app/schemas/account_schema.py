from pydantic import BaseModel, Field, field_validator, model_validator
from decimal import Decimal
from typing import Literal, Optional
from enum import Enum

class AccountType(str, Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

class AccountCreate(BaseModel):
    """
    Schema para criação de contas bancárias.
    
    Campos obrigatórios:
    - name: Nome da conta (2-50 caracteres)
    - is_credit: Define se é conta de crédito
    
    Campos condicionais:
    - credit_limit: Obrigatório para contas de crédito
    - due_day: Obrigatório para contas de crédito (1-31)
    """
    name: str = Field(..., min_length=2, max_length=50, example="Conta Corrente")
    is_credit: bool = Field(
        False,
        description="Define se é conta de crédito (default=False)"
    )
    credit_limit: Optional[Decimal] = Field(
        None,
        description="Limite de crédito (obrigatório para contas de crédito)"
    )
    due_day: Optional[int] = Field(
        None,
        ge=1,
        le=31,
        description="Dia de vencimento (1-31, obrigatório para contas de crédito)"
    )
    balance: Optional[Decimal] = Field(
        None,
        description = "Saldo da Conta"
    )


    @field_validator('due_day')
    def validate_due_day(cls, v, values):
        if values.data.get('is_credit') and v is None:
            raise ValueError("Dia de vencimento é obrigatório para contas de crédito")
        return v

   
class AccountResponse(BaseModel):
    id: int
    name: str
    is_credit: bool
    balance: Optional[Decimal] = Field(
        None, 
        description="Saldo (apenas para contas de débito)"
    )
    credit_limit: Optional[Decimal] = Field(
        None,
        description="Limite total (apenas para contas de crédito)"
    )
    used_credit: Optional[Decimal] = Field(
        None,
        description="Crédito utilizado (apenas para contas de crédito)"
    )
    due_day: Optional[int] = Field(
        None,
        description="Dia de vencimento (apenas para contas de crédito)"
    )
    user_id: int
    available_credit: Optional[Decimal] = Field(
        None,
        description="Crédito disponível (calculado automaticamente)"
    )

    @model_validator(mode='after')
    def calculate_available_credit(self):
        if self.is_credit:
            self.available_credit = self.credit_limit - self.used_credit
        return self


class AccountUpdate(BaseModel):
    """
    Schema para atualização de contas bancárias.
    - Campos permitidos são estritamente controlados pelo tipo da conta (is_credit).
    - Mudança de tipo (is_credit) NÃO é permitida em nenhum caso.
    """
    name: Optional[str] = Field(
        None, min_length=2, max_length=50,
        description="Novo nome para a conta (opcional)"
    )
    balance: Optional[Decimal] = Field(
        None,
        description="Novo saldo (apenas para contas débito)"
    )
    credit_limit: Optional[Decimal] = Field(
        None, ge=0,
        description="Novo limite (apenas para contas crédito)"
    )
    due_day: Optional[int] = Field(
        None, ge=1, le=31,
        description="Novo dia de vencimento (apenas para contas crédito)"
    )
    

class AccountSimpleResponse(BaseModel):
    """Resposta simplificada de conta (para relacionamentos)"""
    id: int = Field(..., example=1)
    is_credit: bool = Field(..., example=False)
    class Config:
        from_attributes = True  # Permite conversão de ORM para Pydantic