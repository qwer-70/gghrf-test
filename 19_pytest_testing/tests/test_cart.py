import pytest
from importlib import import_module

domain = import_module("17_clothing_store_project.01_domain_models.tasks")
Product = domain.Product
ProductStock = domain.ProductStock

cart_mod = import_module("17_clothing_store_project.05_cart.tasks")
Cart = cart_mod.Cart
CartItem = cart_mod.CartItem


@pytest.fixture
def product():
    return Product(1, 1, "Футболка", 1200, "Белый", "", True)


@pytest.fixture
def product2():
    return Product(2, 1, "Худи", 2500, "Черный", "", True)


def test_cart_add_item(product):
    cart = Cart(customer_id=1)
    cart.add_item(product, "M", 2)
    items = cart.get_items()
    assert len(items) == 1
    assert items[0].product == product
    assert items[0].size == "M"
    assert items[0].quantity == 2


def test_cart_add_same_product_size_increases_quantity(product):
    cart = Cart(1)
    cart.add_item(product, "M", 2)
    cart.add_item(product, "M", 3)
    items = cart.get_items()
    assert len(items) == 1
    assert items[0].quantity == 5


def test_cart_different_sizes_are_separate(product):
    cart = Cart(1)
    cart.add_item(product, "M", 2)
    cart.add_item(product, "L", 3)
    items = cart.get_items()
    assert len(items) == 2
    sizes = {item.size for item in items}
    assert sizes == {"M", "L"}


def test_cart_rejects_zero_quantity(product):
    cart = Cart(1)
    with pytest.raises(ValueError, match="положительным"):
        cart.add_item(product, "M", 0)


def test_cart_rejects_negative_quantity(product):
    cart = Cart(1)
    with pytest.raises(ValueError):
        cart.add_item(product, "M", -1)


def test_cart_change_quantity(product):
    cart = Cart(1)
    cart.add_item(product, "M", 2)
    cart.change_quantity(1, "M", 5)
    item = cart.get_items()[0]
    assert item.quantity == 5


def test_cart_change_quantity_to_zero_removes_item(product):
    cart = Cart(1)
    cart.add_item(product, "M", 2)
    cart.change_quantity(1, "M", 0)
    assert len(cart.get_items()) == 0


def test_cart_remove_item(product):
    cart = Cart(1)
    cart.add_item(product, "M", 2)
    cart.remove_item(1, "M")
    assert len(cart.get_items()) == 0


def test_cart_total_sum(product, product2):
    cart = Cart(1)
    cart.add_item(product, "M", 2)
    cart.add_item(product2, "L", 1)
    assert cart.total_sum() == 2*1200 + 2500 == 4900


def test_cart_clear(product):
    cart = Cart(1)
    cart.add_item(product, "M", 2)
    cart.clear()
    assert len(cart.get_items()) == 0


# Тест на проверку остатка (с fake stock repo)
class FakeStockRepo:
    def get_by_product_and_size(self, product_id, size):
        if product_id == 1 and size == "M":
            return ProductStock(1, 1, "M", 3)
        return None


def test_cart_add_with_stock_check(product):
    cart = Cart(1)
    stock_repo = FakeStockRepo()
    cart.add_item(product, "M", 2, stock_repo)  # допустимо
    assert len(cart.get_items()) == 1

    # превышаем остаток
    with pytest.raises(ValueError, match="Недостаточно"):
        cart.add_item(product, "M", 3, stock_repo)