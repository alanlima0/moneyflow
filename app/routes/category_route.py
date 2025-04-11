from fastapi import APIRouter, Depends, HTTPException, status, Response
from app.schemas.category_schema import CategoryResponse
from app.repositories.category_repository import CategoryRepository
from app.services.category_service import CategoryService
from app.exceptions import DatabaseError
from app.services.category_service import CategoryService
from dependencies.category import get_category_service
from typing import List
import logging

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)

@router.get("/")
async def get_categories(category_service: CategoryService = Depends(get_category_service)):
    return await category_service.get_all_categories()