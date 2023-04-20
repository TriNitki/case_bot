import os
import telebot
import requests
import json
import math
import re


from dotenv import load_dotenv
from telebot import types

import db
import models
import graph

load_dotenv()

bot_token = os.getenv("bot_token")
cur_apikey = os.getenv("cur_apikey")

bot = telebot.TeleBot(bot_token)

def get_price(currency_id, item_name):
    req = requests.get(f'https://steamcommunity.com/market/priceoverview/?currency={currency_id}&appid=730&market_hash_name={item_name.title().replace(" ", "%20").replace("&", "%26")}')
    price = float(re.sub("[^0-9.]", "", json.loads(req.text)['median_price']))
    return price

def sell_possibility(user_id, item_id, quantity):
    a_quantity = db.inventories.get.available_quantity(user_id, item_id)
    if a_quantity >= quantity:
        return True
    else:
        return False

def history_operation_selection(message):        
    try:
        operations = db.operations.get.list(message.chat.id)
        operation = operations[int(message.text[3:])-1]
    except:
        bot.send_message(message.chat.id, 'Произошла ошибка.')
        return
    
    bot.send_message(message.chat.id, 'Выберете действие /delete /edit /back')
    bot.send_message(message.chat.id, f'''
operation:    {operation[0]}
item_name: {operation[4]}
quantity:      {operation[1]}
price:              {round(operation[2] * operation[6], 2)}
currency:      {operation[3]}''', reply_markup=get_menu('oper'))
    db.operations.add.selection(message.chat.id, operation[5])

def history_operation_edit_handler(message):
    bot.send_message(message.chat.id, 'Что отредактировать?', reply_markup=get_menu('oper_edit'))

def history_operation_edit(message):
    bot.send_message(message.chat.id, 'Изменить на какое значение?')
    db.operations.add.action(message.chat.id, message.text)

def history_operation_delete(message):
    operation_id = db.operations.get.selection(message.chat.id)
    operation = models.operation(*db.operations.get.operation(operation_id))
    a_quantity = db.inventories.get.available_quantity(operation.user_id, operation.item_id)

    if operation.name == 'sell':
        db.inventories.edit(operation.user_id, 'buy', operation.quantity, operation.item_id)
        db.operations.delete.operation(operation_id)
        db.users.add.income(operation.user_id, -operation.quantity*operation.price)
        return 'success'
    elif a_quantity >= operation.quantity:
        db.inventories.edit(operation.user_id, 'sell', operation.quantity, operation.item_id)
        db.operations.delete.operation(operation_id)
        db.users.add.expense(operation.user_id, -operation.quantity*operation.price)
        return 'success'
    else:
        return 'failure'

