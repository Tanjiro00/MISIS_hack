import sqlite3
import json
import pandas as pd

import database


def create_table_users():
    conn = sqlite3.connect('data.db')

    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE users (
        user_id TEXT,
        username TEXT,
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


def create_table_actions():
    conn = sqlite3.connect('data.db')

    cursor = conn.cursor()

    cursor.execute('''
            CREATE TABLE actions (
            user1 TEXT,
            user2 TEXT,
            action TEXT
            )
        ''')
    conn.commit()
    cursor.close()


def insert_into_actions(user1, user2, action):
    try:
        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sqlite_insert_with_param = """INSERT INTO actions
                                    (user1, user2, action)
                                    VALUES
                                    (?, ?, ?);"""

        cursor.execute(sqlite_insert_with_param, (
            user1,
            user2,
            action
        ))
        sqlite_connection.commit()
        print("Переменные Python успешно вставлены в таблицу actions")

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")

# create_table_actions()
# insert_into_actions('1', '2', 'like')
# insert_into_actions('1', '3', 'like')

def change_action(user1, user2, action):
    try:
        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sqlite_insert_with_param = """
                                        UPDATE actions
                                        SET action = ?
                                        WHERE user1 = ? AND user2 = ?
                                    VALUES
                                    (?, ?, ?);"""

        cursor.execute(sqlite_insert_with_param, (
            action,
            user1,
            user2
        ))
        sqlite_connection.commit()
        print("Переменные Python успешно вставлены в таблицу users")

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def list_of_stop_users(user1):
    try:
        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sqlite_insert_with_param = """
                                        SELECT user2
                                        FROM actions                                        
                                        WHERE user1 = ?;"""

        cursor.execute(sqlite_insert_with_param, (
            user1,
        ))
        records = cursor.fetchall()
        sqlite_connection.commit()
        print("Переменные Python успешно вставлены в таблицу users")

        cursor.close()
        return [rec[0] for rec in records]


    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")



def insert_varible_into_table(profile_data):  # добавление записи
    try:
        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sqlite_insert_with_param = """INSERT INTO users
                                    (user_id, username, name, num_course, institut, program, unions, subjects, anketa, embs)
                                    VALUES
                                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

        cursor.execute(sqlite_insert_with_param, (
            str(profile_data['user_id']),
            profile_data['username'],
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


def update_users(user1, user2, action):
    try:
        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sql_select_query = """UPDATE actions SET action = ? where user1 = ? and user2 = ?"""
        cursor.execute(sql_select_query, (action, user1, user2,))
        sqlite_connection.commit()
        print("Запись успешно удалена")
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
        user_id, username, name, course, institut, program, unions, subjects, text, embs = records[0]
        unions = json.loads(unions)
        subjects = json.loads(subjects)
        embs = json.loads(embs)
        profile_data = {
            'user_id': user_id,  # str
            'username': username, #str
            'name': name,  # str
            'course': course,  # str
            'institut': institut,  # str
            'program': program,  # str
            'unions': unions,  # list
            'subjects': subjects,  # list
            'text': text,  # str
            'embs': embs  # list
        }
        return profile_data

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def delete_user(id):  # удаление записи
    try:
        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sql_select_query = """DELETE from users where user_id = ?"""
        cursor.execute(sql_select_query, (str(id),))
        sqlite_connection.commit()
        print("Запись успешно удалена")
        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def get_user_institut(value, user_id):
    cnx = sqlite3.connect('data.db')
    user_list = list_of_stop_users(user_id)
    if user_list != None:
        user_list = str(user_list)[1:-1]
    else:
        user_list = ''
    sql = f"SELECT * FROM users WHERE user_id not in (0) and institut = '{value}'"
    sql = sql.replace('0', user_list)
    df = pd.read_sql_query(sql, cnx)
    list_columns = ['unions', 'subjects', 'embs']
    for column in list_columns:
        df[column] = df[column].apply(lambda x: json.loads(x))
    return df


def get_user_some(key, value, user_id):
    cnx = sqlite3.connect('data.db')
    user_list = list_of_stop_users(user_id)
    if user_list != None:
        user_list = str(user_list)[1:-1]
    else:
        user_list = ''
    sql = f"SELECT * FROM users WHERE user_id not in (0)"
    sql = sql.replace('0', user_list)
    df = pd.read_sql_query(sql, cnx)
    list_columns = ['unions', 'subjects', 'embs']
    for column in list_columns:
        df[column] = df[column].apply(lambda x: json.loads(x))
    df = df[df[key].apply(lambda x: value in x)]

    return df


def create_df_users():
    cnx = sqlite3.connect('data.db')
    df = pd.read_sql_query("SELECT * FROM users ", cnx)
    list_columns = ['unions', 'subjects', 'embs']
    for column in list_columns:
        df[column] = df[column].apply(lambda x: json.loads(x))
    return df


def get_users_without_users_id(user_id):
    cnx = sqlite3.connect('data.db')
    user_list = list_of_stop_users(user_id)
    if user_list != None:
        user_list = str(user_list)[1:-1]
    else:
        user_list = ''
    sql = "SELECT * FROM users WHERE user_id not in (0)"
    sql = sql.replace('0', user_list)
    df = pd.read_sql_query(sql, cnx)
    list_columns = ['unions', 'subjects', 'embs']
    for column in list_columns:
        df[column] = df[column].apply(lambda x: json.loads(x))
    return df


def create_df_embs(user_id):
    cnx = sqlite3.connect('data.db')
    user_list = list_of_stop_users(user_id)
    if user_list != None:
        user_list = str(user_list)[1:-1]
    else:
        user_list = ''
    sql = "SELECT * FROM users WHERE user_id not in (0)"
    sql = sql.replace('0', user_list)
    df = pd.read_sql_query(sql, cnx)
    list_columns = ['unions', 'subjects', 'embs']
    for column in list_columns:
        df[column] = df[column].apply(lambda x: json.loads(x))
    df = df[['user_id', 'embs', 'subjects']]
    return df


def delete_table(name):
    try:
        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sql_select_query = f"""DROP TABLE {name}"""
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


def delete_user_action(user1, user2):  #удаление записи
    try:
        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sql_select_query = """DELETE from actions where user1 = ? and user2 = ?"""
        cursor.execute(sql_select_query, (user1, user2,))
        sqlite_connection.commit()
        print("Запись успешно удалена")
        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()


def get_offers(user_id):
    try:
        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sql_select_query = """select user1 from actions where user2 = ? and action = 'send_offer'"""
        cursor.execute(sql_select_query, (user_id,))
        records = cursor.fetchall()
        print("Вывод Telegram ", user_id)
        cursor.close()
        return [rec[0] for rec in records]


    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")

#
#


