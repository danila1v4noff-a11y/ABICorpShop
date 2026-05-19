import sys
sys.path.append(".")

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

users_passwords = {
    "ManagerABI": "manager123",
    "DimitryGurko_ABI": "gurko123",
}

db = SessionLocal()
for login, plain_password in users_passwords.items():
    user = db.query(User).filter(User.Login == login).first()
    if user:
        user.hashed_password = get_password_hash(plain_password)
        print(f"Пароль для {login} установлен.")
    else:
        print(f"Пользователь {login} не найден.")
db.commit()
db.close()