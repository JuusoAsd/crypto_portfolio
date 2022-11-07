import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import datetime as dt

import queue


from transaction import Tx


def sell_transaction(date, traded_amount, traded_currencies, new_tx):
    date_str = date.strftime("%d-%m-%Y")
    curr = new_tx.currency
    total_profit = 0
    while traded_amount > 0:
        try:
            first_trade = traded_currencies[curr].queue[0]
            entry_price = first_trade.unit_price
            if first_trade.amount_principal < traded_amount:
                sold_amount = first_trade.amount_principal
                traded_amount -= first_trade.amount_principal
                traded_currencies[curr].get()

            else:
                sold_amount = traded_amount
                first_trade.amount_principal -= traded_amount
                traded_amount = 0

            profit = (new_tx.unit_price - entry_price) * sold_amount
            if new_tx.unit_price > 5 * entry_price:
                hankintameno = True
                profit = (new_tx.unit_price * 0.8) * sold_amount
            else:
                hankintameno = False
            total_profit += profit
            print(
                f"{date_str};{curr};{round(sold_amount,4)};{round(first_trade.unit_price,4)};{round(new_tx.unit_price,2)};{round(profit,4)};{hankintameno}"
            )
            """ print(
                f"Date: {date_str} sold {round(sold_amount,2): <8} {curr:10s} bought at {round(first_trade.unit_price,2):<7} sold for {round(new_tx.unit_price,2):<7} for profit of {round(profit,2):<4}"
            )"""
        except:
            sold_amount = traded_amount
            profit = new_tx.unit_price * sold_amount * 0.8
            total_profit += profit * 0.8
            traded_amount = 0
            hankintameno = True
            print(
                f"{date_str};{curr};{round(sold_amount,4)};{0};{round(new_tx.unit_price,4)};{round(profit,4)};{hankintameno}"
            )
            """
            print(
                f"Date: {date_str} sold {round(sold_amount,2): <8} {curr:10s} earned at {0:<7} sold for {round(new_tx.unit_price,2):<7} for profit of {round(profit,2):<4}"
            )"""

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
    print(f"DATE;ASSET;QTY;ENTRY;EXIT;PROFIT;HANKINTAMENO")
    traded_currencies = {}
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "holdings.txt"), "r"
    ) as f:
        n = 0
        total_profit = 0
        year_profits = {}
        while True:
            n += 1
            line = f.readline()
            if line == "":
                break
            values = line.strip().split(",")
            inv_date, action, curr, bought_amount, cost_usd = values

            try:
                inv_date = dt.datetime.strptime(inv_date, "%d.%m.%Y")
                if inv_date.year not in year_profits:
                    year_profits[inv_date.year] = 0
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
                    tx_profit = sell_transaction(
                        inv_date, traded_amount, traded_currencies, new_tx
                    )
                    total_profit += tx_profit
                else:
                    raise TypeError("Wrong tx type")

                year_profits[inv_date.year] += tx_profit

            except:
                print(f"failed at row: {n}")
        print()
        for year, profit in year_profits.items():
            print(f"Year: {year} profit: {round(profit,2)}")
        print()
    get_remaining_positions(traded_currencies)


if __name__ == "__main__":
    main()
