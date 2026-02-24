from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.api.category import router as category_router
from app.api.transactions import router as transaction_router

app = FastAPI()
    
app.include_router(auth_router)
app.include_router(category_router)
app.include_router(transaction_router)