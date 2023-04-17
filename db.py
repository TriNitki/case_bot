import psycopg2
import os
from datetime import datetime, timedelta

import func as f

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
        
        def steamid(user_id):
            cursor.execute(f"""
                           SELECT steam_id
                           FROM users
                           WHERE user_id = {user_id};
                           """)
            
            steam_id = cursor.fetchone()
            return None if steam_id == None else steam_id[0]
    
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
    
    class set():
        def assets(assets):
            last_update = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            for asset in assets:
                logs.log.user_asset(asset[0], asset[1], last_update)
            
            conn.commit()

        def steamid(user_id, steam_id):
            cursor.execute(f"""
                           UPDATE users
                           SET steam_id = {steam_id}
                           WHERE user_id = {user_id};
                           """)
            conn.commit()
        
        def cur_id(user_id, cur_id):
            cursor.execute(f"""
                           UPDATE users
                           SET currency_id = {cur_id}
                           WHERE user_id = {user_id};
                           """)
            conn.commit()
            

'''OPERATIONS'''
class operations():
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

        def operation(operation_id):
            cursor.execute(f"""SELECT user_id, name, quantity, item_id, price, currency_id, datetime FROM operations WHERE operation_id = {operation_id}""")
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
        def id(cur_name):
            cursor.execute(f"SELECT currency_id FROM currencies WHERE name = '{cur_name}'")
            currencies_id = cursor.fetchone()
            return None if currencies_id == None else currencies_id[0]

        # Принимает аргумент айдишника валюты и возварщает название этой валюты
        def name(cur_id):
            cursor.execute(f"SELECT name FROM currencies WHERE currency_id = {cur_id}")
            currencies_name = cursor.fetchone()
            return None if currencies_name == None else currencies_name[0]
        
        def rate(cur_id):
            cursor.execute(f"SELECT rate_to_usd FROM currency_rates WHERE currency_id = {cur_id}")
            cur_rate = cursor.fetchone()
            return None if cur_rate == None else cur_rate[0]
        
        def symbol(cur_id):
            cursor.execute(f"SELECT symbol FROM currencies WHERE currency_id = {cur_id}")
            symbol = cursor.fetchone()
            return None if symbol == None else symbol[0]
    
    class set():
        def rate(currencies):
            last_update = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            for cur_name, cur_rate in currencies.items():
                cursor.execute(f"""
                               SELECT currency_id
                               FROM currencies 
                               WHERE name = '{cur_name.lower()}'
                               """)
                cur_id = cursor.fetchone()[0]
                
                cursor.execute(f"""
                               SELECT currency_id 
                               FROM currency_rates 
                               WHERE currency_id = {cur_id}
                               """)
                data = cursor.fetchone()
                
                if data == None:
                    cursor.execute(f"""
                                   INSERT INTO currency_rates(currency_id, rate_to_usd, last_update)
                                   VALUES ({cur_id}, {cur_rate}, '{last_update}')
                                   """)
                else:
                    cursor.execute(f"""
                                   UPDATE currency_rates
                                   SET rate_to_usd = {cur_rate}, last_update = '{last_update}'
                                   WHERE currency_id = {cur_id}
                                   """)
    
            conn.commit()


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
                           SELECT user_id, inventory_id, items.name, quantity, item_id
                           FROM inventories
                           LEFT JOIN items USING(item_id)
                           WHERE user_id = {user_id}
                           """)
            inventory = cursor.fetchall()
            return [inventory] if type(inventory) == tuple else inventory
        
        def assets():
            cursor.execute(f"""
                           SELECT user_id, SUM(quantity * price) AS asset
                           FROM inventories
                           LEFT JOIN item_prices USING(item_id)
                           GROUP BY user_id;
                           """)
            assets = cursor.fetchall()
            return assets


'''ITEMS'''
class items():
    class get():
        # Принимает аргумент названия предмета и возвращает его id
        def id(item_name):
            cursor.execute(f"SELECT item_id FROM items WHERE NAME = '{item_name}'")
            item_id = cursor.fetchone()
            return None if item_id == None else item_id[0]

        def all_names():
            cursor.execute("SELECT name FROM items")
            item_names = [item[0] for item in cursor.fetchall()]
            return item_names

'''PRICES'''
class prices():
    class set():
        def price(item_names):
            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            for item_name in item_names:
                price = f.get_price(1, item_name)
                item_id = items.get.id(item_name)
                
                cursor.execute(f"SELECT * FROM item_prices WHERE item_id = {item_id}")
                status = cursor.fetchone()
                
                if status == None:
                    cursor.execute(f"""
                                INSERT INTO item_prices 
                                VALUES(
                                    {item_id}, {price}, '{now}'
                                );
                                """)
                else:
                    cursor.execute(f"""
                                UPDATE item_prices
                                SET price = {price}, last_update = '{now}'
                                WHERE item_id = {item_id};
                                """)
                    
                logs.log.item_price(item_id, price, now)
            
            conn.commit()
    
    class get():
        def price(item_id):
            cursor.execute(f"""
                           SELECT price::FLOAT
                           FROM item_prices
                           WHERE item_id = {item_id}""")
            price = cursor.fetchone()
            return None if price == None else price[0]


class logs():
    class log():
        def item_price(item_id, price, last_update):
            cursor.execute(f"""
                            INSERT INTO hourly_price_logs(item_id, price, update)
                            VALUES(
                                {item_id}, {price}, '{last_update}'
                            );
                            """)
        
        def user_asset(user_id, asset, last_update):
            stats = users.get.stats(user_id)
            cursor.execute(f"""
                            INSERT INTO hourly_asset_logs(user_id, asset, update)
                            VALUES(
                                {user_id}, {asset + stats['income'] - stats['expense']}, '{last_update}'
                            );
                            """)
    
    class get():
        class assets():
            def last24h(user_id):
                now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                cursor.execute(f"""
                               SELECT update, asset
                               FROM hourly_asset_logs
                               WHERE '{now}'-"update"<'1 days' AND user_id = {user_id};
                               """)
                
                assets = cursor.fetchall()
                return assets if len(assets) > 1 else None

        class item_prices():
            def last24h(item_id):
                now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                cursor.execute(f"""
                               SELECT update, price
                               FROM hourly_price_logs
                               WHERE '{now}'-"update"<'1 days' AND item_id = {item_id};
                               """)
                
                prices = cursor.fetchall()
                return prices if len(prices) > 1 else None
            
            def last7d(item_id):
                now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                cursor.execute(f"""
                               SELECT update, price::FLOAT
                               FROM hourly_price_logs
                               WHERE (EXTRACT(HOUR FROM "update") = 12 or EXTRACT(HOUR FROM "update") = 0) 
                               AND item_id = {item_id} AND '{now}'-"update"<'7 days 1 hours';
                               """)
                
                pricee = cursor.fetchall()
                
                for i, value in enumerate(pricee):
                    price = value[1]
                    time = value[0]
                    cursor.execute(f"""
                                   SELECT MAX(price)::FLOAT, MIN(price)::FLOAT
                                   FROM hourly_price_logs
                                   WHERE "update" BETWEEN '{time}' and '{time+timedelta(hours=12)}' AND item_id = {item_id};
                                   """)
                    maxmin = cursor.fetchall()
                    if maxmin != None:
                        pricee[i] = pricee[i] + maxmin[0]
                        if i > 0:
                            pricee[i-1] = pricee[i-1] + (price, )
                    
                pricee[-1] = pricee[-1] + (prices.get.price(item_id), )
                
                return pricee if len(pricee) > 1 else None