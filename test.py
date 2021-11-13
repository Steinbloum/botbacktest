import pandas as pd

df = pd.read_csv('agg/aggregatedETHUSDT_15m.csv')
df = df.set_index('Time')
print(df)
print(df.index[-1])
