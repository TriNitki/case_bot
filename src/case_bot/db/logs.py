import psycopg2
from datetime import datetime

from config import dbname, user, password, host
import db.users

conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
cursor = conn.cursor()



def log_item_price(item_id, price, last_update):
    cursor.execute(f"""
                    INSERT INTO hourly_price_logs(item_id, price, update)
                    VALUES(
                        {item_id}, {price}, '{last_update}'
                    );
                    """)
    conn.commit()

def log_user_asset(user_id, asset, last_update):
    stats = db.users.get_stats(user_id)
    cursor.execute(f"""
                    INSERT INTO hourly_asset_logs(user_id, asset, update)
                    VALUES(
                        {user_id}, {asset + stats['income'] - stats['expense']}, '{last_update}'
                    );
                    """)
    conn.commit()


def get_assets_last24h(user_id):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cursor.execute(f"""
                    SELECT update, asset
                    FROM hourly_asset_logs
                    WHERE '{now}'-"update"<'1 days' AND user_id = {user_id};
                    """)
    
    assets = cursor.fetchall()
    return assets if len(assets) > 0 else None


def get_assets_last7d(user_id):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cursor.execute(f"""
                    SELECT update, asset
                    FROM hourly_asset_logs
                    WHERE (EXTRACT(HOUR FROM "update") = 12 or EXTRACT(HOUR FROM "update") = 0) 
                    AND user_id = {user_id} AND '{now}'-"update"<'7 days 1 hours';
                    """)
    
    assets = cursor.fetchall()

    return assets if len(assets) > 1 else None


def get_item_prices_last24h(item_id):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cursor.execute(f"""
                    SELECT update, price
                    FROM hourly_price_logs
                    WHERE '{now}'-"update"<'1 days' AND item_id = {item_id};
                    """)
    
    prices = cursor.fetchall()
    return prices if len(prices) > 1 else None

def get_item_prices_last7d(item_id):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cursor.execute(f"""
                    SELECT update, price
                    FROM hourly_price_logs
                    WHERE (EXTRACT(HOUR FROM "update") = 12 or EXTRACT(HOUR FROM "update") = 0) 
                    AND item_id = {item_id} AND '{now}'-"update"<'7 days 1 hours';
                    """)
    
    pricee = cursor.fetchall()
    
    '''for i, value in enumerate(pricee):
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
        
    pricee[-1] = pricee[-1] + (prices.get.price(item_id), )'''
    
    return pricee if len(pricee) > 1 else None