from pydantic import BaseModel, EmailStr

# Схема для данных, которые приходят при логине
class UserLogin(BaseModel):
    login: str
    password: str

# Схема для ответа с данными пользователя (без пароля)
class UserResponse(BaseModel):
    employee_id: int
    fio: str
    email: EmailStr
    login: str
    is_manager: bool

    class Config:
        from_attributes = True  # чтобы работало с ORM

# Схема для токена
class Token(BaseModel):
    access_token: str
    token_type: str