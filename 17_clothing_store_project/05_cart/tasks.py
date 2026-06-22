"""
Этап 05. Корзина
"""

from importlib import import_module

domain = import_module("17_clothing_store_project.01_domain_models.tasks")
Product = domain.Product
ProductStock = domain.ProductStock


class CartItem:
    """Позиция корзины."""
    def __init__(self, product, size, quantity):
        if quantity <= 0:
            raise ValueError("Количество должно быть положительным")
        self.product = product
        self.size = size
        self.quantity = quantity
        self.price_per_unit = product.price  # фиксируем цену на момент добавления

    def total_price(self):
        return self.price_per_unit * self.quantity


class Cart:
    """Корзина покупателя (живёт в памяти)."""
    def __init__(self, customer_id):
        self.customer_id = customer_id
        self._items = []  # список CartItem
        self._promo_code = None  # ссылка на объект промокода (из этапа 07)

    def add_item(self, product, size, quantity, stock_repo=None):
        """
        Добавляет товар в корзину.
        Проверяет доступность через stock_repo (если передан).
        """
        if quantity <= 0:
            raise ValueError("Количество должно быть положительным")

        # Проверка остатка
        if stock_repo:
            stock = stock_repo.get_by_product_and_size(product.product_id, size)
            if stock is None or stock.quantity < quantity:
                raise ValueError(f"Недостаточно товара размера {size}. Доступно: {stock.quantity if stock else 0}")

        # Если уже есть такая позиция (товар+размер) – увеличиваем количество
        for item in self._items:
            if item.product.product_id == product.product_id and item.size == size:
                new_qty = item.quantity + quantity
                if stock_repo:
                    stock = stock_repo.get_by_product_and_size(product.product_id, size)
                    if stock and stock.quantity < new_qty:
                        raise ValueError(f"Недостаточно товара размера {size}. Доступно: {stock.quantity}")
                item.quantity = new_qty
                return

        # Новая позиция
        self._items.append(CartItem(product, size, quantity))

    def change_quantity(self, product_id, size, new_quantity, stock_repo=None):
        """Изменяет количество у позиции. Если new_quantity == 0, удаляет."""
        if new_quantity < 0:
            raise ValueError("Количество не может быть отрицательным")
        for item in self._items:
            if item.product.product_id == product_id and item.size == size:
                if new_quantity == 0:
                    self._items.remove(item)
                    return
                if stock_repo:
                    stock = stock_repo.get_by_product_and_size(product_id, size)
                    if stock and stock.quantity < new_quantity:
                        raise ValueError(f"Недостаточно товара размера {size}. Доступно: {stock.quantity}")
                item.quantity = new_quantity
                return
        raise ValueError("Позиция не найдена")

    def remove_item(self, product_id, size):
        """Удаляет позицию."""
        for item in self._items:
            if item.product.product_id == product_id and item.size == size:
                self._items.remove(item)
                return
        raise ValueError("Позиция не найдена")

    def get_items(self):
        return self._items.copy()

    def total_sum(self):
        return sum(item.total_price() for item in self._items)

    def clear(self):
        self._items.clear()
        self._promo_code = None

    def apply_promo_code(self, promo_code):
        """Применяет промокод (только сохраняет ссылку, сумма будет пересчитана с учётом скидки)."""
        self._promo_code = promo_code

    def get_promo_code(self):
        return self._promo_code

    def get_final_sum(self, discount_service=None):
        """
        Возвращает итоговую сумму с учётом применённого промокода.
        Если discount_service не передан, возвращает сумму без скидки.
        """
        total = self.total_sum()
        if self._promo_code and discount_service:
            try:
                total = discount_service.apply_promo_code(total, self._promo_code)
            except ValueError:
                # Если промокод не применился, оставляем сумму без изменений
                pass
        return total


# Задание 8: ручная проверка (будет в тестах)