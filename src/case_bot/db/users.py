import psycopg2
from datetime import datetime

from config import dbname, user, password, host
import db.logs

conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
cursor = conn.cursor()


# Создает запись о пользователе, если таковой нет
def create(user_id):
    cursor.execute(f"SELECT user_id FROM users WHERE user_id = {user_id}")
    
    users_id = cursor.fetchone()
    if users_id == None:
        cursor.execute(f"INSERT INTO users VALUES({user_id})")
        conn.commit()


def get_stats(user_id):
    cursor.execute(f"SELECT income, expense, currency_id FROM users WHERE user_id = {user_id}")
    try:
        stats = cursor.fetchall()[0]
        return {'income': stats[0], 'expense': stats[1], 'currency_id': stats[2]}
    except:
        return None
    

def get_steamid(user_id):
    cursor.execute(f"""
                    SELECT steam_id
                    FROM users
                    WHERE user_id = {user_id};
                    """)
    
    steam_id = cursor.fetchone()
    return None if steam_id == None else steam_id[0]


def add_expense(user_id, value):
    cursor.execute(f"""
                    UPDATE users
                    SET expense = expense + {value}
                    WHERE user_id = {user_id};
                    """)
    conn.commit()

def add_income(user_id, value):
    cursor.execute(f"""
                    UPDATE users
                    SET income = income + {value}
                    WHERE user_id = {user_id};
                    """)
    conn.commit()


def set_assets(assets):
    last_update = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    for asset in assets:
        db.logs.log_user_asset(asset[0], asset[1], last_update)
    
    conn.commit()

def set_steamid(user_id, steam_id):
    cursor.execute(f"""
                    UPDATE users
                    SET steam_id = {steam_id}
                    WHERE user_id = {user_id};
                    """)
    conn.commit()

def set_cur_id(user_id, cur_id):
    cursor.execute(f"""
                    UPDATE users
                    SET currency_id = {cur_id}
                    WHERE user_id = {user_id};
                    """)
    conn.commit()