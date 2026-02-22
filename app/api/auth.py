from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import create_access_token
from app.schemas.auth import UserRegister, UserLogin, TokenResponse
from app.services.auth_service import register_user, authenticate_user
from app.api.deps import get_db


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(user_data: UserRegister, db: Session = Depends(get_db)):    
    try:
        user = register_user(db, user_data)
        return {"message": "User registered successfully", "user_id": user.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    try:
        user = authenticate_user(db, user_data.email, user_data.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        access_token = create_access_token(data={"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))