def edit_operation_handler(oper_id, to_edit, value):
    operation = models.operation(*db.operations.get.operation(operation_id=oper_id))
    
    price_before = operation.quantity * operation.price

    if to_edit == 'price':
        try:
            if float(value) <= 0:
                raise ValueError
        except:
            return 'failure'
        
        
        db.operations.edit(oper_id, 'price', value)
    
    elif to_edit == 'currency':
        cur_id = db.currencies.get.id(value)
        if cur_id != None:
            db.operations.edit(oper_id, 'currency_id', cur_id)
            db.operations.edit(oper_id, 'price', operation.price * db.currencies.get.rate(operation.currency_id) / db.currencies.get.rate(cur_id))
            
        else:
            return 'failure'
    
    elif to_edit == 'operation':
        a_quantiry = db.inventories.get.available_quantity(operation.user_id, operation.item_id)
        if value not in ['buy', 'sell']:
            return 'failure'

        if value != operation.name:
            if value == 'sell' and a_quantiry <= int(operation.quantity)*2:
                return 'failure'
            db.inventories.edit(operation.user_id, operation_name=value, quantity=operation.quantity*2, item_id=operation.item_id)
            db.operations.edit(oper_id, 'name', value)
        else:
            return 'failure'

    elif to_edit == 'quantity':
        a_quantiry = db.inventories.get.available_quantity(operation.user_id, operation.item_id)

        if not value.isnumeric() or int(value) < 0:
            return 'failure'
        
        if (operation.name == 'buy' and operation.quantity < int(value)) or (operation.name == 'sell' and operation.quantity > int(value)):
            if operation.name == 'buy':
                dif = int(value) - operation.quantity
            else:
                dif = operation.quantity - int(value)
            
            db.inventories.edit(operation.user_id, operation_name='buy', quantity=dif, item_id=operation.item_id)
            db.operations.edit(oper_id, 'quantity', value)
        elif (operation.name == 'buy' and operation.quantity > int(value)) or (operation.name == 'sell' and operation.quantity < int(value)):
            if operation.name == 'buy':
                dif = operation.quantity - int(value)
            else:
                dif = int(value) - operation.quantity
            
            if dif > a_quantiry:
                return 'failure'
            else:
                db.inventories.edit(operation.user_id, operation_name='sell', quantity=dif, item_id=operation.item_id)
                db.operations.edit(oper_id, 'quantity', value)
        else:
            return 'failure'
    
    elif to_edit == 'item_name':
        new_item_id = db.items.get.id(value)

        a_quantiry = db.inventories.get.available_quantity(operation.user_id, operation.item_id)
        new_a_quantiry = db.inventories.get.available_quantity(operation.user_id, new_item_id)
        

        if operation.item_id != new_item_id and new_item_id != None:
            if operation.name == 'buy':
                if a_quantiry >= operation.quantity:
                    db.inventories.edit(operation.user_id, 'buy', operation.quantity, new_item_id)
                    db.inventories.edit(operation.user_id, 'sell', operation.quantity, operation.item_id)
                    db.operations.edit(oper_id, 'item_id', new_item_id)
                else:
                    return 'failure'
            else:
                if new_a_quantiry >= operation.quantity:
                    db.inventories.edit(operation.user_id, 'buy', operation.quantity, operation.item_id)
                    db.inventories.edit(operation.user_id, 'sell', operation.quantity, new_item_id)
                    db.operations.edit(oper_id, 'item_id', new_item_id)
                else:
                    return 'failure'
        else:
            return 'failure'
    else:
        return 'failure'
    
    match operation.name: #operation before
        case 'buy':
            db.users.add.expense(operation.user_id, -price_before)
        case 'sell':
            db.users.add.income(operation.user_id, -price_before)
    
    operation = models.operation(*db.operations.get.operation(operation_id=oper_id))
    price_after = operation.quantity * operation.price
    
    match operation.name: #operation after
        case 'buy':
            db.users.add.expense(operation.user_id, price_after)
        case 'sell':
            db.users.add.income(operation.user_id, price_after)
    
    return 'success'
    
def get_menu(type, data = None):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    back      = types.KeyboardButton('/back')
    delete    = types.KeyboardButton('/delete')
    edit      = types.KeyboardButton('/edit')

    stats     = types.KeyboardButton('Статистика 📊')
    buy       = types.KeyboardButton('Купить ➕')
    sell      = types.KeyboardButton('Продать ➖')
    history   = types.KeyboardButton('История 📄')
    inventory = types.KeyboardButton('Инвентарь 📦')
    
    time_24h  = types.KeyboardButton('За 24 часа 🌒')
    time_7d   = types.KeyboardButton('За неделю 🌓')
    time_30d  = types.KeyboardButton('За месяц 🌔')
    all_time  = types.KeyboardButton('За все время 🌕')

    operation = types.KeyboardButton('operation')
    item_name = types.KeyboardButton('item_name')
    quantity  = types.KeyboardButton('quantity')
    price     = types.KeyboardButton('price')
    currency  = types.KeyboardButton('currency')

    if type == 'opers':
        for i in range(int(len(data)/3)):
            item1 = types.KeyboardButton(data[i*3])
            item2 = types.KeyboardButton(data[i*3+1])
            item3 = types.KeyboardButton(data[i*3+2])
            markup.add(item1, item2, item3)
        last_line = math.ceil(len(data)/3)-1
        if len(data) % 3 == 1:
            markup.add(data[last_line*3])
        elif len(data) % 3 == 2:
            markup.add(data[last_line*3], data[last_line*3+1])
        markup.add(back)
        return markup
    elif type == 'oper':
        markup.add(edit, delete, back)
        return markup
    elif type == 'oper_edit':
        markup.add(operation, item_name, quantity, price, currency)
        return markup
    elif type == 'main':
        markup.add(stats)
        markup.add(buy, sell)
        markup.add(history, inventory)
        return markup
    elif type == 'stats_interval':
        markup.add(time_24h, time_7d, time_30d, all_time)
        return markup

