from fastapi import APIRouter, Depends, HTTPException, status
from app.services.user_service import UserService, UserCreate, UserResponse
from app.exceptions import UserAlreadyExistsError, InvalidCredentialsError, DatabaseError
from dependencies.user import get_user_service
from dependencies.auth import get_current_user

router = APIRouter()

@router.post("/users", response_model=UserResponse)
async def create_user( user: UserCreate,
    user_service: UserService = Depends(get_user_service)):
    try:
        return await user_service.create_user(user)
    except UserAlreadyExistsError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/users/{username}", response_model=UserResponse)
async def read_user(
    username: str,
    user_service: UserService = Depends(get_user_service)  # Injeção do UserService
):
    """Rota para buscar um usuário pelo nome de usuário."""
    try:
        db_user = await user_service.get_user_by_username(username)  # Chamada assíncrona
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user
    except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))