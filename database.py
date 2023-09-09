import sqlite3
import json


def create_table():
    conn = sqlite3.connect('data.db')

    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE users (
        user_id TEXT,
        name TEXT,
        num_course TEXT,
        institut TEXT,
        program TEXT,
        unions TEXT,
        subjects TEXT,
        anketa TEXT,
        embs TEXT
        )
    ''')
    conn.commit()
    cursor.close()


def insert_varible_into_table(profile_data):  # добавление записи
    try:
        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sqlite_insert_with_param = """INSERT INTO users
                                    (user_id, name, num_course, institut, program, unions, subjects, anketa, embs)
                                    VALUES
                                    (?, ?, ?, ?, ?, ?, ?, ?, ?);"""

        cursor.execute(sqlite_insert_with_param, (
            str(profile_data['user_id']),
            profile_data['name'],
            profile_data['course'],
            profile_data['institut'],
            profile_data['program'],
            json.dumps(profile_data['unions']),
            json.dumps(profile_data['subjects']),
            profile_data['text'],
            json.dumps(profile_data['embs'])
        ))
        sqlite_connection.commit()
        print("Переменные Python успешно вставлены в таблицу users", str(profile_data['user_id']))

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
        print("Вывод Telegram ", user_id)
        cursor.close()
        user_id, name, course, institut, program, unions, subjects, text, embs = records[0]
        unions = json.loads(unions)
        subjects = json.loads(subjects)
        embs = json.loads(embs)
        profile_data = {
            'user_id': user_id, #str
            'name': name, #str
            'course': course,   #str
            'institut': institut, #str
            'program': program,  #str
            'unions': unions,   #list
            'subjects': subjects, #list
            'text': text,        #str
            'embs': embs        #list
        }
        return profile_data

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