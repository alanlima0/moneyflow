from fastapi import APIRouter, Depends, HTTPException, status, Response
from app.services.account_service import AccountService
from app.schemas.account_schema import AccountResponse, AccountCreate, AccountUpdate
from dependencies.auth import get_current_user
from dependencies.account import get_account_service
from app.models.user_model import User
from app.exceptions import AccountNotFoundError, DebitAccountError, CreditAccountError, DuplicateAccountError, DatabaseIntegrityError, AccountOperationError
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
    dependencies=[Depends(get_current_user)]  
)

@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account: AccountCreate,
    account_service: AccountService = Depends(get_account_service),
    current_user: User = Depends(get_current_user)
):
    try:
        return await account_service.create_account(account, current_user.id)
    except DuplicateAccountError as e:
        logger.warning(f"Conta duplicada: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    except (CreditAccountError, DebitAccountError) as e:
        logger.warning(f"Regra de negócio violada: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
        
    except ValueError as e:
        logger.warning(f"Dados inválidos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    except DatabaseIntegrityError as e:
        logger.error(f"Erro de banco: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    except Exception as e:
        logger.critical(f"Erro crítico: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar conta"
        )


@router.get("", response_model=List[AccountResponse])
async def list_accounts_user(
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    try:
        return await account_service.list_accounts(current_user.id)
    except Exception as e:
        logger.error(f"Erro ao listar contas: {str(e)}", exc_info=True)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno")

@router.patch("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    update_data: AccountUpdate,
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    try:
        # Verifica propriedade da conta
        if not await account_service.verify_ownership(account_id, current_user.id):
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Acesso negado")
        
        # Executa a atualização com todas as validações
        return await account_service.update_account(account_id, update_data)
    
    except AccountNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Conta não encontrada")
    except AccountOperationError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao atualizar conta: {str(e)}", exc_info=True)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar atualização"
        )

@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    try:
        if not await account_service.verify_ownership(account_id, current_user.id):
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Acesso negado")
            
        success = await account_service.delete_account(account_id, current_user.id)
        if not success:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Conta não encontrada")
            
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except AccountOperationError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Erro ao excluir conta")
    except Exception as e:
        logger.error(f"Erro ao excluir conta: {str(e)}", exc_info=True)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno")
    


    
@router.get("/{account_id}/balance")
async def get_account_balance(
    account_id: int,
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Retorna o saldo da conta com verificação de propriedade"""
    try:
        # Verifica se o usuário é dono da conta
        if not await account_service.verify_ownership(account_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar esta conta"
            )
        
        # Pega a conta diretamente do service
        account = await account_service.get_account_by_id(account_id)
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conta não encontrada"
            )
        
        # Resposta direta e limpa
        return {
            "success": True,
            "balance": account.balance,
            "account_id": account.id,
            "account_name": account.name
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter saldo: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao obter saldo"
        )