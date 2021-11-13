from ta.momentum import rsi
from ta.volume import money_flow_index
from ta.trend import ema_indicator, macd, EMAIndicator, macd_signal
from ta.volatility import bollinger_hband_indicator, bollinger_lband_indicator, bollinger_mavg
import os
import glob
import pandas as pd



class Wallet:
    def __init__(self, name="wallet", balance=10000):
        self.balance = balance
        self.name = name
        self.history = []
        self.upnl = 0

    def change_balance(self, amount):
        self.balance += amount
        self.history.append(amount)

    def update_upnl(self, value):
        self.upnl = value


class Simulator:

    """Takes in a folder of format Time-OHLCV, returns a df with indicator values,
    has functions to identify entries for bots
    if force reaggs, overwrtie file
    """

    def __init__(self, name, folder, ticker="BTCUSDT", time_frame="1m", force_reagg = False):
        self.name = name
        self.force_reag = force_reagg
        self.ticker = ticker
        self.time_frame = time_frame
        self.folder = folder
        self.raw_df = self.agg_file(self.folder)
        self.df = self.init_sim()
        self.ema = "None"

    def update_df(self, row):
        updated_df = self.raw_df.iloc[(row - 250) : row]
        self.df = updated_df.set_index("Time")
        return self.df

    def init_sim(self):
        dfinit = self.raw_df.iloc[0:250]
        self.df = dfinit
        return dfinit

    def get_ema_status(self):
        # Ya surement plus simple,  a verifier
        ls = ["EMA10", "EMA25", "EMA50"]
        for n in range(len(ls)):
            ls[n] = self.df[ls[n]].iloc[-1]
        # print(ls)
        if ls == sorted(ls):
            status = "BEAR"
            # io.print_bear("STRONG DOWNTREND DETECTED")
            # print("downtrend")
        elif ls == sorted(ls, reverse=True):
            # io.print_bull("STRONG UPTREND DETECTED")
            status = "BULL"
        else:
            # io.print_statement("Nothing here")
            status = "NEUTRAL"
        # print("MACD {} ".format(status))
        self.ema = status
        return status

    def get_last_time(self):
        last_time = self.df.index[-1]
        return last_time

    def get_last_close(self):
        last_close = self.df["close"][-1]
        return last_close

    def agg_file(self, folder):
        '''tranforms a folder of klines in ione DF with indicators'''
        
        if os.path.isfile("agg/aggregated{}_{}.csv".format(self.ticker, self.time_frame)) and not self.force_reag:
            print("DF already done")
            df = pd.read_csv("agg/aggregated{}_{}.csv".format(self.ticker, self.time_frame))
            return df

        else:

            def make_df(file):
                df = pd.read_csv(file)
                df = df.iloc[:, :6]
                df.columns = ["Time", "open", "high", "low", "close", "volume"]
                # print(df)
                return df

            def add_indics(df):

                df["mfi"] = money_flow_index(df.high, df.low, df.close, df.volume)
                df["macd"] = macd(df.close)
                df["macds"] = macd_signal(df.close)
                df["bolupcross"] = bollinger_hband_indicator(df.close)
                df['bolmav'] = bollinger_mavg(df.close)
                df["boldowncross"] = bollinger_lband_indicator(df.close)
                df["EMA10"] = ema_indicator(df.close, window=10)
                df["EMA25"] = ema_indicator(df.close, window=25)
                df["EMA50"] = ema_indicator(df.close, window=50)
                df["EMA100"] = ema_indicator(df.close, window=100)
                df["EMA200"] = ema_indicator(df.close, window=200)

                return df

            path = folder
            all_files = glob.glob(path + "/*.csv")
            print(all_files)
            n = 0
            df = pd.DataFrame()
            for file in all_files:
                if n == 0:
                    df = make_df(file)
                    df
                    n += 1
                else:
                    df2 = make_df(file)
                    df = df.append(df2, ignore_index=True)
            df = df.set_index("Time")
            df.index = pd.to_datetime(df.index, unit="ms")
            df = df.sort_index()
            df = df.astype(float)
            df = add_indics(df)
            print("compiling done")
            print(df)
            df.to_csv("agg/aggregated{}_{}.csv".format(self.ticker, self.time_frame))
            return df
