import psycopg2
import os
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

dbname = os.getenv("db_name")
user = os.getenv("db_user")
password = os.getenv("db_password")
host = os.getenv("db_host")

conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
cursor = conn.cursor()


'''USERS'''
class users():
    # Создает запись о пользователе, если таковой нет
    def create(user_id):
        cursor.execute(f"SELECT user_id FROM users WHERE user_id = {user_id}")
        
        users_id = cursor.fetchone()
        if users_id == None:
            cursor.execute(f"INSERT INTO users VALUES({user_id})")
            conn.commit()
    
    class get():
        def stats(user_id):
            cursor.execute(f"SELECT income, expense, currency_id FROM users WHERE user_id = {user_id}")
            stats = cursor.fetchall()[0]
            return {'income': stats[0], 'expense': stats[1], 'currency_id': stats[2]}
    
    class add():
        def expense(user_id, value):
            cursor.execute(f"""
                           UPDATE users
                           SET expense = expense + {value}
                           WHERE user_id = {user_id};
                           """)
            conn.commit()
        
        def income(user_id, value):
            cursor.execute(f"""
                           UPDATE users
                           SET income = income + {value}
                           WHERE user_id = {user_id};
                           """)
            conn.commit()


'''OPERATIONS'''
class operations():
    # Создает новое действие
    def new(operation):
        cursor.execute(f"""
                       INSERT INTO operations(user_id, name, quantity, item_id, price, currency_id, datetime)
                       VALUES({operation.user_id}, '{operation.name}', {operation.quantity}, {operation.item_id}, 
                       {operation.price}, {operation.currency_id}, '{operation.datetime}');
                       """)
        
        if operation.name == 'sell':
            income = operation.price * operation.quantity
            cursor.execute(f"""UPDATE users SET income = income + {income} WHERE user_id = {operation.user_id}""")
        elif operation.name == 'buy':
            expense = operation.price * operation.quantity
            cursor.execute(f"""UPDATE users SET expense = expense + {expense} WHERE user_id = {operation.user_id}""")

        a_quantity = inventories.get.available_quantity(operation.user_id, operation.item_id)

        if a_quantity == None:
            cursor.execute(f"""
                           INSERT INTO inventories(user_id, item_id, quantity)
                           VALUES({operation.user_id}, {operation.item_id}, {operation.quantity});
                           """)
        else:
            inventories.edit(operation.user_id, operation.name, operation.quantity, operation.item_id)
        
        conn.commit()

    def edit(oper_id, to_edit, value):
        if type(value) == str:
            cursor.execute(f"UPDATE operations SET {to_edit} = '{value}' WHERE operation_id = {oper_id}")
        else:
            cursor.execute(f"UPDATE operations SET {to_edit} = {value} WHERE operation_id = {oper_id}")
        conn.commit()
    
    class get():
        # Возвращает список всех транзакций пользователя
        def list(user_id):
            cursor.execute(f"""
                           SELECT operations.name, operations.quantity, operations.price, currencies.name, items.name, operations.operation_id
                           FROM operations
                           LEFT JOIN items USING(item_id)
                           LEFT JOIN currencies USING(currency_id)
                           WHERE user_id = {user_id}
                           ORDER BY operations.datetime DESC;
                           """)
            operations = cursor.fetchall()
            return operations

        def operation(operation_id):
            cursor.execute(f"""SELECT * FROM operations WHERE operation_id = {operation_id}""")
            operation = cursor.fetchone()
            return operation

        def selection(user_id):
            cursor.execute(f"""SELECT selection FROM users WHERE user_id = {user_id}""")
            selection = cursor.fetchone()
            return None if selection == None else selection[0]
        
        def action(user_id):
            cursor.execute(f"""SELECT action FROM users WHERE user_id = {user_id}""")
            action = cursor.fetchone()
            return None if action == None else action[0]
    
    class add():
        def selection(user_id, selection):
            cursor.execute (f"""UPDATE users SET selection = {selection} WHERE user_id = {user_id}""")
            conn.commit()
        
        def action(user_id, action):
            cursor.execute(f"""UPDATE users SET action = '{action}' WHERE user_id = {user_id}""")
            conn.commit()

    class delete():
        def operation(operation_id):
            cursor.execute(f"""DELETE FROM operations WHERE operation_id = {operation_id}""")
            conn.commit()

        def selection(user_id):
            cursor.execute(f"UPDATE users SET selection = NULL WHERE user_id = {user_id}")
            conn.commit()

        def action(user_id):
            cursor.execute(f"UPDATE users SET action = NULL WHERE user_id = {user_id}")
            conn.commit()
    

