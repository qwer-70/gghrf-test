"""
Этап 08. Итоговое консольное приложение
"""

import sys
from importlib import import_module

# Импортируем всё необходимое из предыдущих этапов
storage = import_module("17_clothing_store_project.02_postgresql_storage.tasks")
get_connection = storage.get_connection
create_tables = storage.create_tables

repos = import_module("17_clothing_store_project.03_repositories.tasks")
CategoryRepository = repos.CategoryRepository
ProductRepository = repos.ProductRepository
ProductStockRepository = repos.ProductStockRepository
CustomerRepository = repos.CustomerRepository

catalog_module = import_module("17_clothing_store_project.04_catalog_service.tasks")
CatalogService = catalog_module.CatalogService

cart_module = import_module("17_clothing_store_project.05_cart.tasks")
Cart = cart_module.Cart

orders_module = import_module("17_clothing_store_project.06_orders.tasks")
OrderRepository = orders_module.OrderRepository
OrderService = orders_module.OrderService

users_module = import_module("17_clothing_store_project.07_users_discounts.tasks")
Address = users_module.Address
AddressRepository = users_module.AddressRepository
PromoCode = users_module.PromoCode
PromoCodeRepository = users_module.PromoCodeRepository
DiscountService = users_module.DiscountService

# Импортируем модели для работы
domain = import_module("17_clothing_store_project.01_domain_models.tasks")
Category = domain.Category
Product = domain.Product
ProductStock = domain.ProductStock
Customer = domain.Customer


