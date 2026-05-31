from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Импорт моделей
from app.models import user, product, cart, favorite

# Импорт роутеров
from app.api.v1.endpoints import hello, auth
from app.api.v1.endpoints.cart import router as cart_router
from app.api.v1.endpoints.products import router as products_router
from app.api.v1.endpoints.favorites import router as favorites_router
from app.api.v1.endpoints.shared_cart import router as shared_cart_router
from app.api.v1.endpoints.orders import router as orders_router, router_admin
from app.api.v1.endpoints.categories import router as categories_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.blacklist import router as blacklist_router
from app.api.v1.endpoints.pickup import router as pickup_router

app = FastAPI(
    title="ABICorpShop API",
    description="Бэкенд для интернет-магазина",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth.router, prefix="/api/v1")
app.include_router(hello.router, prefix="/api/v1")
app.include_router(cart_router, prefix="/api/v1")
app.include_router(products_router, prefix="/api/v1")
app.include_router(favorites_router, prefix="/api/v1")
app.include_router(shared_cart_router, prefix="/api/v1")   # <-- добавлено
app.include_router(orders_router, prefix="/api/v1")
app.include_router(router_admin, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(blacklist_router, prefix="/api/v1")
app.include_router(pickup_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to ABICorpShop API"}