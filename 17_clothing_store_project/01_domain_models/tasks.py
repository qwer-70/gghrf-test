"""
Этап 01. Доменные модели магазина одежды

Цель: описать основные объекты предметной области без подключения к БД,
меню, репозиториев и сервисов.
"""

# Задание 1: Модель категории
class Category:
    def __init__(self, category_id, name, description=""):
        if category_id <= 0:
            raise ValueError("Идентификатор категории должен быть положительным")
        if not name or not name.strip():
            raise ValueError("Название категории не может быть пустым")
        self.category_id = category_id
        self.name = name.strip()
        self.description = description.strip()


# Задание 2: Модель товара
class Product:
    def __init__(self, product_id, category_id, name, price, color, description="", is_active=True):
        if product_id <= 0:
            raise ValueError("Идентификатор товара должен быть положительным")
        if category_id <= 0:
            raise ValueError("Идентификатор категории должен быть положительным")
        if not name or not name.strip():
            raise ValueError("Название товара не может быть пустым")
        if price < 0:
            raise ValueError("Цена не может быть отрицательной")
        if not color or not color.strip():
            raise ValueError("Цвет не может быть пустым")

        self.product_id = product_id
        self.category_id = category_id
        self.name = name.strip()
        self.price = price
        self.color = color.strip()
        self.description = description.strip()
        self.is_active = is_active

    def change_price(self, new_price):
        if new_price < 0:
            raise ValueError("Новая цена не может быть отрицательной")
        self.price = new_price

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False


# Задание 3: проверки уже встроены в __init__

# Задание 4: Модель остатка по размеру
class ProductStock:
    VALID_SIZES = {"XS", "S", "M", "L", "XL", "XXL"}

    def __init__(self, stock_id, product_id, size, quantity):
        if stock_id <= 0:
            raise ValueError("Идентификатор остатка должен быть положительным")
        if product_id <= 0:
            raise ValueError("Идентификатор товара должен быть положительным")
        if size not in self.VALID_SIZES:
            raise ValueError(f"Недопустимый размер. Допустимы: {', '.join(self.VALID_SIZES)}")
        if quantity < 0:
            raise ValueError("Количество не может быть отрицательным")

        self.stock_id = stock_id
        self.product_id = product_id
        self.size = size
        self.quantity = quantity

    def add_quantity(self, amount):
        if amount < 0:
            raise ValueError("Количество для добавления не может быть отрицательным")
        self.quantity += amount

    def remove_quantity(self, amount):
        if amount < 0:
            raise ValueError("Количество для списания не может быть отрицательным")
        if amount > self.quantity:
            raise ValueError(f"Недостаточно товара на складе. Доступно: {self.quantity}")
        self.quantity -= amount

    def is_available(self, amount=1):
        return self.quantity >= amount


# Задание 6: Модель покупателя
class Customer:
    def __init__(self, customer_id, name, phone, email):
        if customer_id <= 0:
            raise ValueError("Идентификатор покупателя должен быть положительным")
        if not name or not name.strip():
            raise ValueError("Имя покупателя не может быть пустым")
        if not phone or not phone.strip():
            raise ValueError("Телефон не может быть пустым")
        if not email or "@" not in email:
            raise ValueError("Некорректный email")

        self.customer_id = customer_id
        self.name = name.strip()
        self.phone = phone.strip()
        self.email = email.strip()


# Задание 7: ручная проверка (будет выполнена в тестах)