def get_keyboard(type, data = None):
    keyboard = types.InlineKeyboardMarkup()
    
    time_24h  = types.InlineKeyboardButton(text='За 24 часа 🌒', callback_data='timegap_24h')
    time_7d   = types.InlineKeyboardButton(text='За неделю 🌓', callback_data='timegap_7d')
    time_30d  = types.InlineKeyboardButton(text='За месяц 🌔', callback_data='timegap_30d')
    all_time  = types.InlineKeyboardButton(text='За все время 🌕', callback_data='timegap_alltime')

    keyboard.add(time_24h, time_7d, time_30d, all_time)
    return keyboard

def update_currencies():
    req = requests.get(f'https://api.freecurrencyapi.com/v1/latest?apikey={cur_apikey}&currencies=USD%2CGBP%2CEUR%2CRUB%2CPLN%2CJPY%2CCNY')
    currencies = json.loads(req.text)['data']
    db.currencies.set.rate(currencies)

def update_items():
    item_names = db.items.get.all_names()
    db.prices.set.price(item_names)

def update_assets():
    assets = db.inventories.get.assets()
    db.users.set.assets(assets)
        
def get_steam_inventory(steam_id):
    req = requests.get(f"https://steamcommunity.com/inventory/{steam_id}/730/2")
    text = json.loads(req.text)
    '''with open ('data.json', 'r', encoding='utf-8') as f:
        text = json.load(f)'''
    
    descs = text['descriptions']
    assets = text['assets']
    
    result = {}
    items = []
    item_names = db.items.get.all_names()
    
    for asset in assets:
        items.append(asset['classid'])
    
    for item in descs:
        if item['tradable'] and item['marketable'] and item["market_hash_name"].lower() in item_names:
            result[item["market_hash_name"].lower()] = items.count(item["classid"])
    
    return result

def graph_handler(data, cur_id, graph_value, graph_time, item_name=None):
    cur_symbol = db.currencies.get.symbol(cur_id)
    
    if cur_id != 1:
        data = graph_data_to_cur(data, cur_id)
    
    if graph_value == 'item':
        title = f'The price of {item_name} ({graph_time})'
        ylabel = f'Price ({cur_symbol})'
    elif graph_value == 'asset':
        title = f'The price of your assets ({graph_time})'
        ylabel = f'Assets ({cur_symbol})'
    
    if graph_time == '24h':
        new_graph = graph.daily(data, title, ylabel)
    elif graph_time in ['7d', '30d']:
        new_graph = graph.weekly(data, title, ylabel)
    
    return new_graph

def graph_data_to_cur(data, cur_id):
    rate = db.currencies.get.rate(cur_id)
    data = [(item[0], item[1]*rate) for item in data]
    return data

