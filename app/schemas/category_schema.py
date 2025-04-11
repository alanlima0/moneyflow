from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
class CategoryType(str, Enum):
    EXPENSE = "EXPENSE"
    INCOME = "INCOME"

class CategoryBase(BaseModel):
    """Schema base com campos essenciais"""
    name: str = Field(..., max_length=50, example="Alimentação")
    type: CategoryType = Field(..., example="EXPENSE")


class CategoryCreate(CategoryBase):
    """Schema para criação de categorias (herda todos os campos do base)"""
    pass

class CategoryUpdate(BaseModel):
    """Schema para atualização parcial de categorias"""
    name: Optional[str] = Field(None, max_length=50, example="Transporte")
    type: Optional[CategoryType] = Field(None, example="EXPENSE")


class CategoryResponse(CategoryBase):
    """Schema de resposta incluindo ID gerado"""
    id: int = Field(..., example=1)
    
    class Config:
        from_attributes = True  # Permite conversão de ORM para Pydantic
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Alimentação",
                "type": "EXPENSE"
            }
        }