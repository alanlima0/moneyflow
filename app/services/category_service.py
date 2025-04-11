from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.category_repository import CategoryRepository

class CategoryService:
    def __init__(self, db: AsyncSession):  # Recebe a sessão diretamente
        self.repository = CategoryRepository(db)  # Passa a sessão para o repositório

    async def get_all_categories(self):
        return await self.repository.get_all_categories()