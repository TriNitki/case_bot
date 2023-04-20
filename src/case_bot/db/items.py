import psycopg2

from config import dbname, user, password, host

conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
cursor = conn.cursor()


# Принимает аргумент названия предмета и возвращает его id
def get_id(item_name):
    cursor.execute(f"SELECT item_id FROM items WHERE name = '{item_name}'")
    item_id = cursor.fetchone()
    return None if item_id == None else item_id[0]

def get_all_names():
    cursor.execute("SELECT name FROM items")
    item_names = [item[0] for item in cursor.fetchall()]
    return item_names

def get_name(item_id):
    cursor.execute(f"SELECT name FROM items WHERE item_id = {item_id}")
    item_name = cursor.fetchone()
    return None if item_name == None else item_name[0]