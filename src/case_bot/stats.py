import math
import os
import io
from PIL import Image

import graphs
import db.items, db.logs, db.currencies, db.inventories, db.users


def get_24h_msg(user_id, stats, assets):
    invent = db.inventories.get_inv(user_id)
    item_growth_rates = []
    
    
    for item in invent:
        item_id = item[0]
        item_name = db.items.get_name(item_id).title()
        
        prices = db.logs.get_item_prices_last24h(item_id)
        price_before = prices[0][1]
        price_after = prices[-1][1]
        item_difference = price_after - price_before
        item_g_rate = item_difference/price_before*100
        item_growth_rates.append({'item_name': item_name, 'growth_rate': item_g_rate, 'difference': item_difference, 'quantity': item[1]})
    
    emoji_nums = ['1️⃣', '2️⃣', '3️⃣']
    
    sorted_item_g_rates = sorted(item_growth_rates, key=lambda d: d['growth_rate'], reverse=True)[:3]
    
    cur_symbol = db.currencies.get_symbol(stats["currency_id"])
    cur_rate = db.currencies.get_rate(stats["currency_id"])
    
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

def get_7d_msg(user_id, stats, assets):
    invent = db.inventories.get_inv(user_id)
    item_growth_rates = []
    
    
    for item in invent:
        item_id = item[0]
        item_name = db.items.get_name(item_id).title()
        
        prices = db.logs.get_item_prices_last7d(item_id)
        price_before = prices[0][1]
        price_after = prices[-1][1]
        item_difference = price_after - price_before
        item_g_rate = item_difference/price_before*100
        item_growth_rates.append({'item_name': item_name, 'growth_rate': item_g_rate, 'difference': item_difference, 'quantity': item[1]})
    
    emoji_nums = ['1️⃣', '2️⃣', '3️⃣']
    
    sorted_item_g_rates = sorted(item_growth_rates, key=lambda d: d['growth_rate'], reverse=True)[:3]
    
    cur_symbol = db.currencies.get_symbol(stats["currency_id"])
    cur_rate = db.currencies.get_rate(stats["currency_id"])
    
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

def get_24h(user_id):
    user_stats = db.users.get_stats(user_id)
    assets = db.logs.get_assets_last24h(user_id)
    
    if assets == None:
        msg = 'Я о вас совсем ничего не знаю 😓\nПроизведите какие-нибудь операции, либо подождите обновление базы данных\n\nP.S. Обновление базы данных происходит раз в час'
        with open(r'plots\blank_graph.png', "rb") as fh:
            new_graph = io.BytesIO(fh.read())
        return msg, new_graph
    
    msg = get_24h_msg(user_id, user_stats, assets)
    new_graph = graphs.handler(assets, user_stats["currency_id"], 'asset', '24h')
    if not(new_graph != None and len(assets) >= 12):
        with open(r'plots\blank_graph.png', "rb") as fh:
            new_graph = io.BytesIO(fh.read())
        
    return msg, new_graph

def get_7d(user_id):
    user_stats = db.users.get_stats(user_id)
    assets = db.logs.get_assets_last7d(user_id)
    
    if assets == None:
        msg = 'Я о вас совсем ничего не знаю 😓\nПроизведите какие-нибудь операции, либо подождите обновление базы данных\n\nP.S. Обновление базы данных происходит раз в час'
        with open(r'plots\blank_graph.png', "rb") as fh:
            new_graph = io.BytesIO(fh.read())
        return msg, new_graph
    
    msg = get_7d_msg(user_id, user_stats, assets)
    new_graph = graphs.handler(assets, user_stats["currency_id"], 'asset', '7d')
    if not(new_graph != None and len(assets) >= 12):
        with open(r'plots\blank_graph.png', "rb") as fh:
            new_graph = io.BytesIO(fh.read())
        
    return msg, new_graph



'''def stats_alltime(message):
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
        bot.send_photo(message.chat.id, new_graph, reply_markup=f.get_menu('main'))'''