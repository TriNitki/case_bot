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
    db.operations.get.action(message.text, message.chat.id)


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
    if to_edit == 'price':
        db.operations.edit(oper_id, 'price', value)
