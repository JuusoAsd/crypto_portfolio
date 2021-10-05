import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import datetime as dt

import queue


from transaction import Tx



def main():
    
    traded_currencies = {}
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'holdings.txt'), 'r') as f:
        n = 0
        total_profit = 0
        while True:
            n += 1
            line = f.readline()
            if line == '':
                break
            values = line.strip().split(',')
            inv_date, curr, action, bought_amount,cost_usd = values
            
            #try:
            inv_date = dt.datetime.strptime(inv_date, '%d.%m.%Y')
            curr = str(curr)
            action = str(action)
            traded_amount = float(bought_amount)
            value_usd = float(cost_usd)
            new_tx = Tx(inv_date, curr, action, traded_amount, value_usd)
            if curr not in traded_currencies:
                traded_currencies[curr] = queue.Queue(maxsize=0)
            if action == 'BUY':
                traded_currencies[curr].put(new_tx)
                #print(f"Bought {curr} for {value_usd}USD at {new_tx.price}")
            elif action == 'SELL':
                
                while traded_amount > 0:
                    first_trade = traded_currencies[curr].queue[0]
                    entry_price = first_trade.unit_price
                    if first_trade.amount_principal < new_tx.amount_principal:
                        sold_amount = first_trade.amount_principal
                        profit = (new_tx.unit_price - entry_price)*sold_amount
                        traded_amount -= first_trade.amount_principal
                        traded_currencies[curr].get()

                    else:
                        sold_amount = traded_amount
                        first_trade.amount_principal -= traded_amount
                        profit = (new_tx.unit_price - entry_price)*sold_amount
                        traded_amount = 0
                    print(sold_amount, new_tx.unit_price,  entry_price, sold_amount*(new_tx.unit_price-entry_price))
                    total_profit += profit
                    #print(f"sold {sold_amount}{curr} bought at {first_trade.price} for profit of {profit}")
            
        print(total_profit)
                #else:
                #    raise TypeError('Wrong tx type')
                
                



                

            #except:
                #print(f'failed at row: {n}')


if __name__ == '__main__':
    main()