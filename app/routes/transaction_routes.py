from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.transaction_schema import TransactionCreate, TransactionResponse
from app.services.transaction_service import TransactionService
from dependencies.auth import get_current_user
from dependencies.transaction import get_transaction_service
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_model import User
from app.repositories.category_repository import CategoryRepository
from app.exceptions import (
    InvalidCategoryError,
    InsufficientBalanceError,
    AccountNotFoundError,
    DatabaseError, 
    TransactionNotFoundError
)
import logging

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    try:
        new_transaction = await transaction_service.create_transaction(
            transaction, 
            current_user.id
        )
        return new_transaction
    except InvalidCategoryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except InsufficientBalanceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except AccountNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no processamento da transação"
        )
    except Exception as e:
        logger.error(f"Erro não tratado: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )
    
@router.get("/{account_id}", response_model=list[TransactionResponse])
async def get_account_transactions(
    account_id: int,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    try:
        return await transaction_service.get_account_transactions(account_id)
        
    except TransactionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço indisponível"
        )
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno"
        )