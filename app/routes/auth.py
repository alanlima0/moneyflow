# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from ..schemas.token_schema import Token, LoginRequest
from ..services.user_service import UserService
from dependencies.user import get_user_service
from ..utils.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.exceptions import InvalidCredentialsError, DatabaseError
import logging

router = APIRouter(tags=["auth"])

@router.post("/token", response_model=Token)
async def login_for_access_token(
    credentials: LoginRequest, 
    user_service: UserService = Depends(get_user_service)
):
    '''
    Endpoint de autenticação que gera tokens JWT para usuários válidos.

    Args:
        credentials (LoginRequest): Objeto contendo username e password.
        user_service (UserService): Serviço injetado para validação de usuários.

    Returns:
        Token: Objeto contendo access_token e token_type.

    Raises:
        HTTPException: 
            - 401 Unauthorized para credenciais inválidas
            - 500 Internal Server Error para erros de banco de dados

    Examples:
        >>> Request (JSON):
        {
            "username": "usuario123",
            "password": "senhaSegura123"
        }
        
        >>> Response (Success):
        {
            "access_token": "eyJhbGciOi...",
            "token_type": "bearer"
        }
        
        >>> Response (Error - Credenciais):
        {
            "detail": "Usuário não encontrado"
        }
        ou
        {
            "detail": "Senha incorreta"
        }
        
        >>> Response (Error - Banco de dados):
        {
            "detail": "Erro interno no servidor"
        }
    '''
    try:
        # Autentica o usuário (pode lançar InvalidCredentialsError ou DatabaseError)
        user = await user_service.authenticate_user(credentials.username, credentials.password)
        
        # Cria o token JWT
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires,
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    except InvalidCredentialsError as e:
        # Captura erros específicos de autenticação
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),  # Usa a mensagem original do erro
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    except DatabaseError as e:
        # Log detalhado do erro no servidor
        logging.error(f"Erro de banco de dados durante autenticação: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor",
        )
    
    except Exception as e:
        # Captura qualquer outro erro inesperado
        logging.critical(f"Erro inesperado durante autenticação: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor",
        )
# async def login_for_access_token(
#     credentials: LoginRequest, 
#     user_service: UserService = Depends(get_user_service)
# ):
#     '''
#     Endpoint de autenticação que gera tokens JWT para usuários válidos.

#     Args:
#         credentials (LoginRequest): Objeto contendo username e password.
#         user_service (UserService): Serviço injetado para validação de usuários.

#     Returns:
#         Token: Objeto contendo access_token e token_type.

#     Raises:
#         HTTPException: 401 Unauthorized se as credenciais forem inválidas.

#     Examples:
#         >>> Request (JSON):
#         {
#             "username": "usuario123",
#             "password": "senhaSegura123"
#         }
        
#         >>> Response (Success):
#         {
#             "access_token": "eyJhbGciOi...",
#             "token_type": "bearer"
#         }
        
#         >>> Response (Error):
#         {
#             "detail": "Usuário ou senha incorretos"
#         }
#     '''
#     # Autentica o usuário
#     user = await user_service.authenticate_user(credentials.username, credentials.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Usuário ou senha incorretos",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     # Cria o token JWT (expira em 30 minutos por padrão)
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username},  # "sub" é o subject padrão do JWT
#         expires_delta=access_token_expires,
#     )
    
#     return {"access_token": access_token, "token_type": "bearer"}