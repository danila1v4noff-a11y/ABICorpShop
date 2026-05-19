from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserLogin, Token, UserResponse
from app.core.security import verify_password, create_access_token
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.schemas.token import TokenData
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    # Ищем пользователя по логину (поле Login в таблице)
    user = db.query(User).filter(User.Login == user_login.login).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )
    # Проверяем пароль (hashed_password в БД)
    if not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )
    # Создаём JWT токен
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.Login}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ========== НОВЫЙ КОД ДЛЯ /me ==========
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учётные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        login: str = payload.get("sub")
        if login is None:
            raise credentials_exception
        token_data = TokenData(login=login)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.Login == token_data.login).first()
    if user is None:
        raise credentials_exception
    return user

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        employee_id=current_user.EmployeeID,
        fio=current_user.FIO,
        email=current_user.Email,
        login=current_user.Login,
        is_manager=current_user.Manager == 1,
    )