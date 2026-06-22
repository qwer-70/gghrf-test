import pytest
from importlib import import_module
import os
os.environ["DB_NAME"] = "clothing_store_test"

storage = import_module("17_clothing_store_project.02_postgresql_storage.tasks")
get_connection = storage.get_connection
create_tables = storage.create_tables

domain = import_module("17_clothing_store_project.01_domain_models.tasks")
Category = domain.Category
Product = domain.Product
ProductStock = domain.ProductStock
Customer = domain.Customer

repos = import_module("17_clothing_store_project.03_repositories.tasks")
CategoryRepository = repos.CategoryRepository
ProductRepository = repos.ProductRepository
ProductStockRepository = repos.ProductStockRepository
CustomerRepository = repos.CustomerRepository

catalog = import_module("17_clothing_store_project.04_catalog_service.tasks")
CatalogService = catalog.CatalogService

cart_mod = import_module("17_clothing_store_project.05_cart.tasks")
Cart = cart_mod.Cart

orders_mod = import_module("17_clothing_store_project.06_orders.tasks")
OrderRepository = orders_mod.OrderRepository
OrderService = orders_mod.OrderService

disc_mod = import_module("17_clothing_store_project.07_users_discounts.tasks")
PromoCode = disc_mod.PromoCode
PromoCodeRepository = disc_mod.PromoCodeRepository
DiscountService = disc_mod.DiscountService


@pytest.fixture
def full_environment(connection):
    # Создаём все необходимые данные
    cat_repo = CategoryRepository(connection)
    cat_repo.add(Category(1, "Одежда", ""))
    prod_repo = ProductRepository(connection)
    prod_repo.add(Product(1, 1, "Футболка", 1200, "Белый", "", True))
    prod_repo.add(Product(2, 1, "Худи", 2500, "Черный", "", True))
    stock_repo = ProductStockRepository(connection)
    stock_repo.add(ProductStock(1, 1, "M", 5))
    stock_repo.add(ProductStock(2, 2, "L", 3))
    cust_repo = CustomerRepository(connection)
    cust_repo.add(Customer(1, "Покупатель", "+7(999)111-22-33", "buyer@mail.ru"))
    promo_repo = PromoCodeRepository(connection)
    promo_repo.add(PromoCode(1, "TEST10", 10, True, 1000))
    connection.commit()

    return {
        "cat_repo": cat_repo,
        "prod_repo": prod_repo,
        "stock_repo": stock_repo,
        "cust_repo": cust_repo,
        "promo_repo": promo_repo,
    }


def test_full_user_scenario(connection, full_environment):
    prod_repo = full_environment["prod_repo"]
    stock_repo = full_environment["stock_repo"]
    cust_repo = full_environment["cust_repo"]
    promo_repo = full_environment["promo_repo"]

    order_repo = OrderRepository(connection)
    discount_service = DiscountService()
    catalog_service = CatalogService(prod_repo, None, stock_repo)
    order_service = OrderService(order_repo, stock_repo, prod_repo, discount_service)

    # 1. Смотрим каталог
    active = catalog_service.get_active_products()
    assert len(active) == 2

    # 2. Ищем футболку
    found = catalog_service.search_by_name("фут")
    assert len(found) == 1
    product = found[0]

    # 3. Корзина
    cart = Cart(customer_id=1)
    cart.add_item(product, "M", 2, stock_repo)

    # 4. Применяем промокод
    promo = promo_repo.get_by_code("TEST10")
    assert promo is not None
    cart.apply_promo_code(promo)

    # 5. Оформляем заказ
    next_id = 1
    order = order_service.create_order(1, cart, next_id)

    # 6. Проверяем заказ
    assert order.order_id == 1
    assert order.final_total == 2160  # 2*1200 = 2400, скидка 10% = 2160

    # 7. Проверяем остатки
    stock = stock_repo.get_by_product_and_size(1, "M")
    assert stock.quantity == 3  # было 5, списали 2

    # 8. Проверяем, что корзина очищена
    assert len(cart.get_items()) == 0