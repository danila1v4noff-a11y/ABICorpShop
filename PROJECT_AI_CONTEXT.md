# ABICorpShop — Полное описание архитектуры для нейросети

## 🎯 Краткое описание проекта

**ABICorpShop** — это корпоративный интернет-магазин для сотрудников компании АО «АБИ». Полнофункциональное веб-приложение, позволяющее сотрудникам просматривать каталог товаров, управлять корзиной, оформлять заказы с доставкой в офис или самовывозом, работать с избранным и оценивать товары.

**Ключевая особенность**: система работает с партиями товаров, автоматически применяет скидки 40% на товары с истекающим сроком годности (≤14 дней), поддерживает совместные закупки через общие корзины.

---

## 🏗 Архитектура приложения

### Технологический стек

**Frontend:**

- Vue 3 (Composition API) + Vue Router 4
- Vite 7 (сборщик)
- Tailwind CSS 4 (стилизация)
- Axios (HTTP-клиент)

**Backend:**

- FastAPI (Python) — современный асинхронный фреймворк
- SQLAlchemy — ORM для работы с БД
- Pydantic — валидация данных
- python-jose + passlib — JWT аутентификация и хеширование паролей

**База данных:** PostgreSQL/MySQL/SQLite (настраивается через DATABASE_URL)

### Структура проекта

```
ABICorpShop/
├── backend/                    # Бэкенд на FastAPI
│   ├── app/
│   │   ├── api/v1/endpoints/   # API эндпоинты (auth, cart, orders, products...)
│   │   ├── core/               # Конфиг, БД, безопасность
│   │   ├── models/             # SQLAlchemy модели (User, Product, Order...)
│   │   ├── schemas/            # Pydantic схемы
│   │   └── main.py             # Точка входа FastAPI
│   └── requirements.txt
├── src/                        # Фронтенд на Vue.js
│   ├── components/             # Переиспользуемые компоненты (Header, Card, Drawer...)
│   ├── views/                  # Страницы (HomePage, CartPage, ProductPage...)
│   ├── composables/            # Композаблы (useCart, useFavorites)
│   ├── router/                 # Маршрутизация
│   ├── assets/                 # Стили
│   └── main.js                 # Точка входа
└── public/                     # Статика (иконки, изображения)
```

---

## 🔐 Система аутентификации и роли

### Аутентификация

- **JWT токены** со сроком жизни 30 минут
- Логин/пароль хранятся в БД (пароли хешируются через bcrypt)
- Токен хранится в `localStorage` на фронтенде
- Данные текущего пользователя (`user` объект) также в `localStorage`

### Роли

1. **Сотрудник** (`is_manager = false`)
   - Просмотр каталога товаров
   - Управление личной корзиной
   - Оформление заказов
   - Избранное и рейтинги
   - Просмотр своих заказов
   - Создание общих корзин

2. **Менеджер** (`is_manager = true`)
   - Все права сотрудника +
   - Доступ к админ-панели заказов (`/admin/orders`)
   - Управление статусами заказов (принять, отклонить, в работе, готово, завершён, отменить)
   - Управление чёрным списком сотрудников
   - Просмотр количества pending-заказов (уведомление в шапке)

---

## 📦 Модель данных (ключевые сущности)

### User (Пользователь/Сотрудник)

```python
EmployeeID (PK), FIO, Manager (bool), StatusID, Email, Login, hashed_password
```

- Связи: cart_items, favorites, orders, ratings, blacklist_entry, owned_shared_carts

### Product (Товар)

```python
ProductID (PK), Name, Description, Price, Weight, ImageURL, CategoryID, CreatedAt, UpdatedAt
```

- Связи: batches (партии), cart_items, favorited_by, ratings, category

### Batch (Партия товаров)

```python
BatchID (PK), ProductID, Quantity, ExpirationDate, CreatedAt
```

- **Важно**: товары учитываются по партиям с разными сроками годности
- При оформлении заказа применяется **FIFO** (сначала списываются партии с earliest expiration date)

### CartItem (Элемент корзины)

```python
CartItemID (PK), UserID, ProductID, BatchID, Quantity, AddedAt
```

