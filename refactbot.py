import pandas as pd
from simulators import Wallet, Simulator
from main import folder


class Bot:
    def __init__(self, name , wallet, simulator, wallet_allocation = 0.1):
        self.name = name
        self.wallet = wallet.balance * wallet_allocation
        self.initial_wallet = 
        self.simulator = simulator
        self.open_position = False
        self.open_order = False
        self.side = None
        self.position_size = 0
        self.position_value = 0 #inclure d' actualiser dasn run du sous bot
        self.initial_position_size = 0
        self.initial_position_value = 0
        self.initial_price = 0
        self.order_list = []
        self.tp = []
        self.sl = []
        self.trade_history = None

    def set_order(self, price, value, size, type = 'limit', motive = 'open_position', side = "buy"):
        '''retourne un dict au format:
        side : 
        price :
        value :
        size:
        motive :
        type :
        '''
        self.open_order = True
        return {'side' : side,
        'price': price,
        'value' : value,
        'size' : size,
        'motive' : motive,
        'type ' :type}

    def appy_fees(self,amount, type = 'limit'):
        limit = 0.0002
        market = 0.0004
        if type == 'limit':
            amount *= limit
        else :
            amount *= market
        return amount

    def store_history(self, size, price, value, side, motive, pnl, fees, wallet):
        if self.trade_history is None:
            df = pd.DataFrame(columns=['Time', 'price', 'size', 'value', 'side', 'motive', 'pnl', 'fees', 'wallet'])
        else:
            df = self.trade_history
        
        time = self.simulator.get_last_time()
        price = price
        size = size
        side = side
        motive = motive
        pnl = pnl
        fees = fees
        wallet = wallet
        value = value
        ls = [time, price, size, value, side, motive, pnl, fees, wallet]
        df.loc[len(df)] = ls
        #print(df)
        self.trade_history = df

    def open_position(self, order):
        self.open_position = True
        self.initial_position_value = order['value']
        value = self.appy_fees(order['value'])
        size = value/order['price']
        self.initial_position_size = size
        self.initial_price = order['price']
        #ajoute au df de trade
        self.wallet -= value
        self.store_history(size, order['price'], order['side'], order['motive'], 0, self.wallet, value = value)

        print('opened position')

    def set_tp(self, price , amount = 1 ):
        size = self.position_size * amount
        value = size*price
        tp = self.set_order(price, value, size, type = 'limit', motive='tp', side='sell')
        self.order_list.append(tp)

    def trigger_order(self,order):
        pnl = (order['size']*self.simulator.get_last_close())-(order['size']*self.initial_price)
        pnl = self.appy_fees(pnl)
        self.store_history(order['size'], order['price'],order['side'], order['motive'], pnl)
        self.wallet += pnl
        self.position_size -= order['size']
        self.position_value = self.position_size*self.simulator.get_last_close()
        if self.position_size == 0:
            self.close_position()

    def close_position(self):
        self.open_position = False
        self.order_list = []
        self.open_order = False
        self.initial_price = 0
        self.initial_position_size = 0
        self.initial_position_value = 0
        self.side = None

    def buy_market(self, size, motive):

        price = self.simulator.get_last_close()
        value = size * price
        fees = self.appy_fees(value)
        if self.open_position == False:
            self.open_position = True
            self.initial_position_value = value
            self.initial_price = price
            self.side = 'long'
            pnl = 0
        else :
            pnl = (size*price) - (size*self.initial_price)
        motive = motive
        self.position_size += size
        self.position_value = self.position_size*price
        self.wallet -= (value + fees)
        if self.position_size == 0:
            self.close_position()
        self.store_history(size, price = price, value =value, side='buy', motive=motive, pnl=pnl, fees=fees, wallet=self.wallet)

    def sell_market(self, size, motive):
        
        price = self.simulator.get_last_close()
        value = (price * size)
        fees = self.appy_fees(value)
        if self.open_position == False:
            self.open_position = True
            self.initial_position_value = value
            self.initial_price = price
            self.side = 'short'
            pnl = 0
        else :
            pnl = (size*price) - size*self.initial_price
        motive = motive
        self.position_size += -size
        self.position_value = self.position_size*price
        self.wallet += (value+fees)
        if self.position_size == 0:
            self.close_position()
        self.store_history(size, price = price, value = value, side='sell', motive=motive, pnl=pnl, fees=fees, wallet=self.wallet)

    def get_results(self):
        df = self.trade_history
        df = df.set_index('Time')
        trade_count = df['motive'].value_counts()
        trade_count = trade_count['open position']
        roi = sum(df.pnl)/
        print('{} has made {} trades in {}. its profit is {} or % ROI. It has spent {}$ in fees'.format(
            self.name, trade_count, (pd.to_datetime(df.index[-1])-pd.to_datetime(df.index[0])), sum(df.pnl), sum(df.fees)


        ))
        return df


