from app.schemas.transaction_schema import TransactionBase, TransactionResponse, TransactionCreate, TransactionType, TransactionUpdate
from typing import Optional, Tuple, Dict, Any, List
from app.exceptions import UserAlreadyExistsError, InvalidCredentialsError, DatabaseError
from decimal import Decimal
from app.schemas.transaction_schema import TransactionCreate
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.account_repository import AccountRepository
from dependencies.account import get_account_service
from app.models.transaction_model import FinancialTransaction
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.exceptions import (
    InvalidCategoryError,
    InsufficientBalanceError,
    AccountNotFoundError,
    DatabaseError,
    TransactionNotFoundError, 
    AccountOperationError
)

import logging
logger = logging.getLogger(__name__)

class TransactionService:
    def __init__(self, transaction_repo: TransactionRepository,
    category_repo: CategoryRepository,
    account_repo: AccountRepository):
        """Inicializa o serviço com o repositório de contas"""
        self.transaction_repo = transaction_repo
        self.category_repo = category_repo
        self.account_repo = account_repo
        
    async def create_transaction(self, transaction_data: TransactionCreate, user_id: int) -> TransactionResponse:
        try:
            # 1. Validação da conta
            account = await self.account_repo.get_by_id_and_user(transaction_data.account_id, user_id)
            if not account:
                raise AccountNotFoundError("Conta não encontrada ou não pertence ao usuário")

            # 2. Lógica para contas de crédito
            if account.is_credit:
                available_credit = account.credit_limit - account.used_credit
                if transaction_data.amount > available_credit:
                    raise InsufficientBalanceError("Limite de crédito insuficiente")
                
                # Atualiza o crédito utilizado
                account.used_credit += transaction_data.amount
            else:
                # Lógica para contas normais
                if transaction_data.amount > account.balance:
                    raise InsufficientBalanceError("Saldo insuficiente")
                account.balance -= transaction_data.amount

            # 3. Criação da transação
            transaction_dict = transaction_data.model_dump()
            transaction_dict["user_id"] = user_id
            transaction = await self.transaction_repo.create_transaction(account.id, transaction_dict)

            # 4. Atualização da conta
            await self.account_repo.save(account)

            return TransactionResponse.model_validate(transaction)
        
        except (AccountNotFoundError, InsufficientBalanceError) as e:
            # Erros de negócio - apenas relançar
            logger.warning(f"Erro de negócio: {str(e)}")
            raise
            
        except ValueError as e:
            logger.error(f"Erro de validação: {str(e)}")
            raise AccountOperationError(str(e))
            
        except SQLAlchemyError as e:
            logger.error(f"Erro de banco de dados: {str(e)}", exc_info=True)
            raise DatabaseError("Falha ao processar transação")
            
        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
            raise DatabaseError("Erro interno no servidor")

    async def get_account_transactions(self, account_id: int) -> List[TransactionResponse]:
        try:
            if account_id <= 0:
                raise ValueError("ID da conta inválido")
                
            transactions = await self.transaction_repo.get_transactions_by_account(account_id)
            
            if not transactions:
                logger.info(f"Nenhuma transação encontrada para a conta {account_id}")
                
            return [TransactionResponse.model_validate(t) for t in transactions]
            
        except ValueError as e:
            logger.warning(str(e))
            raise TransactionNotFoundError(str(e))
        except DatabaseError as e:
            logger.error(f"Database error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            raise DatabaseError("Erro inesperado")