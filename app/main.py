from fastapi import FastAPI

from app.database import Base, engine
from app.routers import auth, categories, transactions, budgets, reports

# Creates tables if they don't exist yet.
# For real projects, prefer Alembic migrations over this once the schema stabilizes.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Expense & Budget API",
    description="A personal finance backend: income, expenses, categories, budgets, and reports.",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(reports.router)


@app.get("/", tags=["Health"])
def root():
    return {"message": "Smart Expense & Budget API is running"}
