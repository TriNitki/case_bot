import os
import telebot
import math
import matplotlib.pyplot as plt


from dotenv import load_dotenv
from telebot import types

import models
import db
import func as f

load_dotenv()

#bot
bot_token = os.getenv("bot_token")
bot = telebot.TeleBot(bot_token)

operation = models.operation()

@bot.message_handler(commands=['start'])
def start(message):
    db.users.create(message.chat.id)
    bot.send_message(message.chat.id, f'Добро пожаловать в @CS_CaseBot!', reply_markup=f.get_menu('main'))

@bot.message_handler(content_types=['text'])
def command_handler(message):
    db.users.create(message.chat.id)
    if any(item in message.text for item in ['/b', '/buy', '/buoght', '/s', '/sold','/sell']):
        buysell(message)
    elif any(item in message.text for item in ['/stats', 'Статистика 📊']):
        stats(message)
    elif any(item in message.text for item in ['/history', '/h', 'История 📄']):
        history(message)
    elif any(item in message.text for item in ['/inventory', '/inv', 'Инвентарь 📦']):
        inventory(message)

# add buy or sell operation
def buysell(message):
    operation.define(message)

    if operation.possibility:
        db.operations.new(operation)
        bot.send_message(message.chat.id, f'Вы успешно {"продали" if operation.name == "sell" else "купили"} {operation.item_name.title()} в количестве {operation.quantity} на сумму {round(operation.quantity * operation.price, 2)} {operation.currency_name}!')
    else:
        bot.send_message(message.chat.id, f'Введена неверная команда или количество!')

# show info about user
def stats(message):
    stats = db.users.get.stats(message.chat.id)
    inv = db.inventories.get.inventory(message.chat.id)

    profit = float(stats['income'] - stats['expense'])
    for item in inv:
        profit += item[3] * f.get_price(stats['currency_id'], item[2])
    
    profit = round(profit, 2)
    
    if profit < 0:
        bot.send_message(message.chat.id, f'Твои расходы: {math.fabs(profit)} usd 📉')
    else:
        bot.send_message(message.chat.id, f'Твои доходы: {profit} usd 📈')


def history(message):
    data = []
    
    operations = db.operations.get.list(message.chat.id)
    msg = 'История всех действий:\n\n'
    try:
        enum_oper = enumerate(operations)
    except:
        bot.send_message(message.chat.id, 'Произошла ошибка')
        return
    for idx, operation in enum_oper:
        msg += f"/op{idx+1}. {operation[0]} {operation[4]} {operation[1]} psc. for {round(operation[2], 2)} {operation[3]} each\n"     #f'/act{idx+1}. {"Покупка" if operation[0] == "buy" else "Продажа"} {operation[4].title()} {operation[1]} {"штука" if operation[1] == 1 else "штук"} на сумму {round(operation[1] * operation[2], 2)}\n'
        data.append(f"/op{idx+1}")
    
    bot.send_message(message.chat.id, msg, reply_markup=f.get_menu('opers', data))
    bot.register_next_step_handler(message, hist_handler)


def inventory(message):
    inventory = [] # Stores all items here

    db_inv = db.inventories.get.inventory(message.chat.id)
    for items in db_inv:
        inv = models.inventory()
        inv.new(items)
        inventory.append(inv)
    
    msg = "Ваш инвентарь:\n"

    for item in inventory:
        msg += f'{item.item_name}: {item.quantity} pcs.\n'
    
    bot.send_message(message.chat.id, msg)
    
# get info about specific item
#@bot.message_handler(commands=['info'])
def stat(message):
    pass

'buy recoil case 5 psc. for 4.00 usd'
def hist_handler(message):
    if '/op' in message.text:
        f.history_operation_selection(message)
        bot.register_next_step_handler(message, hist_handler)
    elif '/edit' in message.text:
        f.history_operation_edit_handler(message)
        bot.register_next_step_handler(message, hist_handler)
    elif '/del' in message.text:
        f.history_operation_delete(message)
        bot.register_next_step_handler(message, hist_handler)
    elif '/back' in message.text:
        if db.operations.get.selection(message.chat.id):
            db.operations.delete.selection(message.chat.id)
            message.text = '/history'
            history(message)
        else:
            bot.send_message(message.chat.id, 'Добро пожаловать в главное меню!', reply_markup = f.get_menu('main'))
            return #return v main
    elif message.text in ['operation', 'item_name', 'quantity', 'price', 'currency']:
        f.history_operation_edit(message)
        bot.register_next_step_handler(message, hist_handler)
    else:
        action = db.operations.get.action(message.chat.id)
        selection = db.operations.get.selection(message.chat.id)
        if action != None and selection != None:
            result = f.edit_operation_handler(selection, action, message.text)
            db.operations.delete.action(message.chat.id)
            db.operations.delete.selection(message.chat.id)
            if result == 'success':
                bot.send_message(message.chat.id, 'Готово!', reply_markup = f.get_menu('main'))
            else:
                bot.send_message(message.chat.id, 'Произошла ошибка', reply_markup = f.get_menu('main'))


def updater():
    f.update_currency()
    db.update_items()


#bot.enable_save_next_step_handlers(delay=2)
#bot.load_next_step_handlers()
bot.polling(none_stop=True)