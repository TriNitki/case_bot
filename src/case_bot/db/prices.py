import psycopg2
from datetime import datetime

from config import dbname, user, password, host
import db.items, db.logs
import steam
conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
cursor = conn.cursor()




def set_price(item_names):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    for item_name in item_names:
        price = steam.get_item_price(1, item_name)
        item_id = db.items.get_id(item_name)
        
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
            
        db.logs.log_item_price(item_id, price, now)
    
    conn.commit()


def get_price(item_id):
    cursor.execute(f"""
                    SELECT price::FLOAT
                    FROM item_prices
                    WHERE item_id = {item_id}""")
    price = cursor.fetchone()
    return None if price == None else price[0]