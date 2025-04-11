from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from app.models.category_model import Category
from app.schemas.category_schema import CategoryType
from typing import Optional, List
from app.exceptions import (
   DatabaseError
)
import logging
logger = logging.getLogger(__name__)

class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_category(self, category_id: int) -> Optional[Category]:
        """
        Obtém uma categoria pelo ID
        
        Args:
            category_id: ID da categoria
            
        Returns:
            Objeto Category ou None se não encontrado
            
        Raises:
            DatabaseOperationError: Em caso de falha na operação
        """
        try:
            result = await self.db.execute(
                select(Category).where(Category.id == category_id))
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Erro ao buscar categoria: {str(e)}", exc_info=True)
            raise DatabaseError("Falha ao buscar categoria")

    async def get_type(self, category_id: int) -> CategoryType:
        """
        Obtém o tipo de uma categoria pelo ID
        
        Args:
            category_id: ID da categoria a ser consultada
            
        Returns:
            O tipo da categoria (EXPENSE ou INCOME)
            
        Raises:
            ValueError: Se a categoria não for encontrada
            DatabaseError: Em caso de erro no banco de dados
        """
        try:
            # Executa a query de forma assíncrona
            result = await self.db.execute(
                select(Category.type).where(Category.id == category_id)
            )
            
            # Obtém o tipo diretamente (ou None se não existir)
            category_type = result.scalar_one_or_none()
            
            if category_type is None:
                raise ValueError(f"Categoria com ID {category_id} não encontrada")
                
            # Converte para o Enum CategoryType para garantir type safety
            return CategoryType(category_type)
            
        except ValueError as e:
            # Já tratamos o caso de categoria não encontrada acima
            raise
        except SQLAlchemyError as e:
            logging.error(f"Erro de banco de dados ao buscar categoria: {str(e)}")
            raise DatabaseError("Falha ao acessar o banco de dados") from e
        except Exception as e:
            logging.error(f"Erro inesperado ao buscar tipo da categoria: {str(e)}")
            raise
        


    async def get_all_categories(self) -> List[Category]:
            """
            Retorna TODAS as categorias cadastradas no banco de dados.
            
            Returns:
                List[Category]: Lista de categorias (vazia se não houver registros).
                
            Raises:
                DatabaseError: Se ocorrer um erro ao acessar o banco.
            """
            try:
                result = await self.db.execute(select(Category))
                return result.scalars().all()
            except SQLAlchemyError as e:
                logger.error(f"Erro ao buscar categorias: {str(e)}", exc_info=True)
                raise DatabaseError("Falha ao carregar categorias")