- Уникальность: `(UserID, BatchID)` — один товар из одной партии в корзине

### EmployeeOrder (Заказ)

```python
OrderID (PK), UserID, DeliveryMethod, OfficeAddress, Cabinet, DeliveryDate, DeliveryTimeSlot,
PaymentMethod, Status, TotalAmount, TotalWeight, CreatedAt, ProcessedBy, ManagerComment
```

- Статусы: `pending` → `accepted` → `in_progress` → `ready` → `completed`
- Также: `rejected`, `cancelled`
- Отмена пользователем возможна только в статусе `pending` в течение 5 минут

### OrderItem (Позиция заказа)

```python
OrderItemID (PK), OrderID, ProductID, Quantity, PriceAtOrder, BatchID, ExpirationDate
```

### SharedCart (Общая корзина)

```python
id (PK), owner_id, token (UUID), is_active, created_at
```

- Создаётся пользователем, генерируется уникальный токен
- По токену другие пользователи могут добавлять товары
- Владелец может редактировать любые элементы, участники — только свои

### SharedCartItem (Элемент общей корзины)

```python
id (PK), shared_cart_id, product_id, batch_id, quantity, added_by_user_id, added_at
```

### FavoriteProductEmployee (Избранное)

```python
FavoriteID (PK), UserID, ProductID, AddedAt
```

### ProductRating (Рейтинг товара)

```python
RatingID (PK), UserID, ProductID, Rating (1-5), CreatedAt, UpdatedAt
```

### PickupSlot (Слот самовывоза)

```python
SlotID (PK), PickupDate, TimeSlot, BookedCount, MaxCapacity (default=20)
```

- Уникальность: `(PickupDate, TimeSlot)`
- Бронируется при оформлении заказа с самовывозом

### Blacklist (Чёрный список)

```python
BlacklistID (PK), UserID, Reason, CreatedBy, CreatedAt
```

- Заблокированные пользователи не могут добавлять товары в корзину

### Category (Категория)

```python
CategoryID (PK), Name, Description, CreatedAt
```

---

## 🛒 Ключевые бизнес-процессы

### 1. Просмотр товаров (каталог)

- **API**: `GET /api/v1/products/`
- Возвращает список **партий** (Batch) с информацией о товаре
- Параметры: `search` (по названию), `category_names` (фильтр по категориям)
- Флаг `has_expiring` — true, если срок годности ≤ 14 дней от текущей даты
- На фронтенде: CardList.vue отображает карточки товаров с ценами (со скидкой если истекающий)

### 2. Страница товара

- **API**: `GET /api/v1/products/{id}` — детальная информация
- `GET /api/v1/products/{id}/related` — похожие товары (2 случайных из той же категории)
- `GET /api/v1/products/{id}/rating` — рейтинг (средний + оценка пользователя)
- `POST /api/v1/products/{id}/rate` — оценка товара (1-5)
- Автоматическая подстановка `cooking_info` в зависимости от категории:
  - ПГП → "2 минуты в микроволновке"
  - Пельмени → "10 минут на огне"
  - Колбасы → "Отлично сочетается с горчицей и свежим хлебом"
  - Сосиски → "Рекомендуем варить 3-5 минут"
  - Нарезка → "Идеальна для бутербродов"

### 3. Корзина

- **API**: `GET/POST/PUT/DELETE /api/v1/cart/`
- Отображает товары с учётом скидок на истекающие (40% скидка)
- Подсчитывает общую сумму и вес
- Ограничения:
  - Макс. 15 шт. одного товара в корзине
  - Макс. 25 кг общий вес заказа
- Проверка остатков на складе (по партиям)

### 4. Оформление заказа

- **API**: `POST /api/v1/orders/`
- Собирает товары из **личной корзины** + **активной общей корзины** (если есть)
- Параметры доставки:
  - **Доставка**: выбор офиса (4 предустановленных) + кабинет
  - **Самовывоз**: выбор даты (3 ближайших будних дня) + временного слота (10-12 или 14-16)
