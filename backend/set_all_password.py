import sys
sys.path.append(".")

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

# Список логинов, которым нужен пароль (все, кроме ManagerABI и DimitryGurko_ABI)
logins = [
    "AnnaSmirnova_ABI",
    "PetrIvanov_ABI",
    "ElenaKuznetsova_ABI",
    "AlexeySokolov_ABI",
    "OlgaMikhailova_ABI",
    "ArtemFedorov_ABI",
    "TatianaMorozova_ABI",
    "DenisVolkov_ABI",
    "AnastasiaPavlova_ABI",
    "MaximStepanov_ABI",
]

default_password = "password123"

db = SessionLocal()
for login in logins:
    user = db.query(User).filter(User.Login == login).first()
    if user:
        user.hashed_password = get_password_hash(default_password)
        print(f"Пароль для {login} установлен.")
    else:
        print(f"Пользователь {login} не найден.")
db.commit()
db.close()