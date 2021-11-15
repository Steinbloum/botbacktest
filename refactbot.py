class Bot:
    def __init__(self, name , wallet):
        self.name = name
        self.wallet = wallet
        self.open_position = None
        self.open_order = None
        self.position = None
        self.position_size = None
        self.position_value = None
        self.initial_position_size = None
        self.initial_position_value = None
        self.orders = []
        self.tp = []
        self.sl = []

    def set_order(self, value, size, motive = 'open position', side = "buy"):
        '''retourne un dict au format:
        side : 
        value :
        size :
        motive :
        '''
        self.open_order = True

        