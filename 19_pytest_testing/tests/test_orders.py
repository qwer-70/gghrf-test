import pytest
from importlib import import_module

# Используем тестовую БД (переопределяем переменные)
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

cart_mod = import_module("17_clothing_store_project.05_cart.tasks")
Cart = cart_mod.Cart

orders_mod = import_module("17_clothing_store_project.06_orders.tasks")
OrderRepository = orders_mod.OrderRepository
OrderService = orders_mod.OrderService
OrderItem = orders_mod.OrderItem

disc_mod = import_module("17_clothing_store_project.07_users_discounts.tasks")
DiscountService = disc_mod.DiscountService


@pytest.fixture
def setup_data(connection):
    # Создаём категорию, товары, остатки, покупателя
    cat_repo = CategoryRepository(connection)
    cat_repo.add(Category(1, "Обувь", ""))
    prod_repo = ProductRepository(connection)
    prod_repo.add(Product(1, 1, "Кроссовки", 5000, "Белый", "", True))
    prod_repo.add(Product(2, 1, "Туфли", 4000, "Черный", "", True))
    stock_repo = ProductStockRepository(connection)
    stock_repo.add(ProductStock(1, 1, "M", 5))
    stock_repo.add(ProductStock(2, 2, "L", 3))
    cust_repo = CustomerRepository(connection)
    cust_repo.add(Customer(1, "Покупатель", "+7(999)111-22-33", "buyer@mail.ru"))
    connection.commit()
    return prod_repo, stock_repo, cust_repo


def test_order_creation(connection, setup_data):
    prod_repo, stock_repo, cust_repo = setup_data
    order_repo = OrderRepository(connection)
    discount_service = DiscountService()
    order_service = OrderService(order_repo, stock_repo, prod_repo, discount_service)

    # Создаём корзину
    cart = Cart(customer_id=1)
    product1 = prod_repo.get_by_id(1)
    product2 = prod_repo.get_by_id(2)
    cart.add_item(product1, "M", 2, stock_repo)  # у нас 5
    cart.add_item(product2, "L", 1, stock_repo)  # у нас 3

    next_id = 1
    order = order_service.create_order(1, cart, next_id)

    assert order.order_id == 1
    assert order.customer_id == 1
    assert len(order.items) == 2
    assert order.original_total == 2*5000 + 4000 == 14000
    assert order.discount == 0
    assert order.final_total == 14000
    assert order.status == "created"

    # Проверяем, что заказ сохранился
    saved_order = order_repo.get_by_id(1)
    assert saved_order is not None
    assert saved_order.final_total == 14000

    # Проверяем списание остатков
    stock1 = stock_repo.get_by_product_and_size(1, "M")
    assert stock1.quantity == 3  # было 5, списали 2
    stock2 = stock_repo.get_by_product_and_size(2, "L")
    assert stock2.quantity == 2  # было 3, списали 1


def test_order_rejects_empty_cart(connection, setup_data):
    prod_repo, stock_repo, cust_repo = setup_data
    order_repo = OrderRepository(connection)
    discount_service = DiscountService()
    order_service = OrderService(order_repo, stock_repo, prod_repo, discount_service)

    cart = Cart(customer_id=1)
    with pytest.raises(ValueError, match="Корзина пуста"):
        order_service.create_order(1, cart, 1)


def test_order_rejects_insufficient_stock(connection, setup_data):
    prod_repo, stock_repo, cust_repo = setup_data
    order_repo = OrderRepository(connection)
    discount_service = DiscountService()
    order_service = OrderService(order_repo, stock_repo, prod_repo, discount_service)

    cart = Cart(customer_id=1)
    product = prod_repo.get_by_id(1)
    cart.add_item(product, "M", 10, stock_repo)  # больше чем есть

    with pytest.raises(ValueError, match="Недостаточно"):
        order_service.create_order(1, cart, 1)

    # Убедимся, что заказ не сохранился
    assert order_repo.get_by_id(1) is None