from importlib import import_module

domain = import_module("17_clothing_store_project.01_domain_models.tasks")
Customer = domain.Customer


# Задание 3: Модель адреса
class Address:
    def __init__(self, address_id, customer_id, country, city, street, building, apartment="", is_default=False):
        if address_id <= 0:
            raise ValueError("Идентификатор адреса должен быть положительным")
        if customer_id <= 0:
            raise ValueError("Идентификатор покупателя должен быть положительным")
        if not country or not country.strip():
            raise ValueError("Страна не может быть пустой")
        if not city or not city.strip():
            raise ValueError("Город не может быть пустым")
        if not street or not street.strip():
            raise ValueError("Улица не может быть пустой")
        if not building or not building.strip():
            raise ValueError("Номер дома не может быть пустым")

        self.address_id = address_id
        self.customer_id = customer_id
        self.country = country.strip()
        self.city = city.strip()
        self.street = street.strip()
        self.building = building.strip()
        self.apartment = apartment.strip()
        self.is_default = is_default


# Задание 4: Репозиторий адресов
class AddressRepository:
    def __init__(self, connection):
        self.connection = connection

    def add(self, address):
        with self.connection.cursor() as cur:
            cur.execute(
                """INSERT INTO addresses (id, customer_id, country, city, street, building, apartment, is_default)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (address.address_id, address.customer_id, address.country, address.city,
                 address.street, address.building, address.apartment, address.is_default)
            )
        self.connection.commit()

    def get_by_customer(self, customer_id):
        with self.connection.cursor() as cur:
            cur.execute("SELECT id, customer_id, country, city, street, building, apartment, is_default FROM addresses WHERE customer_id = %s", (customer_id,))
            rows = cur.fetchall()
        return [Address(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]) for r in rows]


# Задание 5: Модель промокода
class PromoCode:
    def __init__(self, promo_id, code, discount_percent, is_active=True, min_order_sum=0):
        if promo_id <= 0:
            raise ValueError("Идентификатор промокода должен быть положительным")
        if not code or not code.strip():
            raise ValueError("Код промокода не может быть пустым")
        if not (0 <= discount_percent <= 100):
            raise ValueError("Процент скидки должен быть от 0 до 100")
        if min_order_sum < 0:
            raise ValueError("Минимальная сумма не может быть отрицательной")

        self.promo_id = promo_id
        self.code = code.strip().upper()
        self.discount_percent = discount_percent
        self.is_active = is_active
        self.min_order_sum = min_order_sum


# Задание 6: Репозиторий промокодов
class PromoCodeRepository:
    def __init__(self, connection):
        self.connection = connection

    def add(self, promo):
        with self.connection.cursor() as cur:
            cur.execute(
                """INSERT INTO promo_codes (id, code, discount_percent, is_active, min_order_sum)
                   VALUES (%s, %s, %s, %s, %s)""",
                (promo.promo_id, promo.code, promo.discount_percent, promo.is_active, promo.min_order_sum)
            )
        self.connection.commit()

    def get_by_code(self, code):
        with self.connection.cursor() as cur:
            cur.execute(
                "SELECT id, code, discount_percent, is_active, min_order_sum FROM promo_codes WHERE code = %s",
                (code.strip().upper(),)
            )
            row = cur.fetchone()
        if row is None:
            return None
        return PromoCode(row[0], row[1], row[2], row[3], row[4])

    def get_all_active(self):
        with self.connection.cursor() as cur:
            cur.execute("SELECT id, code, discount_percent, is_active, min_order_sum FROM promo_codes WHERE is_active = TRUE")
            rows = cur.fetchall()
        return [PromoCode(r[0], r[1], r[2], r[3], r[4]) for r in rows]


# Задание 7: Сервис скидок
class DiscountService:
    def apply_promo_code(self, total_sum, promo_code):
        """Применяет промокод, возвращает новую сумму."""
        if promo_code is None:
            return total_sum
        if not promo_code.is_active:
            raise ValueError("Промокод неактивен")
        if total_sum < promo_code.min_order_sum:
            raise ValueError(f"Сумма заказа ({total_sum}) меньше минимальной ({promo_code.min_order_sum})")
        discount = total_sum * promo_code.discount_percent // 100
        new_total = total_sum - discount
        if new_total < 0:
            new_total = 0
        return new_total