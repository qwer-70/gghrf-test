# main.py
# Главный модуль программы: меню, ввод данных, запуск

import sys
from weather import WeatherObservation, WeatherData

def print_menu():
    print("\n--- Система анализа погодных наблюдений ---")
    print("1. Добавить наблюдение")
    print("2. Просмотреть все наблюдения")
    print("3. Рассчитать среднюю температуру")
    print("4. Определить самый тёплый день")
    print("5. Определить самый холодный день")
    print("6. Вывести дни с осадками")
    print("0. Выйти")
    return input("Выберите действие: ")

def input_observation():
    """Запрашивает у пользователя данные и возвращает объект WeatherObservation."""
    try:
        date = input("Введите дату (в любом формате, например, 2026-06-24): ")
        temp = float(input("Введите температуру воздуха (°C): "))
        humidity = float(input("Введите влажность воздуха (%): "))
        wind = float(input("Введите скорость ветра (м/с): "))
        precip = float(input("Введите количество осадков (мм): "))
        return WeatherObservation(date, temp, humidity, wind, precip)
    except ValueError:
        print("Ошибка: введите числовые значения для температуры, влажности, скорости и осадков.")
        return None

def main():
    data = WeatherData()

    # Добавление тестовых данных минимум за 5 дней
    default_obs = [
        ("2026-06-20", 22.5, 65, 3.2, 0.0),
        ("2026-06-21", 24.0, 70, 2.5, 0.5),
        ("2026-06-22", 18.0, 80, 5.0, 10.2),
        ("2026-06-23", 20.0, 75, 4.0, 0.0),
        ("2026-06-24", 25.5, 60, 2.0, 0.0),
    ]
    for date, temp, hum, wind, precip in default_obs:
        obs = WeatherObservation(date, temp, hum, wind, precip)
        try:
            data.add_observation(obs)
        except ValueError as e:
            print(f"Ошибка при добавлении тестовых данных: {e}")

    while True:
        choice = print_menu()
        if choice == '1':
            obs = input_observation()
            if obs:
                try:
                    data.add_observation(obs)
                    print("Наблюдение добавлено.")
                except ValueError as e:
                    print(f"Ошибка: {e}")
        elif choice == '2':
            obs_list = data.get_all()
            if not obs_list:
                print("Нет наблюдений.")
            else:
                for obs in obs_list:
                    print(obs)
        elif choice == '3':
            avg = data.average_temperature()
            if avg is None:
                print("Нет данных для расчёта.")
            else:
                print(f"Средняя температура: {avg:.2f}°C")
        elif choice == '4':
            hot = data.hottest_day()
            if hot is None:
                print("Нет данных.")
            else:
                print(f"Самый тёплый день: {hot}")
        elif choice == '5':
            cold = data.coldest_day()
            if cold is None:
                print("Нет данных.")
            else:
                print(f"Самый холодный день: {cold}")
        elif choice == '6':
            precip_days = data.days_with_precipitation()
            if not precip_days:
                print("Дней с осадками нет.")
            else:
                print("Дни с осадками:")
                for obs in precip_days:
                    print(obs)
        elif choice == '0':
            print("Выход из программы.")
            sys.exit(0)
        else:
            print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()