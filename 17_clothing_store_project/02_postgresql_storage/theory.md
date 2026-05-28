# Этап 02. PostgreSQL: база, схема и подключение

## Зачем этот этап идет перед репозиториями

Репозитории работают с таблицами базы данных. Поэтому перед написанием репозиториев нужно подготовить:

- саму PostgreSQL-базу;
- параметры подключения;
- SQL-схему;
- способ выполнить `schema.sql`;
- проверку, что Python действительно подключается к БД.

На этом этапе еще не нужно писать бизнес-логику магазина. Главная цель - подготовить надежную основу для хранения данных.

## PostgreSQL без ORM

В проекте нельзя использовать ORM: Django ORM, SQLAlchemy ORM, Peewee и похожие инструменты.

Связи между таблицами описываются в SQL через `FOREIGN KEY`, а не в Python-моделях.

Пример:

```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    name TEXT NOT NULL,
    price INTEGER NOT NULL CHECK (price >= 0)
);
```

Python-модель при этом может хранить `category_id` как обычное поле:

```python
class Product:
    def __init__(self, product_id, category_id, name, price):
        self.product_id = product_id
        self.category_id = category_id
        self.name = name
        self.price = price
```

Модель не знает, что `category_id` связан с таблицей `categories`. Это знает база данных и репозиторий.

## Подключение из Python

Стандартная библиотека Python не умеет подключаться к PostgreSQL напрямую. Нужен драйвер.

Один из вариантов:

```bash
pip install "psycopg[binary]"
```

Функцию подключения удобно вынести в отдельный файл, например `database.py`.

```python
import os
import psycopg


def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "clothing_store"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )
```

Пароль не стоит хранить прямо в репозиториях или сервисах. Параметры подключения лучше брать из переменных окружения.

## Базовая схема магазина

Для первых рабочих этапов нужны таблицы:

- `categories` - категории одежды;
- `products` - основные данные товара;
- `product_stocks` - остатки товара по размерам;
- `customers` - покупатели.

Позже схема расширится таблицами адресов, промокодов, заказов и позиций заказов.

Важно: остатки одежды лучше хранить отдельно по размерам. У одного товара может быть разное количество размеров `S`, `M`, `L`.

## Где живут связи

Связи между таблицами должны быть в SQL-схеме:

```sql
category_id INTEGER REFERENCES categories(id)
product_id INTEGER REFERENCES products(id)
customer_id INTEGER REFERENCES customers(id)
```

В Python-моделях достаточно хранить идентификаторы:

- `category_id` у товара;
- `product_id` у остатка;
- `customer_id` у адреса или заказа.

Так модели остаются простыми и не превращаются в ORM.

## Пример из другой области

Представим базу для библиотеки. Книга связана с автором через `author_id`.

```sql
CREATE TABLE authors (
    id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL
);

CREATE TABLE books (
    id INTEGER PRIMARY KEY,
    author_id INTEGER NOT NULL REFERENCES authors(id),
    title TEXT NOT NULL
);
```

А модель книги может выглядеть просто:

```python
class Book:
    def __init__(self, book_id, author_id, title):
        self.book_id = book_id
        self.author_id = author_id
        self.title = title
```

Связь хранится в базе, а объект хранит данные.

## Проверка подключения

После настройки подключения полезно выполнить простой запрос:

```python
with connection.cursor() as cursor:
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
```

Если запрос вернул результат, значит Python видит PostgreSQL и можно переходить к репозиториям.

