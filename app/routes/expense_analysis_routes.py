from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.expense_analysis_service import ExpenseAnalysisService
from app.models.user_model import User
from database.database import get_db
from dependencies.auth import get_current_user
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(
    prefix="/api/analytics", 
    tags=["analytics"],
    dependencies=[Depends(get_current_user)]
)

# Modelos Pydantic
class CategoryExpense(BaseModel):
    category_id: Optional[int]
    category_name: str
    total_amount: float
    transaction_count: int
    percentage: float

class ExpensesByCategoryResponse(BaseModel):
    total_expenses: float
    categories: List[CategoryExpense]
    alerts: List[str] = []

@router.get("/expenses-by-category/{account_id}", response_model=ExpensesByCategoryResponse)
async def get_expenses_by_category(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna análise de despesas por categoria para uma conta específica do usuário.
    
    Parameters:
    - account_id: ID da conta a ser analisada (obrigatório, como parte do caminho da URL)
    """
    try:
        service = ExpenseAnalysisService(db)
        result = await service.get_expenses_by_category(
            user_id=current_user.id,
            account_id=account_id
        )
        
        if not result["categories"]:
            raise HTTPException(
                status_code=404,
                detail="Nenhuma transação de despesa encontrada para esta conta"
            )
            
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar análise: {str(e)}"
        )