from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models import Pet, User
from app.schemas import TokenResponse, UserCreate, UserLogin

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(body: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    user = User(email=body.email, password_hash=hash_password(body.password))
    db.add(user)
    db.flush()

    pet = Pet(user_id=user.id, name="Студент-корги", level=0, hunger=100, current_exp=0)
    db.add(pet)
    db.commit()

    token = create_access_token(user.id)
    return TokenResponse(token=token, user_id=user.id)


@router.post("/login", response_model=TokenResponse)
def login(body: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    token = create_access_token(user.id)
    return TokenResponse(token=token, user_id=user.id)