def get_stats_24h_msg(user_id, stats, assets):
    invent = db.inventories.get.inv(user_id)
    item_growth_rates = []
    
    
    for item in invent:
        item_id = item[0]
        item_name = db.items.get.name(item_id).title()
        
        prices = db.logs.get.item_prices.last24h(item_id)
        price_before = prices[0][1]
        price_after = prices[-1][1]
        item_difference = price_after - price_before
        item_g_rate = item_difference/price_before*100
        item_growth_rates.append({'item_name': item_name, 'growth_rate': item_g_rate, 'difference': item_difference, 'quantity': item[1]})
    
    emoji_nums = ['1️⃣', '2️⃣', '3️⃣']
    
    sorted_item_g_rates = sorted(item_growth_rates, key=lambda d: d['growth_rate'], reverse=True)[:3]
    
    cur_symbol = db.currencies.get.symbol(stats["currency_id"])
    cur_rate = db.currencies.get.rate(stats["currency_id"])
    
    item_msg = []
    for i, item in enumerate(sorted_item_g_rates):
        i_p_or_m = '-' if item['difference'] < 0 else '+'
        item_msg.append(f"{emoji_nums[i]}  \
{item['item_name']}\n        ► \
{i_p_or_m}{math.fabs(round(float(item['growth_rate']), 2))}% \
({i_p_or_m}{math.fabs(round(item['difference'] * item['quantity'] * cur_rate, 2))} {cur_symbol}) \
{'📉' if item['growth_rate'] < 0 else '📈'}")
        
    item_msg = '\n'.join(item_msg)
        
    asset_before = assets[0][1]
    asset_after = assets[-1][1]
    difference = asset_after-asset_before
    growth_rate = difference/asset_before*100
    p_or_m = '-' if difference < 0 else '+'

    if len(assets) < 12:
        msg = f"""⁉️ Я еще не успел собрать вашу полную статистику ⁉️

ℹ️ Вот что я пока знаю:

💵 Цена вложений: {round(asset_after * cur_rate, 2)} {cur_symbol}
💳 Расходы: {round(stats['expense'] * cur_rate, 2)} {cur_symbol}

▪️ Самые лучшие активы: 

{item_msg}"""
        return msg
    
    msg = f'''
▪️ Изменения цен на активы за последние 24 часа:

💰 Изменение ({cur_symbol}): {p_or_m}{math.fabs(round(difference * cur_rate, 2))} {cur_symbol}
💯 Изменение (%): {p_or_m}{math.fabs(round(growth_rate, 2))}%

💵 Цена вложений: {round(asset_after * cur_rate, 2)} {cur_symbol}
💳 Расходы: {round(stats['expense'] * cur_rate, 2)} {cur_symbol}

▪️ Самые лучшие активы: 

{item_msg}'''
    return msg

def get_stats_7d_msg(user_id, stats, assets):
    invent = db.inventories.get.inv(user_id)
    item_growth_rates = []
    
    
    for item in invent:
        item_id = item[0]
        item_name = db.items.get.name(item_id).title()
        
        prices = db.logs.get.item_prices.last7d(item_id)
        price_before = prices[0][1]
        price_after = prices[-1][1]
        item_difference = price_after - price_before
        item_g_rate = item_difference/price_before*100
        item_growth_rates.append({'item_name': item_name, 'growth_rate': item_g_rate, 'difference': item_difference, 'quantity': item[1]})
    
    emoji_nums = ['1️⃣', '2️⃣', '3️⃣']
    
    sorted_item_g_rates = sorted(item_growth_rates, key=lambda d: d['growth_rate'], reverse=True)[:3]
    
    cur_symbol = db.currencies.get.symbol(stats["currency_id"])
    cur_rate = db.currencies.get.rate(stats["currency_id"])
    
    item_msg = []
    for i, item in enumerate(sorted_item_g_rates):
        i_p_or_m = '-' if item['difference'] < 0 else '+'
        item_msg.append(f"{emoji_nums[i]}  \
{item['item_name']}\n        ► \
{i_p_or_m}{math.fabs(round(float(item['growth_rate']), 2))}% \
({i_p_or_m}{math.fabs(round(item['difference'] * item['quantity'] * cur_rate, 2))} {cur_symbol}) \
{'📉' if item['growth_rate'] < 0 else '📈'}")
        
    item_msg = '\n'.join(item_msg)
        
    asset_before = assets[0][1]
    asset_after = assets[-1][1]
    difference = asset_after-asset_before
    growth_rate = difference/asset_before*100
    p_or_m = '-' if difference < 0 else '+'

    if len(assets) < 12:
        msg = f"""⁉️ Я еще не успел собрать вашу полную статистику ⁉️

ℹ️ Вот что я пока знаю:

💵 Цена вложений: {round(asset_after * cur_rate, 2)} {cur_symbol}
💳 Расходы: {round(stats['expense'] * cur_rate, 2)} {cur_symbol}

▪️ Самые лучшие активы: 

{item_msg}"""
        return msg
    
    msg = f'''
▪️ Изменения цен на активы за последние 24 часа:

💰 Изменение ({cur_symbol}): {p_or_m}{math.fabs(round(difference * cur_rate, 2))} {cur_symbol}
💯 Изменение (%): {p_or_m}{math.fabs(round(growth_rate, 2))}%

💵 Цена вложений: {round(asset_after * cur_rate, 2)} {cur_symbol}
💳 Расходы: {round(stats['expense'] * cur_rate, 2)} {cur_symbol}

▪️ Самые лучшие активы: 

{item_msg}'''
    return msg