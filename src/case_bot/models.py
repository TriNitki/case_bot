from datetime import datetime

import db.inventories

class operation():
    def __init__(self, *DATA) -> None:
        try:
            self.user_id, self.name, self.quantity, self.item_id, self.price, self.currency_id, self.datetime = DATA
        except:
            self.user_id = None
            self.name = None
            self.quantity = None
            self.item_id = None
            self.price = None
            self.datetime = None
            self.currency_id = None

        self.currency_symbol = None
        self.item_name = None
        self.possibility = None
    
    
    def define(self, message):
        try:
            msg = message.text.lower().replace('/', '', 1).replace(' ', '|', 1).split('|')
            args = msg[1].strip().split(', ')

            self.user_id = message.chat.id
            self.item_name = args[0]
            self.item_id = db.items.get.id(args[0])
            self.quantity = int(args[1])
            self.datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            if self.quantity < 1 or self.item_id == None:
                self.possibility = False
                return
            
            try:
                currency_name = args[3]
                self.currency_id = db.currencies.get.id(currency_name)
            except:
                self.currency_id = db.users.get.stats(self.user_id)['currency_id']
            
            self.currency_symbol = db.currencies.get.symbol(self.currency_id)
            
            if self.currency_id == 1:
                usd_rate = 1
            else:
                usd_rate = float(db.currencies.get.rate(self.currency_id))
            
            
            
            try:
                self.price = float(args[2]) / usd_rate
            except:
                self.price = db.prices.get.price(self.item_id)
            
            
            if msg[0] in ['s', 'sold','sell']:
                self.name = 'sell'
                self.possibility = _sell_possibility(self.user_id, self.item_id, self.quantity)
            else:
                self.name = 'buy'
                self.possibility = True
        except Exception as e:
            print(e)
            self.possibility = False

class inventory():
    def __init__(self) -> None:
        self.user_id = None
        self.inventory_id = None
        self.item_name = None
        self.quantity = None
    
    def new(self, args):
        self.user_id, self.inventory_id, self.item_name, self.quantity, self.item_id = args

def _sell_possibility(user_id, item_id, quantity):
    a_quantity = db.inventories.get_available_quantity(user_id, item_id)
    if a_quantity >= quantity:
        return True
    else:
        return False