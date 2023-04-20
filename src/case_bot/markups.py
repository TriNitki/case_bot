import math
from telebot import types

def get_reply_keyboard(type, data = None):
    markup    = types.ReplyKeyboardMarkup(resize_keyboard=True)

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

def get_inline_keyboard(type, data = None):
    keyboard = types.InlineKeyboardMarkup()
    
    time_24h  = types.InlineKeyboardButton(text='За 24 часа 🌒', callback_data='timegap_24h')
    time_7d   = types.InlineKeyboardButton(text='За неделю 🌓', callback_data='timegap_7d')
    time_30d  = types.InlineKeyboardButton(text='За месяц 🌔', callback_data='timegap_30d')
    all_time  = types.InlineKeyboardButton(text='За все время 🌕', callback_data='timegap_alltime')

    keyboard.add(time_24h, time_7d, time_30d, all_time)
    return keyboard
