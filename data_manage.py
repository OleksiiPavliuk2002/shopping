import sqlite3
from sqlite3 import Error

# подключение к БД
def connect_to_db(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

# создание таблицы БД
def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        conn.commit()
    except Error as e:
        print(e)

# создание таблицы с заметками о товарах
def initialize_note_table(db_file):
    with connect_to_db(db_file) as conn:
        sql = """CREATE TABLE IF NOT EXISTS notes(id integer PRIMARY KEY, note_title text NOT NULL,
        note_content text NOT NULL, date_written data NOT NULL);"""
        create_table(conn, sql)

# вставка записи о товаре
def insert_entry_to_notes(conn, note_entry):
    sql = '''INSERT INTO notes(note_title, note_content, date_written) VALUES(?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, note_entry)
    conn.commit()


# запрос к записям о товарах
def query_notes(conn):
    cur = conn.cursor()
    cur.execute("SELECT * from notes")
    rows = cur.fetchall()
    return rows



# обновление таблицы с записями о товарах
def update_tasks_table(db_file, new_note):
    with connect_to_db(db_file) as conn:
        cursor = conn.cursor()
        sql_update_query = """UPDATE notes SET note_title=?, note_content=?, date_written=? where id=?"""
        cursor.execute(sql_update_query, new_note)
        conn.commit()


# удаление записи о товаре из таблицы
def delete_entry_by_id(db_file, entry_id):
    with connect_to_db(db_file) as conn:
        cursor = conn.cursor()
        sql_delete_query = """DELETE from notes where id=?"""
        cursor.execute(sql_delete_query, (entry_id,))
        conn.commit()
        cursor.close()