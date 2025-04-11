from sqlalchemy import select
from app.models.category_model import Category

DEFAULT_CATEGORIES = [
    {"name": "Alimentação", "type": "EXPENSE"},
    {"name": "Transporte", "type": "EXPENSE"},
    {"name": "Moradia", "type": "EXPENSE"},
    {"name": "Lazer", "type": "EXPENSE"},
    {"name": "Salário", "type": "INCOME"},
    {"name": "Investimentos", "type": "INCOME"}
]

async def seed_initial_data(db):
    try:
        for cat_data in DEFAULT_CATEGORIES:
            # Correção: Adicionar await e usar execute() corretamente
            result = await db.execute(
                select(Category).where(Category.name == cat_data["name"]))
            if not result.scalars().first():
                db.add(Category(**cat_data))
        await db.commit()
    except Exception as e:
        await db.rollback()
        print(f"Erro ao popular categorias: {e}")
        raise