"""
Этап 04. Сервис каталога
"""

from importlib import import_module

domain = import_module("17_clothing_store_project.01_domain_models.tasks")
Product = domain.Product


class CatalogService:
    def __init__(self, product_repo, category_repo=None, stock_repo=None):
        self.product_repo = product_repo
        self.category_repo = category_repo
        self.stock_repo = stock_repo

    def get_active_products(self):
        """Возвращает все активные товары."""
        all_products = self.product_repo.get_all()
        return [p for p in all_products if p.is_active]

    def search_by_name(self, query):
        """Поиск по части названия (регистронезависимый)."""
        if not query or not query.strip():
            return []
        query_lower = query.strip().lower()
        active = self.get_active_products()
        result = []
        for p in active:
            if query_lower in p.name.lower():
                result.append(p)
        return result

    def filter_by_category(self, products, category_id):
        """Фильтрует переданный список товаров по категории."""
        return [p for p in products if p.category_id == category_id]

    def filter_by_color(self, products, color):
        """Фильтрует по цвету (регистронезависимый)."""
        if not color or not color.strip():
            return products
        color_lower = color.strip().lower()
        return [p for p in products if color_lower in p.color.lower()]

    def filter_by_size(self, products, size):
        """Фильтрует по наличию товара указанного размера (остаток > 0)."""
        if not size or not self.stock_repo:
            return products
        result = []
        for p in products:
            stock = self.stock_repo.get_by_product_and_size(p.product_id, size)
            if stock and stock.quantity > 0:
                result.append(p)
        return result

    def filter_by_price_range(self, products, min_price=None, max_price=None):
        """Фильтрует по диапазону цены."""
        filtered = products
        if min_price is not None:
            filtered = [p for p in filtered if p.price >= min_price]
        if max_price is not None:
            filtered = [p for p in filtered if p.price <= max_price]
        return filtered

    def sort_by_price(self, products, reverse=False):
        """Сортировка по цене."""
        return sorted(products, key=lambda p: p.price, reverse=reverse)

    def sort_by_name(self, products, reverse=False):
        """Сортировка по названию."""
        return sorted(products, key=lambda p: p.name.lower(), reverse=reverse)

    def get_products_with_filters(self, search_query=None, category_id=None, color=None,
                                  size=None, min_price=None, max_price=None,
                                  sort_by=None, sort_reverse=False):
        """
        Универсальный метод фильтрации и сортировки активных товаров.
        """
        # Начинаем с активных
        products = self.get_active_products()

        # Поиск
        if search_query and search_query.strip():
            products = self.search_by_name(search_query)

        # Фильтры
        if category_id is not None:
            products = self.filter_by_category(products, category_id)
        if color:
            products = self.filter_by_color(products, color)
        if size:
            products = self.filter_by_size(products, size)
        products = self.filter_by_price_range(products, min_price, max_price)

        # Сортировка
        if sort_by == "price":
            products = self.sort_by_price(products, sort_reverse)
        elif sort_by == "name":
            products = self.sort_by_name(products, sort_reverse)

        return products


# Задание 7: ручная проверка (будет в тестах)