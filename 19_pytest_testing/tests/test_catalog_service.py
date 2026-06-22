import pytest
from importlib import import_module

domain = import_module("17_clothing_store_project.01_domain_models.tasks")
Product = domain.Product
ProductStock = domain.ProductStock

catalog = import_module("17_clothing_store_project.04_catalog_service.tasks")
CatalogService = catalog.CatalogService


# Fake-репозитории
class FakeProductRepo:
    def __init__(self, products):
        self.products = products

    def get_all(self):
        return self.products


class FakeStockRepo:
    def __init__(self, stocks):
        self.stocks = stocks

    def get_by_product_and_size(self, product_id, size):
        for s in self.stocks:
            if s.product_id == product_id and s.size == size:
                return s
        return None


@pytest.fixture
def catalog_service():
    products = [
        Product(1, 1, "Футболка", 1200, "Белый", "", True),
        Product(2, 1, "Худи", 2500, "Черный", "", True),
        Product(3, 1, "Шорты", 800, "Синий", "", False),  # неактивный
        Product(4, 2, "Джинсы", 3000, "Тёмно-синий", "", True),
    ]
    stocks = [
        ProductStock(1, 1, "M", 5),
        ProductStock(2, 1, "L", 3),
        ProductStock(3, 2, "M", 0),  # нет остатка
        ProductStock(4, 4, "S", 2),
    ]
    product_repo = FakeProductRepo(products)
    stock_repo = FakeStockRepo(stocks)
    return CatalogService(product_repo, None, stock_repo)


def test_get_active_products(catalog_service):
    active = catalog_service.get_active_products()
    assert len(active) == 3
    assert all(p.is_active for p in active)


def test_search_by_name(catalog_service):
    result = catalog_service.search_by_name("фут")
    assert len(result) == 1
    assert result[0].name == "Футболка"


def test_search_case_insensitive(catalog_service):
    result = catalog_service.search_by_name("ХУДИ")
    assert len(result) == 1
    assert result[0].name == "Худи"


def test_filter_by_category(catalog_service):
    products = catalog_service.get_active_products()
    filtered = catalog_service.filter_by_category(products, 1)
    assert len(filtered) == 2
    assert all(p.category_id == 1 for p in filtered)


def test_filter_by_color(catalog_service):
    products = catalog_service.get_active_products()
    filtered = catalog_service.filter_by_color(products, "белый")
    assert len(filtered) == 1
    assert filtered[0].name == "Футболка"


def test_filter_by_size(catalog_service):
    products = catalog_service.get_active_products()
    filtered = catalog_service.filter_by_size(products, "M")
    # только товары с остатком M > 0: футболка (5), джинсы? у джинсов нет M, худи M = 0
    assert len(filtered) == 1
    assert filtered[0].name == "Футболка"


def test_filter_by_price_range(catalog_service):
    products = catalog_service.get_active_products()
    filtered = catalog_service.filter_by_price_range(products, 1000, 2000)
    assert len(filtered) == 2  # футболка (1200) и худи? худи 2500 нет, шорты неактивны
    assert all(1000 <= p.price <= 2000 for p in filtered)


def test_sort_by_price(catalog_service):
    products = catalog_service.get_active_products()
    sorted_asc = catalog_service.sort_by_price(products)
    prices = [p.price for p in sorted_asc]
    assert prices == sorted(prices)


def test_sort_by_name(catalog_service):
    products = catalog_service.get_active_products()
    sorted_names = catalog_service.sort_by_name(products)
    names = [p.name for p in sorted_names]
    assert names == sorted(names, key=lambda x: x.lower())