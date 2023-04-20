import psycopg2

from config import dbname, user, password, host
import db.inventories

conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
cursor = conn.cursor()


# Создает новое действие
def new(operation):
    cursor.execute(f"""
                    INSERT INTO operations(user_id, name, quantity, item_id, price, datetime, currency_id)
                    VALUES({operation.user_id}, '{operation.name}', {operation.quantity}, {operation.item_id}, 
                    {operation.price}, '{operation.datetime}', {operation.currency_id});
                    """)
    
    if operation.name == 'sell':
        income = operation.price * operation.quantity
        cursor.execute(f"""UPDATE users SET income = income + {income} WHERE user_id = {operation.user_id}""")
    elif operation.name == 'buy':
        expense = operation.price * operation.quantity
        cursor.execute(f"""UPDATE users SET expense = expense + {expense} WHERE user_id = {operation.user_id}""")

    a_quantity = db.inventories.get_available_quantity(operation.user_id, operation.item_id)

    if a_quantity == None:
        cursor.execute(f"""
                        INSERT INTO inventories(user_id, item_id, quantity)
                        VALUES({operation.user_id}, {operation.item_id}, {operation.quantity});
                        """)
    else:
        db.inventories.edit(operation.user_id, operation.name, operation.quantity, operation.item_id)
    
    conn.commit()

def edit(oper_id, to_edit, value):
    if type(value) is str:
        cursor.execute(f"UPDATE operations SET {to_edit} = '{value}' WHERE operation_id = {oper_id}")
    else:
        cursor.execute(f"UPDATE operations SET {to_edit} = {value} WHERE operation_id = {oper_id}")
    conn.commit()


    # Возвращает список всех транзакций пользователя
def get_list(user_id):
    cursor.execute(f"""
                    SELECT operations.name, operations.quantity, operations.price, currencies.name, items.name, operations.operation_id, rate_to_usd
                    FROM operations
                    LEFT JOIN items USING(item_id)
                    LEFT JOIN currencies USING(currency_id)
                    LEFT JOIN currency_rates USING(currency_id)
                    WHERE user_id = {user_id}
                    ORDER BY operations.datetime DESC;
                    """)
    operations = cursor.fetchall()
    return operations

def get_operation(operation_id):
    cursor.execute(f"""SELECT user_id, name, quantity, item_id, price, currency_id, datetime FROM operations WHERE operation_id = {operation_id}""")
    operation = cursor.fetchone()
    return operation

def get_selection(user_id):
    cursor.execute(f"""SELECT selection FROM users WHERE user_id = {user_id}""")
    selection = cursor.fetchone()
    return None if selection == None else selection[0]

def get_action(user_id):
    cursor.execute(f"""SELECT action FROM users WHERE user_id = {user_id}""")
    action = cursor.fetchone()
    return None if action == None else action[0]


def add_selection(user_id, selection):
    cursor.execute (f"""UPDATE users SET selection = {selection} WHERE user_id = {user_id}""")
    conn.commit()

def add_action(user_id, action):
    cursor.execute(f"""UPDATE users SET action = '{action}' WHERE user_id = {user_id}""")
    conn.commit()


def delete_operation(operation_id):
    cursor.execute(f"""DELETE FROM operations WHERE operation_id = {operation_id}""")
    conn.commit()

def delete_selection(user_id):
    cursor.execute(f"UPDATE users SET selection = NULL WHERE user_id = {user_id}")
    conn.commit()

def delete_action(user_id):
    cursor.execute(f"UPDATE users SET action = NULL WHERE user_id = {user_id}")
    conn.commit()