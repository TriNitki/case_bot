import db.users, db.items, db.logs
import graphs

def item_stats_24h(user_id, item_name):
    stats = db.users.get_stats(user_id)
    item_id = db.items.get_id(item_name)
    
    prices = db.logs.get_item_prices_last24h(item_id)
    new_graph = graphs.handler(prices, stats["currency_id"], 'item', '24h', item_name=item_name.title())

    return new_graph

def item_stats_7d(user_id, item_name):
    stats = db.users.get_stats(user_id)
    item_id = db.items.get_id(item_name)
    
    prices = db.logs.get_item_prices_last7d(item_id)
    new_graph = graphs.handler(prices, stats["currency_id"], 'item', '7d', item_name=item_name.title())
    
    return new_graph



    