'''CURRENCIES'''
class currencies():
    class get():
        # Получает 2 аргумента. input_data - информация по которой происходит поиск айди валюты
        #                       data_type - тип данных по котором происходит поиск
        def id(input_data, data_type):
            if data_type == 'currency_name':
                cursor.execute(f"SELECT currency_id FROM currencies WHERE name = '{input_data}'")
            else:
                cursor.execute(f"SELECT currency_id FROM users WHERE user_id = {input_data}")
            currencies_id = cursor.fetchone()
            return None if currencies_id == None else currencies_id[0]

        # Принимает аргумент айдишника валюты и возварщает название этой валюты
        def name(cur_id):
            cursor.execute(f"SELECT name FROM currencies WHERE currency_id = {cur_id}")
            currencies_name = cursor.fetchone()
            return None if currencies_name == None else currencies_name[0]


'''INVENTORY'''
class inventories():
    def edit(user_id, operation_name, quantity, item_id):
        a_quantity = inventories.get.available_quantity(user_id, item_id)
        if a_quantity == None:
            cursor.execute(f"""
                           INSERT INTO inventories(user_id, item_id, quantity)
                           VALUES({user_id}, {item_id}, {quantity});
                           """)
        else:
            if operation_name == 'sell':
                cursor.execute( f"""
                               UPDATE inventories
                               SET quantity = (quantity - {quantity})
                               WHERE user_id = {user_id} AND item_id = {item_id}
                               """)
            else:
                cursor.execute(f"""
                               UPDATE inventories
                               SET quantity = (quantity + {quantity})
                               WHERE user_id = {user_id} AND item_id = {item_id}
                               """)
        conn.commit()
    
    class get():
        # Принимает айди пользователя и айди предмета. Возвращает допустимое количество предметов на продажу
        def available_quantity(user_id, item_id):
            try:
                cursor.execute(f"SELECT quantity FROM inventories WHERE user_id = {user_id} AND item_id = {item_id}")
                quantity = cursor.fetchone()
                return None if quantity == None else quantity[0]
            except:
                return None
        
        def inventory(user_id):
            cursor.execute(f"""
                           SELECT user_id, inventory_id, items.name, quantity
                           FROM inventories
                           LEFT JOIN items USING(item_id)
                           WHERE user_id = {user_id}
                           """)
            inventory = cursor.fetchall()
            return [inventory] if type(inventory) == tuple else inventory


'''ITEMS'''
class items():
    class get():
        # Принимает аргумент названия предмета и возвращает его id
        def id(item_name):
            cursor.execute(f"""SELECT item_id FROM items WHERE NAME = '{item_name}'""")
            item_id = cursor.fetchone()
            return None if item_id == None else item_id[0]

def update_cur(currencies):
    last_update = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    for cur_name, cur_rate in currencies.items():
        cursor.execute(f"""
                       UPDATE currency_rates
                       SET rate_to_usd = {cur_rate}, last_update = '{last_update}'
                       WHERE currency_id = (
                           SELECT currency_id 
                           FROM currencies 
                           WHERE name = '{cur_name.lower()}'
                       );
                       """)
    
    conn.commit()
    
