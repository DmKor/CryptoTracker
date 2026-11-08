import requests
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkinter import messagebox
import threading

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

class CryptoTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Tracker")
        self.root.geometry("600x500")
        self.create_widgets()

    def create_widgets(self):
        title = tk.Label(
            self.root,
            text="Crypto Tracker",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=15)
        columns = ("symbol", "price", "change")
        self.tree = ttk.Treeview(
            self.root,
            columns=columns,
            show="headings"
        )
        style = ttk.Style()
        # style.theme_use("clam")
        style.configure(
            "Treeview",
            rowheight=32,
            font=("Arial", 11),
            foreground="#333333"
        )

        style.configure(
            "Treeview.Heading",
            font=("Arial", 11, "bold"),
            background="#DCE6F1",
            foreground="#333333"
        )
        self.tree.tag_configure("even", background="#F0F4F8")
        self.tree.tag_configure("odd", background="#FFFFFF")

        self.tree.tag_configure("negative", foreground="#CC3333")
        self.tree.tag_configure("positive", foreground="#008800")

        self.tree.heading("symbol", text="Криптовалюта")
        self.tree.heading("price", text="Цена (USDT)")
        self.tree.heading("change", text="Изменение за 24 ч.")

        self.tree.column("symbol", width=180, anchor="center")
        self.tree.column("price", width=160, anchor="e")
        self.tree.column("change", width=180, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.update_label = tk.Label(
            self.root,
            text="Последнее обновление: ещё не выполнялось"
        )
        self.update_label.pack(pady=5)

        self.refresh_button = tk.Button(
            self.root,
            text="Обновить котировки",
            command=self.update_table,
            padx=20,
            pady=10
        )
        self.refresh_button.pack(pady=30)

    def update_table(self):
        cryptos, errors = get_all_crypto_data()

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

        for item in self.tree.get_children():
            self.tree.delete(item)

        for index, crypto in enumerate(cryptos):
            tag = "even" if index % 2 == 0 else "odd"

            if crypto["change"] < 0:
                change_tag = "negative"
            else:
                change_tag = "positive"

            self.tree.insert(
                "",
                "end",
                values=(
                    crypto["symbol"],
                    f'{crypto["price"]:.4f}'.rstrip("0").rstrip("."),
                    f'{crypto["change"]:.2f}%'
                ),
                tags=(tag, change_tag)
            )

        current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        self.update_label.config(
            text=f"Последнее обновление: {current_time}"
        )

# columns = ("symbol", "price", "change")
#
# tree = ttk.Treeview(root, columns=columns, show="headings")
# style = ttk.Style()
# style.configure(
#     "Treeview",
#     rowheight=32,
#     font=("Arial", 11),
#     foreground="#333333"
# )
# # style.theme_use("clam")
#
# style.configure(
#     "Treeview.Heading",
#     font=("Arial", 11, "bold"),
#     background="#DCE6F1",
#     foreground="#333333"
# )
#
# style.configure(
#     "Treeview",
#     rowheight=32
# )
#
# style.configure(
#     "Treeview",
#     font=("Arial", 11)
# )
#
# style.configure(
#     "Treeview",
#     foreground="#333333"
# )
#
# tree.tag_configure("even", background="#F0F4F8")
# tree.tag_configure("odd", background="#FFFFFF")
#
# tree.tag_configure("negative", foreground="#CC3333")
# tree.tag_configure("positive", foreground="#008800")
#
# tree.heading("symbol", text="Криптовалюта")
# tree.heading("price", text="Цена (USDT)")
# tree.heading("change", text="Изменение за 24 ч.")
#
# tree.column("symbol", width=180, anchor="center")
# tree.column("price", width=160, anchor="e")
# tree.column("change", width=180, anchor="center")
#
# tree.pack(fill="both", expand=True, padx=10, pady=10)
#
# update_label = tk.Label(root, text="Последнее обновление: ещё не выполнялось")
# update_label.pack(pady=5)
#
# def update_table():
#     cryptos, errors = get_all_crypto_data()
#
#     if not cryptos:
#         messagebox.showerror(
#             "Ошибка",
#             "Не удалось получить данные о криптовалютах."
#         )
#         return
#
#     if errors:
#         messagebox.showwarning(
#             "Предупреждение",
#             "Не удалось получить данные по некоторым криптовалютам:\n"
#             + "\n".join(errors)
#         )
#
#     for item in tree.get_children():
#         tree.delete(item)
#
#     for index, crypto in enumerate(cryptos):
#         tag = "even" if index % 2 == 0 else "odd"
#
#         if crypto["change"] < 0:
#             change_tag = "negative"
#         else:
#             change_tag = "positive"
#
#         tree.insert(
#             "",
#             "end",
#             values=(
#                 crypto["symbol"],
#                 f'{crypto["price"]:.4f}'.rstrip("0").rstrip("."),
#                 f'{crypto["change"]:.2f}%'
#             ),
#             tags=(tag, change_tag)
#         )
#
#     current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
#     update_label.config(text=f"Последнее обновление: {current_time}")
#
# refresh_button = tk.Button(
#     root,
#     text="Обновить котировки",
#     command=update_table,
#     padx=20,
#     pady=10
# )
#
# refresh_button.pack(pady=30)
# update_table()
#
# def auto_update():
#     update_table()
#     root.after(10000, auto_update)
#
# root.after(10000, auto_update)

root = tk.Tk()
app = CryptoTracker(root)

root.after(100, app.update_table)

root.mainloop()