import requests
import re
import json

import db.items

def get_user_inventory(steam_id):
    req = requests.get(f"https://steamcommunity.com/inventory/{steam_id}/730/2")
    text = json.loads(req.text)
    '''with open ('data.json', 'r', encoding='utf-8') as f:
        text = json.load(f)'''
    
    descs = text['descriptions']
    assets = text['assets']
    
    result = {}
    items = []
    item_names = db.items.get_all_names()
    
    for asset in assets:
        items.append(asset['classid'])
    
    for item in descs:
        if item['tradable'] and item['marketable'] and item["market_hash_name"].lower() in item_names:
            result[item["market_hash_name"].lower()] = items.count(item["classid"])
    
    return result

def get_item_price(currency_id, item_name):
    req = requests.get(f'https://steamcommunity.com/market/priceoverview/?currency={currency_id}&appid=730&market_hash_name={item_name.title().replace(" ", "%20").replace("&", "%26")}')
    price = float(re.sub("[^0-9.]", "", json.loads(req.text)['median_price']))
    return price