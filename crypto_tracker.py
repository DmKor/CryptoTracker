import requests
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkinter import messagebox

API_URL = "https://data-api.binance.vision/api/v3/ticker/24hr"

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "BNBUSDT",
    "XRPUSDT"
    ]

def get_crypto_data(symbol):
    response = requests.get(
        API_URL,
        params={"symbol": symbol},
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    price = float(data["lastPrice"])
    change = float(data["priceChangePercent"])

    return price, change

def get_all_crypto_data():
    cryptos = []
    errors = []

    for symbol in SYMBOLS:
        try:
           price, change = get_crypto_data(symbol)

           cryptos.append({
               "symbol": symbol,
               "price": price,
               "change": change
                })

        except (
            requests.exceptions.RequestException,
            KeyError,
            ValueError
        ) as error:
            errors.append(f"{symbol}: {error}")

    return cryptos, errors

root = tk.Tk()
root.title("Crypto Tracker")
root.geometry("600x400")

columns = ("symbol", "price", "change")

tree = ttk.Treeview(root, columns=columns, show="headings")

tree.heading("symbol", text="Криптовалюта")
tree.heading("price", text="Цена (USDT)")
tree.heading("change", text="Изменение за 24 ч.")

tree.pack(fill="both", expand=True)

update_label = tk.Label(root, text="Последнее обновление: ещё не выполнялось")
update_label.pack(pady=5)

def update_table():
    cryptos, errors = get_all_crypto_data()

    print("ТИП cryptos:", type(cryptos))
    print("ТИП ПЕРВОГО ЭЛЕМЕНТА:", type(cryptos[0]) if cryptos else "Список пуст")

    if not cryptos:
        messagebox.showerror(
            "Ошибка",
            "Не удалось получить данные о криптовалютах."
        )
        return

    if errors:
        messagebox.showwarning(
            "Предупреждение",
            "Не удалось получить данные по некоторым криптовалютам:\n"
            + "\n".join(errors)
        )

    for item in tree.get_children():
        tree.delete(item)

    print("Содержимое cryptos:", cryptos)
    print("Тип первого элемента:", type(cryptos[0]))

    for crypto in cryptos:
        tree.insert(
            "",
            "end",
            values=(
                crypto["symbol"],
                crypto["price"],
                f'{crypto["change"]:.2f}%'
            )
        )
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    update_label.config(text=f"Последнее обновление: {current_time}")

refresh_button = tk.Button(
    root,
    text="Обновить котировки",
    command=update_table
)

refresh_button.pack(pady=10)
update_table()

root.mainloop()