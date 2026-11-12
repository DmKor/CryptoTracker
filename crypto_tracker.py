
import requests
import tkinter as tk
from tkinter import ttk
from datetime import datetime
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


def get_error_message(error):

    if isinstance(error, requests.exceptions.Timeout):
        return "Сервер не ответил вовремя. Попробуйте позже."

    elif isinstance(error, requests.exceptions.ConnectionError):
        return "Не удалось подключиться к серверу. Проверьте интернет."

    elif isinstance(error, requests.exceptions.HTTPError):

        response = error.response
        status_code = response.status_code

        if status_code >= 500:
            return "Сервер временно недоступен. Попробуйте позже."

        elif status_code == 400:
            try:
                error_data = response.json()

                if error_data.get("code") == -1121:
                    return "Выбрана неизвестная криптовалюта."

            except ValueError:
                pass

            return "Сервер отклонил запрос. Проверьте параметры."

        elif status_code == 404:
            return "Запрашиваемая котировка не найдена."

        else:
            return "Сервер отклонил запрос. Попробуйте позже."

    elif isinstance(error, (ValueError, KeyError)):
        return "Сервер вернул некорректные данные."

    else:
        return "Не удалось обновить котировку. Попробуйте позже."

class CryptoTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Tracker")
        self.root.geometry("680x620")
        self.root.minsize(620, 500)
        self.root.configure(bg="#F3F5F8")

        self.is_updating = False
        self.is_closing = False
        self.result_queue = queue.Queue()

        self.queue_check_id = None
        self.auto_update_id = None

        self.create_widgets()

        self.queue_check_id = self.root.after(50, self.check_queue)
        self.auto_update_id = self.root.after(60000, self.auto_update)

        self.root.protocol("WM_DELETE_WINDOW", self.close)

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

        # Баннер уведомлений

        # Зарезервированное место для баннера
        self.status_area = tk.Frame(
            card,
            bg="#FFFFFF",
            height=55
        )

        self.status_area.pack(
            fill="x",
            padx=20,
            pady=(15, 5)
        )

        self.status_area.pack_propagate(False)

        # Баннер уведомлений
        self.status_banner = tk.Frame(
            self.status_area,
            bg="#E8F7EF"
        )

        self.status_label = tk.Label(
            self.status_banner,
            text="",
            font=("Arial", 9),
            bg="#E8F7EF",
            fg="#159767",
            wraplength=500,
            justify="center",
            anchor="center"
        )

        self.status_label.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=8
        )

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

    def show_status(self, message, success=True):
        if success:
            bg_color = "#E8F7EF"
            text_color = "#159767"
        else:
            bg_color = "#FDECEC"
            text_color = "#DC4545"

        self.status_banner.config(bg=bg_color)

        self.status_label.config(
            text=message,
            bg=bg_color,
            fg=text_color
        )

        # Подбираем ширину баннера под текст
        self.status_area.update_idletasks()

        available_width = self.status_area.winfo_width() - 20

        self.status_label.config(
            wraplength=max(150, min(500, available_width - 28))
        )

        self.status_banner.update_idletasks()

        banner_width = min(
            self.status_banner.winfo_reqwidth(),
            available_width
        )

        banner_height = self.status_banner.winfo_reqheight()

        # Размещаем баннер по центру
        self.status_banner.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
            width=banner_width,
            height=banner_height
        )

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
            errors = [get_error_message(error)]

        self.result_queue.put((cryptos, errors))

    def check_queue(self):
        try:
            cryptos, errors = self.result_queue.get_nowait()

            self.is_updating = False
            self.refresh_button.config(state="normal")

            if not cryptos:
                self.show_status(
                    errors[0] if errors else "Не удалось получить данные.",
                    success=False
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
                self.show_status(
                    errors[0],
                    success=False
                )
            else:
                self.show_status(
                    f"Котировка {crypto['symbol']} успешно обновлена."
                )

        except queue.Empty:
            pass

        finally:

            if not self.is_closing:
                self.queue_check_id = self.root.after(

                    50, self.check_queue

                )

    def auto_update(self):
        if self.is_closing:
            return

        self.update_table()

        self.auto_update_id = self.root.after(
            60000, self.auto_update
        )

    def close(self):
        self.is_closing = True

        if self.queue_check_id is not None:
            self.root.after_cancel(self.queue_check_id)

        if self.auto_update_id is not None:
            self.root.after_cancel(self.auto_update_id)

        self.root.destroy()

root = tk.Tk()
app = CryptoTracker(root)

root.after(50, app.update_table)

root.mainloop()
