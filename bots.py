
import pandas as pd
from simulators import Simulator, Wallet
from main import folder



class Bot:
    """General class for bot, takes in params the wallet
    wallet allocation  and simulator.
    Stategy set upo in subclass"""

    def __init__(self, simulator, wallet, wallet_allocation = 0.1):
        self.wallet = wallet.balance*wallet_allocation
        self.simulator = simulator
        self.open_position = False
        self.open_order = False
        self.pnl = 0
        self.profit = 0
        self.history = pd.DataFrame(
        )
        self.side = "neutral"
        self.position_size = 0
        self.position_value = 0
        self.orders = []
        self.position_initial_size = 0
        self.position_initial_value = 0
        self.active_bots = []

    def set_buy_order(self, qtt, price):
        qtt = qtt
        price = price
        size = qtt / price
        self.open_order = True

        return {"qtt": qtt, "price": price, "size": size}

    def set_sell_order(self, qtt, price):
        qtt = -qtt
        price = price
        size = qtt / price
        self.open_order = True
        return {"qtt": qtt, "price": price, "size": size}

    def cancel_order(self):
        self.open_order = False

    def trigger_order(self, qtt, price):
        self.open_order = False
        self.open_position = True
        qtt_after_fees = qtt * 0.96
        size = qtt_after_fees / price
        self.wallet.change_balance(-qtt)
        self.position_size = size
        self.history = self.history.append(
            {
                "Time": self.simulator.raw_df.index[-1],
                "status": "OPEN",
                "qtt": qtt,
                "Price": price,
                "Pnl": 0,
                "motive":"OPEN"
            },
            ignore_index=True,
        )

    def close_position(self, motive):
        self.open_order = False
        self.open_position = False
        pnl = self.position_size * self.simulator.get_last_close()
        self.wallet.change_balance(pnl)
        self.pnl += pnl
        self.position_size = 0
        self.position_value = 0
        self.history = self.history.append(
            {
                "Time": self.simulator.df.index[-1],
                "status": "CLOSE",
                "qtt": pnl,
                "Price": self.simulator.get_last_close(),
                "Pnl": pnl - self.history["qtt"].iloc[-1],
                "motive": motive,
            },
            ignore_index=True,
        )
        print("closing position")

    def get_position_value(self):
        pos_val = self.position_size * self.simulator.get_last_close()
        self.position_value = pos_val
        return pos_val

    def apply_fees(amount, mode='market', market = 0.04, limit = 0.02):

        '''applies market or limit fees on an amount, can be param, default is binance fees'''
        if mode == 'market':
            mode = market
        elif mode == 'limit':
            mode = limit
        amount *= mode
        return amount

class Bollinger_bot(Bot):
    def __init__(self, simulator, wallet, wallet_allocation=0.1):
        super().__init__(simulator, wallet, wallet_allocation=wallet_allocation)
        self.analist_df = self.analyse()
    
    def analyse(self):
        df = pd.DataFrame({"Time":self.simulator.df.index[-1], 'bol_cross_up' : self.simulator.df.bolupcross[-1], 
        'bol_cross-down' : self.simulator.df.boldowncross[-1], 'bolmav': self.simulator.df.bolmav[-1]}, index = [0])
        df = df.set_index('Time')
        self.analist_df = df
        print(df)
        return df



wallet = Wallet()
ethusdt15m = Simulator('ethusdt15m', folder, 'ETHUSDT', '15m')
bolbot = Bollinger_bot(ethusdt15m, wallet)
print(bolbot.wallet)
for n in range(250,500):
    ethusdt15m.update_df(n)
    bolbot.analyse()