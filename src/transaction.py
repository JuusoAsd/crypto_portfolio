
class Tx():

    def __init__(self, time, currency, side,amount_principal, amount_usd):
        self.currency = currency
        self.time = time
        self.side = side
        self.amount_principal = amount_principal
        self.total_price = amount_usd
        self.unit_price = amount_usd /amount_principal
        #self.price = amount_usd /amount_principal


