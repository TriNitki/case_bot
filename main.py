import os
import telebot
import math
from datetime import datetime

from PIL import Image


from dotenv import load_dotenv

import models
import db
import func as f
import graph

load_dotenv()

#bot
bot_token = os.getenv("bot_token")
bot = telebot.TeleBot(bot_token)

'''
f.update_currencies()
f.update_items()
f.update_assets()
'''

@bot.message_handler(commands=['start'])
def start(message):
    db.users.create(message.chat.id)
    bot.send_message(message.chat.id, f'Добро пожаловать в @CS_CaseBot!', reply_markup=f.get_menu('main'))

@bot.message_handler(content_types=['text'])
def command_handler(message):
    db.users.create(message.chat.id)
    if any(item in message.text for item in ['/b ', '/buy', '/buoght', '/s ', '/sold','/sell']):
        buysell(message)
    elif any(item in message.text for item in ['/stats', 'Статистика 📊']):
        stats_handler(message)
    elif any(item in message.text for item in ['/history', '/h ', 'История 📄']):
        history(message)
    elif any(item in message.text for item in ['/inventory', '/inv', 'Инвентарь 📦']):
        inventory(message)
    elif any(item in message.text for item in ['/steamid']):
        steamid(message)
    elif any(item in message.text for item in ['/getinv']):
        inv_transfer(message)
    elif any(item in message.text for item in ['/item ']):
        item_stats(message)
    elif any(item in message.text for item in ['/setcur']):
        setcur(message)
    elif any(item in message.text for item in ['/item7d']):
        item_stats_7d(message)

# add buy or sell operation
def buysell(message):
    operation = models.operation()
    operation.define(message)

    if operation.possibility:
        db.operations.new(operation)
        bot.send_message(message.chat.id, f'Вы успешно {"продали" if operation.name == "sell" else "купили"} {operation.item_name.title()} в количестве {operation.quantity} на сумму {round(operation.quantity * operation.price * float(db.currencies.get.rate(operation.currency_id)), 2)}{operation.currency_symbol}!')
    else:
        bot.send_message(message.chat.id, f'Введена неверная команда или количество!')

# show info about user
def stats_handler(message):
    def stats_alltime(message):
        stats = db.users.get.stats(message.chat.id)
        inv = db.inventories.get.inventory(message.chat.id)
        rate = db.currencies.get.rate(stats['currency_id'])

        profit = float(stats['income'] - stats['expense']) * float(rate)
        for item in inv:
            price = db.prices.get.price(item[4])
            if price and rate:
                profit += item[3] * float(price) * float(rate)
        
        profit = round(profit, 2)
        
        cur_symbol = db.currencies.get.symbol(stats["currency_id"])
        
        if profit < 0:
            bot.send_message(message.chat.id, f'Твои расходы: {math.fabs(profit)}{cur_symbol} 📉')
        else:
            bot.send_message(message.chat.id, f'Твои доходы: {profit}{cur_symbol} 📈')
        
        assets = db.logs.get.assets.last24h(user_id=message.chat.id)
        
        new_graph = f.graph_handler(assets, stats["currency_id"], 'asset 24h')
        if new_graph != None:
            bot.send_photo(message.chat.id, new_graph, reply_markup=f.get_menu('main'))
    
    if message.text == 'Статистика 📊':
        msg, new_graph = stats_24h(message.chat.id)
        bot.send_photo(message.chat.id, caption=msg, photo=new_graph, reply_markup=f.get_keyboard(None))

    
def history(message):
    def hist_handler(message):
        if '/op' in message.text:
            f.history_operation_selection(message)
            bot.register_next_step_handler(message, hist_handler)
        elif '/edit' in message.text:
            f.history_operation_edit_handler(message)
            bot.register_next_step_handler(message, hist_handler)
        elif '/del' in message.text:
            result = f.history_operation_delete(message)
            if result == 'success':
                bot.send_message(message.chat.id, 'Готово!')
            else:
                bot.send_message(message.chat.id, 'Произошла ошибка')
            db.operations.delete.selection(message.chat.id)
            message.text = '/history'
            history(message)
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

    data = []
    
    operations = db.operations.get.list(message.chat.id)
    msg = 'История всех действий:\n\n'
    try:
        enum_oper = enumerate(operations)
    except:
        bot.send_message(message.chat.id, 'Произошла ошибка')
        return
    for idx, operation in enum_oper:
        msg += f"/op{idx+1}. {operation[0]} {operation[4]} {operation[1]} psc. for {round(operation[2]*operation[6], 2)} {operation[3]} each\n"     #f'/act{idx+1}. {"Покупка" if operation[0] == "buy" else "Продажа"} {operation[4].title()} {operation[1]} {"штука" if operation[1] == 1 else "штук"} на сумму {round(operation[1] * operation[2], 2)}\n'
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
        if item.quantity > 0:
            msg += f'{item.item_name}: {item.quantity} pcs.\n'
    
    bot.send_message(message.chat.id, msg)
 
 
