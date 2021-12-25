import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import datetime as dt

import queue


from transaction import Tx


def sell_transaction(traded_amount, traded_currencies, new_tx):
    curr = new_tx.currency
    total_profit = 0
    while traded_amount > 0:
        #print(traded_amount)
        try:
            first_trade = traded_currencies[curr].queue[0]
            entry_price = first_trade.unit_price
            if first_trade.amount_principal < traded_amount:
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
        except:
            sold_amount = traded_amount
            profit = new_tx.unit_price * sold_amount
            total_profit += profit
            traded_amount = 0
            print(
                f"sold {round(sold_amount,2): <8} {curr:10s} earned at {0:<7} sold for {round(new_tx.unit_price,2):<7} for profit of {round(profit,2):<4}"
            )
            
    return total_profit


def get_remaining_positions(position_dict):
    total_value = 0
    for currency, q in position_dict.items():
        total_amount = 0
        total_price = 0
        while True:
            if q.empty():
                break
            tx = q.get()
            total_amount += tx.amount_principal
            total_price += tx.amount_principal * tx.unit_price
        if total_amount != 0:
            avg_price = total_price / total_amount
            total_value += avg_price * total_amount
            print(
                f"Currency: {currency:10s} left: {round(total_amount,2):<9} average price: {round(avg_price,5):<12} value: {round(avg_price*total_amount,2):<6}"
            )
        else:
            print(f"Currency: {currency:10s} left: {0:<5}")
    print()
    print(f"Residual value: {round(total_value,2)}")
    print()


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
                    total_profit += sell_transaction(
                        traded_amount, traded_currencies, new_tx
                    )
                else:
                    raise TypeError("Wrong tx type")

            except:
                print(f"failed at row: {n}")
        print()
        print(f"Total profit: {round(total_profit,2)}\n")

    get_remaining_positions(traded_currencies)


if __name__ == "__main__":
    main()
