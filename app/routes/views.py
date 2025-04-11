from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()

# Caminho relativo correto para a pasta templates
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})