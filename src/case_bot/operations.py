import models
import db.operations, db.currencies, db.inventories, db.items, db.users

def edit_handler(oper_id, to_edit, value):
    def _try_price(value):
        try:
            if float(value) <= 0:
                raise ValueError
        except:
            return False
        
        db.operations.edit(oper_id, 'price', value)
        return True
    
    def _try_currency(value):
        cur_id = db.currencies.get_id(value)
        if cur_id != None:
            db.operations.edit(oper_id, 'currency_id', cur_id)
            db.operations.edit(oper_id, 'price', operation.price * db.currencies.get_rate(operation.currency_id) / db.currencies.get.rate(cur_id))
            return True
        else:
            return False
    
    def _try_operation(value):
        a_quantiry = db.inventories.get_available_quantity(operation.user_id, operation.item_id)
        if value not in ['buy', 'sell']:
            return False

        if value != operation.name:
            if value == 'sell' and a_quantiry <= int(operation.quantity)*2:
                return False
            db.inventories.edit(operation.user_id, operation_name=value, quantity=operation.quantity*2, item_id=operation.item_id)
            db.operations.edit(oper_id, 'name', value)
            return True
        else:
            return False
    
    def _try_quantity(value):
        a_quantiry = db.inventories.get_available_quantity(operation.user_id, operation.item_id)

        if not value.isnumeric() or int(value) < 0:
            return False
        
        if (operation.name == 'buy' and operation.quantity < int(value)) or (operation.name == 'sell' and operation.quantity > int(value)):
            if operation.name == 'buy':
                dif = int(value) - operation.quantity
            else:
                dif = operation.quantity - int(value)
            
            db.inventories.edit(operation.user_id, operation_name='buy', quantity=dif, item_id=operation.item_id)
            db.operations.edit(oper_id, 'quantity', value)
            return True
        elif (operation.name == 'buy' and operation.quantity > int(value)) or (operation.name == 'sell' and operation.quantity < int(value)):
            if operation.name == 'buy':
                dif = operation.quantity - int(value)
            else:
                dif = int(value) - operation.quantity
            
            if dif > a_quantiry:
                return False
            else:
                db.inventories.edit(operation.user_id, operation_name='sell', quantity=dif, item_id=operation.item_id)
                db.operations.edit(oper_id, 'quantity', value)
                return True
        else:
            return False
    
    def _try_currency(value):
        new_item_id = db.items.get_id(value)

        a_quantiry = db.inventories.get_available_quantity(operation.user_id, operation.item_id)
        new_a_quantiry = db.inventories.get_available_quantity(operation.user_id, new_item_id)
        

        if operation.item_id != new_item_id and new_item_id != None:
            if operation.name == 'buy':
                if a_quantiry >= operation.quantity:
                    db.inventories.edit(operation.user_id, 'buy', operation.quantity, new_item_id)
                    db.inventories.edit(operation.user_id, 'sell', operation.quantity, operation.item_id)
                    db.operations.edit(oper_id, 'item_id', new_item_id)
                    return True
                else:
                    return False
            else:
                if new_a_quantiry >= operation.quantity:
                    db.inventories.edit(operation.user_id, 'buy', operation.quantity, operation.item_id)
                    db.inventories.edit(operation.user_id, 'sell', operation.quantity, new_item_id)
                    db.operations.edit(oper_id, 'item_id', new_item_id)
                    return True
                else:
                    return False
        else:
            return False
    
    operation = models.operation(*db.operations.get_operation(operation_id=oper_id))
    
    price_before = operation.quantity * operation.price

    match to_edit:
        case 'price':
            is_successful = _try_price(value)
        case 'currency':
            is_successful = _try_currency(value)
        case 'operation':
            is_successful = _try_operation(value)
        case 'quantity':
            is_successful = _try_quantity(value)
        case 'item_name':
            is_successful = _try_currency(value)
        case _:
            is_successful = False
    
    if is_successful is False:
        return 'failure'
    
    match operation.name: #operation before
        case 'buy':
            db.users.add_expense(operation.user_id, -price_before)
        case 'sell':
            db.users.add_income(operation.user_id, -price_before)
    
    operation = models.operation(*db.operations.get_operation(operation_id=oper_id))
    price_after = operation.quantity * operation.price
    
    match operation.name: #operation after
        case 'buy':
            db.users.add_expense(operation.user_id, price_after)
        case 'sell':
            db.users.add_income(operation.user_id, price_after)
    
    return 'success'