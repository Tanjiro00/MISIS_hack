import sqlite3


def create_table():
    conn = sqlite3.connect('data.db')

    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE users (
        user_id TEXT,
        category TEXT,
        text TEXT
        )
    ''')


def insert_varible_into_table(user_id, category, text):  # добавление записи
    try:
        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sqlite_insert_with_param = """INSERT INTO users
                                    (user_id, category, text)
                                    VALUES
                                    (?, ?, ?);"""

        cursor.execute(sqlite_insert_with_param, (user_id, category, text))
        sqlite_connection.commit()
        print("Переменные Python успешно вставлены в таблицу users")

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def get_developer_info(user_id):  # выгрузка записи
    try:
        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sql_select_query = """select * from users where user_id = ?"""
        cursor.execute(sql_select_query, (user_id,))
        records = cursor.fetchall()
        user_id, text, category = records[0]
        print("Вывод Telegram ", user_id)
        cursor.close()

        return text, category

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def delete_table():
    try:
        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sql_select_query = """DROP TABLE users"""
        cursor.execute(sql_select_query)
        sqlite_connection.commit()
        print("Запись успешно удалена")
        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")
