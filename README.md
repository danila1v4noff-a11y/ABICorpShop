# ABICorpShop

Корпоративный интернет-магазин для сотрудников ABI Corp. Проект представляет собой полнофункциональное веб-приложение с возможностью просмотра каталога товаров, управления корзиной, оформления заказов, работы с избранное и рейтингами товаров.

## 📋 Оглавление

- [Технологии](#технологии)
- [Структура проекта](#структура-проекта)
- [Быстрый старт](#быстрый-старт)
- [Настройка окружения](#настройка-окружения)
- [API документация](#api-документация)
- [Модели данных](#модели-данных)
- [Особенности приложения](#особенности-приложения)
- [Разработка](#разработка)
- [Сборка и деплой](#сборка-и-деплой)

## 🛠 Технологии

### Frontend

- **Vue 3** (Composition API) - прогрессивный JavaScript-фреймворк
- **Vue Router 4** - маршрутизация для Vue.js
- **Vite 7** - современный сборщик проектов
- **Tailwind CSS 4** - утилитарный CSS-фреймворк
- **Axios** - HTTP-клиент для запросов к API
- **ESLint + Prettier** - линтинг и форматирование кода

### Backend

- **FastAPI** - современный веб-фреймворк на Python
- **SQLAlchemy** - ORM для работы с базой данных
- **Pydantic** - валидация данных и сериализация
- **python-jose** - работа с JWT токенами
- **passlib** - хеширование паролей

### Требования к окружению

- **Node.js**: ^20.19.0 || >=22.12.0
- **Python**: 3.8+
- **База данных**: PostgreSQL/MySQL/SQLite (настраивается)

## 📁 Структура проекта

```
ABICorpShop/
├── backend/                    # Бэкенд часть на FastAPI
│   ├── app/
│   │   ├── api/v1/endpoints/   # API эндпоинты
│   │   │   ├── auth.py         # Аутентификация
│   │   │   ├── cart.py         # Корзина
│   │   │   ├── orders.py       # Заказы
│   │   │   ├── products.py     # Товары и рейтинги
│   │   │   ├── favorites.py    # Избранное
│   │   │   ├── shared_cart.py  # Общие корзины
│   │   │   ├── categories.py   # Категории
│   │   │   └── ...
│   │   ├── core/               # Конфигурация и настройки
│   │   │   ├── config.py       # Настройки приложения
│   │   │   ├── database.py     # Подключение к БД
│   │   │   └── security.py     # Безопасность (JWT, пароли)
│   │   ├── models/             # Модели базы данных
│   │   │   ├── user.py         # Пользователи
│   │   │   ├── product.py      # Товары
│   │   │   ├── order.py        # Заказы
│   │   │   ├── cart.py         # Корзина
│   │   │   ├── batch.py        # Партии товаров
│   │   │   └── ...
│   │   ├── schemas/            # Pydantic схемы
│   │   └── main.py             # Точка входа FastAPI
│   ├── requirements.txt        # Python зависимости
│   └── set_passwords.py        # Скрипт установки паролей
├── src/                        # Фронтенд часть на Vue.js
│   ├── components/             # Vue компоненты
│   │   ├── Header.vue          # Шапка сайта
│   │   ├── Card.vue            # Карточка товара
│   │   ├── Drawer.vue          # Боковая панель (фильтры)
│   │   └── ...
│   ├── views/                  # Страницы приложения
│   │   ├── HomePage.vue        # Главная страница (каталог)
│   │   ├── ProductPage.vue     # Страница товара
│   │   ├── CartPage.vue        # Корзина
│   │   ├── LoginPage.vue       # Вход
│   │   ├── ProfilePage.vue     # Профиль
│   │   ├── AdminOrdersPage.vue # Админ-панель заказов
│   │   └── ...
│   ├── composables/            # Композаблы (логика)
│   │   ├── useCart.js          # Логика корзины
│   │   └── useFavorites.js     # Логика избранного
│   ├── router/                 # Маршрутизация
│   │   └── router.js           # Настройка маршрутов
│   ├── assets/                 # Статические ресурсы
│   └── main.js                 # Точка входа Vue
├── public/                     # Публичные файлы (иконки, изображения)
├── index.html                  # HTML шаблон
├── vite.config.js              # Конфигурация Vite
├── package.json                # Зависимости Node.js
└── README.md                   # Документация
```

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/danila1v4noff-a11y/ABICorpShop.git
cd ABICorpShop
```

### 2. Настройка фронтенда

```bash
# Установка зависимостей
npm install

# Запуск сервера разработки
npm run dev
```

Фронтенд будет доступен по адресу: `http://localhost:5173`

### 3. Настройка бэкенда

```bash
# Перейдите в директорию backend
cd backend

# Создайте виртуальное окружение (рекомендуется)
python -m venv venv

# Активируйте виртуальное окружение
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt

# Создайте файл .env в директории backend/
# Пример содержимого .env:
# DATABASE_URL=sqlite:///./abicorpshop.db
# SECRET_KEY=your-secret-key-here

# Запустите сервер
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Бэкенд будет доступен по адресу: `http://localhost:8000`

## ⚙️ Настройка окружения

### Переменные окружения для бэкенда

Создайте файл `.env` в директории `backend/`:

```env
# URL подключения к базе данных
# Примеры:
# SQLite: sqlite:///./abicorpshop.db
# PostgreSQL: postgresql://user:password@localhost:5432/abicorpshop
# MySQL: mysql://user:password@localhost:3306/abicorpshop
DATABASE_URL=sqlite:///./abicorpshop.db

# Секретный ключ для JWT токенов (должен быть сложным и уникальным)
SECRET_KEY=your-super-secret-key-change-this-in-production
```

### Настройка CORS

В файле `backend/app/main.py` настроен CORS для разрешения запросов с фронтенда:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Измените на ваш домен в продакшене
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Установка паролей пользователей

После первого запуска и создания базы данных, установите пароли для пользователей:

```bash
cd backend
python set_passwords.py
```

По умолчанию создаются пользователи:

- **ManagerABI** (менеджер) - пароль: `manager123`
- **DimitryGurko_ABI** (сотрудник) - пароль: `gurko123`

## 📡 API документация

### Базовый URL API

```
http://localhost:8000/api/v1
```

### Аутентификация

#### POST `/auth/login`

Получение JWT токена.

**Тело запроса:**

```json
{
  "login": "ManagerABI",
  "password": "manager123"
}
```

**Ответ:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### GET `/auth/me`

Получение информации о текущем пользователе.

**Заголовки:**

```
Authorization: Bearer <token>
```

**Ответ:**

```json
{
  "employee_id": 1,
  "fio": "Manager ABI",
  "email": "manager@abicorp.com",
  "login": "ManagerABI",
  "is_manager": true
}
```

### Товары

#### GET `/products/`

Получение списка товаров с фильтрацией.

**Параметры запроса:**

- `search` (string) - поиск по названию
- `category_names` (array) - фильтр по категориям

**Ответ:**

```json
[
  {
    "product_id": 1,
    "name": "Пельмени Домашние",
    "price": 250.0,
    "weight": 500,
    "image_url": "/images/pelmeni.jpg",
    "stock": 100,
    "has_expiring": false
  }
]
```

#### GET `/products/{product_id}`

Получение детальной информации о товаре.

**Ответ:**

```json
{
  "product_id": 1,
  "name": "Пельмени Домашние",
  "price": 250.0,
  "weight": 500,
  "image_url": "/images/pelmeni.jpg",
  "stock": 100,
  "has_expiring": false,
  "description": "Домашние пельмени из отборного мяса",
  "category_id": 1,
  "category_name": "Пельмени",
  "expiration_date": "2026-06-01",
  "cooking_info": "10 минут на огне"
}
```

#### GET `/products/{product_id}/related`

Получение похожих товаров.

#### POST `/products/{product_id}/rate`

Оценка товара (1-5 звёзд).

**Тело запроса:**

```json
{
  "rating": 5
}
```

#### GET `/products/{product_id}/rating`

Получение рейтинга товара.

### Корзина

#### GET `/cart/`

Получение содержимого корзины.

**Ответ:**

```json
{
  "items": [
    {
      "cart_item_id": 1,
      "product_id": 1,
      "product_name": "Пельмени Домашние",
      "price": 250.0,
      "quantity": 2,
      "total_price": 500.0,
      "image_url": "/images/pelmeni.jpg",
      "discount_price": null
    }
  ],
  "total_sum": 500.0,
  "total_weight": 1000
}
```

#### POST `/cart/add`

Добавление товара в корзину.

**Тело запроса:**

```json
{
  "product_id": 1,
  "quantity": 2
}
```

#### PUT `/cart/{item_id}`

Обновление количества товара в корзине.

**Тело запроса:**

```json
{
  "quantity": 3
}
```

#### DELETE `/cart/{item_id}`

Удаление товара из корзины.

### Заказы

#### POST `/orders/`

Создание заказа.

**Тело запроса:**

```json
{
  "delivery_method": "office",
  "office_address": "Дворянская 27АК17",
  "cabinet": "101",
  "delivery_date": "2026-05-25",
  "delivery_time_slot": "10:00",
  "payment_method": "card",
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ]
}
```

**Ограничения:**

- Максимальный вес заказа: 25 кг
- Максимальное количество одного товара: 15 шт

#### GET `/orders/`

Получение списка заказов текущего пользователя.

### Админ-панель (только для менеджеров)

#### GET `/admin/orders/`

Получение всех заказов.

#### PUT `/admin/orders/{order_id}/status`

Изменение статуса заказа.

**Тело запроса:**

```json
{
  "status": "approved"
}
```

**Доступные статусы:**

- `pending` - ожидает подтверждения
- `approved` - подтверждён
- `rejected` - отклонён
- `cancelled` - отменён
- `completed` - завершён

#### GET `/admin/orders/pending-count`

Получение количества заказов, ожидающих подтверждения.

### Избранное

#### GET `/favorites/`

Получение списка избранных товаров.

#### POST `/favorites/`

Добавление товара в избранное.

**Тело запроса:**

```json
{
  "product_id": 1
}
```

#### DELETE `/favorites/{product_id}`

Удаление товара из избранного.

### Общие корзины

#### POST `/shared-cart/`

Создание общей корзины.

**Ответ:**

```json
{
  "id": 1,
  "owner_id": 1,
  "owner_name": "Ivanov Ivan",
  "token": "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8",
  "is_active": true,
  "created_at": "2026-05-20T10:00:00",
  "items": []
}
```

#### GET `/shared-cart/{token}`

Получение общей корзины по токену.

#### POST `/shared-cart/{token}/add`

Добавление товара в общую корзину.

#### PUT `/shared-cart/{token}/item/{item_id}`

Обновление элемента в общей корзине.

#### DELETE `/shared-cart/{token}/item/{item_id}`

Удаление элемента из общей корзины.

### Категории

#### GET `/categories/`

Получение списка категорий товаров.

**Ответ:**

```json
[
  {
    "category_id": 1,
    "name": "Пельмени"
  }
]
```

## 🗄 Модели данных

### User (Пользователь)

- `EmployeeID` - уникальный идентификатор
- `FIO` - ФИО
- `Manager` - флаг менеджера (1 - менеджер, 0 - сотрудник)
- `StatusID` - статус
- `Email` - электронная почта
- `Login` - логин
- `hashed_password` - хеш пароля

### Product (Товар)

- `ProductID` - уникальный идентификатор
- `Name` - название
- `Description` - описание
- `Price` - цена
- `Weight` - вес (в граммах)
- `ImageURL` - URL изображения
- `CategoryID` - идентификатор категории
- `CreatedAt` - дата создания
- `UpdatedAt` - дата обновления

### Batch (Партия товаров)

- `BatchID` - уникальный идентификатор
- `ProductID` - идентификатор товара
- `Quantity` - количество
- `ExpirationDate` - дата истечения срока годности

### EmployeeOrder (Заказ)

- `OrderID` - уникальный идентификатор
- `UserID` - идентификатор пользователя
- `DeliveryMethod` - способ доставки
- `OfficeAddress` - адрес офиса
- `Cabinet` - кабинет
- `DeliveryDate` - дата доставки
- `DeliveryTimeSlot` - временной слот доставки
- `PaymentMethod` - способ оплаты
- `Status` - статус заказа
- `TotalAmount` - общая сумма
- `TotalWeight` - общий вес
- `CreatedAt` - дата создания
- `ProcessedBy` - идентификатор обработавшего менеджера
- `ManagerComment` - комментарий менеджера

### CartItem (Элемент корзины)

- `CartItemID` - уникальный идентификатор
- `UserID` - идентификатор пользователя
- `ProductID` - идентификатор товара
- `Quantity` - количество

### FavoriteProductEmployee (Избранное)

- `FavoriteID` - уникальный идентификатор
- `UserID` - идентификатор пользователя
- `ProductID` - идентификатор товара

### SharedCart (Общая корзина)

- `id` - уникальный идентификатор
- `owner_id` - идентификатор владельца
- `token` - уникальный токен доступа
- `is_active` - активна ли корзина
- `created_at` - дата создания

### ProductRating (Рейтинг товара)

- `UserID` - идентификатор пользователя
- `ProductID` - идентификатор товара
- `Rating` - оценка (1-5)
- `UpdatedAt` - дата обновления

## ✨ Особенности приложения

### 1. Система скидок на истекающие товары

Автоматическая скидка 40% на товары, у которых срок годности истекает в ближайшие 14 дней.

### 2. Управление партиями (FIFO)

При оформлении заказа товары списываются с партий по принципу FIFO (First In, First Out), начиная с самых ранних по сроку годности.

### 3. Общие корзины

Возможность создания общих корзин для совместных закупок с коллегами. Доступ по уникальному токену.

### 4. Ролевая модель

- **Сотрудник** - может просматривать товары, управлять корзиной, оформлять заказы, оценивать товары
- **Менеджер** - имеет доступ к админ-панели для управления заказами (подтверждение, отклонение, отмена)

### 5. Ограничения заказов

- Максимальный вес заказа: 25 кг
- Максимальное количество одного товара: 15 штук
- Автоматическая проверка доступности товаров на складе

### 6. Интерфейс

- Адаптивный дизайн с использованием Tailwind CSS
- Поиск товаров с автодополнением
- Фильтрация по категориям
- Интуитивное управление корзиной
- Отслеживание статусов заказов

## 🔧 Разработка

### Команды фронтенда

```bash
# Установка зависимостей
npm install

# Запуск сервера разработки
npm run dev

# Сборка для продакшена
npm run build

# Предварительный просмотр продакшен-сборки
npm run preview

# Линтинг и форматирование
npm run lint          # Запуск ESLint и oxlint
npm run format        # Форматирование кода с Prettier
```

### Команды бэкенда

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск сервера разработки
uvicorn app.main:app --reload

# Запуск в продакшене
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Рекомендуемые расширения VS Code

- **Vue (Official)** - официальное расширение для Vue.js
- **Volar** - поддержка Vue 3
- **Prettier - Code formatter** - форматирование кода
- **ESLint** - линтинг JavaScript
- **Python** - поддержка Python
- **SQLite** - работа с SQLite базами данных

## 📦 Сборка и деплой

### Фронтенд

```bash
# Сборка для продакшена
npm run build

# Результат будет в директории dist/
```

Полученные файлы из `dist/` можно разместить на любом статическом хостинге (Nginx, Apache, Vercel, Netlify и т.д.).

### Бэкенд

Для продакшена рекомендуется использовать:

```bash
# С Gunicorn и Uvicorn workers
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker (опционально)

При необходимости можно создать Dockerfile для контейнеризации приложения.

## 📝 Лицензия

Проект создан для внутреннего использования в ABI Corp.

## 👥 Авторы

- [danila1v4noff-a11y](https://github.com/danila1v4noff-a11y)

---

**Документация актуальна на момент последнего обновления проекта.**
