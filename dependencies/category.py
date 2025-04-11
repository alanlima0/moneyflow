from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from app.services.category_service import CategoryService

async def get_category_service(db: AsyncSession = Depends(get_db)):
    return CategoryService(db)