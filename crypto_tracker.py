
import requests
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkinter import messagebox
import threading
import queue

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


class CryptoTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Tracker")
        self.root.geometry("680x540")
        self.root.minsize(620, 500)
        self.root.configure(bg="#F3F5F8")

        self.is_updating = False
        self.result_queue = queue.Queue()

        self.create_widgets()

        self.root.after(50, self.check_queue)
        self.root.after(60000, self.auto_update)

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Modern.TCombobox",
            font=("Arial", 12),
            padding=8,
            fieldbackground="#FFFFFF",
            background="#FFFFFF",
            foreground="#202B3C",
            bordercolor="#DCE3EC",
            lightcolor="#DCE3EC",
            darkcolor="#DCE3EC",
            arrowcolor="#2878D0"
        )

        style.map(
            "Modern.TCombobox",
            fieldbackground=[("readonly", "#FFFFFF")],
            foreground=[("readonly", "#202B3C")]
        )

        style.configure(
            "Primary.TButton",
            font=("Arial", 11, "bold"),
            padding=(22, 12),
            background="#2878D0",
            foreground="#FFFFFF",
            borderwidth=0
        )

        style.map(
            "Primary.TButton",
            background=[
                ("active", "#1D65B3"),
                ("disabled", "#AABBD0")
            ],
            foreground=[("disabled", "#FFFFFF")]
        )

        header = tk.Frame(self.root, bg="#F3F5F8")
        header.pack(fill="x", padx=35, pady=(20, 12))

        brand = tk.Label(
            header,
            text="●  BINANCE MARKET DATA",
            font=("Arial", 9, "bold"),
            bg="#F3F5F8",
            fg="#2878D0"
        )
        brand.pack(pady=(0, 7))

        title = tk.Label(
            header,
            text="Crypto Tracker",
            font=("Arial", 23, "bold"),
            bg="#F3F5F8",
            fg="#202B3C"
        )
        title.pack()

        subtitle = tk.Label(
            header,
            text="Мониторинг криптовалютных котировок",
            font=("Arial", 10),
            bg="#F3F5F8",
            fg="#718096"
        )
        subtitle.pack(pady=(4, 0))

        card = tk.Frame(
            self.root,
            bg="#FFFFFF",
            highlightbackground="#E2E8F0",
            highlightthickness=1
        )

        card.pack(
            fill="both",
            expand=True,
            padx=45,
            pady=(8, 25)
        )

        select_label = tk.Label(
            card,
            text="КРИПТОВАЛЮТА",
            font=("Arial", 9, "bold"),
            bg="#FFFFFF",
            fg="#718096"
        )
        select_label.pack(pady=(25, 8))

        self.crypto_combo = ttk.Combobox(
            card,
            values=SYMBOLS,
            state="readonly",
            font=("Arial", 12),
            width=20,
            style="Modern.TCombobox"
        )

        self.crypto_combo.pack()
        self.crypto_combo.current(0)

        self.crypto_combo.bind(
            "<<ComboboxSelected>>",
            lambda event: self.update_table()
        )

        tk.Frame(
            card,
            height=1,
            bg="#E9EEF5"
        ).pack(fill="x", padx=35, pady=(25, 20))

        price_caption = tk.Label(
            card,
            text="ТЕКУЩАЯ ЦЕНА",
            font=("Arial", 9, "bold"),
            bg="#FFFFFF",
            fg="#718096"
        )
        price_caption.pack(pady=(0, 5))

        self.price_label = tk.Label(
            card,
            text="— USDT",
            font=("Arial", 27, "bold"),
            bg="#FFFFFF",
            fg="#202B3C"
        )
        self.price_label.pack()

        self.change_label = tk.Label(
            card,
            text="Изменение за 24 часа: —",
            font=("Arial", 12, "bold"),
            bg="#F1F5F9",
            fg="#64748B",
            padx=15,
            pady=9
        )
        self.change_label.pack(pady=18)

        self.update_label = tk.Label(
            card,
            text="Последнее обновление: ещё не выполнялось",
            font=("Arial", 9),
            bg="#FFFFFF",
            fg="#94A3B8"
        )
        self.update_label.pack(pady=(5, 18))

        self.refresh_button = ttk.Button(
            card,
            text="↻   Обновить котировку",
            command=self.update_table,
            style="Primary.TButton"
        )
        self.refresh_button.pack(pady=(3, 20))

    def update_table(self):
        if self.is_updating:
            return

        symbol = self.crypto_combo.get()

        self.is_updating = True
        self.refresh_button.config(state="disabled")

        threading.Thread(
            target=self.load_data,
            args=(symbol,),
            daemon=True
        ).start()

    def load_data(self, symbol):
        try:
            price, change = get_crypto_data(symbol)

            cryptos = [{
                "symbol": symbol,
                "price": price,
                "change": change
            }]

            errors = []

        except Exception as error:
            cryptos = []
            errors = [f"{symbol}: {error}"]

        self.result_queue.put((cryptos, errors))

    def check_queue(self):
        try:
            cryptos, errors = self.result_queue.get_nowait()

            self.is_updating = False
            self.refresh_button.config(state="normal")

            if not cryptos:
                messagebox.showerror(
                    "Ошибка",
                    "Не удалось получить данные о криптовалюте.\n"
                    + "\n".join(errors)
                )
                return

            crypto = cryptos[0]

            price = f'{crypto["price"]:,.4f}'.rstrip("0").rstrip(".")

            self.price_label.config(
                text=f"{price} USDT"
            )

            change = crypto["change"]

            self.change_label.config(
                text=f"Изменение за 24 часа: {change:+.2f}%"
            )

            if change < 0:
                self.change_label.config(
                    fg="#DC4545",
                    bg="#FDECEC"
                )
            else:
                self.change_label.config(
                    fg="#159767",
                    bg="#E8F7EF"
                )

            current_time = datetime.now().strftime(
                "%d.%m.%Y %H:%M:%S"
            )

            self.update_label.config(
                text=f"Последнее обновление: {current_time}"
            )

            if errors:
                messagebox.showwarning(
                    "Предупреждение",
                    "\n".join(errors)
                )

        except queue.Empty:
            pass

        finally:
            self.root.after(50, self.check_queue)

    def auto_update(self):
        self.update_table()
        self.root.after(60000, self.auto_update)


root = tk.Tk()
app = CryptoTracker(root)

root.after(50, app.update_table)

root.mainloop()
