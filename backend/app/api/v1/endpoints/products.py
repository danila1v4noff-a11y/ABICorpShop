from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func as sqlfunc, asc
from typing import List, Optional
from datetime import date, timedelta
import random

from app.core.database import get_db
from app.models.product import Product
from app.models.batch import Batch
from app.models.category import Category
from app.models.user import User
from app.models.rating import ProductRating
from app.schemas.product import ProductResponse, ProductDetailResponse, RelatedProduct, BatchResponse
from app.schemas.rating import RatingCreate, RatingResponse
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", response_model=list[BatchResponse])
def get_products(
    search: Optional[str] = Query(None),
    category_names: Optional[List[str]] = Query(None, alias="category_names"),
    db: Session = Depends(get_db)
):
    query = db.query(Batch).join(Product).join(Category, isouter=True)
    if search:
        query = query.filter(Product.Name.ilike(f"%{search}%"))
    if category_names:
        query = query.filter(Category.Name.in_(category_names))

    batches = query.order_by(Batch.ExpirationDate.asc()).all()
    threshold = date.today() + timedelta(days=14)

    result = []
    for b in batches:
        product = b.product
        has_exp = b.ExpirationDate and b.ExpirationDate <= threshold
        result.append(BatchResponse(
            batch_id=b.BatchID,
            product_id=product.ProductID,
            product_name=product.Name,
            price=float(product.Price),
            weight=product.Weight,
            image_url=product.ImageURL,
            quantity=b.Quantity,
            expiration_date=b.ExpirationDate,
            has_expiring=has_exp,
            category_id=product.CategoryID,
            category_name=product.category.Name if product.category else None
        ))
    return result


@router.get("/{product_id}", response_model=ProductDetailResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.ProductID == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    total_qty = db.query(sqlfunc.coalesce(sqlfunc.sum(Batch.Quantity), 0))\
                  .filter(Batch.ProductID == product.ProductID).scalar()

    threshold = date.today() + timedelta(days=14)
    nearest_exp = db.query(Batch).filter(
        Batch.ProductID == product.ProductID,
        Batch.Quantity > 0
    ).order_by(asc(Batch.ExpirationDate)).first()

    has_exp = db.query(Batch).filter(
        Batch.ProductID == product.ProductID,
        Batch.Quantity > 0,
        Batch.ExpirationDate <= threshold
    ).first() is not None

    category_name = product.category.Name if product.category else None
    category_id = product.category.CategoryID if product.category else None

    cooking_info = None
    if category_name:
        if category_name == "ПГП":
            cooking_info = "2 минуты в микроволновке"
        elif category_name == "Пельмени":
            cooking_info = "10 минут на огне"
        elif category_name == "Колбасы":
            cooking_info = "Отлично сочетается с горчицей и свежим хлебом"
        elif category_name == "Сосиски":
            cooking_info = "Рекомендуем варить 3-5 минут"
        elif category_name == "Нарезка":
            cooking_info = "Идеальна для бутербродов"

    return ProductDetailResponse(
        product_id=product.ProductID,
        name=product.Name,
        price=float(product.Price),
        weight=product.Weight,
        image_url=product.ImageURL,
        stock=total_qty,
        has_expiring=has_exp,
        description=product.Description,
        category_id=category_id,
        category_name=category_name,
        expiration_date=nearest_exp.ExpirationDate if nearest_exp else None,
        cooking_info=cooking_info
    )


@router.get("/{product_id}/related", response_model=list[RelatedProduct])
def get_related_products(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.ProductID == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    if not product.CategoryID:
        return []

    all_related = db.query(Product).filter(
        Product.CategoryID == product.CategoryID,
        Product.ProductID != product_id
    ).all()

    if len(all_related) <= 2:
        chosen = all_related
    else:
        chosen = random.sample(all_related, 2)

    return [RelatedProduct(product_id=p.ProductID, name=p.Name, image_url=p.ImageURL) for p in chosen]


def get_rating_response(product_id: int, user_id: int, db: Session):
    avg = db.query(sqlfunc.avg(ProductRating.Rating)).filter(
        ProductRating.ProductID == product_id
    ).scalar()
    user_rating = db.query(ProductRating.Rating).filter(
        ProductRating.ProductID == product_id,
        ProductRating.UserID == user_id
    ).scalar()
    return RatingResponse(
        average_rating=round(float(avg), 1) if avg else None,
        user_rating=user_rating
    )


@router.post("/{product_id}/rate", response_model=RatingResponse)
def rate_product(
    product_id: int,
    rating_data: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if rating_data.rating < 1 or rating_data.rating > 5:
        raise HTTPException(status_code=400, detail="Оценка должна быть от 1 до 5")
    product = db.query(Product).filter(Product.ProductID == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    existing = db.query(ProductRating).filter(
        ProductRating.UserID == current_user.EmployeeID,
        ProductRating.ProductID == product_id
    ).first()
    if existing:
        existing.Rating = rating_data.rating
        existing.UpdatedAt = sqlfunc.now()
    else:
        rating = ProductRating(
            UserID=current_user.EmployeeID,
            ProductID=product_id,
            Rating=rating_data.rating
        )
        db.add(rating)
    db.commit()
    return get_rating_response(product_id, current_user.EmployeeID, db)


@router.get("/{product_id}/rating", response_model=RatingResponse)
def get_product_rating(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.ProductID == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return get_rating_response(product_id, current_user.EmployeeID, db)