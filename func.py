import os
import telebot
import requests
import json

from dotenv import load_dotenv

import db

load_dotenv()

bot_token = os.getenv("bot_token")
bot = telebot.TeleBot(bot_token)

def get_price(currency_id, item_name):
    req = requests.get(f'https://steamcommunity.com/market/priceoverview/?currency={currency_id}&appid=730&market_hash_name={item_name.title().replace(" ", "%20")}')
    price = float(json.loads(req.text)['median_price'][1:])
    return price

def sell_possibility(user_id, item_id, quantity):
    a_quantity = db.inventories.get.available_quantity(user_id, item_id)
    if a_quantity >= quantity:
        return True
    else:
        return False

def history_operation_selection(message):
    operations = db.operations.get.list(message)
    operation = operations[int(message.text[3:])-1]
    bot.send_message(message.chat.id, 'Выберете действие /delete /edit /back')
    bot.send_message(message.chat.id, f'''
operation:    {operation[0]}
item_name: {operation[4]}
quantity:      {operation[1]}
price:              {operation[2]}
currency:      {operation[3]}''')
    db.operations.add.selection(message, operation[5])

def history_operation_edit_handler(message):
    bot.send_message(message.chat.id, 'Что отредактировать?')

def history_operation_edit(message):
    bot.send_message(message.chat.id, 'Изменить на какое значение?')
    db.operations.add.action(message.text, message.chat.id)


def history_operation_delete(message):
    operation_id = db.operations.get.selection(message.chat.id)
    operation = db.operations.get.operation(operation_id)
    a_quantity = db.inventories.get.available_quantity(operation[1], operation[4])

    if operation[2] == 'sell':
        db.inventories.edit(operation[1], 'buy', operation[3], operation[4])
        db.operations.delete.operation(operation_id)
    elif a_quantity >= operation[3]:
        db.inventories.edit(operation[1], 'sell', operation[3], operation[4])
        db.operations.delete.operation(operation_id)
    else:
        print('no del')

def edit_operation_handler(oper_id, to_edit, value):
    if to_edit == 'price': #['item_name']
        db.operations.edit(oper_id, 'price', value)
        result = 'success'
    
    elif to_edit == 'currency':
        cur_id = db.currencies.get.id(value, 'currency_name')
        if cur_id != None:
            db.operations.edit(oper_id, 'currency_id', cur_id)
            result = 'success'
        else:
            result = 'failure'
    
    elif to_edit == 'operation':
        operation = db.operations.get.operation(operation_id=oper_id)
        a_quantiry = db.inventories.get.available_quantity(user_id=operation[1], item_id=operation[4])
        if value not in ['buy', 'sell']:
            result = 'failure'
            return result
        print(a_quantiry, value)

        if value != operation[2]:
            print(a_quantiry, value, int(operation[3])*2)
            if value == 'sell' and a_quantiry <= int(operation[3])*2:
                result = 'failure'
                return result
            db.inventories.edit(user_id=operation[1], operation_name=value, quantity=operation[3]*2, item_id=operation[4])
            db.operations.edit(oper_id, 'name', value)
            result = 'success'
        else:
            result = 'failure'

    elif to_edit == 'quantity':
        operation = db.operations.get.operation(operation_id=oper_id)
        a_quantiry = db.inventories.get.available_quantity(user_id=operation[1], item_id=operation[4])
        
        if (operation[2] == 'buy' and operation[3] < int(value)) or (operation[2] == 'sell' and operation[3] > int(value)):
            if operation[2] == 'buy':
                dif = int(value) - operation[3]
            else:
                dif = operation[3] - int(value)
            
            db.inventories.edit(user_id=operation[1], operation_name='buy', quantity=dif, item_id=operation[4])
            db.operations.edit(oper_id, 'quantity', value)
            result = 'success'
        elif (operation[2] == 'buy' and operation[3] > int(value)) or (operation[2] == 'sell' and operation[3] < int(value)):
            if operation[2] == 'buy':
                dif = operation[3] - int(value)
            else:
                dif = int(value) - operation[3]
            
            if dif > a_quantiry:
                result = 'failure'
            else:
                db.inventories.edit(user_id=operation[1], operation_name='sell', quantity=dif, item_id=operation[4])
                db.operations.edit(oper_id, 'quantity', value)
                result = 'success'
        else:
            result = 'failure'
    return result
    
