"""
Этап 02. PostgreSQL: база, схема и подключение
"""

import os
import psycopg2

# Задание 1-3: функция подключения
def get_connection():
    """Возвращает подключение к PostgreSQL, используя переменные окружения."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "clothing_store"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )


# Задание 6: функция создания таблиц из schema.sql
def create_tables(connection):
    """Выполняет SQL-скрипт schema.sql для создания таблиц."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        sql = f.read()

    with connection.cursor() as cursor:
        cursor.execute(sql)
    connection.commit()


# Задание 7-8: проверка подключения (можно вызвать отдельно)
if __name__ == "__main__":
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            print("Подключение успешно")
        create_tables(conn)
        print("Таблицы созданы")
        # Проверка наличия таблиц
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'")
            print(f"Таблиц в базе: {cur.fetchone()[0]}")
    except Exception as e:
        print("Ошибка:", e)
    finally:
        conn.close()