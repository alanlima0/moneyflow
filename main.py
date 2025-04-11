from contextlib import asynccontextmanager
from sqlalchemy import text
from database.database import engine, AsyncSessionLocal
from database.seed import seed_initial_data
from app.routes import account_route, auth, transaction_routes, user_routes,views, category_route, expense_analysis_routes
from app.models import category_model, user_model, transaction_model, account_model
from fastapi import FastAPI
import logging
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSessionLocal() as db:
        await seed_initial_data(db)
        logger.info("Categorias padrão cadastradas com sucesso!")
    
    yield

BASE_DIR = Path(__file__).parent

app = FastAPI(lifespan=lifespan)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "app" / "static"),  # app/static/
    name="static"
)

templates = Jinja2Templates(directory=BASE_DIR / "app" / "templates")  # app/templates/

# Inclui as rotas
app.include_router(expense_analysis_routes.router)
app.include_router(user_routes.router)
app.include_router(auth.router)
app.include_router(account_route.router)
app.include_router(transaction_routes.router)
app.include_router(views.router)
app.include_router(category_route.router)

# # Rota raiz
# @app.get("/")
# async def read_root():
#     return {"message": "Hello, World!", "status": "API is running"}