- Способ оплаты: картой (всегда) или наличными (только при самовывозе)
- **Списание товаров**:
  - Если указан batch_id — списание из конкретной партии
  - Иначе — FIFO (сначала самые ранние по сроку годности)
- **Бронирование слота**: при самовывозе увеличивается `BookedCount` в PickupSlot
- Очистка личной и общей корзины после успешного заказа

### 5. Общая корзина (совместные закупки)

- **API**: `POST /api/v1/shared-cart/` — создание (генерируется UUID токен)
- `GET /api/v1/shared-cart/{token}` — просмотр
- `POST /api/v1/shared-cart/{token}/add` — добавление товара (требуется авторизация)
- `PUT/DELETE /api/v1/shared-cart/{token}/item/{item_id}` — редактирование
- Права:
  - Владелец может редактировать любые элементы
  - Другие пользователи — только свои (по `added_by_user_id`)
- Ссылка вида `/shared/{token}` копируется в буфер обмена
- При оформлении заказа общая корзина деактивируется

### 6. Избранное

- **API**: `GET/POST/DELETE /api/v1/favorites/`
- Простое добавление/удаление товаров в избранное
- Отображается в профиле пользователя

### 7. Профиль пользователя

- **API**: `GET /api/v1/orders/` — история заказов
- Отображение избранных товаров
- Возможность отмены заказа в течение 5 минут (пока статус `pending`)
- При отмене: товары возвращаются на склад (создаётся новая партия с сроком +14 дней), слот самовывоза освобождается

### 8. Админ-панель (менеджер)

- **API**: `GET /api/v1/admin/orders/` — все заказы
- `PUT /api/v1/admin/orders/{id}/status` — смена статуса
- `GET /api/v1/admin/orders/pending-count` — количество ожидающих (для бейджика в шапке)
- **Чёрный список**: `GET/POST/DELETE /api/v1/admin/blacklist/`
  - Нельзя заблокировать менеджера
  - Заблокированные не могут добавлять товары в корзину

### 9. Слоты самовывоза

- **API**: `GET /api/v1/pickup-slots/available`
- Автоматически создаёт слоты при запросе (если не существуют)
- Показывает оставшиеся места: `remaining = MaxCapacity - BookedCount`
- Временные слоты: "10-12" и "14-16"
- Максимальная ёмкость: 20 заказов на слот

---

## 🎨 Фронтенд компоненты и страницы

### Компоненты (src/components/)

- **App.vue** — корневой компонент (просто `<router-view />`)
- **Header.vue** — шапка с логотипом, поиском, фильтрами, корзиной, уведомлениями (для менеджера), профилем, выбором адреса
- **Footer.vue** — подвал
- **Card.vue** — карточка товара (изображение, название, цена, кнопки +/-, избранное)
- **CardList.vue** — сетка товаров с фильтрацией и анимациями
- **Drawer.vue** — боковая панель фильтров (категории, даты срока годности)
- **DrawerHead.vue** — заголовок drawer

### Страницы (src/views/)

- **HomePage.vue** — главная: каталог товаров + фильтры
- **ProductPage.vue** — страница товара: детальная информация, рейтинг, похожие товары
- **CartPage.vue** — корзина: товары, выбор доставки/оплаты, оформление заказа, кнопка "Поделиться корзиной"
- **LoginPage.vue** — вход (логин/пароль)
- **ProfilePage.vue** — профиль: избранное, последние заказы (2 или все), отмена заказа
- **SharedCartPage.vue** — общая корзина: просмотр добавленных товаров, добавление новых
- **AdminOrdersPage.vue** — админ-панель заказов: список, смена статусов, переход в чёрный список
- **BlacklistPage.vue** — управление чёрным списком (добавление/удаление)
- **RulesPage.vue** — правила пользования магазином (статичная страница)

### Композаблы (src/composables/)

- **useCart.js** — глобальное состояние корзины (cartItems, totalSum, totalWeight), методы: fetchCart, addToCart, updateCartItem, removeFromCart, clearCart
- **useFavorites.js** — глобальное состояние избранного, методы: fetchFavorites, addFavorite, removeFavorite, clearFavorites

### Маршрутизация (src/router/router.js)

