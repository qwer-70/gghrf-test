# weather.py
# Классы для представления и обработки погодных данных

class WeatherObservation:
    """Класс для представления одного погодного наблюдения."""
    
    def __init__(self, date, temperature, humidity, wind_speed, precipitation):
        self.date = date
        self.temperature = temperature
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.precipitation = precipitation

    def __str__(self):
        return (f"{self.date}: T={self.temperature}°C, H={self.humidity}%, "
                f"W={self.wind_speed} м/с, P={self.precipitation} мм")


class WeatherData:
    """Класс для хранения и анализа набора погодных наблюдений."""
    
    def __init__(self):
        self.observations = []

    def add_observation(self, obs):
        """Добавляет наблюдение с проверкой корректности данных."""
        if not (0 <= obs.humidity <= 100):
            raise ValueError("Влажность должна быть от 0 до 100%")
        if obs.wind_speed < 0:
            raise ValueError("Скорость ветра не может быть отрицательной")
        if obs.precipitation < 0:
            raise ValueError("Количество осадков не может быть отрицательным")
        self.observations.append(obs)

    def get_all(self):
        """Возвращает список всех наблюдений."""
        return self.observations

    def average_temperature(self):
        """Возвращает среднюю температуру по всем наблюдениям, или None, если данных нет."""
        if not self.observations:
            return None
        total = sum(obs.temperature for obs in self.observations)
        return total / len(self.observations)

    def hottest_day(self):
        """Возвращает наблюдение с самой высокой температурой, или None, если данных нет."""
        if not self.observations:
            return None
        return max(self.observations, key=lambda obs: obs.temperature)

    def coldest_day(self):
        """Возвращает наблюдение с самой низкой температурой, или None, если данных нет."""
        if not self.observations:
            return None
        return min(self.observations, key=lambda obs: obs.temperature)

    def days_with_precipitation(self):
        """Возвращает список наблюдений, в которых были осадки (>0)."""
        return [obs for obs in self.observations if obs.precipitation > 0]