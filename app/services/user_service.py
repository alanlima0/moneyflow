from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate, UserResponse
from typing import Optional, Tuple, Dict, Any, List
from app.models.user_model import User
from app.utils.auth import verify_password, get_hash_password
from app.exceptions import UserAlreadyExistsError, InvalidCredentialsError, DatabaseError
import logging
from typing import Optional

class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        """
        Inicializa o serviço de usuário com o repositório injetado.
        
        Args:
            user_repository: Instância do UserRepository para operações de banco de dados
        """
        self.user_repository = user_repository

    async def create_user(self, user: UserCreate) -> Optional[User]:
        """
        Cria um novo usuário no sistema com validações.
        
        Args:
            user: Dados do usuário a ser criado (username, email, password)
            
        Returns:
            User: Objeto do usuário criado
            None: Em caso de erro não tratado
            
        Raises:
            UserAlreadyExistsError: Se username ou email já estiverem cadastrados
            DatabaseError: Para erros inesperados no banco de dados
            
        Processo:
            1. Verifica se usuário já existe por username/email
            2. Se não existir, cria o novo usuário
            3. Retorna o usuário criado ou None em caso de falha
        """
        try:
            # Verificação de existência prévia (username ou email)
            if await self.user_repository.verify_user_existence(user.username, user.email):
                raise UserAlreadyExistsError("Usuário já cadastrado")

            # Verificações individuais para logs mais específicos
            if await self.user_repository.get_user_by_username(user.username):
                raise UserAlreadyExistsError("Username já cadastrado")

            if await self.user_repository.get_user_by_email(user.email):
                raise UserAlreadyExistsError("Email já cadastrado")

            # Criação efetiva do usuário
            return await self.user_repository.create_user(user)

        except UserAlreadyExistsError:
            # Exceção específica - não capturamos para propagar ao controller
            raise
        except Exception as e:
            logging.error(f"Erro inesperado ao criar usuário: {str(e)}", exc_info=True)
            raise DatabaseError("Erro ao criar usuário")

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Autentica um usuário com credenciais.
        
        Args:
            username: Nome de usuário para login
            password: Senha para verificação
            
        Returns:
            User: Objeto do usuário autenticado
            None: Se autenticação falhar
            
        Raises:
            InvalidCredentialsError: Para credenciais inválidas
            DatabaseError: Para erros inesperados
            
        Processo:
            1. Busca usuário pelo username
            2. Verifica senha com hash
            3. Retorna usuário se credenciais válidas
        """
        try:
            # Busca usuário no banco de dados
            user = await self.user_repository.get_user_by_username(username)
            if not user:
                raise InvalidCredentialsError("Usuário não encontrado")
            
            # Verificação de senha com bcrypt
            if not verify_password(password, user.hashed_password):
                raise InvalidCredentialsError("Senha incorreta")
            
            return user

        except InvalidCredentialsError:
            # Exceção específica para credenciais inválidas
            raise
        except Exception as e:
            logging.error(f"Erro inesperado ao autenticar: {str(e)}", exc_info=True)
            raise DatabaseError("Erro ao autenticar usuário")