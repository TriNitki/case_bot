import telebot

from config import bot_token
import db.operations
import db.inventories
import db.users
from markups import get_reply_keyboard
import models

bot = telebot.TeleBot(bot_token)

def operation_selection(message):        
    try:
        operations = db.operations.get_list(message.chat.id)
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
currency:      {operation[3]}''', reply_markup=get_reply_keyboard('oper'))
    db.operations.add_selection(message.chat.id, operation[5])

def operation_edit_handler(message):
    bot.send_message(message.chat.id, 'Что отредактировать?', reply_markup=get_reply_keyboard('oper_edit'))

def operation_edit(message):
    bot.send_message(message.chat.id, 'Изменить на какое значение?')
    db.operations.add_action(message.chat.id, message.text)

def operation_delete(message):
    operation_id = db.operations.get_selection(message.chat.id)
    operation = models.operation(*db.operations.get_operation(operation_id))
    a_quantity = db.inventories.get_available_quantity(operation.user_id, operation.item_id)

    if operation.name == 'sell':
        db.inventories.edit(operation.user_id, 'buy', operation.quantity, operation.item_id)
        db.operations.delete_operation(operation_id)
        db.users.add_income(operation.user_id, -operation.quantity*operation.price)
        return 'success'
    elif a_quantity >= operation.quantity:
        db.inventories.edit(operation.user_id, 'sell', operation.quantity, operation.item_id)
        db.operations.delete_operation(operation_id)
        db.users.add_expense(operation.user_id, -operation.quantity*operation.price)
        return 'success'
    else:
        return 'failure'
