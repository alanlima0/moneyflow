from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.models.transaction_model import FinancialTransaction
from app.models.account_model import Account
from decimal import Decimal
from typing import List, Optional
from app.exceptions import (
   DatabaseError,
   TransactionNotFoundError
)
import logging

logger = logging.getLogger(__name__)

class TransactionRepository:
    def __init__(self, db: AsyncSession):
            self.db = db

    async def create_transaction(self, account_id: int, transaction_data: dict) -> FinancialTransaction:
        try:
            # Correção: Verifica se account_id é um inteiro válido
            if not isinstance(account_id, int) or account_id <= 0:
                raise ValueError("ID da conta inválido")

            # Correção: Busca a conta corretamente
            stmt = select(Account).where(Account.id == account_id)
            result = await self.db.execute(stmt)
            account = result.scalar_one_or_none()
            
            if not account:
                raise ValueError("Conta não encontrada")

            # Cria a transação
            new_transaction = FinancialTransaction(**transaction_data)
            self.db.add(new_transaction)
            
            await self.db.commit()
            await self.db.refresh(new_transaction)
            return new_transaction
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Erro de banco de dados: {str(e)}", exc_info=True)
            raise ValueError(f"Erro ao criar transação: {str(e)}")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
            raise

  
    async def get_transactions_by_account(self, account_id: int) -> List[FinancialTransaction]:
        try:
            result = await self.db.execute(
                select(FinancialTransaction)
                .where(FinancialTransaction.account_id == account_id)
            )
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Database error: {str(e)}", exc_info=True)
            raise DatabaseError("Erro ao buscar transações")