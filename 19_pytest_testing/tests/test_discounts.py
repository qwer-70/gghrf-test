import pytest
from importlib import import_module

disc_mod = import_module("17_clothing_store_project.07_users_discounts.tasks")
PromoCode = disc_mod.PromoCode
DiscountService = disc_mod.DiscountService
Address = disc_mod.Address


def test_promo_code_creation():
    p = PromoCode(1, "SALE10", 10, True, 1000)
    assert p.code == "SALE10"
    assert p.discount_percent == 10
    assert p.is_active is True
    assert p.min_order_sum == 1000


def test_promo_code_rejects_invalid_percent():
    with pytest.raises(ValueError):
        PromoCode(1, "BAD", 110)


def test_discount_service_applies_active_promo():
    service = DiscountService()
    promo = PromoCode(1, "SALE10", 10, True, 1000)
    total = 2000
    new_total = service.apply_promo_code(total, promo)
    assert new_total == 1800


def test_discount_service_inactive_promo():
    service = DiscountService()
    promo = PromoCode(1, "SALE10", 10, False, 1000)
    with pytest.raises(ValueError, match="неактивен"):
        service.apply_promo_code(2000, promo)


def test_discount_service_min_sum_not_met():
    service = DiscountService()
    promo = PromoCode(1, "SALE10", 10, True, 1500)
    with pytest.raises(ValueError, match="меньше минимальной"):
        service.apply_promo_code(1200, promo)


def test_discount_service_total_not_negative():
    service = DiscountService()
    promo = PromoCode(1, "BIG", 100, True, 0)
    total = 100
    new_total = service.apply_promo_code(total, promo)
    assert new_total == 0


def test_address_creation():
    addr = Address(1, 1, "Россия", "Москва", "Тверская", "15", "42", True)
    assert addr.country == "Россия"
    assert addr.city == "Москва"