import psycopg2

from config import dbname, user, password, host

conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
cursor = conn.cursor()

def edit(user_id, operation_name, quantity, item_id):
    a_quantity = get_available_quantity(user_id, item_id)
    if a_quantity == None:
        cursor.execute(f"""
                        INSERT INTO inventories(user_id, item_id, quantity)
                        VALUES({user_id}, {item_id}, {quantity});
                        """)
    else:
        if operation_name == 'sell':
            cursor.execute(f"""
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


# Принимает айди пользователя и айди предмета. Возвращает допустимое количество предметов на продажу
def get_available_quantity(user_id, item_id):
    try:
        cursor.execute(f"SELECT quantity FROM inventories WHERE user_id = {user_id} AND item_id = {item_id}")
        quantity = cursor.fetchone()
        return None if quantity == None else quantity[0]
    except:
        return None

def get_inventory(user_id):
    cursor.execute(f"""
                    SELECT user_id, inventory_id, items.name, quantity, item_id
                    FROM inventories
                    LEFT JOIN items USING(item_id)
                    WHERE user_id = {user_id}
                    """)
    inventory = cursor.fetchall()
    return [inventory] if type(inventory) == tuple else inventory

def get_assets():
    cursor.execute(f"""
                    SELECT user_id, SUM(quantity * price) AS asset
                    FROM inventories
                    LEFT JOIN item_prices USING(item_id)
                    GROUP BY user_id;
                    """)
    assets = cursor.fetchall()
    return assets

def get_inv(user_id):
    cursor.execute(f"""
                    SELECT item_id, quantity
                    FROM inventories
                    WHERE user_id = {user_id};
                    """)
    inventory = cursor.fetchall()
    return inventory