"""
Этап 06. Заказы
"""

from importlib import import_module
from datetime import datetime

domain = import_module("17_clothing_store_project.01_domain_models.tasks")
Product = domain.Product
ProductStock = domain.ProductStock
Customer = domain.Customer

# Импортируем модели корзины и репозитории
cart_module = import_module("17_clothing_store_project.05_cart.tasks")
Cart = cart_module.Cart
CartItem = cart_module.CartItem


class OrderItem:
    """Позиция заказа (снимок данных)."""
    def __init__(self, product_id, product_name, size, price_per_unit, quantity):
        if quantity <= 0:
            raise ValueError("Количество должно быть положительным")
        if price_per_unit < 0:
            raise ValueError("Цена не может быть отрицательной")
        self.product_id = product_id
        self.product_name = product_name
        self.size = size
        self.price_per_unit = price_per_unit
        self.quantity = quantity
        self.total_price = price_per_unit * quantity


class Order:
    """Заказ."""
    STATUSES = ("created", "paid", "shipped", "completed", "cancelled")

    def __init__(self, order_id, customer_id, items, original_total, discount, final_total,
                 status="created", created_at=None):
        if order_id <= 0:
            raise ValueError("Идентификатор заказа должен быть положительным")
        if customer_id <= 0:
            raise ValueError("Идентификатор покупателя должен быть положительным")
        if status not in self.STATUSES:
            raise ValueError(f"Недопустимый статус: {status}")
        if original_total < 0 or discount < 0 or final_total < 0:
            raise ValueError("Суммы не могут быть отрицательными")
        if discount > original_total:
            raise ValueError("Скидка не может превышать исходную сумму")

        self.order_id = order_id
        self.customer_id = customer_id
        self.items = items  # список OrderItem
        self.original_total = original_total
        self.discount = discount
        self.final_total = final_total
        self.status = status
        self.created_at = created_at if created_at else datetime.now()

    def cancel(self):
        if self.status in ("completed", "cancelled"):
            raise ValueError(f"Нельзя отменить заказ со статусом {self.status}")
        self.status = "cancelled"


class OrderRepository:
    def __init__(self, connection):
        self.connection = connection

    def add_order(self, order):
        """Сохраняет заказ и его позиции в БД."""
        with self.connection.cursor() as cur:
            cur.execute(
                """INSERT INTO orders (id, customer_id, created_at, status, original_total, discount, final_total)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (order.order_id, order.customer_id, order.created_at, order.status,
                 order.original_total, order.discount, order.final_total)
            )
            for item in order.items:
                cur.execute(
                    """INSERT INTO order_items (order_id, product_id, product_name, size, price_per_unit, quantity, total_price)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (order.order_id, item.product_id, item.product_name, item.size,
                     item.price_per_unit, item.quantity, item.total_price)
                )
        self.connection.commit()

    def get_by_id(self, order_id):
        with self.connection.cursor() as cur:
            cur.execute("SELECT id, customer_id, created_at, status, original_total, discount, final_total FROM orders WHERE id = %s", (order_id,))
            row = cur.fetchone()
        if row is None:
            return None
        # загружаем позиции
        with self.connection.cursor() as cur:
            cur.execute("SELECT product_id, product_name, size, price_per_unit, quantity, total_price FROM order_items WHERE order_id = %s", (order_id,))
            items_rows = cur.fetchall()
        items = [OrderItem(r[0], r[1], r[2], r[3], r[4]) for r in items_rows]
        return Order(row[0], row[1], items, row[4], row[5], row[6], row[3], row[2])

    def get_by_customer(self, customer_id):
        with self.connection.cursor() as cur:
            cur.execute("SELECT id FROM orders WHERE customer_id = %s", (customer_id,))
            order_ids = cur.fetchall()
        return [self.get_by_id(oid[0]) for oid in order_ids]


class OrderService:
    def __init__(self, order_repo, stock_repo, product_repo, discount_service=None):
        self.order_repo = order_repo
        self.stock_repo = stock_repo
        self.product_repo = product_repo
        self.discount_service = discount_service

    def create_order(self, customer_id, cart, next_order_id):
        """
        Оформляет заказ из корзины.
        Возвращает созданный объект Order.
        Транзакционность обеспечивается на уровне вызова (внешний код управляет commit/rollback).
        """
        if not cart.get_items():
            raise ValueError("Корзина пуста")

        # Проверяем остатки и фиксируем снимок
        order_items = []
        for cart_item in cart.get_items():
            product = cart_item.product
            stock = self.stock_repo.get_by_product_and_size(product.product_id, cart_item.size)
            if stock is None or stock.quantity < cart_item.quantity:
                raise ValueError(f"Недостаточно товара {product.name} размера {cart_item.size}")
            # создаём позицию заказа
            order_items.append(OrderItem(
                product_id=product.product_id,
                product_name=product.name,
                size=cart_item.size,
                price_per_unit=cart_item.price_per_unit,
                quantity=cart_item.quantity
            ))

        original_total = cart.total_sum()
        discount = 0
        final_total = original_total

        # Применяем скидку, если есть
        promo = cart.get_promo_code()
        if promo and self.discount_service:
            try:
                final_total = self.discount_service.apply_promo_code(original_total, promo)
                discount = original_total - final_total
            except ValueError:
                # Если промокод не применился, скидка не действует
                pass

        # Создаём заказ
        order = Order(
            order_id=next_order_id,
            customer_id=customer_id,
            items=order_items,
            original_total=original_total,
            discount=discount,
            final_total=final_total,
            status="created"
        )

        # Сохраняем заказ в БД (этот метод сам делает commit)
        self.order_repo.add_order(order)

        # Списание остатков
        for item in order_items:
            stock = self.stock_repo.get_by_product_and_size(item.product_id, item.size)
            # проверяем ещё раз (на случай параллельных изменений)
            if stock is None or stock.quantity < item.quantity:
                raise ValueError(f"Недостаточно товара для списания (product_id={item.product_id}, size={item.size})")
            stock.remove_quantity(item.quantity)
            self.stock_repo.update_quantity(stock.stock_id, stock.quantity)

        # Очищаем корзину (внешний код может это сделать)
        cart.clear()

        return order