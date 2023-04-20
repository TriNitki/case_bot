import requests
import json
import db.currencies, db.items, db.prices, db.inventories, db.users

from config import cur_apikey

def update_currencies():
    req = requests.get(f'https://api.freecurrencyapi.com/v1/latest?apikey={cur_apikey}&currencies=USD%2CGBP%2CEUR%2CRUB%2CPLN%2CJPY%2CCNY')
    currency_rates = json.loads(req.text)['data']
    db.currencies.set_rate(currency_rates)

def update_items():
    item_names = db.items.get_all_names()
    db.prices.set_price(item_names)

def update_assets():
    assets = db.inventories.get_assets()
    db.users.set_assets(assets)
