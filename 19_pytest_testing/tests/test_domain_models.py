import pytest
from importlib import import_module

domain = import_module("17_clothing_store_project.01_domain_models.tasks")
Category = domain.Category
Product = domain.Product
ProductStock = domain.ProductStock
Customer = domain.Customer


def test_category_creation():
    cat = Category(1, "Футболки", "Одежда для верха")
    assert cat.category_id == 1
    assert cat.name == "Футболки"
    assert cat.description == "Одежда для верха"


def test_category_rejects_empty_name():
    with pytest.raises(ValueError, match="Название категории не может быть пустым"):
        Category(1, "")


def test_product_creation():
    p = Product(1, 1, "Футболка", 1200, "Белый", "Хлопок", True)
    assert p.product_id == 1
    assert p.price == 1200
    assert p.is_active is True


def test_product_rejects_negative_price():
    with pytest.raises(ValueError, match="Цена не может быть отрицательной"):
        Product(1, 1, "Футболка", -100, "Белый")


def test_product_change_price():
    p = Product(1, 1, "Футболка", 1200, "Белый")
    p.change_price(1500)
    assert p.price == 1500


def test_product_activate_deactivate():
    p = Product(1, 1, "Футболка", 1200, "Белый", is_active=False)
    assert p.is_active is False
    p.activate()
    assert p.is_active is True
    p.deactivate()
    assert p.is_active is False


def test_stock_creation():
    s = ProductStock(1, 1, "M", 10)
    assert s.size == "M"
    assert s.quantity == 10


def test_stock_rejects_invalid_size():
    with pytest.raises(ValueError, match="Недопустимый размер"):
        ProductStock(1, 1, "XXL", 5)  # недопустим


def test_stock_add_remove():
    s = ProductStock(1, 1, "M", 5)
    s.add_quantity(3)
    assert s.quantity == 8
    s.remove_quantity(2)
    assert s.quantity == 6


def test_stock_remove_too_much():
    s = ProductStock(1, 1, "M", 3)
    with pytest.raises(ValueError, match="Недостаточно товара"):
        s.remove_quantity(5)


def test_customer_creation():
    c = Customer(1, "Иван", "+7(999)123-45-67", "ivan@mail.ru")
    assert c.name == "Иван"
    assert c.email == "ivan@mail.ru"


def test_customer_rejects_invalid_email():
    with pytest.raises(ValueError, match="Некорректный email"):
        Customer(1, "Иван", "+7(999)123-45-67", "ivanmail")