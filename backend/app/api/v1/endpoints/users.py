from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.api.v1.endpoints.auth import get_current_user
from pydantic import BaseModel

class UserResponse(BaseModel):
    employee_id: int
    fio: str
    manager: bool

    class Config:
        from_attributes = True

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=list[UserResponse])
def get_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.Manager != 1:
        raise HTTPException(status_code=403, detail="Требуются права менеджера")
    users = db.query(User).all()
    return [UserResponse(employee_id=u.EmployeeID, fio=u.FIO, manager=bool(u.Manager)) for u in users]