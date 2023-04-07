import os
import telebot
import requests
import json
import math

from dotenv import load_dotenv
from telebot import types

import db
import models

load_dotenv()

bot_token = os.getenv("bot_token")
cur_apikey = os.getenv("cur_apikey")

bot = telebot.TeleBot(bot_token)

def get_price(currency_id, item_name):
    req = requests.get(f'https://steamcommunity.com/market/priceoverview/?currency={currency_id}&appid=730&market_hash_name={item_name.title().replace(" ", "%20").replace("&", "%26")}')
    price = float(json.loads(req.text)['median_price'][1:])
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
price:              {operation[2]}
currency:      {operation[3]}''', reply_markup=get_menu('oper'))
    db.operations.add.selection(message.chat.id, operation[5])

def history_operation_edit_handler(message):
    bot.send_message(message.chat.id, 'Что отредактировать?', reply_markup=get_menu('oper_edit'))

def history_operation_edit(message):
    bot.send_message(message.chat.id, 'Изменить на какое значение?')
    db.operations.add.action(message.chat.id, message.text)

def history_operation_delete(message):
    operation_id = db.operations.get.selection(message.chat.id)
    operation = models.operation(db.operations.get.operation(operation_id))
    a_quantity = db.inventories.get.available_quantity(operation.user_id, operation.item_id)

    if operation.name == 'sell':
        db.inventories.edit(operation.user_id, 'buy', operation.quantity, operation.item_id)
        db.operations.delete.operation(operation_id)
    elif a_quantity >= operation.quantity:
        db.inventories.edit(operation.user_id, 'sell', operation.quantity, operation.item_id)
        db.operations.delete.operation(operation_id)
    else:
        print('no del')

def edit_operation_handler(oper_id, to_edit, value):
    operation = models.operation(db.operations.get.operation(operation_id=oper_id))
    
    price_before = operation.quantity * operation.price

    if to_edit == 'price':
        try:
            if float(value) <= 0:
                raise ValueError
        except:
            return 'failure'
        
        
        db.operations.edit(oper_id, 'price', value)
    
    elif to_edit == 'currency':
        cur_id = db.currencies.get.id(value, 'currency_name')
        if cur_id != None:
            db.operations.edit(oper_id, 'currency_id', cur_id)
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
    
    operation = models.operation(db.operations.get.operation(operation_id=oper_id))
    price_after = operation.quantity * operation.price
    
    match operation.name: #operation after
        case 'buy':
            db.users.add.expense(operation.user_id, price_after)
        case 'sell':
            db.users.add.income(operation.user_id, price_after)
    
    return 'success'
    
def get_menu(type, data = None):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    back = types.KeyboardButton('/back')
    delete = types.KeyboardButton('/delete')
    edit = types.KeyboardButton('/edit')

    stats = types.KeyboardButton('Статистика 📊')
    buy = types.KeyboardButton('Купить ➕')
    sell = types.KeyboardButton('Продать ➖')
    history = types.KeyboardButton('История 📄')
    inventory = types.KeyboardButton('Инвентарь 📦')

    operation = types.KeyboardButton('operation')
    item_name = types.KeyboardButton('item_name')
    quantity = types.KeyboardButton('quantity')
    price = types.KeyboardButton('price')
    currency = types.KeyboardButton('currency')

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

def update_currencies():
    req = requests.get(f'https://api.freecurrencyapi.com/v1/latest?apikey={cur_apikey}&currencies=USD%2CGBP%2CEUR%2CRUB%2CPLN%2CJPY%2CCNY')
    currencies = json.loads(req.text)['data']
    db.currencies.set.rate(currencies)

def update_items():
    item_names = [item[0] for item in db.items.get.all_names()]
    db.prices.set.price(item_names)

def update_assets():
    assets = db.inventories.get.assets()
    db.users.set.assets(assets)
        
        
    