class ConsoleApp:
    def __init__(self):
        self.connection = None
        self.cart = None
        self.current_customer = None

        # Репозитории
        self.category_repo = None
        self.product_repo = None
        self.stock_repo = None
        self.customer_repo = None
        self.order_repo = None
        self.address_repo = None
        self.promo_repo = None

        # Сервисы
        self.catalog_service = None
        self.order_service = None
        self.discount_service = None

    def connect(self):
        """Устанавливает соединение и инициализирует зависимости."""
        self.connection = get_connection()
        create_tables(self.connection)  # создаём таблицы, если их нет

        self.category_repo = CategoryRepository(self.connection)
        self.product_repo = ProductRepository(self.connection)
        self.stock_repo = ProductStockRepository(self.connection)
        self.customer_repo = CustomerRepository(self.connection)
        self.order_repo = OrderRepository(self.connection)
        self.address_repo = AddressRepository(self.connection)
        self.promo_repo = PromoCodeRepository(self.connection)

        self.catalog_service = CatalogService(self.product_repo, self.category_repo, self.stock_repo)
        self.discount_service = DiscountService()
        self.order_service = OrderService(self.order_repo, self.stock_repo, self.product_repo, self.discount_service)

        # Загружаем стартовые данные
        self._seed_data()

        # Создаём корзину для текущего пользователя (по умолчанию – первый покупатель)
        customers = self.customer_repo.get_all()
        if customers:
            self.current_customer = customers[0]
            self.cart = Cart(self.current_customer.customer_id)
        else:
            print("Нет покупателей в БД. Создайте хотя бы одного через меню.")

    def _seed_data(self):
        """Добавляет стартовые данные, если их нет."""
        # Категории
        if not self.category_repo.get_all():
            categories = [
                Category(1, "Футболки", "Майки и футболки"),
                Category(2, "Худи", "Толстовки и свитшоты"),
                Category(3, "Джинсы", "Джинсы всех фасонов"),
            ]
            for c in categories:
                self.category_repo.add(c)

        # Товары
        if not self.product_repo.get_all():
            products = [
                Product(1, 1, "Футболка классика", 1200, "Белый", "Хлопковая футболка", True),
                Product(2, 1, "Футболка оверсайз", 1500, "Серый", "Свободный крой", True),
                Product(3, 2, "Худи с капюшоном", 2500, "Черный", "Тёплое худи", True),
                Product(4, 2, "Худи легкое", 2000, "Синий", "Для прохладной погоды", False),  # неактивный
                Product(5, 3, "Джинсы скинни", 3000, "Тёмно-синий", "Узкие джинсы", True),
                Product(6, 3, "Джинсы прямые", 2800, "Черный", "Классический крой", True),
            ]
            for p in products:
                self.product_repo.add(p)

        # Остатки
        if not self.stock_repo.get_by_product(1):
            stocks = [
                ProductStock(1, 1, "S", 5),
                ProductStock(2, 1, "M", 10),
                ProductStock(3, 1, "L", 7),
                ProductStock(4, 2, "M", 3),
                ProductStock(5, 2, "L", 6),
                ProductStock(6, 3, "M", 4),
                ProductStock(7, 3, "L", 8),
                ProductStock(8, 5, "S", 2),
                ProductStock(9, 5, "M", 5),
                ProductStock(10, 6, "M", 6),
                ProductStock(11, 6, "L", 9),
            ]
            for s in stocks:
                self.stock_repo.add(s)

        # Покупатели
        if not self.customer_repo.get_all():
            customers = [
                Customer(1, "Алексей Иванов", "+7(999)123-45-67", "alex@mail.ru"),
                Customer(2, "Мария Петрова", "+7(888)987-65-43", "maria@mail.ru"),
            ]
            for c in customers:
                self.customer_repo.add(c)

        # Промокоды
        if not self.promo_repo.get_by_code("SALE10"):
            promos = [
                PromoCode(1, "SALE10", 10, True, 1000),
                PromoCode(2, "DISCOUNT20", 20, True, 2000),
                PromoCode(3, "OLDCODE", 5, False, 0),
            ]
            for p in promos:
                self.promo_repo.add(p)

        # Адреса (пример)
        if not self.address_repo.get_by_customer(1):
            addr = Address(1, 1, "Россия", "Москва", "Тверская", "15", "42", True)
            self.address_repo.add(addr)

    def close(self):
        if self.connection:
            self.connection.close()

    def run(self):
        self.connect()
        try:
            while True:
                self._show_main_menu()
                choice = input("Выберите действие: ").strip()
                if choice == "0":
                    print("До свидания!")
                    break
                elif choice == "1":
                    self._show_catalog()
                elif choice == "2":
                    self._search_products()
                elif choice == "3":
                    self._add_to_cart()
                elif choice == "4":
                    self._show_cart()
                elif choice == "5":
                    self._apply_promo()
                elif choice == "6":
                    self._checkout()
                elif choice == "7":
                    self._order_history()
                else:
                    print("Неизвестная команда. Попробуйте снова.")
        finally:
            self.close()

    def _show_main_menu(self):
        print("\n--- ГЛАВНОЕ МЕНЮ ---")
        print("1. Показать каталог")
        print("2. Поиск товара")
        print("3. Добавить товар в корзину")
        print("4. Просмотр корзины")
        print("5. Применить промокод")
        print("6. Оформить заказ")
        print("7. История заказов")
        print("0. Выход")

    def _show_catalog(self):
        print("\n--- КАТАЛОГ ---")
        products = self.catalog_service.get_active_products()
        if not products:
            print("Нет активных товаров.")
            return
        for p in products:
            print(f"{p.product_id}. {p.name} - {p.price} руб. ({p.color})")
            # показать остатки
            stocks = self.stock_repo.get_by_product(p.product_id)
            if stocks:
                sizes = ", ".join(f"{s.size}: {s.quantity}" for s in stocks)
                print(f"   Размеры: {sizes}")
            else:
                print("   Нет остатков")

    def _search_products(self):
        query = input("Введите текст для поиска: ").strip()
        if not query:
            print("Поисковый запрос не может быть пустым.")
            return
        products = self.catalog_service.search_by_name(query)
        if not products:
            print("Товары не найдены.")
        else:
            print(f"Найдено {len(products)} товаров:")
            for p in products:
                print(f"{p.product_id}. {p.name} - {p.price} руб.")

    def _add_to_cart(self):
        try:
            product_id = int(input("Введите ID товара: "))
            size = input("Введите размер (XS,S,M,L,XL,XXL): ").strip().upper()
            quantity = int(input("Введите количество: "))
        except ValueError:
            print("Некорректный ввод.")
            return

        product = self.product_repo.get_by_id(product_id)
        if not product:
            print("Товар не найден.")
            return
        if not product.is_active:
            print("Товар неактивен.")
            return

        try:
            self.cart.add_item(product, size, quantity, self.stock_repo)
            print("Товар добавлен в корзину.")
        except ValueError as e:
            print("Ошибка:", e)

    def _show_cart(self):
        if not self.cart.get_items():
            print("Корзина пуста.")
            return
        print("\n--- КОРЗИНА ---")
        total = 0
        for idx, item in enumerate(self.cart.get_items(), 1):
            print(f"{idx}. {item.product.name} (размер {item.size}) x {item.quantity} = {item.total_price()} руб.")
            total += item.total_price()
        print(f"Итого: {total} руб.")
        promo = self.cart.get_promo_code()
        if promo:
            print(f"Применён промокод: {promo.code} (скидка {promo.discount_percent}%)")
            final = self.cart.get_final_sum(self.discount_service)
            print(f"Сумма со скидкой: {final} руб.")
        else:
            print("Промокод не применён.")

    def _apply_promo(self):
        code = input("Введите код промокода: ").strip().upper()
        if not code:
            print("Код не может быть пустым.")
            return
        promo = self.promo_repo.get_by_code(code)
        if not promo:
            print("Промокод не найден.")
            return
        try:
            self.cart.apply_promo_code(promo)
            print("Промокод применён.")
        except ValueError as e:
            print("Ошибка:", e)

    def _checkout(self):
        if not self.cart.get_items():
            print("Корзина пуста. Нельзя оформить заказ.")
            return
        if self.current_customer is None:
            print("Не выбран покупатель. Создайте покупателя через меню (не реализовано).")
            return

        try:
            # Получаем следующий ID заказа (для простоты считаем максимальный + 1)
            orders = self.order_repo.get_by_customer(self.current_customer.customer_id)
            next_id = max([o.order_id for o in orders], default=0) + 1

            # Используем транзакцию
            with self.connection:
                order = self.order_service.create_order(
                    self.current_customer.customer_id,
                    self.cart,
                    next_id
                )
                print(f"Заказ №{order.order_id} успешно оформлен на сумму {order.final_total} руб.")
                self.cart = Cart(self.current_customer.customer_id)  # новая корзина
        except ValueError as e:
            print("Ошибка оформления заказа:", e)
            self.connection.rollback()  # откат

    def _order_history(self):
        if self.current_customer is None:
            print("Не выбран покупатель.")
            return
        orders = self.order_repo.get_by_customer(self.current_customer.customer_id)
        if not orders:
            print("У вас нет заказов.")
            return
        print("\n--- ИСТОРИЯ ЗАКАЗОВ ---")
        for order in orders:
            print(f"Заказ №{order.order_id} от {order.created_at.strftime('%d.%m.%Y %H:%M')}")
            print(f"  Сумма: {order.final_total} руб., статус: {order.status}")
            print("  Позиции:")
            for item in order.items:
                print(f"    {item.product_name} ({item.size}) x {item.quantity} = {item.total_price} руб.")
            print("---")


if __name__ == "__main__":
    app = ConsoleApp()
    app.run()