from fastapi import Depends
from sqlalchemy.orm import Session
from database.database import get_db
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.account_repository import AccountRepository
from app.services.transaction_service import TransactionService


def get_transaction_service(db: Session = Depends(get_db)):
    """Retorna uma instância do TransactionService."""
    transaction_repository = TransactionRepository(db)
    category_repo = CategoryRepository(db)
    account_repo =AccountRepository(db)
    return TransactionService(transaction_repository, category_repo, account_repo)