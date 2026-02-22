from sqlalchemy.orm import Session
from app.db.models.user import User
from app.core.security import verify_password, hash_password, create_access_token


def register_user(db: Session, user_data):
    user_exists = db.query(User).filter(User.email == user_data.email).first()    
    if user_exists:
        raise ValueError("User alredy exists with this email")

    hashed_password = hash_password(user_data.hashed_password)

    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        contact_number=user_data.contact_number,
        hashed_password=hashed_password,
        is_active=True,
        role_id=user_data.role_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None

    return user


def login_user(db: Session, email: str, password: str):
    user = authenticate_user(db, email, password)
    if not user:
        return None
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}