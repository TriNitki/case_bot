from datetime import datetime

import db
import func as f

class operation():
    def __init__(self, DATA = None) -> None:
        if DATA != None:
            self.id, self.user_id, self.name, self.quantity, self.item_id, self.price, self.currency_id, self.datetime = DATA
        else:
            self.id = None
            self.user_id = None
            self.name = None
            self.quantity = None
            self.item_id = None
            self.price = None
            self.currency_id = None
            self.datetime = None

        self.item_name = None
        self.currency_name = None
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
            
            try:
                self.currency_name = args[3]
                data = db.currencies.get.id(self.currency_name, 'currency_name')
                self.currency_id = int(data)
            except:
                data = db.currencies.get.id(self.user_id, 'user_id')
                
                if data == None:
                    self.currency_id = 1
                else:
                    self.currency_id = int(data)
                
                self.currency_name = db.currencies.get.name(self.currency_id)
            
            try:
                self.price = float(args[2])
            except:
                self.price = f.get_price(self.currency_id, self.item_name)
            
            if msg[0] in ['s', 'sold','sell']:
                self.name = 'sell'
                self.possibility = f.sell_possibility(self.user_id, self.item_id, self.quantity)
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
        self.user_id, self.inventory_id, self.item_name, self.quantity = args