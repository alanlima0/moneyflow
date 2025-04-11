from decimal import Decimal
from typing import Dict, List
from sqlalchemy import select, func, case, and_
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.transaction_model import FinancialTransaction, TransactionType
from app.models.category_model import Category


class ExpenseAnalysisService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_expenses_by_category(self, user_id: int, account_id: int) -> dict:
        # Filtros base
        filters = [
            FinancialTransaction.user_id == user_id,
            FinancialTransaction.transaction_type == TransactionType.EXPENSE,
            FinancialTransaction.account_id == account_id  # Adicionado filtro por account_id
        ]

        # Query para total de despesas
        total_query = select(
            func.coalesce(func.sum(FinancialTransaction.amount), Decimal('0'))
        ).where(and_(*filters))
        
        total = (await self.db.execute(total_query)).scalar_one()
        total_abs = abs(total) if total else Decimal('0')

        # Query para categorias
        stmt = (
            select(
                FinancialTransaction.category_id,
                Category.name.label("category_name"),
                func.abs(func.sum(FinancialTransaction.amount)).label("total_amount"),
                func.count(FinancialTransaction.id).label("transaction_count")
            )
            .join(Category, FinancialTransaction.category_id == Category.id, isouter=True)
            .where(and_(*filters))
            .group_by(FinancialTransaction.category_id, Category.name)
        )

        result = await self.db.execute(stmt)
        categories = []
        
        for row in result:
            percentage = (abs(row.total_amount) / total_abs * 100) if total_abs > 0 else 0
            categories.append({
                "category_id": row.category_id,
                "category_name": row.category_name or "Sem Categoria",
                "total_amount": float(row.total_amount),
                "transaction_count": row.transaction_count,
                "percentage": float(percentage)
            })

        alerts = []
        if categories:
            maior_categoria = max(categories, key=lambda x: x["percentage"])
            
            if maior_categoria["percentage"] > 30:
                alerts.append(
                    f"Seus maiores gastos são com {maior_categoria['category_name']} "
                    f"(representam {maior_categoria['percentage']:.0f}% do total)"
                )

        return {
            "total_expenses": float(total_abs),
            "categories": categories,
            "alerts": alerts
        }