class Marketbolbot(Bot):
    '''un bot un peu con qui passe tout en market au signal. achete ou vend les bornes, ferme `a la m'ediane ou en sl de 5%'''
    def __init__(self, name, wallet, simulator, wallet_allocation=0.1):
        super().__init__(name, wallet, simulator, wallet_allocation=wallet_allocation)
        self.analist_df = None
    def run(self):
        self.analyse()
        
        low = self.simulator.get_last('low')
        high = self.simulator.get_last('high')
        price = self.simulator.get_last_close()
        self.position_value = self.position_size*price
        #print(self.analist_df)
        if self.open_position == False:
            if self.analist_df['boldowncross'].iloc[-1]>0:
                size = (self.wallet*0.2)/price
                self.buy_market(size, 'open position')
                """elif self.analist_df['bolupcross'].iloc[-1]>0:
                size = price/(self.wallet*0.2)
                self.sell_market(size*0.2, 'open position') """
        elif self.open_position == True:
            if self.side=='long':
                if price>self.analist_df['bolup'].iloc[-1]:
                    self.sell_market((self.position_size), 'tp')
                    self.close_position()
                elif self.position_value < self.initial_position_value*0.98:
                    self.sell_market((self.position_size), 'sl')
                    self.close_position()
            elif self.side=='short':
                if price<self.analist_df['bolmav'].iloc[-1]:
                    self.buy_market((self.position_size), 'tp')
                    self.close_position()
                elif self.position_value < self.initial_position_value*0.95:
                    self.buy_market((self.position_size), 'sl')
                    self.close_position()
        
                

                
    def analyse(self):     
        df = pd.DataFrame(
            {
                "Time": self.simulator.get_last_time(),
                "bolup": self.simulator.get_last("bolup"),
                "boldown": self.simulator.get_last("boldown"),
                "bolmav": self.simulator.get_last("bolmav"),
                'boldowncross':self.simulator.get_last("boldowncross"),
                'bolupcross':self.simulator.get_last("bolupcross")
            },
            index=[0],
        )
        df = df.set_index("Time")

        if self.analist_df is not None:
            ls = ["bolupcross", "boldowncross"]
            for bol in ls:
                if self.simulator.get_last(bol) != 0:

                    if self.analist_df[bol].iloc[-1] != 0:

                        df[bol].iloc[-1] = self.analist_df[bol].iloc[-1] + 1
        self.analist_df = df
        return df




wallet = Wallet()
ethusdt15m = Simulator("ethusdt15m", folder, "ETHUSDT", "15m")
stupidbot = Marketbolbot('stupidbot', wallet, ethusdt15m)
print(stupidbot.wallet)
for n in range(251, 3000):
    ethusdt15m.update_df(n)
    # print(bolbot.analyse())
    stupidbot.run()
    # print(n)
    # print(bolbot.analist_df.bolmav[-1])
print(stupidbot.get_results())