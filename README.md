📌 **MONEY FLOW** - Sistema Financeiro

```bash
# Tecnologias
- 🐍 Python + FastAPI (Backend)
- ✨ Jinja2 (Templates HTML)
- 🐳 Docker + PostgreSQL
- 🔄 Alembic (Migrações)

# Como rodar:
1. docker-compose up -d --build
2.docker-compose exec api bash
3. alembic revision --autogenerate -n "inicializacao"
4. alembic upgrade head
2. Acesse: http://localhost:8000

# Comandos úteis:
🔸 docker-compose exec backend alembic upgrade head  # Rodar migrações
🔸 docker-compose logs -f  # Ver logs
🔸 docker-compose down  # Parar sistema


