-- Этап 02. SQL-схема проекта

-- Таблица категорий
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT
);

-- Таблица товаров
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    name TEXT NOT NULL,
    price INTEGER NOT NULL CHECK (price >= 0),
    color TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Таблица остатков по размерам
CREATE TABLE IF NOT EXISTS product_stocks (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    size TEXT NOT NULL CHECK (size IN ('XS','S','M','L','XL','XXL')),
    quantity INTEGER NOT NULL CHECK (quantity >= 0)
);

-- Таблица покупателей
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL CHECK (email LIKE '%@%')
);

-- Таблица заказов (этап 06)
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'created' CHECK (status IN ('created','paid','shipped','completed','cancelled')),
    original_total INTEGER NOT NULL CHECK (original_total >= 0),
    discount INTEGER NOT NULL DEFAULT 0 CHECK (discount >= 0),
    final_total INTEGER NOT NULL CHECK (final_total >= 0)
);

-- Таблица позиций заказа (этап 06)
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    product_name TEXT NOT NULL,
    size TEXT NOT NULL CHECK (size IN ('XS','S','M','L','XL','XXL')),
    price_per_unit INTEGER NOT NULL CHECK (price_per_unit >= 0),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    total_price INTEGER NOT NULL CHECK (total_price >= 0)
);

-- Таблица адресов доставки (этап 07)
CREATE TABLE IF NOT EXISTS addresses (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    country TEXT NOT NULL,
    city TEXT NOT NULL,
    street TEXT NOT NULL,
    building TEXT NOT NULL,
    apartment TEXT,
    is_default BOOLEAN NOT NULL DEFAULT FALSE
);

-- Таблица промокодов (этап 07)
CREATE TABLE IF NOT EXISTS promo_codes (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    discount_percent INTEGER NOT NULL CHECK (discount_percent BETWEEN 0 AND 100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    min_order_sum INTEGER NOT NULL CHECK (min_order_sum >= 0)
);