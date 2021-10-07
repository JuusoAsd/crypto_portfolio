import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import datetime as dt

import queue


from transaction import Tx


def main():

    traded_currencies = {}
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "holdings.txt"), "r"
    ) as f:
        n = 0
        total_profit = 0
        while True:
            n += 1
            line = f.readline()
            if line == "":
                break
            values = line.strip().split(",")
            inv_date, action, curr, bought_amount, cost_usd = values

            try:
                inv_date = dt.datetime.strptime(inv_date, "%d.%m.%Y")
                curr = str(curr)
                action = str(action)
                traded_amount = float(bought_amount)
                value_usd = float(cost_usd)
                new_tx = Tx(inv_date, curr, action, traded_amount, value_usd)
                if curr not in traded_currencies:
                    traded_currencies[curr] = queue.Queue(maxsize=0)
                if action == "BUY":
                    traded_currencies[curr].put(new_tx)
                elif action == "SELL":

                    while traded_amount > 0:
                        first_trade = traded_currencies[curr].queue[0]
                        entry_price = first_trade.unit_price
                        if first_trade.amount_principal < new_tx.amount_principal:
                            sold_amount = first_trade.amount_principal
                            profit = (new_tx.unit_price - entry_price) * sold_amount
                            traded_amount -= first_trade.amount_principal
                            traded_currencies[curr].get()

                        else:
                            sold_amount = traded_amount
                            first_trade.amount_principal -= traded_amount
                            profit = (new_tx.unit_price - entry_price) * sold_amount
                            traded_amount = 0
                        total_profit += profit
                        print(
                            f"sold {round(sold_amount,2): <8} {curr:10s} bought at {round(first_trade.unit_price,2):<7} sold for {round(new_tx.unit_price,2):<7} for profit of {round(profit,2):<4}"
                        )
                else:
                    raise TypeError("Wrong tx type")
            except:
                print(f"failed at row: {n}")
        print("\n", total_profit)


if __name__ == "__main__":
    main()
