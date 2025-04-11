from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.exc import SQLAlchemyError  
from app.models.account_model import Account
from typing import Optional, List
import logging 
logger = logging.getLogger(__name__)
class AccountRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, account_id: int, for_update: bool = False) -> Optional[Account]:
        """Busca conta por ID com opção de FOR UPDATE"""
        try:
            stmt = select(Account).where(Account.id == account_id)
            if for_update:
                stmt = stmt.with_for_update()
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Erro ao buscar conta {account_id}: {e}")
            raise

    async def create(self, account: dict) -> Optional[Account]:
        """Cria uma conta que pode ser de débito ou crédito"""
        try:
            db_account = Account(**account)
            self.db.add(db_account)
            await self.db.commit()
            await self.db.refresh(db_account)
            return db_account
        except SQLAlchemyError as e:  
            await self.db.rollback()
            logging.error(f"Erro ao criar conta: {e}")
            raise

    async def update(self, account_id: int, update_data: dict) -> Optional[Account]:
        """Atualiza a conta de um User"""
        try:
            # Usa get_by_id com for_update para garantir consistência
            db_account = await self.get_by_id(account_id, for_update=True)
            if not db_account:
                return None
        
            for key, value in update_data.items():
                setattr(db_account, key, value)
                
            await self.db.commit()
            await self.db.refresh(db_account)
            return db_account
        except SQLAlchemyError as e:
            await self.db.rollback()
            logging.error(f"Erro ao atualizar conta {account_id}: {e}")
            raise

    async def delete(self, account_id: int) -> bool:
        """Deleta a Conta de um User"""
        try:
            # Verifica existência da conta primeiro
            account = await self.get_by_id(account_id, for_update=True)
            if not account:
                return False
                
            await self.db.delete(account)
            await self.db.commit()
            return True
        except SQLAlchemyError as e:
            await self.db.rollback()
            logging.error(f"Erro ao deletar conta {account_id}: {e}")
            raise

    async def get_by_name_and_user(self, name: str, user_id: int) -> Optional[Account]:
        """Retorna uma conta com nome e user fornecidos"""
        try:
            result = await self.db.execute(
                select(Account)
                .where(Account.name == name)
                .where(Account.user_id == user_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logging.error(f"Erro ao buscar conta por nome: {e}")
            raise

    async def get_all_by_user(self, user_id: int) -> List[Account]:
        """Retorna todas as contas referentes a um User"""
        try:
            result = await self.db.execute(
                select(Account)
                .where(Account.user_id == user_id)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logging.error(f"Erro ao buscar contas do usuário {user_id}: {e}")
            raise

    async def get_by_id_and_user(self, account_id: int, user_id: int) -> Optional[Account]:
        """Retorna uma conta com ID e user fornecidos"""
        try:
            result = await self.db.execute(
                select(Account)
                .where(Account.id == account_id)
                .where(Account.user_id == user_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logging.error(f"Erro ao buscar conta {account_id} do usuário {user_id}: {e}")
            raise


    async def save(self, account: Account) -> None:
        """Persiste as alterações de uma conta existente"""
        try:
            await self.db.commit()
            await self.db.refresh(account)
        except SQLAlchemyError as e:
            await self.db.rollback()
            logging.error(f"Erro ao salvar conta {account.id}: {e}")
            raise