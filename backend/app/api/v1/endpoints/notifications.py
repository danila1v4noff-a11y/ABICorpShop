from fastapi import APIRouter, Depends, BackgroundTasks, Query, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import date
from app.core.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.batch import Batch
from app.models.favorite import FavoriteProductEmployee
from app.core.email import send_email
from app.core.security import decode_access_token

router = APIRouter(prefix="/admin", tags=["notifications"])

security = HTTPBearer()

def get_current_user_from_bearer(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Недействительный токен")
    login = payload.get("sub")                     # берём sub (логин)
    if login is None:
        raise HTTPException(status_code=401, detail="В токене отсутствует sub")
    user = db.query(User).filter(User.Login == login).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user

def require_manager(current_user: User = Depends(get_current_user_from_bearer)):
    if current_user.Manager != 1:
        raise HTTPException(status_code=403, detail="Требуются права менеджера")
    return current_user

@router.post("/notify-subscribers")
async def notify_subscribers(
    db: Session = Depends(get_db),
    manager: User = Depends(require_manager),
    product_id: int = Query(..., description="ID товара")
):
    product = db.query(Product).get(product_id)
    if not product:
        return {"error": "Товар не найден"}

    subscribers = db.query(User).join(
        FavoriteProductEmployee,
        User.EmployeeID == FavoriteProductEmployee.UserID
    ).filter(
        FavoriteProductEmployee.ProductID == product_id,
        User.Email.isnot(None)
    ).all()

    if not subscribers:
        return {"message": "Нет подписчиков с email"}

    today = date.today()
    batches = db.query(Batch).filter(
        Batch.ProductID == product_id,
        Batch.ExpirationDate >= today
    ).all()

    batches_info = ""
    if batches:
        batches_info = "<ul>" + "".join(
            [f"<li>Партия №{b.BatchID}, срок годности {b.ExpirationDate}</li>" for b in batches]
        ) + "</ul>"
    else:
        batches_info = "<p>Новых партий нет.</p>"

    subject = f"ABICorpShop: товар «{product.Name}»"
    body = f"""
    <h3>Уважаемый сотрудник!</h3>
    <p>Информируем о наличии товара «{product.Name}».</p>
    {batches_info}
    <p>Перейти к товару: <a href="http://localhost:5173/product/{product.ProductID}">страница товара</a></p>
    """

    emails = [user.Email for user in subscribers]
    
    # Прямая отправка с перехватом ошибок
    try:
        from app.core.email import send_email
        await send_email(emails, subject, body)
        return {"message": f"Рассылка отправлена {len(subscribers)} подписчикам"}
    except Exception as e:
        return {"error": str(e)}