import db

import func as f

class operation():
    def __init__(self) -> None:
        self.user_id = None
        self.name = None
        self.item_id = None
        self.item_name = None
        self.quantity = None
        self.price = None
        self.currency_id = None
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
            
            try:
                self.currency_name = args[3]
                data = db.currencies.get.id({'currency_name': self.currency_name})
                self.currency_id = int(data)
            except:
                data = db.currencies.get.id({'user_id': self.user_id})
                
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


    def get_all(self):
        return {'user_id': self.user_id, 'name': self.name, 'item_id': self.item_id, 'quantity': self.quantity, 'price': self.price,  'currency_id': self.currency_id}

        