```javascript
/               → HomePage (требует auth)
/profile        → ProfilePage (требует auth)
/cart           → CartPage (требует auth)
/login          → LoginPage (без auth, перенаправляет на / если уже авторизован)
/shared/:token  → SharedCartPage (без auth, но действия требуют токен)
/product/:id    → ProductPage (без auth, но корзина/избранное требуют токен)
/rules          → RulesPage (без auth)
/admin/orders   → AdminOrdersPage (требует auth + is_manager)
/admin/blacklist→ BlacklistPage (требует auth + is_manager)
```

---

## 🔄 Поток данных

### Типичный сценарий покупки:

1. Пользователь логинится → токен и user сохраняются в localStorage
2. Открывает главную → CardList загружает товары через API
3. Ищет товар, фильтрует по категории/датам
4. Открывает страницу товара → видит рейтинг, описание, похожие товары
5. Добавляет в корзину (создаётся CartItem с привязкой к batch_id)
6. Переходит в корзину → видит товары со скидками, выбирает доставку/оплату
7. Оформляет заказ → POST /orders/, корзина очищается
8. Видит сообщение "Заказ взят в работу" → перенаправление на главную
9. Менеджер видит заказ в админ-панели → меняет статусы
10. Пользователь видит статусы в профиле

### Сценарий совместной закупки:

1. Пользователь нажимает "Поделиться корзиной" в корзине
2. Создаётся SharedCart с UUID токеном, ссылка копируется
3. Коллега переходит по ссылке `/shared/{token}` → видит общую корзину
4. Коллега добавляет товары через интерфейс SharedCartPage
5. Владелец видит добавленные товары в своей корзине (combinedItems)
6. При оформлении заказа товары из общей корзины также включаются

---

## ⚙️ Конфигурация и запуск

### Переменные окружения (backend/.env)

```env
DATABASE_URL=sqlite:///./abicorpshop.db  # или PostgreSQL/MySQL
SECRET_KEY=your-secret-key-here           # для JWT
```

### Запуск

```bash
# Frontend
npm install
npm run dev  # http://localhost:5173

# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# API: http://localhost:8000/api/v1
```

### CORS

Бэкенд разрешает запросы с `http://localhost:5173` (настройка в `backend/app/main.py`)

### API Base URL

- Frontend использует `http://127.0.0.1:8000/api/v1` (жестко задан в composables и компонентах)

---

## 📊 Особенности реализации

1. **Система скидок**: 40% на товары с expiration_date ≤ today + 14 дней
2. **FIFO списание**: при оформлении заказа товары списываются из партий с earliest expiration date
3. **Учёт партий**: каждый CartItem привязан к конкретному BatchID
4. **Ограничения**: 15 шт. на товар, 25 кг на заказ
5. **Отмена заказа**: только в течение 5 минут, товары возвращаются на склад
6. **Бронирование слотов**: при самовывозе слот бронируется, при отмене — освобождается
7. **Чёрный список**: блокирует возможность добавления в корзину
8. **Адаптивный UI**: Tailwind CSS с responsive классами (sm:, md:, lg:)
9. **Анимации**: Vue transitions для плавного появления элементов
10. **Глобальное состояние**: composables с реактивными ref для корзины и избранного

---

## 🎯 Ключевые файлы для понимания

### Backend

- `backend/app/main.py` — точка входа, подключение роутеров
- `backend/app/api/v1/endpoints/orders.py` — логика создания заказа, FIFO, бронирование слотов
- `backend/app/api/v1/endpoints/cart.py` — управление корзиной, проверки лимитов
- `backend/app/api/v1/endpoints/shared_cart.py` — общая корзина
- `backend/app/models/*.py` — все модели данных

### Frontend

- `src/router/router.js` — маршруты и guards
- `src/composables/useCart.js` — состояние корзины
- `src/views/CartPage.vue` — самая сложная страница (доставка, оплата, общая корзина, оформление)
- `src/views/HomePage.vue` — каталог с фильтрами
- `src/components/CardList.vue` — отображение товаров, фильтрация по датам
- `src/components/Header.vue` — навигация, поиск, уведомления менеджера
