import os
import telebot
import decimal
import math

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



# add buy or sell operation
@bot.message_handler(commands=['b', 'buy', 'buoght', 's', 'sold','sell'])
def buy(message):
    db.users.create(message)

    operation.define(message)
    if operation.possibility:
        db.operations.new(operation)
        bot.send_message(message.chat.id, f'Вы успешно {"продали" if operation.name == "sell" else "купили"} {operation.item_name.title()} в количестве {operation.quantity} на сумму {round(operation.quantity * operation.price, 2)} {operation.currency_name}!')
    else:
        bot.send_message(message.chat.id, f'Введена неверная команда или количество!')

# show info about account
@bot.message_handler(commands=['stats'])
def stats(message):
    db.users.create(message)

    profit = decimal.Decimal('0')
    template_item = {"name": None, "currency": None, "buy": 0,  "sell": 0}
    items = []
    operations = db.operations.get.list(message)

    for oper in operations:
        d = next(filter(lambda d: d.get('name') == oper[4] and d.get('currency') == oper[3], items), None)
        if d == None:
            temp = template_item
            temp["name"] = oper[4]
            temp["currency"] = oper[3]
            items.append(temp)
            d = temp
        
        if oper[0] == 'buy':
            profit -= oper[1] * oper[2]
            items[items.index(d)]['buy'] += oper[1]
        else:
            profit += oper[1] * oper[2]
            items[items.index(d)]['sell'] += oper[1]
    
    for item in items:
        if item['buy'] > item['sell']:
            extra = decimal.Decimal(f.get_price(item['currency'], item['name']) * (item['buy'] - item['sell']))
            profit += extra

    profit = round(profit, 2)
    
    if profit < 0:
        bot.send_message(message.chat.id, f'Ты в минусе на {math.fabs(profit)} usd =(')
    else:
        bot.send_message(message.chat.id, f'Твой профит {profit} usd!')

@bot.message_handler(commands=['history'])
def history(message):
    db.users.create(message)

    operations = db.operations.get.list(message)
    msg = 'История всех действий:\n\n'
    for idx, operation in enumerate(operations):
        msg += f"/op{idx+1}. {operation[0]} {operation[4]} {operation[1]} psc. for {round(operation[2], 2)} {operation[3]} each\n"     #f'/act{idx+1}. {"Покупка" if operation[0] == "buy" else "Продажа"} {operation[4].title()} {operation[1]} {"штука" if operation[1] == 1 else "штук"} на сумму {round(operation[1] * operation[2], 2)}\n'

    bot.send_message(message.chat.id, msg)
    bot.register_next_step_handler(message, hist_handler)

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
    elif message.text in ['operation', 'item_name', 'quantity', 'price', 'currency']:
        f.history_operation_edit(message)
        bot.register_next_step_handler(message, hist_handler)
    else:
        action = db.operations.get.action(message.chat.id)
        selection = db.operations.get.selection(message.chat.id)
        print(action, selection)
        if action != None:
            result = f.edit_operation_handler(selection, action, message.text)
            if result == 'success':
                db.operations.delete.action(message.chat.id)
                db.operations.delete.selection(message.chat.id)
                bot.send_message(message.chat.id, 'Готово!')
            else:
                bot.send_message(message.chat.id, 'Произошла ошибка')
    


# get info about specific item
@bot.message_handler(commands=['info'])
def stat(message):
    pass

bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.polling(none_stop=True)