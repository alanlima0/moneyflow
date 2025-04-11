from decimal import Decimal, InvalidOperation
from typing import List, Optional
from app.exceptions import (
    AccountValidationError,
    AccountNotFoundError,
    DuplicateAccountError,
    CreditAccountError,
    DebitAccountError,
    DatabaseIntegrityError,
    AccountOperationError, 
    AccountOwnershipError
)
from app.schemas.account_schema import AccountCreate, AccountUpdate
from app.models.account_model import Account
from app.repositories.account_repository import AccountRepository
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class AccountService:
    def __init__(self, account_repository: AccountRepository):
        """Inicializa o serviço com o repositório de contas"""
        self.repository = account_repository

    async def create_account(self, account_data: AccountCreate, user_id: int) -> Account:
        """
        Cria uma nova conta bancária com validações robustas
        
        Args:
            account_data: Dados da conta a ser criada
            user_id: ID do usuário dono da conta
            
        Returns:
            Account: Objeto da conta criada
            
        Raises:
            DuplicateAccountError: Se já existir conta com mesmo nome para o usuário
            CreditAccountError: Se validações de conta crédito falharem
            DebitAccountError: Se validações de conta débito falharem  
            DatabaseIntegrityError: Se ocorrer erro de integridade no banco
            AccountOperationError: Para erros inesperados na operação
        """
        try:
            # Verificação de nome duplicado para o usuário
            if await self.repository.get_by_name_and_user(account_data.name, user_id):
                raise DuplicateAccountError("Já existe uma conta com este nome")

            account_dict = account_data.model_dump()
            account_dict["user_id"] = user_id

            # --- Validações específicas para contas de crédito ---
            if account_data.is_credit:
                if not account_data.credit_limit:
                    raise CreditAccountError("Contas de crédito requerem um limite")
                
                if account_data.balance is not None:
                    raise CreditAccountError("Contas de crédito não podem ter saldo inicial")
                
                if account_data.due_day is None:
                    raise CreditAccountError("Dia de vencimento é obrigatório para contas de crédito")
                
                if not isinstance(account_data.due_day, int) or not (1 <= account_data.due_day <= 31):
                    raise CreditAccountError("Dia de vencimento deve ser um número entre 1 e 31")
                
                # Garante que saldo seja None para crédito
                account_dict["balance"] = None

            # --- Validações específicas para contas de débito ---
            else:
                if account_data.credit_limit or account_data.due_day:
                    raise DebitAccountError("Contas de débito não podem ter limite ou dia de vencimento")
                
                if account_data.balance is None:
                    raise DebitAccountError("Contas de débito precisam de saldo inicial")
                
                # Remove campos específicos de crédito
                account_dict["credit_limit"] = None
                account_dict["due_day"] = None

            # Persiste a conta no banco de dados
            return await self.repository.create(account_dict)

        except (DuplicateAccountError, 
           CreditAccountError, 
           DebitAccountError,
           ValueError) as e:
        # Propaga erros de negócio sem modificação
            raise
        
        except IntegrityError as e:
            logger.error(f"Erro de integridade: {str(e)}", exc_info=True)
            raise DatabaseIntegrityError("Violação de regras do banco de dados")
            
        except Exception as e:
            logger.critical(f"Erro inesperado: {str(e)}", exc_info=True)
            raise AccountOperationError("Falha crítica ao criar conta")

    async def update_account(self, account_id: int, update_data: AccountUpdate) -> Account:
        """
        Atualiza os dados de uma conta existente com validação completa
        
        Args:
            account_id: ID da conta a ser atualizada
            update_data: Dados para atualização
            
        Returns:
            Account: Conta atualizada
            
        Raises:
            AccountNotFoundError: Se conta não existir
            AccountOperationError: Para erros na operação
        """
        try:
            # 1. Obtém a conta do banco de dados
            account = await self.repository.get_by_id(account_id)
            if not account:
                raise AccountNotFoundError("Conta não encontrada")

            # 2. Validação adicional baseada no tipo de conta real
            update_dict = update_data.model_dump(exclude_unset=True)
            
            # 2.1 Verifica se está tentando alterar o tipo da conta
            if "is_credit" in update_dict:
                raise AccountOperationError("Mudança de tipo de conta não é permitida")

            # 2.2 Valida campos específicos por tipo de conta
            if account.is_credit:
                if "balance" in update_dict:
                    raise AccountOperationError("Contas de crédito não podem ter saldo")
            else:
                if "credit_limit" in update_dict or "due_day" in update_dict:
                    raise AccountOperationError("Contas de débito não podem ter limite ou dia de vencimento")

            # 3. Aplica as atualizações válidas
            return await self.repository.update(account_id, update_dict)
            
        except AccountNotFoundError:
            raise
        except AccountOperationError as e:
            logger.warning(f"Tentativa de operação inválida: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro ao atualizar conta: {str(e)}")
            raise AccountOperationError("Erro ao atualizar conta")\
            
    async def delete_account(self, account_id: int, user_id: int) -> bool:
        """
        Remove uma conta do sistema após verificar propriedade
        
        Args:
            account_id: ID da conta a ser removida
            user_id: ID do usuário solicitante
            
        Returns:
            bool: True se exclusão foi bem-sucedida
            
        Raises:
            AccountOwnershipError: Se conta não pertencer ao usuário
            AccountOperationError: Para erros na operação
        """
        try:
            # Verifica se conta pertence ao usuário
            account = await self.repository.get_by_id_and_user(account_id, user_id)
            if not account:
                raise AccountOwnershipError("Conta não encontrada ou não pertence ao usuário")

            await self.repository.delete(account_id)
            return True
            
        except Exception as e:
            logger.error(f"Erro ao excluir conta: {str(e)}")
            raise AccountOperationError("Erro ao excluir conta")

    async def list_accounts(self, user_id: int) -> List[Account]:
        """
        Lista todas as contas de um usuário
        
        Args:
            user_id: ID do usuário dono das contas
            
        Returns:
            List[Account]: Lista de contas do usuário
            
        Raises:
            AccountOperationError: Para erros na operação
        """
        try:
            return await self.repository.get_all_by_user(user_id)
        except Exception as e:
            logger.error(f"Erro ao listar contas: {str(e)}")
            raise AccountOperationError("Erro ao listar contas")

    async def verify_ownership(self, account_id: int, user_id: int) -> bool:
        """
        Verifica se uma conta pertence a um usuário
        
        Args:
            account_id: ID da conta
            user_id: ID do usuário
            
        Returns:
            bool: True se conta pertence ao usuário
            
        Raises:
            AccountOperationError: Para erros na verificação
        """
        try:
            account = await self.repository.get_by_id_and_user(account_id, user_id)
            return account is not None
        except Exception as e:
            logger.error(f"Erro ao verificar propriedade: {str(e)}")
            raise AccountOperationError("Erro ao verificar propriedade da conta")
        

    async def get_account_by_id(self, account_id: int) -> Optional[Account]:
        """Obtém uma conta pelo ID"""
        try:
            return await self.repository.get_by_id(account_id)
        except SQLAlchemyError as e:
            logger.error(f"Erro ao buscar conta: {str(e)}")
            raise AccountOperationError("Erro ao buscar conta no banco de dados")