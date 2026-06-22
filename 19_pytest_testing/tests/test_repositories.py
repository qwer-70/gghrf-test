import os
import pytest
import psycopg2
from importlib import import_module

# Для тестов используем отдельную базу
os.environ["DB_NAME"] = "clothing_store_test"
os.environ["DB_USER"] = "postgres"
os.environ["DB_PASSWORD"] = "postgres"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"

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


@pytest.fixture(scope="function")
def connection():
    conn = get_connection()
    create_tables(conn)  # создаём таблицы
    conn.autocommit = False
    yield conn
    # Очистка после теста
    with conn.cursor() as cur:
        cur.execute("DELETE FROM product_stocks")
        cur.execute("DELETE FROM products")
        cur.execute("DELETE FROM categories")
        cur.execute("DELETE FROM customers")
    conn.commit()
    conn.close()


def test_category_repository(connection):
    repo = CategoryRepository(connection)
    cat = Category(1, "Обувь", "Кроссовки, туфли")
    repo.add(cat)
    fetched = repo.get_by_id(1)
    assert fetched is not None
    assert fetched.name == "Обувь"
    all_cats = repo.get_all()
    assert len(all_cats) == 1


def test_product_repository(connection):
    cat_repo = CategoryRepository(connection)
    cat_repo.add(Category(1, "Обувь", ""))
    repo = ProductRepository(connection)
    p = Product(1, 1, "Кроссовки", 5000, "Белый", "Спортивные", True)
    repo.add(p)
    fetched = repo.get_by_id(1)
    assert fetched.name == "Кроссовки"
    all_products = repo.get_all()
    assert len(all_products) == 1
    p.price = 5500
    repo.update(p)
    updated = repo.get_by_id(1)
    assert updated.price == 5500
    repo.delete(1)
    assert repo.get_by_id(1) is None


def test_stock_repository(connection):
    # нужен товар
    cat_repo = CategoryRepository(connection)
    cat_repo.add(Category(1, "Обувь", ""))
    prod_repo = ProductRepository(connection)
    prod_repo.add(Product(1, 1, "Кроссовки", 5000, "Белый", "", True))
    repo = ProductStockRepository(connection)
    stock = ProductStock(1, 1, "M", 10)
    repo.add(stock)
    fetched = repo.get_by_id(1)
    assert fetched.quantity == 10
    fetched_by_prod = repo.get_by_product(1)
    assert len(fetched_by_prod) == 1
    repo.update_quantity(1, 5)
    updated = repo.get_by_id(1)
    assert updated.quantity == 5


def test_customer_repository(connection):
    repo = CustomerRepository(connection)
    c = Customer(1, "Анна", "+7(999)111-22-33", "anna@mail.ru")
    repo.add(c)
    fetched = repo.get_by_id(1)
    assert fetched.name == "Анна"
    all_customers = repo.get_all()
    assert len(all_customers) == 1
    c.name = "Анна Сергеевна"
    repo.update(c)
    updated = repo.get_by_id(1)
    assert updated.name == "Анна Сергеевна"
    repo.delete(1)
    assert repo.get_by_id(1) is None