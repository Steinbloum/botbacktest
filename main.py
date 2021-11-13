from simulators import Wallet, Simulator

folder = "raw_files/ethusdt15min"

ethusdt15m = Simulator("ethusdt15m", folder, "ETHUSDT", '15m', force_reagg=True)
print(ethusdt15m.df)