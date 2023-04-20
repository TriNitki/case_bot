import psycopg2
from datetime import datetime

from config import dbname, user, password, host

conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
cursor = conn.cursor()

def get_id(cur_name):
    cursor.execute(f"SELECT currency_id FROM currencies WHERE name = '{cur_name}'")
    currencies_id = cursor.fetchone()
    return None if currencies_id == None else currencies_id[0]

# Принимает аргумент айдишника валюты и возварщает название этой валюты
def get_name(cur_id):
    cursor.execute(f"SELECT name FROM currencies WHERE currency_id = {cur_id}")
    currencies_name = cursor.fetchone()
    return None if currencies_name == None else currencies_name[0]

def get_rate(cur_id):
    cursor.execute(f"SELECT rate_to_usd FROM currency_rates WHERE currency_id = {cur_id}")
    cur_rate = cursor.fetchone()
    return None if cur_rate == None else cur_rate[0]

def get_symbol(cur_id):
    cursor.execute(f"SELECT symbol FROM currencies WHERE currency_id = {cur_id}")
    symbol = cursor.fetchone()
    return None if symbol == None else symbol[0]


def set_rate(currencies):
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