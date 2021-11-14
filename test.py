import pandas as pd

chart = 1000

class Bot:

    def __init__(self, name, wallet = 1000):
        self.name = name
        self.wallet = wallet
        self.entry = None
        self.intial_size = None
        self.initial_value = None
        self.tp = None
        self.sl = None

    def open_position(self, amount = 0.2, price):
        