def steamid(message):
    msg = message.text.split(' ')
    steam_id = None
    
    if len(msg) == 1:
        try: 
            steam_id = int(msg[0])
        except:
            if msg[0] in ['/steamid']:
                bot.send_message(message.chat.id, 'Введите steam id')
                bot.register_next_step_handler(message, steamid)
                return
            else:
                bot.send_message(message.chat.id, 'Произошла ошибка. Введен неверный формат steamid.')
    elif len(msg) == 2:
        try: 
            steam_id = int(msg[1])
        except:
            pass
    
    if steam_id != None:
        db.users.set.steamid(message.chat.id, steam_id)
        bot.send_message(message.chat.id, 'SteamId был успешно добавлен!', reply_markup=f.get_menu('main'))
        return
    else:
        bot.send_message(message.chat.id, 'Произошла ошибка. Введен неверный формат steamid.', reply_markup=f.get_menu('main'))


def inv_transfer(message):
    steam_id = db.users.get.steamid(message.chat.id)
    if steam_id == None:
        pass
    else:
        steam_inv = f.get_steam_inventory(steam_id)
        time_now = datetime.now()
        for item_name, quantity in steam_inv.items():
            item_id = db.items.get.id(item_name)
            user_id = message.chat.id
            price = db.prices.get.price(item_id)
            cur_id = db.users.get.stats(user_id)['currency_id']
            operation = models.operation(user_id, 'buy', quantity, item_id, price, cur_id, time_now)
            db.operations.new(operation)
# get info about specific item
#@bot.message_handler(commands=['info'])
def item_stats(message):
    msg = message.text.split(' ')
    stats = db.users.get.stats(message.chat.id)
    item_name = ' '.join(msg[1:])
    item_id = db.items.get.id(item_name)

    if item_id != None:
        prices = db.logs.get.item_prices.last24h(item_id)
        new_graph = f.graph_handler(prices, stats["currency_id"], 'item 24h', item_name=item_name.title())
        
        if new_graph != None:
            bot.send_photo(message.chat.id, new_graph)
            return
    bot.send_message(message.chat.id, 'Произошла ошибка!')
    

def setcur(message):
    msg = message.text.split(' ')
    cur_id = db.currencies.get.id(msg[1])
    if cur_id != None:
        db.users.set.cur_id(message.chat.id, cur_id)
        bot.send_message(message.chat.id, f'Ваша основная валюта была успешна изменена на значение "{msg[1]}"!')
        return
    bot.send_message(message.chat.id, 'Произошла ошибка!')


def item_stats_7d(message):
    msg = message.text.split(' ')
    stats = db.users.get.stats(message.chat.id)
    item_name = ' '.join(msg[1:])
    item_id = db.items.get.id(item_name)

    if item_id != None:
        prices = db.logs.get.item_prices.last7d(item_id)
        new_graph = f.graph_handler(prices, stats["currency_id"], 'item 7d', item_name=item_name.title())
        
        if new_graph != None:
            bot.send_photo(message.chat.id, new_graph)
            return
    bot.send_message(message.chat.id, 'Произошла ошибка!')


@bot.callback_query_handler(func=lambda call: call.data.startswith('timegap'))
def callback_worker(call):
    time_gap = call.data.split('_')[1]
    if time_gap == "24h":
        try:
            msg, new_graph = stats_24h(call.message.chat.id)
            media = telebot.types.InputMedia(type='photo', media=new_graph, caption=msg)
            bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=media, reply_markup=f.get_keyboard(None))
        except Exception as e:
            print(e)
    elif time_gap == "7d":
        #try:
            msg, new_graph = stats_7d(call.message.chat.id)
            media = telebot.types.InputMedia(type='photo', media=new_graph, caption=msg)
            bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=media, reply_markup=f.get_keyboard(None))
        #except Exception as e:
        #    print(e)
        #bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='7d', reply_markup=f.get_keyboard(None))
    elif time_gap == "30d":
        pass
        #bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='30d', reply_markup=f.get_keyboard(None))
    elif time_gap == "alltime":
        pass
        #bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='alltime', reply_markup=f.get_keyboard(None))


def stats_24h(user_id):
    stats = db.users.get.stats(user_id)
    assets = db.logs.get.assets.last24h(user_id)
    
    if assets == None:
        msg = 'Я о вас совсем ничего не знаю 😓\nПроизведите какие-нибудь операции, либо подождите обновление базы данных\n\nP.S. Обновление базы данных происходит раз в час'
        new_graph = Image.open(os.path.join(r'plots\blank_graph.png'))
        return msg, new_graph
    
    msg = f.get_stats_24h_msg(user_id, stats, assets)
    new_graph = f.graph_handler(assets, stats["currency_id"], 'asset', '24h')
    if not(new_graph != None and len(assets) >= 12):
        new_graph = Image.open(os.path.join(r'plots\blank_graph.png'))
        
    return msg, new_graph

def stats_7d(user_id):
    stats = db.users.get.stats(user_id)
    assets = db.logs.get.assets.last7d(user_id)
    
    if assets == None:
        msg = 'Я о вас совсем ничего не знаю 😓\nПроизведите какие-нибудь операции, либо подождите обновление базы данных\n\nP.S. Обновление базы данных происходит раз в час'
        new_graph = Image.open(os.path.join(r'plots\blank_graph.png'))
        return msg, new_graph
    
    msg = f.get_stats_7d_msg(user_id, stats, assets)
    new_graph = f.graph_handler(assets, stats["currency_id"], 'asset', '7d')
    if not(new_graph != None and len(assets) >= 12):
        new_graph = Image.open(os.path.join(r'plots\blank_graph.png'))
        
    return msg, new_graph
    
#bot.enable_save_next_step_handlers(delay=2)
#bot.load_next_step_handlers()
bot.polling(none_stop=True)