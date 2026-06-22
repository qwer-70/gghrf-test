"""
Этап 03. Репозитории
"""

from importlib import import_module

# Импорт моделей
domain = import_module("17_clothing_store_project.01_domain_models.tasks")
Category = domain.Category
Product = domain.Product
ProductStock = domain.ProductStock
Customer = domain.Customer


class CategoryRepository:
    def __init__(self, connection):
        self.connection = connection

    def add(self, category):
        with self.connection.cursor() as cur:
            cur.execute(
                "INSERT INTO categories (id, name, description) VALUES (%s, %s, %s)",
                (category.category_id, category.name, category.description)
            )
        self.connection.commit()

    def get_by_id(self, category_id):
        with self.connection.cursor() as cur:
            cur.execute("SELECT id, name, description FROM categories WHERE id = %s", (category_id,))
            row = cur.fetchone()
        if row is None:
            return None
        return Category(row[0], row[1], row[2])

    def get_all(self):
        with self.connection.cursor() as cur:
            cur.execute("SELECT id, name, description FROM categories")
            rows = cur.fetchall()
        return [Category(row[0], row[1], row[2]) for row in rows]


class ProductRepository:
    def __init__(self, connection):
        self.connection = connection

    def add(self, product):
        with self.connection.cursor() as cur:
            cur.execute(
                """INSERT INTO products (id, category_id, name, price, color, description, is_active)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (product.product_id, product.category_id, product.name, product.price,
                 product.color, product.description, product.is_active)
            )
        self.connection.commit()

    def get_by_id(self, product_id):
        with self.connection.cursor() as cur:
            cur.execute(
                "SELECT id, category_id, name, price, color, description, is_active FROM products WHERE id = %s",
                (product_id,)
            )
            row = cur.fetchone()
        if row is None:
            return None
        return Product(row[0], row[1], row[2], row[3], row[4], row[5], row[6])

    def get_all(self):
        with self.connection.cursor() as cur:
            cur.execute("SELECT id, category_id, name, price, color, description, is_active FROM products")
            rows = cur.fetchall()
        return [Product(r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rows]

    def update(self, product):
        with self.connection.cursor() as cur:
            cur.execute(
                """UPDATE products SET category_id=%s, name=%s, price=%s, color=%s, description=%s, is_active=%s
                   WHERE id=%s""",
                (product.category_id, product.name, product.price, product.color,
                 product.description, product.is_active, product.product_id)
            )
        self.connection.commit()

    def delete(self, product_id):
        with self.connection.cursor() as cur:
            cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
        self.connection.commit()


class ProductStockRepository:
    def __init__(self, connection):
        self.connection = connection

    def add(self, stock):
        with self.connection.cursor() as cur:
            cur.execute(
                "INSERT INTO product_stocks (id, product_id, size, quantity) VALUES (%s, %s, %s, %s)",
                (stock.stock_id, stock.product_id, stock.size, stock.quantity)
            )
        self.connection.commit()

    def get_by_id(self, stock_id):
        with self.connection.cursor() as cur:
            cur.execute("SELECT id, product_id, size, quantity FROM product_stocks WHERE id = %s", (stock_id,))
            row = cur.fetchone()
        if row is None:
            return None
        return ProductStock(row[0], row[1], row[2], row[3])

    def get_by_product_and_size(self, product_id, size):
        with self.connection.cursor() as cur:
            cur.execute(
                "SELECT id, product_id, size, quantity FROM product_stocks WHERE product_id = %s AND size = %s",
                (product_id, size)
            )
            row = cur.fetchone()
        if row is None:
            return None
        return ProductStock(row[0], row[1], row[2], row[3])

    def get_by_product(self, product_id):
        with self.connection.cursor() as cur:
            cur.execute("SELECT id, product_id, size, quantity FROM product_stocks WHERE product_id = %s", (product_id,))
            rows = cur.fetchall()
        return [ProductStock(r[0], r[1], r[2], r[3]) for r in rows]

    def update_quantity(self, stock_id, new_quantity):
        with self.connection.cursor() as cur:
            cur.execute(
                "UPDATE product_stocks SET quantity = %s WHERE id = %s",
                (new_quantity, stock_id)
            )
        self.connection.commit()

    def delete(self, stock_id):
        with self.connection.cursor() as cur:
            cur.execute("DELETE FROM product_stocks WHERE id = %s", (stock_id,))
        self.connection.commit()


class CustomerRepository:
    def __init__(self, connection):
        self.connection = connection

    def add(self, customer):
        with self.connection.cursor() as cur:
            cur.execute(
                "INSERT INTO customers (id, name, phone, email) VALUES (%s, %s, %s, %s)",
                (customer.customer_id, customer.name, customer.phone, customer.email)
            )
        self.connection.commit()

    def get_by_id(self, customer_id):
        with self.connection.cursor() as cur:
            cur.execute("SELECT id, name, phone, email FROM customers WHERE id = %s", (customer_id,))
            row = cur.fetchone()
        if row is None:
            return None
        return Customer(row[0], row[1], row[2], row[3])

    def get_all(self):
        with self.connection.cursor() as cur:
            cur.execute("SELECT id, name, phone, email FROM customers")
            rows = cur.fetchall()
        return [Customer(r[0], r[1], r[2], r[3]) for r in rows]

    def update(self, customer):
        with self.connection.cursor() as cur:
            cur.execute(
                "UPDATE customers SET name=%s, phone=%s, email=%s WHERE id=%s",
                (customer.name, customer.phone, customer.email, customer.customer_id)
            )
        self.connection.commit()

    def delete(self, customer_id):
        with self.connection.cursor() as cur:
            cur.execute("DELETE FROM customers WHERE id = %s", (customer_id,))
        self.connection.commit()