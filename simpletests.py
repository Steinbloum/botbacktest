wallet = 1000

def order(price, size, side = 'buy'):
    if side =='sell':
        size *=-1
    
    value = price*size
    return value

open = order(500, 1, 'sell')
close = order(400, 1, 'sell')
pnl = close-open
print(pnl)