from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.blacklist import Blacklist
from app.schemas.blacklist import BlacklistCreate, BlacklistResponse
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter(prefix="/admin/blacklist", tags=["Blacklist"])

def require_manager(current_user: User = Depends(get_current_user)):
    if current_user.Manager != 1:
        raise HTTPException(status_code=403, detail="Требуются права менеджера")
    return current_user

@router.get("/", response_model=list[BlacklistResponse])
def get_blacklist(
    manager: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    entries = db.query(Blacklist).all()
    result = []
    for entry in entries:
        result.append(BlacklistResponse(
            blacklist_id=entry.BlacklistID,
            user_id=entry.UserID,
            user_name=entry.user.FIO if entry.user else "",
            reason=entry.Reason,
            created_at=entry.CreatedAt,
            created_by_name=entry.created_by_manager.FIO if entry.created_by_manager else None
        ))
    return result

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=BlacklistResponse)
def add_to_blacklist(
    data: BlacklistCreate,
    manager: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.EmployeeID == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if user.Manager == 1:
        raise HTTPException(status_code=400, detail="Нельзя заблокировать менеджера")
    existing = db.query(Blacklist).filter(Blacklist.UserID == data.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь уже в чёрном списке")
    entry = Blacklist(UserID=data.user_id, Reason=data.reason, CreatedBy=manager.EmployeeID)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return BlacklistResponse(
        blacklist_id=entry.BlacklistID,
        user_id=entry.UserID,
        user_name=entry.user.FIO,
        reason=entry.Reason,
        created_at=entry.CreatedAt,
        created_by_name=manager.FIO
    )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_blacklist(
    user_id: int,
    manager: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    entry = db.query(Blacklist).filter(Blacklist.UserID == user_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    db.delete(entry)
    db.commit()
    return